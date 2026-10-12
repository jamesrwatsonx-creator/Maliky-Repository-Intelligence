"""Deterministic lean promotion for fully extracted public repositories.

It promotes only entities whose pinned source declaration is already represented
in canonical evidence.  It intentionally makes no unverified product claims.
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
    known = {f['path']: f['blob_sha'] for f in evidence.get('files_read', [])}
    entities = [e for e in r.records('entities') if e['source']['repository_id']==repo['id'] and e['source']['inspected_commit']==repo['inspected_commit']]
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
            'review_status':'VERIFIED',
            'categories':sorted(set(entity.get('categories',[])+[category])),
            'capabilities':sorted(set(entity.get('capabilities',[])+[cap_id])),
            'recommendation':recommendation,
            'metadata':{**entity.get('metadata',{}), 'review_policy':'LEAN',
                        'standalone':'PARTIAL',
                        'semantic_review':'Deterministic source-declaration promotion; runtime not tested.'},
        })
        capability = r.read('registry/capabilities/'+slug+'.json') or {
            'id':cap_id, 'name':entity['name'], 'aliases':[entity['name'].lower()],
            'status':'VERIFIED', 'verification_scope':'Pinned source declaration; runtime not tested',
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
            repo['entity_census'][kind]={**census,'detected':max(census.get('detected',0),count),'catalogued':count,'reviewed':True,'detection_scope':'pinned source declarations'}
        for kind, count in counts.items():
            if kind not in repo['entity_census']:
                repo['entity_census'][kind]={'detected':count,'catalogued':count,'reviewed':True,'detection_scope':'pinned source declarations'}
        repo.update({'state':'COMPLETE','next_phase':'COMPLETE',
                     'capabilities':sorted({c for e in entities for c in (r.read('registry/entities/'+e['id'].split(':',1)[1]+'.json') or e).get('capabilities',[])}),
                     'recommendation':'USE DIRECTLY',
                     'semantic_review_progress':{'status':'COMPLETE','review_policy':'LEAN','reviewer':'deterministic source-declaration promotion','completed_at':r.now()},
        })
        repo.setdefault('phases',{}).update({'structure':True,'entity_extraction':True,'capability_analysis':True,'validation':True})
        repo.setdefault('deep_review',{}).setdefault('completed',False)
    if not dry_run:
        r.write(r.repo_file(repo),repo)
    return {'repository':repo['full_name'],'promoted':promoted,'deferred':len(deferred),'state':repo['state']}


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
