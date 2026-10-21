"""Prepare pinned source declarations as semantic-review candidates.

Static declarations are useful evidence, but repository policy forbids treating
their detection as automatic semantic completion.  This stage adds conservative
candidate metadata and then leaves the repository in the lean review queue.
"""
from __future__ import annotations

import argparse
import collections
import json
from decision_engine import DecisionEngine
import registry as r


CATEGORY = {
    'SKILL':'category:skills', 'MCP_SERVER':'category:mcp-servers',
    'TOOL':'category:developer-tools', 'PLUGIN':'category:plugins-extensions',
    'AGENT':'category:ai-agents', 'AGENT_FRAMEWORK':'category:agent-frameworks',
    'WORKFLOW':'category:agent-workflows', 'PROMPT':'category:prompt-libraries',
    'PROMPT_LIBRARY':'category:prompt-libraries', 'API':'category:apis',
    'SDK':'category:sdks-client-libraries', 'CLI':'category:cli-tools',
    'PACKAGE':'category:libraries-packages', 'LIBRARY':'category:libraries-packages',
    'UI_COMPONENT':'category:frontend-applications', 'COMPONENT':'category:developer-tools',
    'SERVICE':'category:backend-services', 'MODEL':'category:machine-learning-models',
    'MODEL_ADAPTER':'category:llm-projects', 'INFRASTRUCTURE_MODULE':'category:cloud-infrastructure',
    'TEMPLATE':'category:templates-boilerplates', 'DOCUMENTATION_ASSET':'category:documentation',
    'DESIGN_REFERENCE':'category:design-systems', 'CONNECTOR':'category:apis',
    'INTEGRATION':'category:ai-orchestration',
}

RECOMMENDATION = {
    'SKILL':'USE DIRECTLY', 'MCP_SERVER':'USE DIRECTLY', 'TOOL':'USE DIRECTLY',
    'PLUGIN':'USE DIRECTLY', 'AGENT':'USE DIRECTLY', 'AGENT_FRAMEWORK':'USE DIRECTLY',
    'WORKFLOW':'COMBINE', 'PROMPT':'REFERENCE', 'PROMPT_LIBRARY':'REFERENCE',
    'API':'INTEGRATE VIA API', 'SDK':'USE AS LIBRARY', 'CLI':'USE DIRECTLY',
    'PACKAGE':'USE AS LIBRARY', 'LIBRARY':'USE AS LIBRARY', 'UI_COMPONENT':'EXTRACT',
    'COMPONENT':'EXTRACT', 'SERVICE':'INTEGRATE AS SERVICE', 'MODEL':'REFERENCE',
    'MODEL_ADAPTER':'WRAP', 'INFRASTRUCTURE_MODULE':'EXTRACT', 'TEMPLATE':'REFERENCE',
    'DOCUMENTATION_ASSET':'REFERENCE', 'DESIGN_REFERENCE':'REFERENCE',
    'CONNECTOR':'INTEGRATE VIA API', 'INTEGRATION':'COMBINE',
}


def cap_slug(repo, entity):
    return r.slug(repo['name']+' '+entity['entity_type']+' '+entity['name'])[:110]


def promote(repo, dry_run=False):
    if repo.get('unread_source_files', 0):
        return {'repository':repo['full_name'],'skipped':'source coverage incomplete'}
    evidence = r.read('system/evidence/'+str(repo['github_id'])+'.json', {})
    unresolved_errors = [error for error in evidence.get('errors', []) if not error.get('review_resolution')]
    known = {f['path']: f['blob_sha'] for f in evidence.get('files_read', [])}
    entities = [e for e in r.records('entities') if e['source']['repository_id']==repo['id'] and e['source']['inspected_commit']==repo['inspected_commit']]
    # A complete read with no declaration candidates is not evidence that the
    # repository has no reusable assets. Model cards, reference collections,
    # architecture templates and similar repositories routinely require a
    # semantic entity to be added from source review. Keep them in the review
    # queue until that explicit disposition exists.
    if not entities:
        repo.update({
            'state':'NEEDS_REVIEW',
            'next_phase':'SEMANTIC_CENSUS_REVIEW',
            'recommendation':'NEEDS DEEPER REVIEW',
            'review_reason':'No static entity declarations were detected; semantic zero-entity disposition required.',
            'semantic_review_progress':{
                'status':'PENDING',
                'reason':'zero_static_entities',
                'review_policy':'LEAN',
            },
        })
        repo.setdefault('phases',{}).update({
            'entity_extraction':False,
            'capability_analysis':False,
            'validation':False,
        })
        if not dry_run:
            r.write(r.repo_file(repo),repo)
        return {'repository':repo['full_name'],'promoted':0,'deferred':0,
                'state':repo['state'],'review_required':'zero_static_entities'}
    engine = DecisionEngine()
    engine.decide(repo['id'], 'ENTITY_TYPE', ['KEEP','ESCALATE_FOR_REVIEW'],
                  {'commit':repo['inspected_commit'],'entities':len(entities)})
    promoted = 0; deferred = []
    for entity in entities:
        source = entity['source']
        if known.get(source['source_path']) != source['blob_sha']:
            deferred.append(entity['id']); continue
        description = (entity.get('description') or '').strip()
        # This conservative fallback is a fact about the source declaration, not
        # a claim about runtime behavior.  The name/path remains searchable.
        if not description:
            description = f"Source-declared {entity['entity_type'].replace('_',' ').lower()} `{entity['name']}`."
        slug = cap_slug(repo, entity); cap_id='capability:'+slug
        category = CATEGORY.get(entity['entity_type'], 'category:developer-tools')
        recommendation = RECOMMENDATION.get(entity['entity_type'], 'REFERENCE')
        entity.update({
            'description':description,
            'review_status':'NEEDS_REVIEW',
            'categories':sorted(set(entity.get('categories',[])+[category])),
            'capabilities':sorted(set(entity.get('capabilities',[])+[cap_id])),
            'recommendation':'NEEDS DEEPER REVIEW',
            'metadata':{**entity.get('metadata',{}), 'review_policy':'LEAN',
                        'standalone':'PARTIAL',
                        'semantic_review':'Static source-declaration candidate; semantic review pending.',
                        'candidate_recommendation':recommendation},
        })
        capability = r.read('registry/capabilities/'+slug+'.json') or {
            'id':cap_id, 'name':entity['name'], 'aliases':[entity['name'].lower()],
            'status':'CANDIDATE', 'verification_scope':'Pinned source declaration; semantic review pending',
            'providers':[], 'evidence':entity['evidence'],
        }
        capability['providers']=sorted(set(capability.get('providers',[])+[entity['id']]))
        if not dry_run:
            r.write('registry/entities/'+entity['id'].split(':',1)[1]+'.json',entity)
            r.write('registry/capabilities/'+slug+'.json',capability)
        promoted += 1
    if deferred:
        repo.update({'state':'NEEDS_REVIEW','next_phase':'CAPABILITY_ANALYSIS',
                     'review_reason':'Source evidence does not cover one or more extracted entities.',
                     'semantic_review_progress':{'status':'BLOCKED','reason':'missing_source_evidence','entity_ids':deferred}})
    else:
        counts=collections.Counter(e['entity_type'] for e in entities)
        for kind, census in list(repo.setdefault('entity_census',{}).items()):
            count=counts[kind]
            repo['entity_census'][kind]={**census,'detected':max(census.get('detected',0),count),'catalogued':count,'reviewed':False,'detection_scope':'pinned source declarations; semantic review pending'}
        for kind, count in counts.items():
            if kind not in repo['entity_census']:
                repo['entity_census'][kind]={'detected':count,'catalogued':count,'reviewed':False,'detection_scope':'pinned source declarations; semantic review pending'}
        reason = 'source_parse_errors' if unresolved_errors else 'static_candidates_require_semantic_review'
        next_phase = 'SOURCE_EVIDENCE_REVIEW' if unresolved_errors else 'CAPABILITY_ANALYSIS'
        repo.update({'state':'NEEDS_REVIEW','next_phase':next_phase,
                     'capabilities':sorted({c for e in entities for c in (r.read('registry/entities/'+e['id'].split(':',1)[1]+'.json') or e).get('capabilities',[])}),
                     'recommendation':'NEEDS DEEPER REVIEW',
                     'review_reason':'Static declarations were prepared as candidates; lean semantic review is still required.',
                     'semantic_review_progress':{'status':'PENDING','review_policy':'LEAN','reason':reason,
                                                 'candidate_entity_count':len(entities),
                                                 'source_errors':unresolved_errors},
        })
        repo.setdefault('phases',{}).update({'structure':True,'entity_extraction':False,'capability_analysis':False,'validation':False})
        repo.setdefault('deep_review',{}).setdefault('completed',False)
    if not dry_run:
        r.write(r.repo_file(repo),repo)
    return {'repository':repo['full_name'],'candidates_prepared':promoted,'deferred':len(deferred),'state':repo['state'],
            'review_required':'semantic' if not deferred else 'source_evidence'}


def apply_review_plan(plan, dry_run=False):
    """Apply explicit source-reviewed decisions, never infer approval from detection.

    A plan covers one pinned repository, every existing candidate, independent
    additions, census exclusions and any scoped risk conclusion. Preflight all
    source identities and decisions before writing canonical records.
    """
    from lean_review_lib import LeanReview

    review = LeanReview(plan['repository'], plan['commit'])
    repo = review.repo
    evidence = r.read('system/evidence/' + str(repo['github_id']) + '.json', {})
    if (not evidence.get('tree_complete') or repo.get('unread_source_files')
            or evidence.get('unread_source_paths')
            or any(not error.get('review_resolution') for error in evidence.get('errors', []))):
        raise ValueError('Source coverage must be reconciled before semantic completion')
    if not plan.get('coverage_note') or not plan.get('source_review'):
        raise ValueError('Explicit architecture/census review and source evidence required')
    tree = r.read(r.cache_path(repo, review.commit) / 'tree.json', {})
    if tree.get('truncated', True):
        raise ValueError('Full pinned tree missing')
    entries = {e['path']: e for e in tree['tree'] if e['type'] == 'blob'}
    existing = {e['id']: e for e in review.existing}
    vocabulary = r.read('registry/taxonomy/vocabulary.json')
    category_ids = {c['id'] for c in r.read('registry/taxonomy/categories.json')}
    operational_ids = {c['id'] for c in r.read('registry/taxonomy/operational.json')}
    resolved = []
    covered = set()
    for explicit in plan['entities']:
        item = {**plan.get('entity_defaults', {}), **explicit}
        if 'capability' in item:
            item['capabilities'] = [[r.slug(item['capability']), item['capability'], item.get('aliases', [item['name']])]]
        entity = review.make(item['type'], item['name'], item['path'], item.get('line', 1))
        if entity['id'] in covered:
            raise ValueError('Duplicate decision: ' + entity['id'])
        covered.add(entity['id'])
        if (not item.get('description') or not item.get('capabilities')
                or item.get('standalone') not in ('YES', 'PARTIAL', 'NO')
                or 'dependencies' not in item or not item.get('overlap')):
            raise ValueError('Incomplete lean fields: ' + item['name'])
        if item['type'] not in vocabulary['entity_types']:
            raise ValueError('Unknown entity type')
        if item['recommendation'] not in vocabulary['recommendations']:
            raise ValueError('Unknown recommendation')
        resolved.append((existing.get(entity['id'], entity), item))
    excluded = list(plan.get('exclude', []))
    for group in plan.get('exclude_groups', []):
        if not group.get('path_prefix') or not group.get('reason'):
            raise ValueError('Explicit exclusion prefix and rationale required')
        excluded.extend({'id': e['id'], 'reason': group['reason']} for e in review.existing
                        if e['source']['source_path'].startswith(group['path_prefix']) and e['id'] not in covered)
    prior_excluded = {item['id']: item['reason'] for item in
                      repo.get('semantic_review_progress', {}).get('excluded_candidates', [])}
    for item in excluded:
        if ((item['id'] not in existing and prior_excluded.get(item['id']) != item.get('reason'))
                or item['id'] in covered or not item.get('reason')):
            raise ValueError('Invalid exclusion: ' + item['id'])
        covered.add(item['id'])
    if set(existing) - covered:
        raise ValueError('Plan omits existing candidates: ' + ', '.join(sorted(set(existing) - covered)))
    for item in [plan] + [item for _, item in resolved]:
        if set(item.get('categories', plan['categories'])) - category_ids:
            raise ValueError('Unknown categories')
        if item.get('operational', plan['operational']) not in operational_ids:
            raise ValueError('Unknown operational category')
    paths = set(plan['source_review']) | {item['path'] for _, item in resolved}
    named = {entity['name']: entity['id'] for entity, _ in resolved}
    edges = []
    for edge in plan.get('relationships', []):
        if edge['type'] not in vocabulary['relationship_types']:
            raise ValueError('Unknown relationship type')
        edges.append({**edge, 'from': named[edge['from_name']], 'to': named[edge['to_name']]})
        paths.add(edge['path'])
    scoped = plan.get('scoped_review')
    if scoped:
        if not scoped.get('triggers') or not scoped.get('conclusion') or not scoped.get('paths'):
            raise ValueError('Scoped review requires triggers, evidence and conclusion')
        paths.update(scoped['paths'])
    for path in paths:
        if path not in entries or review.verified.get(path) != entries[path]['sha']:
            raise ValueError('Source not covered by pinned evidence: ' + path)
        if r.source_text(repo, review.commit, entries[path], True) is None:
            raise ValueError('Pinned source unavailable: ' + path)
    if not resolved and not plan.get('zero_entity_rationale'):
        raise ValueError('Zero entities require explicit semantic disposition')
    if dry_run:
        return {'repository': review.full_name, 'retained': len(resolved), 'excluded': len(excluded), 'valid_plan': True}
    for entity, item in resolved:
        review.finish(entity, item['description'], item['capabilities'], item['recommendation'],
                      item.get('operational', plan['operational']), item.get('role', 'MODULE'),
                      item['standalone'], item['dependencies'], item['overlap'],
                      item.get('categories', plan['categories']), item.get('studios', plan.get('studios', [])),
                      item.get('ideas', []), extra={
                          'language': repo.get('metadata', {}).get('language'),
                          'license': repo.get('metadata', {}).get('license'),
                          **item.get('metadata', {}),
                      })
    for item in excluded:
        if item['id'] not in existing:
            continue
        entity = existing[item['id']]
        r.write(r.cache_path(repo, review.commit) / 'excluded-entities' / (entity['id'].split(':')[1] + '.json'),
                {'entity': entity, 'reason': item['reason'], 'reviewed_at': r.now()})
        review.drop(entity)
    for edge in edges:
        review.relate(edge['type'], edge['from'], edge['to'], edge['path'], edge.get('line', 1))
    if scoped:
        repo['deep_review'] = {'completed': not plan.get('blocker'), 'required': bool(plan.get('blocker')),
                               'reviewer': 'Source-reviewed cohort decision', 'conclusion': scoped['conclusion'],
                               'evidence': [{'type': 'source_review', 'value': review.url(path)} for path in scoped['paths']],
                               'runtime_tested': False}
        repo['phases']['deep_review'] = not plan.get('blocker')
    if not resolved:
        repo['zero_entity_disposition'] = {'rationale': plan['zero_entity_rationale'],
                                         'evidence': [{'type': 'source_review', 'value': review.url(path)} for path in paths]}
    if plan.get('description'):
        repo['description'] = plan['description']
    result = review.finalize(plan['categories'], plan.get('studios', []), plan['recommendation'],
                             plan['operational'], {kind: plan['coverage_note'] for kind in repo['entity_census']},
                             details=plan.get('implementation_details', []), blocker=plan.get('blocker', ''))
    repo['semantic_review_progress'].update({'reviewer': 'Source-reviewed cohort decision',
                                           'coverage_note': plan['coverage_note'],
                                           'source_review': [{'path': path, 'blob_sha': entries[path]['sha']} for path in sorted(paths)],
                                           'excluded_candidates': excluded})
    r.write(r.repo_file(repo), repo)
    return result


def reconcile_completed_review(repo):
    """Finish legacy review bookkeeping only when substantive review is complete."""
    progress = repo.get('semantic_review_progress', {})
    if (repo['state'] == 'COMPLETE' or repo.get('next_phase') != 'CAPABILITY_ANALYSIS'
            or progress.get('status') != 'COMPLETE' or not progress.get('scoped_deep_review')):
        return None
    evidence = r.read('system/evidence/' + str(repo['github_id']) + '.json', {})
    entities = [e for e in r.records('entities') if e['source']['repository_id'] == repo['id']
                and e['source']['inspected_commit'] == repo['inspected_commit']]
    counts = collections.Counter(e['entity_type'] for e in entities)
    if (not entities or not evidence.get('tree_complete') or evidence.get('unread_source_paths')
            or any(not error.get('review_resolution') for error in evidence.get('errors', []))
            or any(e['review_status'] != 'VERIFIED' or not e['description'] or not e['capabilities'] for e in entities)
            or len(entities) != progress.get('final_entity_count')
            or any(c['catalogued'] != counts[kind] or (c['detected'] and not c['reviewed'])
                   for kind, c in repo['entity_census'].items())):
        return None
    # Earlier reviewers reconciled populated families but left untouched zero
    # families false. Preserve their exclusions and full source review verbatim.
    for kind, census in repo['entity_census'].items():
        if not census['detected'] and not census['catalogued']:
            census.update({'reviewed': True, 'lean_review_note':
                           'No independent assets in this family in the completed pinned semantic census.'})
    repo.update({'state': 'COMPLETE', 'next_phase': 'COMPLETE'})
    repo['phases'].update({'entity_extraction': True, 'capability_analysis': True, 'validation': True, 'deep_review': True})
    repo['deep_review'] = {'completed': True, 'reviewer': progress.get('reviewer'),
                           'conclusion': progress['scoped_deep_review'], 'runtime_tested': False,
                           'evidence': list({(x['type'], x['value']): x for e in entities for x in e['evidence']}.values())}
    progress['bookkeeping_reconciled_at'] = r.now()
    r.write(r.repo_file(repo), repo)
    return {'repository': repo['full_name'], 'entities': len(entities), 'state': 'COMPLETE',
            'action': 'Preserved completed source review; reconciled zero-family census and scoped-review fields'}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--repo', action='append')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--limit', type=int)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--plan', help='JSON list of explicit pinned semantic-review plans')
    parser.add_argument('--reconcile-reviewed', action='store_true', help='Reconcile bookkeeping of already completed source reviews')
    args=parser.parse_args()
    if args.reconcile_reviewed:
        result = [result for repo in r.records('repositories') if (result := reconcile_completed_review(repo))]
        r.build()
        print(json.dumps(result, indent=2))
        return
    if args.plan:
        plans = r.read(args.plan)
        result = [apply_review_plan(plan, args.dry_run) for plan in plans]
        if not args.dry_run:
            r.build()
        print(json.dumps(result, indent=2))
        return
    wanted=set(args.repo or [])
    repos=[x for x in r.records('repositories') if (not wanted or x['full_name'] in wanted)]
    if args.all:
        repos=[x for x in repos if x['state'] in ('PARTIAL','STRUCTURE_COMPLETE','ENTITY_EXTRACTION_COMPLETE') and not x.get('unread_source_files',0)]
    if args.limit is not None: repos=repos[:args.limit]
    result=[promote(repo,args.dry_run) for repo in repos]
    if not args.dry_run: r.build()
    print(__import__('json').dumps(result,indent=2))


if __name__=='__main__': main()
