"""Idempotent deterministic entrypoint for one owned repository or fork."""
from __future__ import annotations

import argparse
import json
import re

import registry as r
from review_extracted_batch import promote


def identity(value):
    value=value.strip().rstrip('/')
    match=re.fullmatch(r'(?:https?://github\.com/)?([^/\s]+)/([^/\s#]+)',value)
    if not match: raise ValueError('Expected owner/repository or GitHub repository URL')
    return match.group(1)+'/'+match.group(2).removesuffix('.git')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repository')
    parser.add_argument('--structure-only',action='store_true')
    parser.add_argument('--snapshot',action='store_true')
    parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args()
    full_name=identity(args.repository)
    if args.dry_run:
        print(json.dumps({'repository':full_name,'dry_run':True})); return
    repo=r.intake_record(full_name)
    if repo is None:
        print(json.dumps({'repository':'PRIVATE_REDACTED','status':'LOCAL_ONLY'})); return
    result=r.ingest(repo['full_name'],structure_only=args.structure_only,snapshot=args.snapshot)
    repo=next(x for x in r.records('repositories') if x['id']==repo['id'])
    if not args.structure_only and not result.get('error') and not repo.get('unread_source_files',0):
        result['promotion']=promote(repo)
    r.build()
    result['validation']=r.validate()['valid']
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
