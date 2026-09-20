"""Record the LEAN SEMANTIC REVIEW of babysitter at its existing pinned commit.

The declaration scan catalogued skills and agents but missed the library's ~2,100 process
definitions (JS files with an `@process` header), which are the repository's main reusable
workflow assets; they are added here as WORKFLOW entities. Bulk library skills, agents and
processes are grouped under per-specialization capabilities derived from their path.
Scoped deep review covered the MCP server (dynamic entrypoint import) and the SDK runtime.

Source: set BS_TARBALL to the pinned tarball (`gh api repos/<repo>/tarball/<commit>`); every
file used is verified against the git blob SHA in system/evidence/1250xxxxxx.json first.
"""
from __future__ import annotations
import hashlib,json,os,re,tarfile
import registry as r

REPOSITORY='jamesrwatsonx-creator/babysitter'
COMMIT='d97a2e46a84cbc3ca4589050a9bddbcbf792a785'
BASE='https://github.com/jamesrwatsonx-creator/babysitter/blob/'+COMMIT+'/'
NOTE='Verified from pinned source; runtime not tested'
SDK_PKG='Node >=20','@a5c-ai/babysitter-sdk'
MCP_FINDING=('run_create/run_iterate take a process `entrypoint` ("path/to/file.js#export") that the SDK loads with a dynamic import() (packages/sdk/src/runtime/orchestrateIteration.ts), '
             'so any agent connected to the babysitter MCP server can make it execute local JavaScript. Use only with a trusted process library and a trusted MCP client.')
SENSITIVE_AREAS={'security-research':'dual-use security research content','cryptography-blockchain':'cryptography and blockchain guidance'}

KEEP_UI={'packages/observer-dashboard':{'BreakpointApproval','BreakpointPanel','FilePreview','BreakpointBanner','CatchUpBanner','ExecutiveSummaryBanner','GlobalSearch','KpiGrid','ProjectAccordion','ProjectHealthCard','ProjectListView','ProjectSection','RunCard','RunFilterBar','RunList','VirtualizedRunList','AgentPanel','JsonTree','JsonTreeView','SummaryBlock','AtAGlanceHeader','FindingsSection','ScoreBar','LogViewer','TaskDetailPanel','TimingPanel','EventItem','EventStream','EventStreamProvider','NotificationPanel','NotificationProvider','ToastStack','ParallelGroup','PipelineView','StepCard','SettingsModal','ShortcutsHelp','OutcomeBanner','MetricsRow','StatusBadge','KindBadge','ProgressBar','SessionPill','EmptyState','ErrorBoundary','SearchFilter'},
         'packages/catalog':{'AgentDetail','ProcessDetail','SkillDetail','AgentCard','DomainCard','ProcessCard','SkillCard','EntityList','FilterPanel','MetadataDisplay','RelatedItems','SearchBar','SortDropdown','TreeView','Pagination','SearchInput','Tag','BarChart','PieChart','TreemapChart','MetricCard','StatsOverview','RecentActivity','Sidebar','Breadcrumb','ArwesFrame','CodeBlock','FrontmatterDisplay','MarkdownRenderer','TableOfContents'}}
KEEP_WORKFLOWS={'CI','Release','Docker Publish'}
DROP_PACKAGES={'babysitter-video','babysitter'}   # video marketing project; monorepo root (matched by path below)
CI_CAP=('ci-test-and-release-pipeline','CI test and release pipeline',['python monorepo CI','GitHub Actions release'])

def url(path,line=1): return BASE+path+'#L'+str(line)
def humanize(text): return re.sub(r'\s+',' ',re.sub(r'[-_/]+',' ',text)).strip()
def capability(identifier,name,aliases,providers,path,line=1):
    file='registry/capabilities/'+identifier+'.json'
    record=r.read(file)
    if record: providers=sorted(set(record['providers'])|set(providers));aliases=sorted(set(record['aliases'])|set(aliases))
    r.write(file,record and {**record,'providers':providers,'aliases':aliases} or {'id':'capability:'+identifier,'name':name,'aliases':sorted(aliases),'status':'VERIFIED','verification_scope':'Static source contract; runtime not tested','providers':sorted(providers),'evidence':[{'type':'source_review','value':url(path,line)}]})
def relationship(kind,source,target,path,line=1):
    identifier='relationship:'+hashlib.sha256('\0'.join([kind,source,target]).encode()).hexdigest()[:24]
    r.write('registry/relationships/'+identifier.split(':')[1]+'.json',{'id':identifier,'type':kind,'from':source,'to':target,'evidence':[{'type':'source_review','value':url(path,line)}]})

def library_area(path):
    parts=path.split('/')
    if parts[0]=='library':
        if parts[1]=='specializations': return '/'.join(parts[2:5]) if parts[2]=='domains' else parts[2]
        if parts[1]=='methodologies': return 'methodologies/'+parts[2]
        return '/'.join(parts[1:3])
    return None

def clean_comment(lines):
    return re.sub(r'\s+',' ',' '.join(re.sub(r'^\s*\*\s?','',l) for l in lines)).strip()

def parse_process(path,text):
    head=text[:6000]
    name=re.search(r'@process\s+(\S+)',head)
    desc=re.search(r'@description\s+((?:.+\n)(?:\s*\*\s+(?!@).+\n)*)',head)
    inputs=re.search(r'@inputs\s+(.+)',head);outputs=re.search(r'@outputs\s+(.+)',head)
    description=clean_comment(desc.group(1).splitlines()) if desc else ''
    if not description:
        first=re.search(r'/\*\*\s*\n?\s*\*?\s*([^@\n][^\n]*)',head);description=first.group(1).strip() if first else ''
    return (name.group(1) if name else path[len('library/'):-3]),description[:400],(inputs.group(1).strip()[:300] if inputs else None),(outputs.group(1).strip()[:300] if outputs else None)

def main():
    repo=next(x for x in r.records('repositories') if x['full_name']==REPOSITORY)
    if repo['inspected_commit']!=COMMIT: raise ValueError('babysitter commit changed; preserve this review and queue a new revision')
    evidence=r.read('system/evidence/'+str(repo['github_id'])+'.json')
    verified={p['path']:p['blob_sha'] for p in evidence['files_read']}
    tree={e['path']:e for e in evidence['tree_entries']}
    def entry(path):
        if verified.get(path)!=tree[path]['sha']: raise ValueError('Verified evidence missing for '+path)
        return tree[path]
    existing=[e for e in r.records('entities') if e['source']['repository_id']==repo['id'] and e['source']['inspected_commit']==COMMIT]
    empty_skills={e['source']['source_path'] for e in existing if e['entity_type']=='SKILL' and not e['description']}
    wanted=lambda n:(n.startswith('library/') and n.endswith('.js') and '/skills/' not in n and '/agents/' not in n) or n.endswith('package.json') or n.startswith('packages/sdk/src/mcp/tools/') or n in empty_skills
    files={}
    with tarfile.open(os.environ['BS_TARBALL']) as archive:
        for member in archive:
            if not member.isfile(): continue
            name=member.name.split('/',1)[1]
            if wanted(name) and name in tree:
                data=archive.extractfile(member).read()
                if r.git_blob(data)!=tree[name]['sha']: raise ValueError('Tarball file does not match pinned blob: '+name)
                files[name]=data.decode('utf-8','replace')
    caps={};out={};removed=[];providers_by_cap=caps
    def add_cap(cap,name,aliases,entity_id,path):
        info=caps.setdefault(cap,{'name':name,'aliases':set(),'providers':[],'path':path});info['aliases'].update(aliases);info['providers'].append(entity_id)
    def finish(entity,description,cap_specs,recommendation,opcat,role,standalone,deps,overlap,categories,studios=(),extra=None):
        cap_ids=[]
        for cap,cap_name,aliases in cap_specs:
            cap_ids.append('capability:'+cap);add_cap(cap,cap_name,aliases,entity['id'],entity['source']['source_path'])
        entity.update({'description':description,'capabilities':cap_ids,'recommendation':recommendation,'operational_category':opcat,'contribution_role':role,'review_status':'VERIFIED','categories':list(categories),'studios':list(studios),'ideas':[],
                       'evidence':[{'type':'source_review','value':url(entity['source']['source_path'],entity['source'].get('line',1))}],
                       'metadata':{'semantic_review':NOTE,'review_policy':'LEAN','standalone':standalone,'dependencies':deps,'overlap':overlap,**(extra or {})}})
        r.write('registry/entities/'+entity['id'].split(':')[1]+'.json',entity);out[entity['id']]=entity
    def drop(entity):
        (r.ROOT/'registry/entities'/(entity['id'].split(':')[1]+'.json')).unlink();removed.append(entity['id'])
    seen_sha={}
    def duplicate_of(entity):
        sha=entity['source']['blob_sha'];first=seen_sha.setdefault(sha,entity['source']['source_path'])
        return {'duplicate_of':first} if first!=entity['source']['source_path'] else {}

    studio=['studio:agent-studio']
    tools_by_file={}
    for name,text in files.items():
        if name.startswith('packages/sdk/src/mcp/tools/'):
            for m in re.finditer(r'\.tool\(\s*\n?\s*"([a-z_]+)",\s*\n?\s*"([^"]+)"',text): tools_by_file[m.group(1)]=(m.group(2),name,text[:m.start()].count('\n')+1)
    tool_caps={'run_':('babysitter-run-lifecycle-management','Babysitter run lifecycle management',['create and iterate babysitter runs']),'task_':('babysitter-task-inspection-and-posting','Babysitter task inspection and posting',['post task results','list run tasks']),
               'session_':('babysitter-session-management','Babysitter session management',['orchestration session state']),'':('babysitter-discovery-and-health','Babysitter discovery and health',['discover skills agents processes','babysitter health check'])}
    host_names={'babysitter':'claude-code','babysitter-codex':'codex','babysitter-cursor':'cursor','babysitter-github':'github-copilot','babysitter-gemini':'gemini','babysitter-opencode':'opencode','babysitter-omp':'omp','babysitter-pi':'pi'}
    package_descriptions={n:json.loads(t).get('description','') for n,t in files.items() if n.endswith('package.json')}

    for entity in sorted(existing,key=lambda e:e['id']):
        kind=entity['entity_type'];path=entity['source']['source_path'];area=library_area(path)
        if kind in ('SKILL','AGENT') and (area or path.startswith(('plugins/','.claude/'))):
            is_skill=kind=='SKILL';noun='skills' if is_skill else 'agents'
            if area:
                group=area;cap=('babysitter-library-'+re.sub(r'[^a-z0-9]+','-',group.lower()).strip('-')+'-'+noun,humanize(group).title()+' '+noun,[humanize(group)+' '+noun])
                sensitivity=next((v for k,v in SENSITIVE_AREAS.items() if group.startswith(k)),None)
            elif path.startswith('plugins/'):
                host=host_names.get(path.split('/')[1],path.split('/')[1]);cap=('babysitter-plugin-'+host+'-skills','Babysitter '+host+' plugin skills',['babysitter '+host+' plugin commands']);sensitivity=None
            else:
                cap=('babysitter-process-authoring','Babysitter process authoring',['scaffold babysitter process']) if is_skill else ('babysitter-repo-dev-agents','Babysitter repository development agents',['review babysitter SDK code']);sensitivity=None
            description=entity['description'] or clean_comment(re.sub(r'^---.*?---','',files.get(path,''),flags=re.S).splitlines()[:6])[:300]
            extra=duplicate_of(entity)
            if sensitivity: extra['sensitivity']=sensitivity
            finish(entity,description or humanize(entity['name']),[cap],'USE EXISTING SKILL' if is_skill else 'USE DIRECTLY','operational:01' if is_skill else 'operational:03','SKILL' if is_skill else 'MODULE','PARTIAL',['Agent host that loads '+('SKILL.md skills' if is_skill else 'agent definitions')+' (optional babysitter runtime)'],'',['category:skills' if is_skill else 'category:ai-agents'],extra=extra)
        elif kind=='UI_COMPONENT':
            package=next((p for p in KEEP_UI if path.startswith(p+'/')),None)
            if package and entity['name'] in KEEP_UI[package]:
                dashboard=package.endswith('observer-dashboard')
                cap=('run-observability-ui-components','Run observability UI components',['babysitter run dashboard components']) if dashboard else ('process-library-catalog-ui-components','Process library catalog UI components',['catalog browser components'])
                finish(entity,('Observer dashboard' if dashboard else 'Process catalog')+' React component '+entity['name']+' ('+path.rsplit('/',1)[-1]+').',[cap],'EXTRACT COMPONENTS','operational:16','COMPONENT','NO',['React','Next.js app context'],'',['category:web-applications'])
            else: drop(entity)
        elif kind=='MCP_SERVER':
            if path=='packages/sdk/src/mcp/server.ts':
                finish(entity,'babysitter MCP server (McpServer, stdio via babysitter-mcp-server): 15 tools for creating and iterating runs, posting task results, managing sessions and discovering skills/agents/processes.',[('babysitter-mcp-server-exposure','Babysitter MCP server exposure',['orchestration MCP server','process runtime MCP'])],'SECURITY REVIEW REQUIRED','operational:02','SERVICE','PARTIAL',['@modelcontextprotocol/sdk','zod','babysitter SDK runtime','process library'],'',['category:mcp-servers','category:agent-workflows'],studio,extra={'deep_review_finding':MCP_FINDING})
                server=entity
            else: drop(entity)
        elif kind=='TOOL':
            description,file,line=tools_by_file[entity['name']]
            prefix=next((p for p in ('run_','task_','session_') if entity['name'].startswith(p)),'')
            finish(entity,description+'.',[tool_caps[prefix]],'INTEGRATE VIA MCP','operational:02','SERVICE','NO',['babysitter MCP server','run directory and journal'],'',['category:mcp-servers','category:agent-workflows'],studio,extra={'deep_review_finding':MCP_FINDING} if entity['name'] in ('run_create','run_iterate') else None)
        elif kind=='WORKFLOW':
            if entity['name'] in KEEP_WORKFLOWS: finish(entity,entity['name']+' GitHub Actions workflow for the monorepo.',[CI_CAP],'REFERENCE ONLY','operational:14','COMPONENT','NO',['GitHub Actions'],'',['category:ci-cd'])
            else: drop(entity)
        elif kind in ('PACKAGE','CLI','PLUGIN'):
            segments=path.split('/')
            if path=='package.json' or segments[0]=='video' or '/examples/' in path: drop(entity);continue
            base=segments[1] if segments[0]=='plugins' else None
            manifest=path if path.endswith('package.json') else path
            description=package_descriptions.get(manifest) or ''
            if segments[0]=='packages' and segments[1]=='sdk': cap=('deterministic-process-orchestration-runtime','Deterministic process orchestration runtime',['event-sourced agent workflow runtime','babysitter SDK','process journal runtime'])
            elif segments[0]=='packages' and segments[1]=='babysitter': cap=('deterministic-process-orchestration-runtime','Deterministic process orchestration runtime',[])
            elif segments[0]=='packages' and segments[1]=='observer-dashboard': cap=('run-observability-dashboard','Run observability dashboard',['babysitter observer dashboard','agent run monitoring UI'])
            elif segments[0]=='packages' and segments[1]=='catalog': cap=('process-library-catalog-browser','Process library catalog browser',['browse babysitter process library'])
            elif segments[0]=='plugins': cap=('babysitter-harness-plugin-installation','Babysitter harness plugin installation',['install babysitter into Claude Code Codex Cursor Gemini Copilot opencode omp pi'])
            else: drop(entity);continue
            label={'PACKAGE':'npm package','CLI':'command-line entry','PLUGIN':'plugin manifest'}[kind]
            finish(entity,(entity['name']+' '+label+': '+description) if description else entity['name']+' '+label+' in '+('/'.join(segments[:2]))+'.',[cap],'USE AS LIBRARY' if kind=='PACKAGE' else 'USE DIRECTLY','operational:20' if segments[1]!='catalog' else 'operational:24','MODULE' if base else 'CORE','YES' if segments[0]=='packages' else 'NO',['Node >=20','babysitter SDK'],'',['category:agent-workflows','category:ai-orchestration'],studio,extra={'deep_review_finding':MCP_FINDING} if kind=='CLI' and entity['name']=='babysitter-mcp-server' else None)
        else: drop(entity)

    # process definitions
    process_count=0;skipped=[]
    for name in sorted(files):
        if not name.startswith('library/') or not name.endswith('.js'): continue
        text=files[name]
        if '/shared/' in name or 'shared-common' in name or not re.search(r'export\s+(?:async\s+)?(?:function|const)\s+process\b',text): skipped.append(name);continue
        process,description,inputs,outputs=parse_process(name,text)
        area=library_area(name) or 'library'
        entity=r.entity_record(repo,COMMIT,entry(name),{'type':'WORKFLOW','symbol':process,'description':'','line':1})
        cap=('babysitter-library-'+re.sub(r'[^a-z0-9]+','-',area.lower()).strip('-')+'-processes',humanize(area).title()+' processes',[humanize(area)+' process definitions'])
        extra=duplicate_of(entity)
        if inputs: extra['inputs']=inputs
        if outputs: extra['outputs']=outputs
        sensitivity=next((v for k,v in SENSITIVE_AREAS.items() if area.startswith(k)),None)
        if sensitivity: extra['sensitivity']=sensitivity
        finish(entity,description or 'Babysitter process definition '+process+'.',[cap],'USE DIRECTLY','operational:20','MODULE','NO',['@a5c-ai/babysitter-sdk runtime','agent/skill tasks the process dispatches'],'',['category:agent-workflows'],extra=extra)
        process_count+=1
    for cap,info in caps.items(): capability(cap,info['name'],info['aliases'],info['providers'],info['path'])

    by_kind={};[by_kind.setdefault(e['entity_type'],[]).append(e) for e in out.values()]
    tools=[e for e in by_kind.get('TOOL',[])]
    for tool in tools: relationship('CONTAINS',server['id'],tool['id'],tool['source']['source_path'],tool['source'].get('line',1))
    mcp_cli=next((e for e in by_kind.get('CLI',[]) if e['name']=='babysitter-mcp-server'),None)
    if mcp_cli: relationship('EXPOSES_MCP',mcp_cli['id'],server['id'],'packages/sdk/package.json',1)
    relationship('MAPS_TO_STUDIO',server['id'],'studio:agent-studio','packages/sdk/src/mcp/server.ts',1)

    counts={k:len(v) for k,v in by_kind.items()}
    notes={'UI_COMPONENT':'Retained observer-dashboard and catalog domain components; removed route pages, layouts, loading/error fragments, shadcn-style primitives, sub-fragments, providers-as-glue and the 16 video marketing components','MCP_SERVER':'Retained the babysitter server; removed 5 test-file misdetections','WORKFLOW':'%d library process definitions (+3 CI workflows); helper/shared modules without a process export were skipped, 5 generic CI workflows removed'%process_count,'PACKAGE':'Removed monorepo root, video and example packages','SKILL':'Library, methodology, plugin and repo-dev skills retained; exact duplicates across plugin hosts are flagged in metadata','AGENT':'All library agents retained'}
    for kind,count in counts.items():
        census=repo['entity_census'][kind]
        repo['entity_census'][kind]={**census,'detected':max(census['detected'],count),'catalogued':count,'reviewed':True,'detection_scope':'semantic source review','lean_review_note':notes.get(kind,'Retained by lean test')}
    repo['capabilities']=sorted({c for e in out.values() for c in e['capabilities']})
    repo['categories']=['category:agent-workflows','category:ai-orchestration','category:skills','category:ai-agents'];repo['studios']=studio;repo['recommendation']='USE DIRECTLY';repo['operational_category']='operational:20'
    repo['entity_count']=len(out);repo['phases'].update({'entity_extraction':True,'capability_analysis':True})
    repo['state']='NEEDS_REVIEW';repo['next_phase']='CAPABILITY_ANALYSIS'
    repo['semantic_review_progress']={'started_at':r.now(),'completed_at':r.now(),'status':'COMPLETE','review_policy':'LEAN','reviewer':'Claude Code lean static review','final_entity_count':len(out),'removed_entity_ids':removed,
        'confirmed_capabilities':repo['capabilities'],'scoped_deep_review':'MCP server and SDK runtime reviewed. '+MCP_FINDING,
        'implementation_details_not_catalogued':['SDK runtime, storage, replay and CLI command internals','library shared/helper JS modules ('+str(len(skipped))+' skipped files), reference markdown under skills, e2e tests, docs, video project']}
    r.write(r.repo_file(repo),repo)
    print({'repository':REPOSITORY,'entities':len(out),'by_type':counts,'processes':process_count,'removed':len(removed),'capabilities':len(repo['capabilities']),'skipped_js':len(skipped)})
if __name__=='__main__':main()
