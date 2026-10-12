"""Prepare pinned source declarations as semantic-review candidates.

Static declarations are useful evidence, but repository policy forbids treating
their detection as automatic semantic completion.  This stage adds conservative
candidate metadata and then leaves the repository in the lean review queue.
"""
from __future__ import annotations

import argparse
import collections
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


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--repo', action='append')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--limit', type=int)
    parser.add_argument('--dry-run', action='store_true')
    args=parser.parse_args()
    wanted=set(args.repo or [])
    repos=[x for x in r.records('repositories') if (not wanted or x['full_name'] in wanted)]
    if args.all:
        repos=[x for x in repos if x['state'] in ('PARTIAL','STRUCTURE_COMPLETE','ENTITY_EXTRACTION_COMPLETE') and not x.get('unread_source_files',0)]
    if args.limit is not None: repos=repos[:args.limit]
    result=[promote(repo,args.dry_run) for repo in repos]
    if not args.dry_run: r.build()
    print(__import__('json').dumps(result,indent=2))


if __name__=='__main__': main()
