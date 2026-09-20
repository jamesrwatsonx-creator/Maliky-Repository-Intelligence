import argparse,json,pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from analysis.runner import run_static,r
p=argparse.ArgumentParser();p.add_argument('repository');p.add_argument('tool',choices=['semgrep','scancode','syft']);p.add_argument('--timeout',type=int,default=120)
a=p.parse_args();repo=next(x for x in r.records('repositories') if x['full_name']==a.repository)
print(json.dumps(run_static(repo,a.tool,a.timeout)))
