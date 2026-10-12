"""Requeue false zero-entity completions for explicit lean semantic review."""
from __future__ import annotations

import json
import registry as r


def main():
    changed=[]
    for repo in r.records('repositories'):
        if repo.get('state')!='COMPLETE' or repo.get('entity_count',0) or repo.get('zero_entity_disposition'):
            continue
        repo.update({
            'state':'NEEDS_REVIEW',
            'next_phase':'SEMANTIC_CENSUS_REVIEW',
            'recommendation':'NEEDS DEEPER REVIEW',
            'review_reason':'No canonical entities were recorded; explicit semantic disposition is required.',
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
        for kind,census in repo.get('entity_census',{}).items():
            repo['entity_census'][kind]={**census,'reviewed':False,
                'lean_review_note':'Explicit semantic zero-entity disposition pending'}
        r.write(r.repo_file(repo),repo)
        changed.append(repo['full_name'])
    r.build()
    print(json.dumps({'requeued':len(changed),'repositories':changed},indent=2))


if __name__=='__main__':
    main()
