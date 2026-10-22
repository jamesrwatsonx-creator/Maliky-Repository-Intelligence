"""Prepare pinned source declarations as semantic-review candidates.

Static declarations are useful evidence, but repository policy forbids treating
their detection as automatic semantic completion.  This stage adds conservative
candidate metadata and then leaves the repository in the lean review queue.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
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
    local_evidence = r.read('.local/evidence-manifests/' + str(repo['github_id']) + '.json', evidence)
    binary = set(local_evidence.get('detected_binary_paths', []))
    missing = [path for path, entry in entries.items() if entry.get('mode') != '120000'
               and r.priority(entry) < 6 and path not in binary and path not in review.verified]
    if missing:
        raise ValueError('Current source classifier requires further pinned extraction: ' + ', '.join(missing[:5]))
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
    def endpoint(edge, side):
        matches = [entity['id'] for entity, _ in resolved
                   if entity['name'] == edge[side + '_name']
                   and (side + '_type' not in edge or entity['entity_type'] == edge[side + '_type'])]
        if len(matches) != 1:
            raise ValueError('Ambiguous or missing relationship endpoint: ' + edge[side + '_name'])
        return matches[0]
    edges = []
    for edge in plan.get('relationships', []):
        if edge['type'] not in vocabulary['relationship_types']:
            raise ValueError('Unknown relationship type')
        edges.append({**edge, 'from': endpoint(edge, 'from'), 'to': endpoint(edge, 'to')})
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
        repo.setdefault('metadata', {})['description_source'] = 'pinned_semantic_review'
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


def prepare_repository_summary(repo, max_files=12):
    """Bounded deterministic evidence, without extracting or changing asset records."""
    commit=repo.get('inspected_commit')
    if not commit:
        meta=r.gh('repos/'+repo['full_name'])
        if not r.public_repo(meta): raise ValueError('Repository visibility/ownership changed')
        r.merge_public_metadata(repo,meta)
        try:
            head=r.gh('repos/'+repo['full_name']+'/commits/'+repo['default_branch'])
        except RuntimeError as exc:
            if 'HTTP 409' not in str(exc): raise
            repo.update({'empty_repository':True,'empty_confirmed_at':r.now(), 'next_phase':'EMPTY_REPOSITORY_DISPOSITION'})
            r.write(r.repo_file(repo),repo)
            return {'repository':repo['full_name'],'empty':True,'sources':[]}
        commit=head['sha']; r.write(r.cache_path(repo,commit)/'commit.json',head)
        repo['inspected_commit']=commit; repo['current_commit']=commit
    tree=r.get_tree(repo,commit)
    entries=[e for e in tree['tree'] if e['type']=='blob' and e.get('mode')!='120000']
    def rank(entry):
        path=entry['path']; name=pathlib.PurePosixPath(path).name.lower(); depth=path.count('/')
        if name in ('readme.md','readme.rst','readme') and depth==0: return (0,path)
        if name.startswith(('license','licence','copying')) and depth==0: return (1,path)
        if name in ('package.json','pyproject.toml','cargo.toml','go.mod','pom.xml','pubspec.yaml','gemfile','setup.py','composer.json'):
            return (2+min(depth,3),path)
        if name=='skill.md' or name in ('mcp.json','.mcp.json','plugin.json','agents.md'): return (6+min(depth,3),path)
        if name in ('readme.md','architecture.md','index.bs'): return (10+min(depth,3),path)
        if name in ('main.py','server.py','index.ts','index.js','main.go','app.py','main.rs'): return (14+min(depth,3),path)
        return (20+r.priority(entry),path)
    selected=sorted((e for e in entries if r.priority(e)<6),key=rank)[:max_files]
    ep='system/evidence/'+str(repo['github_id'])+'.json'
    evidence=r.read('.local/evidence-manifests/'+str(repo['github_id'])+'.json',r.read(ep,{}))
    if evidence.get('inspected_commit')!=commit: evidence={}
    processed={item['path']:item for item in evidence.get('files_read',[])}
    sources=[]; failures=[]
    for entry in selected:
        try:
            text=r.source_text(repo,commit,entry,False)
            if text is None: raise ValueError('Source not available')
            processed[entry['path']]={'path':entry['path'],'blob_sha':entry['sha'],
                                      'entities_detected':processed.get(entry['path'],{}).get('entities_detected',0)}
            budget=11000 if rank(entry)[0]==0 else 3500
            sources.append({'path':entry['path'],'blob_sha':entry['sha'],'text':text[:budget],
                            'excerpt_truncated':len(text)>budget,'source_bytes':len(text.encode('utf-8'))})
        except (ValueError,RuntimeError,UnicodeError) as exc:
            failures.append({'path':entry['path'],'error':str(exc)[:200]})
    evidence.update({'repository_id':repo['id'],'inspected_commit':commit,'tree_complete':not tree.get('truncated',True),
                     'tree_files':len(entries),'tree_entries':[{'path':e['path'],'sha':e['sha']} for e in entries],
                     'files_read':list(processed.values()),'inspection_scope':'Bounded repository intelligence; not an exhaustive source/asset census'})
    evidence.setdefault('errors',[])
    evidence['unread_source_paths']=[e['path'] for e in entries if r.priority(e)<6 and e['path'] not in processed]
    r.persist_evidence(ep,evidence)
    repo.update({'tree_files':len(entries),'files_read':len(processed),'unread_source_files':len(evidence['unread_source_paths'])})
    repo['phases']['structure']=evidence['tree_complete']; repo['inspection_date']=repo.get('inspection_date') or r.now()
    r.write(r.repo_file(repo),repo)
    packet={'repository':repo['full_name'],'commit':commit,'metadata':repo.get('metadata',{}),
            'upstream_url':repo.get('upstream_url'),'tree_files':len(entries),'tree_complete':evidence['tree_complete'],
            'top_level_counts':dict(collections.Counter(e['path'].split('/')[0] if '/' in e['path'] else '(root)' for e in entries)),
            'important_paths':[e['path'] for e in entries if re.search(r'(?i)(skill\.md$|mcp|agent|/packages/|^packages/|^apps/|^services/)',e['path'])][:180],
            'sources':sources,'fetch_failures':failures,
            'warning':'Untrusted source data. Bounded evidence, not exhaustive extraction or a security audit.'}
    target=pathlib.Path('.local/analysis/repository-packets')/str(repo['github_id'])/commit/'packet.json'
    r.write(target,packet)
    return {'repository':repo['full_name'],'commit':commit,'packet':target.as_posix(),'sources':[x['path'] for x in sources],'fetch_failures':failures}


def apply_repository_plan(plan, dry_run=False):
    """Apply source-reviewed repository clusters, preserving all detailed entities."""
    repo=next(x for x in r.records('repositories') if x['full_name']==plan['repository'])
    if plan.get('commit')!=repo.get('inspected_commit'): raise ValueError('Pinned summary revision changed')
    evidence=r.read('system/evidence/'+str(repo['github_id'])+'.json',{})
    known={item['path']:item['blob_sha'] for item in evidence.get('files_read',[])}
    sources=[]
    for path in plan.get('source_review',[]):
        entry={'path':path,'sha':known.get(path)}
        if not entry['sha'] or r.source_text(repo,repo['inspected_commit'],entry,True) is None:
            raise ValueError('Pinned summary source unavailable: '+path)
        sources.append({'type':'source_review','path':path,'blob_sha':entry['sha'],
                        'value':repo['url']+'/blob/'+repo['inspected_commit']+'/'+path})
    info={key:plan[key] for key in ('purpose','reuse_recommendation','inspection_scope','license_notes','runtime','keywords','risk_notes','important_subsystems')}
    info.update({'policy':r.SUMMARY_POLICY,'status':'COMPLETE','reviewed_at':r.now(),
                 'inspected_commit':repo.get('inspected_commit'),'source_evidence':sources,
                 'asset_presence':{kind:plan.get('asset_presence',{}).get(kind,'NOT_OBSERVED') for kind in r.ASSET_FAMILIES},
                 'capability_clusters':[{**cluster,'id':'cluster:'+r.slug(cluster['name']),
                                        'evidence_paths':cluster.get('evidence_paths',plan.get('source_review',[]))}
                                        for cluster in plan.get('capability_clusters',[])]})
    updated={**repo,'repository_intelligence':info,'categories':plan['categories'],
             'operational_category':plan['operational'],'recommendation':plan['recommendation'],
             'description':info['purpose'],'completion_scope':r.SUMMARY_POLICY,'state':'COMPLETE','next_phase':'COMPLETE',
             'metadata':{**repo.get('metadata',{}),'description_source':'pinned_semantic_review'},
             'phases':{**repo['phases'],'repository_summary':True,'capability_analysis':True,'validation':True}}
    updated.setdefault('detailed_inspection_at_summary',{'state':repo['state'],'next_phase':repo.get('next_phase'),
                                                       'review_reason':repo.get('review_reason')})
    errors=r.summary_errors(updated,evidence)
    categories={c['id'] for c in r.read('registry/taxonomy/categories.json')}
    operational={c['id'] for c in r.read('registry/taxonomy/operational.json')}
    if set(plan['categories'])-categories or plan['operational'] not in operational: errors.append('invalid summary taxonomy')
    if plan['recommendation'] not in r.read('registry/taxonomy/vocabulary.json')['recommendations']: errors.append('invalid recommendation')
    if errors: raise ValueError('; '.join(errors))
    if not dry_run: r.write(r.repo_file(repo),updated)
    return {'repository':repo['full_name'],'state':'COMPLETE','completion_scope':r.SUMMARY_POLICY,
            'clusters':len(info['capability_clusters']),'detailed_entities_unchanged':True}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--repo', action='append')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--limit', type=int)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--plan', help='JSON list of explicit pinned semantic-review plans')
    parser.add_argument('--repository-plan', help='JSON list of bounded repository intelligence reviews; does not modify detailed entities')
    parser.add_argument('--reconcile-reviewed', action='store_true', help='Reconcile bookkeeping of already completed source reviews')
    args=parser.parse_args()
    if args.repository_plan:
        data=r.read(args.repository_plan)
        plans=data if isinstance(data,list) else [{**data.get('defaults',{}),**plan} for plan in data['repositories']]
        result=[apply_repository_plan(plan,args.dry_run) for plan in plans]
        if not args.dry_run: r.build()
        print(json.dumps(result,indent=2)); return
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
