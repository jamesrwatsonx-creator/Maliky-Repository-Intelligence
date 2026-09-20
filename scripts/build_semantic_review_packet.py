"""Gather cached source plus optional native reports without changing the registry."""
import argparse,json,pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from analysis.pipeline import analyze,build_packet
import registry as r

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('repository');p.add_argument('--max-bytes',type=int,default=80000)
    p.add_argument('--report',nargs=3,action='append',default=[],metavar=('TOOL','VERSION','FILE'))
    args=p.parse_args();repo=next((x for x in r.records('repositories') if x['full_name']==args.repository),None)
    if repo is None: p.error('Repository is not in the canonical public registry')
    result,sources=analyze(repo,args.report);packet,path=build_packet(repo,result,sources,args.max_bytes)
    print(json.dumps({'packet':str(path.relative_to(r.ROOT)), 'coverage':{k:v for k,v in result['coverage'].items() if k not in ('missing','errors')},'cache':result['cache'],'counts':packet['counts'],'reduction_percent':packet['source_to_packet_reduction_percent'],'adapter_status':result['adapter_status']}))
if __name__=='__main__': main()
