"""Read-only source ingestion and conservative capability registry operations."""
from __future__ import annotations
import argparse, ast, base64, collections, concurrent.futures, hashlib, json, os, pathlib, re, subprocess, sys, tempfile, time
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
OWNER = 'jamesrwatsonx-creator'
SELF = OWNER + '/Maliky-Repository-Intelligence'
SHA = re.compile(r'^[0-9a-f]{40}$')
SOURCE_EXTENSIONS = {'.py','.js','.jsx','.ts','.tsx','.mjs','.cjs','.go','.rs','.java','.kt','.kts','.swift','.cs','.cpp','.c','.h','.vue','.svelte','.sh','.rb','.php'}

def now(): return datetime.now(timezone.utc).isoformat()
def slug(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
def read(path, default=None):
    p=ROOT/path
    return json.loads(p.read_text(encoding='utf-8-sig')) if p.exists() else default
def write(path, data):
    p=ROOT/path; p.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile('w',encoding='utf-8',dir=p.parent,delete=False) as f:
        json.dump(data,f,indent=2,ensure_ascii=False); f.write('\n'); name=f.name
    os.replace(name,p)
def records(kind):
    return [json.loads(p.read_text(encoding='utf-8')) for p in sorted((ROOT/'registry'/kind).glob('*.json'))]
def gh(endpoint):
    # Literal argument list; credentials are supplied by gh's configured credential store.
    for attempt in range(3):
        p=subprocess.run(['gh','api','--method','GET',endpoint],capture_output=True,text=True,encoding='utf-8',errors='replace')
        if p.returncode==0: return json.loads(p.stdout)
        if attempt==2: raise RuntimeError(p.stderr.strip()[:600])
        time.sleep(attempt+1)
def git_blob(data): return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def repo_file(repo): return 'registry/repositories/'+str(repo['github_id'])+'.json'
def cache_path(repo,commit): return pathlib.Path('.local/cache')/str(repo['github_id'])/commit
def archive_record(repo):
    if repo.get('inspected_commit'):
        write(pathlib.Path('.local/history')/str(repo['github_id'])/(repo['inspected_commit']+'.json'),repo)
def public_repo(meta):
    return meta.get('private') is False and meta.get('visibility','public')=='public' and meta.get('owner',{}).get('login')==OWNER
def blank_repo(meta):
    return {'id':'repository:'+str(meta['id']),'github_id':meta['id'],'entity_type':'REPOSITORY','name':meta['name'],'full_name':meta['full_name'],'url':meta['html_url'],'owner':OWNER,'visibility':'public','affiliation':'FORKED_UNDER_USER_ACCOUNT' if meta['fork'] else 'OWNED','fork':meta['fork'],'default_branch':meta['default_branch'],'upstream_url':meta.get('parent',{}).get('html_url'),'description':meta.get('description') or '', 'metadata':{'language':meta.get('language'),'license':(meta.get('license') or {}).get('spdx_id'),'archived':meta['archived'],'pushed_at':meta['pushed_at']},'state':'DISCOVERED','inspected_commit':None,'current_commit':None,'inspection_date':None,'categories':[],'operational_category':'operational:25','secondary_operational_categories':[],'capabilities':[],'studios':[],'ideas':[],'scores':{},'tier':None,'tier_reason':None,'recommendation':'NEEDS DEEPER REVIEW','entity_census':{},'deep_review':{'completed':False,'reviewer':None,'evidence':[]},'phases':{'structure':False,'entity_extraction':False,'capability_analysis':False,'deep_review':False,'validation':False}}

def discover(input_path=None):
    if input_path:
        pages=json.loads(pathlib.Path(input_path).read_text(encoding='utf-8-sig'))
        raw=[r for page in pages for r in page] if pages and isinstance(pages[0],list) else pages
    else:
        raw=[]; page=1
        while True:
            batch=gh(f'user/repos?per_page=100&affiliation=owner,collaborator,organization_member&sort=full_name&page={page}')
            if not batch: break
            raw.extend(batch); page+=1
    raw=list({r['id']:r for r in raw}.values())
    write('.local/discovery-private.json',raw)
    owned=[r for r in raw if r['owner']['login']==OWNER]
    public=[r for r in owned if public_repo(r)]
    visible_ids={r['id'] for r in public}
    # Never silently leave formerly-public records in a future publishable tree.
    restricted=[r['id'] for r in records('repositories') if r['github_id'] not in visible_ids]
    if restricted:
        write('.local/visibility-blockers.json',restricted)
        raise RuntimeError('Previously catalogued repositories are no longer verified public. Publication blocked; preserve and relocate affected records before proceeding.')
    for m in public:
        r=read(repo_file({'github_id':m['id']})) or blank_repo(m)
        fresh=blank_repo(m)
        for k in ['name','full_name','url','owner','visibility','affiliation','fork','default_branch','description','metadata']:
            r[k]=fresh[k]
        r['visibility_verified_at']=now()
        write(repo_file(r),r)
    stats={'accessible':len(raw),'owned':len(owned),'forks_owned':sum(r['fork'] for r in owned),'public_owned':len(public),'private_owned':sum(r['private'] for r in owned),'other_accessible':len(raw)-len(owned),'private_other_access':sum(r['private'] for r in raw if r['owner']['login']!=OWNER)}
    write('system/discovery-manifest.json',{'schema_version':1,'discovered_at':now(),'scope':'Authenticated GitHub account accessibility; ownership filtered exactly; pagination exhausted','target_owner':OWNER,'counts':stats,'repositories':[{'id':'repository:'+str(r['id']),'github_id':r['id'],'full_name':r['full_name'],'visibility':'public','affiliation':'FORKED_UNDER_USER_ACCOUNT' if r['fork'] else 'OWNED'} for r in public],'private_policy':'Aggregate counts only; identifiers and evidence excluded from public files'})
    print(json.dumps(stats))

def recover(legacy_root):
    old=pathlib.Path(legacy_root)
    inventory=json.loads((old/'reports/MASTER-INVENTORY.json').read_text(encoding='utf-8-sig'))
    current={r['full_name']:r for r in records('repositories')}
    count=collections.Counter(); hashes=[]
    for item in inventory:
        repo=current.get(item['full_name'])
        if not repo or item.get('is_private'): continue
        caches=list((old/'raw').glob('*/'+item['repository_name']+'/metadata.json'))
        repo['legacy_review']={'completed_phase':'pass2.5','legacy_completion_not_equivalent_to_entity_census':True,'prior_deep_review':item.get('pass1_source')=='EXISTING_DEEP_AUDIT','source_date':item.get('pass1_completed_at'),'capability_hints':item.get('pass1_obvious_reusable_capabilities',[]),'scores_not_promoted':True}
        repo['upstream_url']=('https://github.com/'+item['upstream']) if item.get('upstream') else None
        for metadata_path in caches:
            folder=metadata_path.parent
            tree=json.loads((folder/'tree.json').read_text(encoding='utf-8-sig'))
            cp=folder/'recent-commits.json'
            commits=json.loads(cp.read_text(encoding='utf-8-sig')) if cp.exists() else []
            if not commits or not isinstance(tree,dict) or 'tree' not in tree: continue
            commit=commits[0]['sha']
            dest=cache_path(repo,commit)
            write(dest/'tree.json',tree)
            write(dest/'commit.json',commits[0])
            blobs={x['path']:x for x in tree['tree'] if x['type']=='blob'}
            verified=[]; mismatches=[]
            for file in (folder/'content').rglob('*'):
                if not file.is_file(): continue
                path=file.relative_to(folder/'content').as_posix(); blob=blobs.get(path)
                if not blob: continue
                data=file.read_bytes()
                # Legacy PowerShell downloads may have a UTF-8 BOM or CRLF conversion.
                candidates=[data,data.removeprefix(b'\xef\xbb\xbf'),data.replace(b'\r\n',b'\n'),data.removeprefix(b'\xef\xbb\xbf').replace(b'\r\n',b'\n')]
                matched=next((b for b in candidates if git_blob(b)==blob['sha']),None)
                if matched is None: mismatches.append(path); continue
                out=ROOT/dest/'blobs'/blob['sha']; out.parent.mkdir(parents=True,exist_ok=True); out.write_bytes(matched)
                verified.append({'path':path,'blob_sha':blob['sha'],'bytes':len(matched)})
            repo['legacy_cache']={'commit':commit,'tree_complete':not tree.get('truncated',True),'verified_source_files':len(verified),'unverified_source_files':len(mismatches)}
            write(dest/'recovery.json',{'files':verified,'hash_mismatch_paths':mismatches,'recovered_at':now()})
            count['cached_repositories']+=1; count['verified_source_files']+=len(verified); count['unverified_source_files']+=len(mismatches)
        profile=old/(item.get('profile_path') or item.get('pass1_profile_path') or '')
        if profile.is_file():
            data=profile.read_bytes(); digest=hashlib.sha256(data).hexdigest()
            # Keep original narrative locally pending publication review.
            out=ROOT/'.local/legacy-profiles'/(str(repo['github_id'])+'.md'); out.parent.mkdir(parents=True,exist_ok=True); out.write_bytes(data)
            hashes.append({'repository_id':repo['id'],'sha256':digest})
        write(repo_file(repo),repo); count['repository_records']+=1
    write('system/recovery-import.json',{'imported_at':now(),'counts':dict(count),'profile_hashes':hashes,'policy':'Legacy files unchanged. Only blob-hash-verified cached text is reusable source evidence. Narrative hints require semantic review.'})
    print(json.dumps(dict(count)))

def safe_path(path):
    p=pathlib.PurePosixPath(path)
    return bool(path) and not p.is_absolute() and '..' not in p.parts and '\\' not in path

def get_tree(repo, commit):
    dest=cache_path(repo,commit); tree=read(dest/'tree.json')
    if tree and not tree.get('truncated',True): return tree
    tree=gh(f'repos/{repo["full_name"]}/git/trees/{commit}?recursive=1')
    if tree.get('truncated'):
        # Complete large trees using nonrecursive subtree traversal, preserving paths.
        root=gh(f'repos/{repo["full_name"]}/git/trees/{commit}')
        todo=[('',root)]; entries=[]
        while todo:
            prefix, node=todo.pop()
            if node.get('truncated'): raise RuntimeError('Nonrecursive tree unexpectedly truncated')
            for entry in node['tree']:
                e=dict(entry); e['path']=prefix+entry['path']; entries.append(e)
                if e['type']=='tree': todo.append((e['path']+'/',gh(f'repos/{repo["full_name"]}/git/trees/{e["sha"]}')))
        tree={'sha':root['sha'],'tree':entries,'truncated':False,'expanded_subtrees':True}
    if any(not safe_path(x['path']) for x in tree['tree']): raise RuntimeError('Unsafe source path')
    write(dest/'tree.json',tree); return tree

def source_text(repo, commit, entry, offline):
    p=ROOT/cache_path(repo,commit)/'blobs'/entry['sha']
    if p.exists(): data=p.read_bytes()
    elif offline: return None
    else:
        blob=gh(f'repos/{repo["full_name"]}/git/blobs/{entry["sha"]}')
        if blob.get('encoding')!='base64': raise RuntimeError('Unsupported blob encoding')
        data=base64.b64decode(blob['content']); p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(data)
    if git_blob(data)!=entry['sha']: raise RuntimeError('Source blob hash mismatch')
    return data.decode('utf-8-sig')

def frontmatter(text):
    if not text.startswith('---'): return {}
    end=text.find('\n---',3)
    if end<0: return {}
    result={}
    for m in re.finditer(r'^([\w-]+):\s*(.*?)\s*$',text[3:end],re.M):
        val=m[2].strip().strip('\"\'')
        if val not in ('>','|','>-','|-'): result[m[1]]=val
    return result

def detect(path,text):
    """Explicit declarations only. All results remain semantic review candidates."""
    found=[]; name=pathlib.PurePosixPath(path).name
    def add(kind,symbol,description='',line=1):
        found.append({'type':kind,'symbol':symbol,'description':description[:1500],'line':line})
    if name.lower()=='skill.md':
        fm=frontmatter(text); add('SKILL',fm.get('name') or str(pathlib.PurePosixPath(path).parent),fm.get('description',''))
    if name=='package.json':
        try:
            m=json.loads(text)
            if m.get('name'): add('PACKAGE',m['name'],m.get('description',''))
            for bin_name in (m.get('bin',{}) if isinstance(m.get('bin'),dict) else {m.get('name','cli'):m['bin']} if m.get('bin') else {}): add('CLI',bin_name,m.get('description',''))
        except (ValueError,TypeError): pass
    if name=='pyproject.toml':
        import tomllib
        try:
            m=tomllib.loads(text); project=m.get('project') or m.get('tool',{}).get('poetry',{})
            if project.get('name'): add('PACKAGE',project['name'],project.get('description',''))
            for cmd in project.get('scripts',{}): add('CLI',cmd,project['scripts'][cmd])
        except ValueError: pass
    if name.endswith(('.yaml','.yml')) and path.startswith('.github/workflows/'):
        m=re.search(r'^name:\s*[\"\']?(.+?)\s*$',text,re.M); add('WORKFLOW',m[1].strip('\"\'') if m else name)
    if name=='plugin.json' and ('.claude-plugin/' in path or '.codex-plugin/' in path):
        try:
            m=json.loads(text); add('PLUGIN',m.get('name',path),m.get('description',''))
        except ValueError: pass
    if name.endswith('.md') and name.lower() not in ('readme.md','skill.md','agents.md'):
        fm=frontmatter(text)
        if fm.get('name') and fm.get('description') and ('agents/' in path or any(k in fm for k in ('tools','model','color'))): add('AGENT',fm['name'],fm['description'])
    if name.endswith('.py'):
        try:
            tree=ast.parse(text)
            for node in ast.walk(tree):
                if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
                    decorators=[ast.unparse(x) for x in node.decorator_list]
                    if any(re.search(r'(?:mcp|server)\.tool\(',d) for d in decorators): add('TOOL',node.name,ast.get_docstring(node) or '',node.lineno)
                    if any(re.match(r'(?:app|router)\.(?:get|post|put|patch|delete)\(',d) for d in decorators): add('API',node.name,ast.get_docstring(node) or '',node.lineno)
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in ('FastMCP','Server') and node.args and isinstance(node.args[0],ast.Constant) and isinstance(node.args[0].value,str):
                    if node.func.id=='FastMCP' or 'mcp.server' in text: add('MCP_SERVER',node.args[0].value,'MCP server constructor',node.lineno)
        except SyntaxError: pass
    if name.endswith(('.ts','.js','.mjs','.tsx','.jsx')):
        for m in re.finditer(r'\b(?:server|mcp)\.(?:registerTool|tool)\(\s*[\"\']([^\"\']+)[\"\']',text): add('TOOL',m[1],'Explicit MCP tool registration',text[:m.start()].count('\n')+1)
        for m in re.finditer(r'new\s+McpServer\s*\(\s*\{\s*name\s*:\s*[\"\']([^\"\']+)',text): add('MCP_SERVER',m[1],'MCP server constructor',text[:m.start()].count('\n')+1)
        if name.endswith(('.tsx','.jsx')):
            for m in re.finditer(r'export\s+(?:default\s+)?(?:function|class|const)\s+([A-Z][A-Za-z0-9_]*)',text):
                if re.search(r'<[A-Za-z]',text): add('UI_COMPONENT',m[1],'Exported JSX component candidate',text[:m.start()].count('\n')+1)
    return list({(f['type'],f['symbol']):f for f in found}.values())

def entity_record(repo,commit,entry,found):
    identity='\0'.join([repo['id'],entry['path'],found['type'],found['symbol']])
    identifier='entity:'+hashlib.sha256(identity.encode()).hexdigest()[:24]
    return {'id':identifier,'entity_type':found['type'],'name':found['symbol'],'description':found['description'],'source':{'repository_id':repo['id'],'repository_name':repo['full_name'],'repository_url':repo['url'],'upstream_url':repo.get('upstream_url'),'source_path':entry['path'],'inspected_commit':commit,'inspection_date':now(),'blob_sha':entry['sha'],'line':found['line']},'evidence':[{'type':'source_path','value':entry['path']},{'type':'exported_symbol' if found['type'] in ('TOOL','UI_COMPONENT','API') else 'manifest','value':found['symbol']}],'review_status':'NEEDS_REVIEW','categories':[],'operational_category':'operational:01' if found['type']=='SKILL' else 'operational:25','secondary_operational_categories':[],'capabilities':[],'studios':[],'ideas':[],'metadata':{},'scores':{},'tier':None,'tier_reason':None,'recommendation':'NEEDS DEEPER REVIEW','contribution_role':'SKILL' if found['type']=='SKILL' else 'COMPONENT'}

def priority(entry):
    p=entry['path']; name=pathlib.PurePosixPath(p).name
    if name.lower()=='skill.md': return 0
    if name in ('package.json','pyproject.toml','plugin.json','Cargo.toml','go.mod','mcp.json'): return 1
    if name.lower().startswith('readme'): return 2
    if p.startswith('.github/workflows/'): return 3
    if pathlib.PurePosixPath(p).suffix in SOURCE_EXTENSIONS: return 4
    if pathlib.PurePosixPath(p).suffix in ('.md','.json','.yaml','.yml','.toml'): return 5
    return 6

def ingest(full_name, offline=False,max_files=None,structure_only=False):
    matches=[r for r in records('repositories') if r['full_name']==full_name]
    if not matches: raise ValueError('Repository not in verified public owned inventory; run discovery')
    r=matches[0]
    try:
        if offline:
            commit=r.get('inspected_commit') or r.get('legacy_cache',{}).get('commit')
            if not commit: raise RuntimeError('No pinned cache available')
        else:
            meta=gh(f'repos/{full_name}')
            if not public_repo(meta): raise RuntimeError('Source no longer verified public and owned; publication blocked')
            r['visibility_verified_at']=now(); r['upstream_url']=(meta.get('parent') or {}).get('html_url')
            if meta['size']==0:
                r['state']='NEEDS_REVIEW'; r['empty_repository']=True; r['next_phase']='CONFIRM_EMPTY_REPOSITORY'; write(repo_file(r),r); return {'repo':full_name,'state':r['state'],'empty':True}
            head=gh(f'repos/{full_name}/commits/{meta["default_branch"]}')
            commit=head['sha']; write(cache_path(r,commit)/'commit.json',head)
        r['current_commit']=commit
        if r.get('inspected_commit')!=commit and r.get('inspected_commit'):
            archive_record(r); r['previous_inspected_commit']=r['inspected_commit']; r['phases']={k:False for k in r['phases']}; r['deep_review']={'completed':False,'reviewer':None,'evidence':[]}
            r['inspection_date']=now()
        if r['state']=='COMPLETE' and r.get('inspected_commit')==commit:
            write(repo_file(r),r); return {'repo':full_name,'skipped':'COMPLETE at current commit'}
        if r.get('inspected_commit')==commit and ((structure_only and r['phases']['structure']) or r['phases']['entity_extraction']):
            write(repo_file(r),r); return {'repo':full_name,'skipped':'Requested phase already complete at inspected commit','next_phase':r.get('next_phase')}
        tree=read(cache_path(r,commit)/'tree.json') if offline else get_tree(r,commit)
        if not tree: raise RuntimeError('No tree cache available')
        entries=[e for e in tree['tree'] if e['type']=='blob' and e.get('mode')!='120000']
        r['inspected_commit']=commit; r['inspection_date']=r.get('inspection_date') or now()
        r['phases']['structure']=not tree.get('truncated',True)
        r['tree_files']=len(entries); r['state']='STRUCTURE_COMPLETE' if r['phases']['structure'] else 'PARTIAL'
        ep='system/evidence/'+str(r['github_id'])+'.json'
        previous=read(ep,{})
        previous=previous if previous.get('inspected_commit')==commit else {}
        processed={e['path']:e for e in previous.get('files_read',[])}
        errors=previous.get('errors',[]); count=0
        if not structure_only:
            for e in sorted(entries,key=lambda e:(priority(e),e['path'])):
                if priority(e)==6 or e['path'] in processed: continue
                if max_files is not None and count>=max_files: break
                try:
                    text=source_text(r,commit,e,offline)
                    if text is None: continue
                    found=detect(e['path'],text)
                    for candidate in found:
                        ent=entity_record(r,commit,e,candidate); f='registry/entities/'+ent['id'].split(':')[1]+'.json'; old=read(f)
                        if old:
                            if old['source']['blob_sha']==ent['source']['blob_sha']:
                                # Preserve annotations when implementation has not changed.
                                for key in ['review_status','categories','operational_category','secondary_operational_categories','capabilities','studios','ideas','metadata','scores','tier','tier_reason','recommendation','contribution_role']: ent[key]=old[key]
                            else:
                                write(pathlib.Path('.local/entity-history')/ent['id'].split(':')[1]/(old['source']['inspected_commit']+'.json'),old)
                        write(f,ent)
                    processed[e['path']]={'path':e['path'],'blob_sha':e['sha'],'entities_detected':len(found)}; count+=1
                except (UnicodeDecodeError,ValueError,RuntimeError) as exc:
                    errors=[er for er in errors if er['path']!=e['path']]+[{'path':e['path'],'error':str(exc)[:250]}]
        ents=[e for e in records('entities') if e['source']['repository_id']==r['id'] and e['source']['inspected_commit']==commit]
        counts=collections.Counter(e['entity_type'] for e in ents)
        skill_detected=sum(pathlib.PurePosixPath(e['path']).name.lower()=='skill.md' for e in entries)
        all_types=read('registry/taxonomy/vocabulary.json')['entity_types']
        r['entity_census']={kind:{'detected':skill_detected if kind=='SKILL' else counts[kind],'catalogued':counts[kind],'detection_scope':'complete_tree_paths' if kind=='SKILL' else 'read_source_declarations','reviewed':False} for kind in all_types if kind!='REPOSITORY'}
        eligible=[e['path'] for e in entries if priority(e)<6]
        unread=[p for p in eligible if p not in processed]
        r['files_read']=len(processed); r['entity_count']=len(ents); r['unread_source_files']=len(unread)
        r['phases']['entity_extraction']=False # Only a reviewed census may finish this phase.
        r['next_phase']='ENTITY_EXTRACTION' if unread else 'SEMANTIC_CENSUS_REVIEW'
        if processed: r['state']='PARTIAL' if unread or skill_detected!=counts['SKILL'] else 'NEEDS_REVIEW'
        r.pop('last_error',None)
        write(ep,{'repository_id':r['id'],'inspected_commit':commit,'tree_complete':r['phases']['structure'],'tree_files':len(entries),'tree_entries':[{'path':e['path'],'sha':e['sha']} for e in entries],'files_read':list(processed.values()),'unread_source_paths':unread,'excluded_nontext_paths':[e['path'] for e in entries if priority(e)==6],'errors':errors,'census_review_required':True,'detector_version':1})
        write(repo_file(r),r)
        return {'repo':full_name,'state':r['state'],'files_read':len(processed),'entities':len(ents),'unread':len(unread)}
    except Exception as exc:
        r['state']='FAILED' if not r.get('phases',{}).get('structure') else 'PARTIAL'; r['last_error']=str(exc)[:600]; write(repo_file(r),r)
        return {'repo':full_name,'error':str(exc)[:300]}

def build():
    repos=records('repositories'); entities=records('entities'); caps=records('capabilities'); edges=records('relationships')
    active=[e for e in entities if any(r['id']==e['source']['repository_id'] and r.get('inspected_commit')==e['source']['inspected_commit'] for r in repos)]
    generated_edges=[{'id':'contains:'+e['id'],'type':'CONTAINS','from':e['source']['repository_id'],'to':e['id'],'evidence':e['evidence']} for e in active]
    for e in active:
        for cap in e['capabilities']: generated_edges.append({'id':e['id']+':provides:'+cap,'type':'PROVIDES','from':e['id'],'to':cap,'evidence':e['evidence']})
    docs=[]
    for r in repos:
        docs.append({'id':r['id'],'entity_type':'REPOSITORY','name':r['full_name'],'text':r['full_name']+' '+r['description'],'repository':r['full_name'],'url':r['url'],'state':r['state'],'capabilities':r['capabilities'],'inspected_commit':r['inspected_commit']})
    cap_map={c['id']:c for c in caps}
    for e in active:
        synonyms=' '.join(' '.join(cap_map[c].get('aliases',[])) for c in e['capabilities'] if c in cap_map)
        docs.append({'id':e['id'],'entity_type':e['entity_type'],'name':e['name'],'text':' '.join([e['name'],e['description'],e['source']['source_path'],synonyms]),'repository':e['source']['repository_name'],'url':e['source']['repository_url']+'/blob/'+e['source']['inspected_commit']+'/'+e['source']['source_path'],'state':e['review_status'],'capabilities':e['capabilities'],'source_path':e['source']['source_path'],'inspected_commit':e['source']['inspected_commit']})
    for c in caps: docs.append({'id':c['id'],'entity_type':'CAPABILITY','name':c['name'],'text':' '.join([c['name']]+c.get('aliases',[])),'state':c['status'],'capabilities':[c['id']]})
    p=ROOT/'search/search-index.jsonl'; p.parent.mkdir(exist_ok=True); p.write_text(''.join(json.dumps(d,ensure_ascii=False)+'\n' for d in docs),encoding='utf-8')
    write('MASTER-INVENTORY.json',[{k:r[k] for k in ['id','full_name','url','affiliation','state','inspected_commit','capabilities']} for r in repos])
    nodes=[{'id':d['id'],'type':d['entity_type'],'name':d['name']} for d in docs]
    for kind in ('ideas','studios','compositions'): nodes.extend({'id':x['id'],'type':kind.upper(),'name':x['name']} for x in records(kind))
    write('CAPABILITY-GRAPH.json',{'nodes':nodes,'edges':edges+generated_edges})
    dimensions=['entity_type','repository','state','capabilities']
    for dim in dimensions:
        index=collections.defaultdict(list)
        for d in docs:
            values=d.get(dim,[]); values=values if isinstance(values,list) else [values]
            for value in values: index[value].append(d['id'])
        write('registry/indexes/'+dim+'.json',dict(index))
    for dim in ('categories','studios','ideas','contribution_role','recommendation','tier','operational_category'):
        index=collections.defaultdict(list)
        for d in repos+active:
            values=d.get(dim,[]); values=values if isinstance(values,list) else [values]
            for value in values:
                if value is not None: index[value].append(d['id'])
        write('registry/indexes/'+dim+'.json',dict(index))
    for dim in ('language','license'):
        index=collections.defaultdict(list)
        for d in repos+active:
            if d.get('metadata',{}).get(dim): index[d['metadata'][dim]].append(d['id'])
        write('registry/indexes/'+dim+'.json',dict(index))
    queue=[{'repository_id':r['id'],'repository':r['full_name'],'state':r['state'],'next_phase':r.get('next_phase','STRUCTURE'),'inspected_commit':r['inspected_commit']} for r in repos if r['state']!='COMPLETE']
    stats={'generated_at':now(),'public_repository_records':len(repos),'active_entity_records':len(active),'historical_entity_records':len(entities)-len(active),'entity_types':dict(collections.Counter(e['entity_type'] for e in active)),'repositories_by_state':dict(collections.Counter(r['state'] for r in repos)),'complete_trees':sum(r['phases']['structure'] for r in repos),'verified_source_files_read':sum(r.get('files_read',0) for r in repos),'verified_capabilities':sum(c['status']=='VERIFIED' for c in caps),'search_documents':len(docs),'pending_repositories':len(queue),'completion_policy':'Structural readiness is separate from semantic coverage. No candidate is automatically COMPLETE.'}
    write('system/statistics.json',stats); write('system/inspection-state.json',{'generated_at':now(),'queue':queue,'next':queue[0] if queue else None})
    return stats

def query(text,limit=20,kind=None,verified=False):
    p=ROOT/'search/search-index.jsonl'; docs=[json.loads(line) for line in p.read_text(encoding='utf-8').splitlines()]
    terms=set(re.findall(r'[a-z0-9]+',text.lower())); results=[]
    # Resolve aliases through canonical capabilities, then retrieve their providers.
    matching_caps={c['id'] for c in records('capabilities') if text.lower() in [x.lower() for x in [c['name']]+c.get('aliases',[])]}
    for d in docs:
        if kind and d['entity_type']!=kind: continue
        if verified and d['state'] not in ('VERIFIED','COMPLETE'): continue
        words=set(re.findall(r'[a-z0-9]+',d['text'].lower())); score=len(terms & words)
        if matching_caps & set(d.get('capabilities',[])): score+=10
        if score: results.append({**d,'match_score':score})
    return sorted(results,key=lambda d:(-d['match_score'],d['id']))[:limit]

def compose(requirements):
    """Greedy set cover of verified providers; uncovered requirements remain explicit."""
    if isinstance(requirements,str):
        idea=next((i for i in records('ideas') if i['id']==requirements),None)
        if not idea: raise ValueError('Unknown idea ID')
        requirements=idea['requirements']
    wanted=set(requirements); remaining=set(wanted)
    verified_caps={c['id'] for c in records('capabilities') if c['status']=='VERIFIED'}
    active_commits={r['id']:r['inspected_commit'] for r in records('repositories')}
    pool=[e for e in records('entities') if e['review_status']=='VERIFIED' and e['source']['inspected_commit']==active_commits.get(e['source']['repository_id'])]
    selected=[]
    while remaining:
        choices=[(len(remaining & set(e['capabilities']) & verified_caps),e) for e in pool if e not in selected]
        choices.sort(key=lambda x:(-x[0],x[1]['id']))
        if not choices or choices[0][0]==0: break
        best=choices[0][1]; selected.append(best); remaining-=set(best['capabilities']) & verified_caps
    return {'requirements':sorted(wanted),'selected':[{'id':e['id'],'name':e['name'],'source':e['source'],'role':e['contribution_role'],'supplies':sorted(wanted & set(e['capabilities']))} for e in selected],'alternatives':[e['id'] for e in pool if e not in selected and wanted & set(e['capabilities'])],'missing_capabilities':sorted(remaining),'method':'Deterministic greedy cover; not a mathematical optimality guarantee','empty_requirements':not bool(wanted),'caveat':'Missing means not established by reviewed evidence. Dependencies and compatibility need review.'}

def validate():
    errors=[]; vocab=read('registry/taxonomy/vocabulary.json'); repos=records('repositories'); entities=records('entities')
    caps=records('capabilities'); studios=records('studios'); ideas=records('ideas'); compositions=records('compositions'); relationships=records('relationships')
    all_records=repos+entities+caps+studios+ideas+compositions+relationships
    ids=[r.get('id') for r in all_records]; by_id={r.get('id'):r for r in all_records}
    if len(ids)!=len(set(ids)): errors.append('Duplicate canonical IDs')
    category_ids={c['id'] for c in read('registry/taxonomy/categories.json')}; op_ids={c['id'] for c in read('registry/taxonomy/operational.json')}
    cap_ids={c['id'] for c in caps}; studio_ids={c['id'] for c in studios}; idea_ids={c['id'] for c in ideas}
    manifest=read('system/discovery-manifest.json',{}); allowed={r['id'] for r in manifest.get('repositories',[])}
    for r in repos:
        prefix=r['id']
        if r['id'] not in allowed or r['visibility']!='public' or r['owner']!=OWNER: errors.append(prefix+': not verified public owned')
        if r['state'] not in vocab['inspection_states']: errors.append(prefix+': invalid state')
        if r.get('inspected_commit') and not SHA.fullmatch(r['inspected_commit']): errors.append(prefix+': invalid commit')
        evidence=read('system/evidence/'+str(r['github_id'])+'.json',{})
        current_ents=[e for e in entities if e['source']['repository_id']==r['id'] and e['source']['inspected_commit']==r['inspected_commit']]
        counts=collections.Counter(e['entity_type'] for e in current_ents)
        for kind,census in r.get('entity_census',{}).items():
            if census['catalogued']!=counts[kind]: errors.append(prefix+': census count mismatch '+kind)
            if census['detected']<census['catalogued']: errors.append(prefix+': detection count below catalogued '+kind)
        if r['state']=='COMPLETE':
            if not all(r['phases'].values()) or not r['deep_review']['completed'] or not r['deep_review'].get('reviewer') or not r['deep_review'].get('evidence'): errors.append(prefix+': completion lacks reviewed phases')
            if not r.get('entity_census') or any(c['detected']!=c['catalogued'] or not c['reviewed'] for c in r['entity_census'].values()): errors.append(prefix+': unreconciled census')
            if evidence.get('unread_source_paths') or evidence.get('errors') or not evidence.get('tree_complete'): errors.append(prefix+': incomplete source coverage')
            if set(r['scores'])!=set(vocab['score_dimensions']) or not r.get('tier_reason'): errors.append(prefix+': completion lacks justified scores/tier')
            if any(e['review_status']!='VERIFIED' for e in current_ents): errors.append(prefix+': unreviewed entities')
    for e in entities:
        s=e.get('source',{}); repo=by_id.get(s.get('repository_id'))
        if not repo or repo not in repos: errors.append(e['id']+': missing repository'); continue
        for key in ['repository_name','repository_url','source_path','inspected_commit','inspection_date','blob_sha']:
            if not s.get(key): errors.append(e['id']+': missing provenance '+key)
        if not safe_path(s.get('source_path','')) or not SHA.fullmatch(s.get('inspected_commit','')): errors.append(e['id']+': invalid path/commit')
        if s['repository_name']!=repo['full_name'] or s['repository_url']!=repo['url']: errors.append(e['id']+': repository provenance mismatch')
        if s['inspected_commit']==repo['inspected_commit']:
            ev=read('system/evidence/'+str(repo['github_id'])+'.json',{}); paths={p['path']:p['blob_sha'] for p in ev.get('files_read',[])}
            if paths.get(s['source_path'])!=s['blob_sha']: errors.append(e['id']+': unverified source evidence')
        if not e.get('evidence'): errors.append(e['id']+': missing evidence')
    for r in repos+entities:
        if r['entity_type'] not in vocab['entity_types']: errors.append(r['id']+': invalid entity type')
        for field,allowed_values in [('categories',category_ids),('capabilities',cap_ids),('studios',studio_ids),('ideas',idea_ids),('secondary_operational_categories',op_ids)]:
            if set(r.get(field,[]))-allowed_values: errors.append(r['id']+': invalid references '+field)
        if r['operational_category'] not in op_ids: errors.append(r['id']+': invalid operational category')
        if r.get('recommendation') not in vocab['recommendations']: errors.append(r['id']+': invalid recommendation')
        if r.get('tier') is not None and (r['tier'] not in vocab['tiers'] or not r.get('tier_reason')): errors.append(r['id']+': invalid tier')
        for key,score in r.get('scores',{}).items():
            if key not in vocab['score_dimensions'] or not isinstance(score,dict) or not isinstance(score.get('value'),(int,float)) or not 1<=score['value']<=10 or not score.get('reason') or not score.get('evidence'): errors.append(r['id']+': invalid score '+key)
    for c in caps:
        if not c.get('aliases') or not c.get('evidence'): errors.append(c['id']+': missing aliases/evidence')
        for provider in c.get('providers',[]):
            if provider not in by_id or c['id'] not in by_id[provider].get('capabilities',[]): errors.append(c['id']+': inconsistent provider')
    for edge in relationships:
        if edge['type'] not in vocab['relationship_types'] or edge['from'] not in by_id or edge['to'] not in by_id or not edge.get('evidence'): errors.append(edge['id']+': invalid relationship')
    for idea in ideas:
        if set(idea['requirements'])-cap_ids: errors.append(idea['id']+': unknown capability requirement')
    for comp in compositions:
        if set(comp.get('requirements',[]))-cap_ids or any(x not in by_id for x in comp.get('entities',[])): errors.append(comp['id']+': invalid composition reference')
    for p in ROOT.rglob('*.json'):
        if any(part in ('.git','.local','.venv') for part in p.relative_to(ROOT).parts): continue
        try: json.loads(p.read_text(encoding='utf-8'))
        except Exception: errors.append(str(p.relative_to(ROOT))+': malformed JSON')
    index=ROOT/'search/search-index.jsonl'
    if index.exists():
        docs=[json.loads(x) for x in index.read_text(encoding='utf-8').splitlines()]
        if len({d['id'] for d in docs})!=len(docs): errors.append('Duplicate search IDs')
        if any(d['id'] not in by_id for d in docs): errors.append('Search references missing records')
    graph=read('CAPABILITY-GRAPH.json',{})
    graph_ids={n['id'] for n in graph.get('nodes',[])}
    if any(e['from'] not in graph_ids or e['to'] not in graph_ids for e in graph.get('edges',[])): errors.append('Dangling graph edge')
    report={'validated_at':now(),'valid':not errors,'errors':errors,'canonical_records_checked':len(all_records),'complete_repositories':sum(r['state']=='COMPLETE' for r in repos)}
    write('system/validation-report.json',report); return report

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('command',choices=['discover','recover','ingest','batch','build','validate','status','query','compose']); parser.add_argument('value',nargs='?'); parser.add_argument('--input'); parser.add_argument('--offline',action='store_true'); parser.add_argument('--all-accessible',action='store_true'); parser.add_argument('--max-files',type=int); parser.add_argument('--structure-only',action='store_true'); parser.add_argument('--workers',type=int,default=4); parser.add_argument('--limit',type=int,default=20); parser.add_argument('--kind'); parser.add_argument('--verified',action='store_true')
    a=parser.parse_args()
    if a.command=='discover': discover(a.input)
    elif a.command=='recover': recover(a.value)
    elif a.command=='ingest':
        result=ingest(a.value,a.offline,a.max_files,a.structure_only); build(); print(json.dumps(result)); return 1 if 'error' in result else 0
    elif a.command=='batch':
        targets=[r['full_name'] for r in records('repositories') if r['full_name']!=SELF and (not a.offline or r.get('legacy_cache'))]
        if a.value: targets=targets[:int(a.value)]
        errors=0
        with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
            jobs=[pool.submit(ingest,name,a.offline,a.max_files,a.structure_only) for name in targets]
            for i,f in enumerate(concurrent.futures.as_completed(jobs),1):
                result=f.result(); errors+='error' in result
                print(json.dumps({'completed':i,'total':len(jobs),**result}),flush=True)
        build(); return bool(errors)
    elif a.command=='build': print(json.dumps(build()))
    elif a.command=='validate':
        report=validate(); print(json.dumps(report)); return 0 if report['valid'] else 1
    elif a.command=='status': print(json.dumps(read('system/statistics.json'),indent=2))
    elif a.command=='query': print(json.dumps(query(a.value,a.limit,a.kind,a.verified),indent=2,ensure_ascii=False))
    elif a.command=='compose': print(json.dumps(compose(a.value),indent=2))
    return 0

if __name__=='__main__': sys.exit(main())
