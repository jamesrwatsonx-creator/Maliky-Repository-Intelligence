"""Resumable bulk intake. Processes selected repositories independently."""
from __future__ import annotations

import argparse
import json

import registry as r
from review_extracted_batch import promote, prepare_repository_summary


def candidates(args):
    repos=r.records('repositories')
    if args.repo:
        names=set(args.repo); return [x for x in repos if x['full_name'] in names]
    if args.repository_summaries:
        # Empty-repository disposition is a separate state transition. These
        # entries have no pinned source to summarize, so do not let them occupy
        # every summary batch; retain them in the canonical queue for explicit
        # disposition handling.
        repos=[x for x in repos if x.get('repository_intelligence',{}).get('status')!='COMPLETE'
               and not (x.get('state')=='NEEDS_REVIEW' and x.get('next_phase')=='EMPTY_REPOSITORY_DISPOSITION')]
        return sorted(repos,key=lambda x:(x['full_name']==r.SELF,not bool(x.get('inspected_commit')),x.get('tree_files',0),x['github_id']))
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
    parser.add_argument('--repository-summaries',action='store_true',help='Prepare bounded purpose/cluster evidence without extracting assets')
    parser.add_argument('--summary-files',type=int,default=12)
    args=parser.parse_args()
    targets=candidates(args)[:args.limit]
    if args.dry_run:
        print(json.dumps([{'repository':x['full_name'],'state':x['state'],'next_phase':x.get('next_phase')} for x in targets],indent=2)); return
    output=[]
    for repo in targets:
        if args.repository_summaries:
            print('Preparing repository summary: '+repo['full_name'],flush=True)
            try: result=prepare_repository_summary(repo,args.summary_files)
            except (ValueError,RuntimeError,OSError) as exc: result={'repository':repo['full_name'],'error':str(exc)[:300]}
            output.append(result); continue
        result=r.ingest(repo['full_name'],snapshot=args.snapshot,
                        pinned=bool(args.pinned and repo.get('inspected_commit')))
        current=next(x for x in r.records('repositories') if x['id']==repo['id'])
        temporary_handoff=current.get('next_phase') in ('SEMANTIC_CENSUS_REVIEW','ENTITY_EXTRACTION','CAPABILITY_ANALYSIS')
        if not result.get('error') and not current.get('unread_source_files',0) and temporary_handoff:
            result['promotion']=promote(current)
        output.append(result)
    if args.repository_summaries:
        r.write('system/repository-summary-batch.json',{'prepared_at':r.now(),'results':output})
    stats=r.build(); validation=r.validate()
    print(json.dumps({'processed':len(output),'results':output,'statistics':stats,'validation':validation},indent=2))
    raise SystemExit(0 if validation['valid'] else 1)


if __name__=='__main__': main()
