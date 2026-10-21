"""Resumable bulk intake. Processes selected repositories independently."""
from __future__ import annotations

import argparse
import json

import registry as r
from review_extracted_batch import promote


def candidates(args):
    repos=r.records('repositories')
    if args.repo:
        names=set(args.repo); return [x for x in repos if x['full_name'] in names]
    allowed=('PARTIAL','STRUCTURE_COMPLETE','ENTITY_EXTRACTION_COMPLETE','DISCOVERED')
    repos=[x for x in repos if x['state'] in allowed and x['full_name']!=r.SELF]
    if args.priority:
        rank={'PARTIAL':0,'STRUCTURE_COMPLETE':1,'ENTITY_EXTRACTION_COMPLETE':2,'DISCOVERED':3}
        repos.sort(key=lambda x:(rank.get(x['state'],9),x.get('tree_files',0),x['github_id']))
    else: repos.sort(key=lambda x:x['github_id'])
    return repos


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    selector=parser.add_mutually_exclusive_group(required=False)
    selector.add_argument('--all',action='store_true')
    selector.add_argument('--repo',action='append')
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--limit',type=int,default=25)
    parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--priority',action='store_true')
    parser.add_argument('--snapshot',action='store_true')
    parser.add_argument('--pinned',action='store_true',help='Resume the inspected revision instead of moving an unfinished review to live HEAD.')
    parser.add_argument('--retry-jev',action='store_true')
    args=parser.parse_args()
    targets=candidates(args)[:args.limit]
    if args.dry_run:
        print(json.dumps([{'repository':x['full_name'],'state':x['state'],'next_phase':x.get('next_phase')} for x in targets],indent=2)); return
    output=[]
    for repo in targets:
        if args.pinned and repo.get('inspected_commit'):
            if args.snapshot:
                tree=r.get_tree(repo,repo['inspected_commit'])
                r.cache_snapshot(repo,repo['inspected_commit'],[e for e in tree['tree'] if e['type']=='blob' and e.get('mode')!='120000'])
            result=r.ingest(repo['full_name'],offline=True)
        else:
            result=r.ingest(repo['full_name'],snapshot=args.snapshot)
        current=next(x for x in r.records('repositories') if x['id']==repo['id'])
        temporary_handoff=current.get('next_phase') in ('SEMANTIC_CENSUS_REVIEW','ENTITY_EXTRACTION','CAPABILITY_ANALYSIS')
        if not result.get('error') and not current.get('unread_source_files',0) and temporary_handoff:
            result['promotion']=promote(current)
        output.append(result)
    stats=r.build(); validation=r.validate()
    print(json.dumps({'processed':len(output),'results':output,'statistics':stats,'validation':validation},indent=2))
    raise SystemExit(0 if validation['valid'] else 1)


if __name__=='__main__': main()
