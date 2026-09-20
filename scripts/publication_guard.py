"""Block publication of private identifiers, source caches and likely credentials."""
import json,pathlib,re,subprocess,sys
from registry import ROOT,read

def check():
    private=read('.local/discovery-private.json',[])
    forbidden=[r['full_name'].lower() for r in private if r.get('private')]
    patterns=[re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}'),re.compile(r'github_pat_[A-Za-z0-9_]{30,}'),re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),re.compile(r'sk-proj-[A-Za-z0-9_-]{30,}')]
    failures=[]
    candidates=subprocess.run(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT,capture_output=True,check=True).stdout.decode().split('\0')
    for rel in sorted(set(candidates)):
        if not rel: continue
        path=ROOT/rel
        if not path.is_file(): continue
        if any(p in ('.local','.cache','.venv') for p in pathlib.PurePosixPath(rel).parts): failures.append({'path':rel,'reason':'private cache tracked'}); continue
        text=path.read_text(encoding='utf-8',errors='replace')
        if any(re.search(re.escape(name)+r'(?![a-z0-9_.-])',text.lower()) for name in forbidden): failures.append({'path':rel,'reason':'private repository identifier'})
        if any(p.search(text) for p in patterns): failures.append({'path':rel,'reason':'credential-like content'})
    if (ROOT/'.local/visibility-blockers.json').exists(): failures.append({'path':'.local/visibility-blockers.json','reason':'visibility review unresolved'})
    return {'valid':not failures,'files_scanned':len(set(candidates))-(1 if '' in candidates else 0),'private_identifiers_checked':len(forbidden),'failures':failures}
if __name__=='__main__':
    result=check(); print(json.dumps(result)); sys.exit(0 if result['valid'] else 1)
