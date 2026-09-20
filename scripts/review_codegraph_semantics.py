"""Record the LEAN SEMANTIC REVIEW of codegraph at its existing pinned commit.

Evidence base: system/evidence/1247306274.json (verified tree and blob SHAs) plus
the exact pinned source files named in each `source_review` evidence URL. No target
code was executed.
"""
from __future__ import annotations
import hashlib
import registry as r

REPOSITORY='jamesrwatsonx-creator/codegraph'
COMMIT='f366222dbd6b7e43047072a9417289b1b02ae457'
BASE='https://github.com/jamesrwatsonx-creator/codegraph/blob/'+COMMIT+'/'
AGENT_STUDIOS=['studio:agent-studio','studio:hermes-app-builder-studio']
CATEGORIES=['category:mcp-servers','category:developer-tools','category:knowledge-graphs']

def url(path,line): return BASE+path+'#L'+str(line)
def review(entity,description,capabilities,recommendation,operational,role,note,evidence,*,standalone,dependencies,categories=None,studios=None,overlaps=''):
    entity['description']=description;entity['capabilities']=capabilities;entity['recommendation']=recommendation
    entity['operational_category']=operational;entity['contribution_role']=role;entity['review_status']='VERIFIED'
    entity['categories']=categories or [];entity['studios']=studios or []
    entity['evidence']=[{'type':'source_review','value':url(p,l)} for p,l in evidence]
    entity['metadata']={'semantic_review':note,'review_policy':'LEAN','standalone':standalone,'dependencies':dependencies,'overlap':overlaps}
    r.write('registry/entities/'+entity['id'].split(':')[1]+'.json',entity)

def capability(identifier,name,aliases,providers,path,line,scope='Static source contract; runtime not tested'):
    r.write('registry/capabilities/'+identifier+'.json',{'id':'capability:'+identifier,'name':name,'aliases':aliases,'status':'VERIFIED','verification_scope':scope,'providers':sorted(providers),'evidence':[{'type':'source_review','value':url(path,line)}]})

def relationship(kind,source,target,path,line):
    identifier='relationship:'+hashlib.sha256('\0'.join([kind,source,target]).encode()).hexdigest()[:24]
    r.write('registry/relationships/'+identifier.split(':')[1]+'.json',{'id':identifier,'type':kind,'from':source,'to':target,'evidence':[{'type':'source_review','value':url(path,line)}]})

def main():
    repo=next(x for x in r.records('repositories') if x['full_name']==REPOSITORY)
    if repo['inspected_commit']!=COMMIT: raise ValueError('codegraph commit changed; preserve this review and queue a new revision')
    evidence=r.read('system/evidence/'+str(repo['github_id'])+'.json')
    read_paths={p['path']:p['blob_sha'] for p in evidence['files_read']}
    tree={e['path']:e for e in evidence['tree_entries']}
    for path in ('src/mcp/index.ts','src/mcp/tools.ts'):
        if path not in read_paths or read_paths[path]!=tree[path]['sha']: raise ValueError('Verified evidence missing for '+path)
    existing={(e['entity_type'],e['name']):e for e in r.records('entities') if e['source']['repository_id']==repo['id'] and e['source']['inspected_commit']==COMMIT}
    server_path,tools_path='src/mcp/index.ts','src/mcp/tools.ts'
    tool_specs=[('codegraph_search',305,'code-symbol-search','Symbol search by name','Quick symbol-name search over the index; returns locations only, no source. Optional node-kind filter and result limit.',['symbol search','find function by name','code symbol lookup']),
                ('codegraph_context',330,'task-context-code-retrieval','Task-context code retrieval','Primary retrieval tool: composes search, node, callers and callees for a task or bug description and returns entry points, related symbols and key code in one call.',['code context for task','codebase question answering context','architecture context retrieval']),
                ('codegraph_callers',355,'code-call-graph-navigation','Code call-graph navigation','Lists the functions, methods and classes that call a given symbol (default limit 20).',['find callers','who calls this function','call graph lookup']),
                ('codegraph_callees',375,'code-call-graph-navigation','Code call-graph navigation','Lists the functions, methods and classes a given symbol calls (default limit 20).',['find callees','what does this function call','dependency flow']),
                ('codegraph_impact',395,'code-change-impact-analysis','Code change impact analysis','Traverses dependents of a symbol to a configurable depth (default 2) to show code that could be affected by changing it.',['blast radius','change impact','impact radius']),
                ('codegraph_node',415,'code-symbol-detail-lookup','Code symbol detail lookup','Returns location, signature and docstring for one symbol; with includeCode returns a function body or a compact member outline for classes.',['symbol details','get function source','symbol signature lookup']),
                ('codegraph_explore',435,'multi-symbol-code-exploration','Multi-symbol code exploration','Returns source for several related symbols grouped by file plus a relationship map in one capped call (default 12 files).',['explore related code','multi-file code read','symbol relationship map']),
                ('codegraph_status',455,'code-index-status-and-file-structure','Code index status and file structure','Reports index statistics: indexed files, nodes and edges.',['index status','code index statistics']),
                ('codegraph_files',465,'code-index-status-and-file-structure','Code index status and file structure','Returns the indexed project file tree (tree, flat or grouped by language) with language and symbol counts, filterable by path or glob.',['project file structure','file tree from index'])]
    # MCP server and tools were not detected by the declaration census; they are read directly from source.
    server=r.entity_record(repo,COMMIT,tree[server_path],{'type':'MCP_SERVER','symbol':'codegraph','description':'','line':49})
    server_id=server['id']
    tool_entities={}
    for name,line,cap,cap_name,description,aliases in tool_specs:
        tool=r.entity_record(repo,COMMIT,tree[tools_path],{'type':'TOOL','symbol':name,'description':'','line':line})
        tool_entities[name]=tool
    review(server,'Local stdio MCP server named codegraph (started with `codegraph serve --mcp`) exposing nine code-graph tools over a per-project SQLite index; resolves the project root from client roots/list with cwd fallback.',
           ['capability:code-intelligence-mcp-server-exposure'],'INTEGRATE VIA MCP','operational:02','SERVICE','Verified server info and tool registry in source; runtime connection not tested',[(server_path,49),(tools_path,305)],
           standalone='PARTIAL',dependencies=['Node >=20 or bundled runtime','.codegraph/ index created by `codegraph init --index`','web-tree-sitter grammars','SQLite'],categories=CATEGORIES,studios=AGENT_STUDIOS,
           overlaps='ALTERNATIVE_TO jamesrwatsonx-creator/vibe-studio-seperate-idea-with-orca-codebase-memory-mcp (codebase-memory-mcp); COMPLEMENTS TencentDB-Agent-Memory knowledge MCP (different data: code graph vs memory)')
    caps={}
    for name,line,cap,cap_name,description,aliases in tool_specs:
        tool=tool_entities[name]
        review(tool,description,['capability:'+cap],'INTEGRATE VIA MCP','operational:02','SERVICE','Verified MCP tool definition (name, description, input schema); runtime not tested',[(tools_path,line)],
               standalone='NO',dependencies=['codegraph MCP server','initialized .codegraph/ index'],categories=CATEGORIES,studios=AGENT_STUDIOS)
        caps.setdefault(cap,{'name':cap_name,'aliases':set(),'providers':[],'line':line})
        caps[cap]['aliases'].update(aliases);caps[cap]['providers'].append(tool['id'])
    for cap,info in caps.items(): capability(cap,info['name'],sorted(info['aliases']),info['providers'],tools_path,info['line'])
    capability('code-intelligence-mcp-server-exposure','Code intelligence MCP server exposure',['code graph MCP server','codebase index MCP','local code knowledge graph MCP'],[server_id],server_path,49)

    cli=existing[('CLI','codegraph')];package=existing[('PACKAGE','@colbymchenry/codegraph')]
    review(cli,'`codegraph` command: init/index/sync/status/query/files/context/callers/callees/impact/affected/serve --mcp/install/uninstall. Builds a local tree-sitter to SQLite code knowledge graph and installs MCP config and instructions into Claude Code, Cursor, Codex CLI, opencode and Hermes Agent.',
           ['capability:local-code-knowledge-graph-indexing','capability:multi-agent-mcp-config-installation'],'USE DIRECTLY','operational:24','CORE','Verified package bin entry and README command surface; runtime not tested',[('package.json',7),('README.md',344),('src/installer/targets/registry.ts',17)],
           standalone='YES',dependencies=['Node >=20 <25 (or bundled runtime)','web-tree-sitter','tree-sitter-wasms','SQLite'],categories=CATEGORIES,studios=AGENT_STUDIOS,
           overlaps='ALTERNATIVE_TO codebase-memory-mcp fork in this registry; installer writes agent config files and git hooks (review before running globally)')
    review(package,'npm package @colbymchenry/codegraph 0.9.4 (MIT): thin installer plus dist library entry (main/types) for the graph, extraction, resolution, sync and MCP modules.',
           ['capability:local-code-knowledge-graph-indexing'],'USE AS LIBRARY','operational:24','MODULE','Verified package manifest; library API surface not enumerated',[('package.json',2),('package.json',44)],
           standalone='YES',dependencies=['Node >=20 <25','web-tree-sitter','tree-sitter-wasms','commander'],categories=CATEGORIES,studios=AGENT_STUDIOS,overlaps='Same distribution as the codegraph CLI entity; not a separate product')
    capability('local-code-knowledge-graph-indexing','Local code knowledge-graph indexing',['code knowledge graph','tree-sitter symbol index','pre-indexed codebase graph','local code index'],[cli['id'],package['id']],'package.json',7,'README and manifest contract; runtime not tested')
    capability('multi-agent-mcp-config-installation','Multi-agent MCP config installation',['install MCP server into Claude Code Cursor Codex','agent MCP installer'],[cli['id']],'src/installer/targets/registry.ts',17)

    add_lang=existing[('SKILL','add-lang')];agent_eval=existing[('SKILL','agent-eval')];release=existing[('WORKFLOW','Release')]
    review(add_lang,'Claude Code skill (/add-lang) that wires a new tree-sitter language into codegraph: grammar health check, extractor and tests, then benchmarks on three real repos and updates README/CHANGELOG without committing.',
           ['capability:tree-sitter-language-support-onboarding'],'REFERENCE ONLY','operational:24','SKILL','Verified SKILL.md frontmatter and workflow; not executed',[('.claude/skills/add-lang/SKILL.md',1)],
           standalone='NO',dependencies=['codegraph repo root and scripts/add-lang','node, git, gh','logged-in claude CLI'],categories=['category:skills','category:developer-tools'],studios=[],
           overlaps='Complements babysitter Tree-sitter skill (jamesrwatsonx-creator/babysitter); codegraph-specific')
    review(agent_eval,'Claude Code skill (/agent-eval) that benchmarks codegraph retrieval by running headless and tmux-driven claude sessions with and without codegraph on corpus repos.',
           ['capability:code-retrieval-agent-benchmarking'],'REFERENCE ONLY','operational:23','SKILL','Verified SKILL.md frontmatter and workflow; not executed',[('.claude/skills/agent-eval/SKILL.md',1)],
           standalone='NO',dependencies=['codegraph repo scripts/agent-eval and corpus.json','tmux 3+','logged-in claude CLI','node, git'],categories=['category:skills','category:ai-evaluation'],studios=[])
    review(release,'Manually triggered GitHub Actions release: builds per-platform self-contained bundles, checksums, creates a GitHub Release from CHANGELOG notes, publishes the npm shim and platform packages, and verifies them on the registry.',
           ['capability:multi-platform-release-publishing'],'REFERENCE ONLY','operational:14','COMPONENT','Verified workflow header and steps; not executed',[('.github/workflows/release.yml',1)],
           standalone='NO',dependencies=['package.json and CHANGELOG.md conventions','scripts/build-bundle.sh, scripts/pack-npm.sh','NPM_TOKEN secret'],categories=['category:ci-cd','category:devops'],studios=[])
    capability('tree-sitter-language-support-onboarding','Tree-sitter language support onboarding',['add language to code indexer','tree-sitter grammar wiring'],[add_lang['id']],'.claude/skills/add-lang/SKILL.md',1)
    capability('code-retrieval-agent-benchmarking','Code retrieval agent benchmarking',['agent A/B benchmark with and without tool','MCP retrieval quality audit'],[agent_eval['id']],'.claude/skills/agent-eval/SKILL.md',1)
    capability('multi-platform-release-publishing','Multi-platform release publishing',['GitHub release and npm publish workflow','cross-platform bundle release'],[release['id']],'.github/workflows/release.yml',1)

    relationship('EXPOSES_MCP',cli['id'],server_id,'README.md',359)
    relationship('CONTAINS',package['id'],cli['id'],'package.json',7)
    for tool in tool_entities.values(): relationship('CONTAINS',server_id,tool['id'],tools_path,int(tool['source']['line']))
    relationship('DEPENDS_ON',add_lang['id'],cli['id'],'.claude/skills/add-lang/SKILL.md',1)
    relationship('DEPENDS_ON',agent_eval['id'],cli['id'],'.claude/skills/agent-eval/SKILL.md',1)
    peer=next((x for x in r.records('repositories') if x['full_name']=='jamesrwatsonx-creator/vibe-studio-seperate-idea-with-orca-codebase-memory-mcp'),None)
    if peer: relationship('ALTERNATIVE_TO',repo['id'],peer['id'],'README.md',1)

    counts={'MCP_SERVER':1,'TOOL':len(tool_specs),'SKILL':2,'WORKFLOW':1,'PACKAGE':1,'CLI':1}
    for kind,count in counts.items():
        note={'MCP_SERVER':'Read from src/mcp/index.ts; not found by declaration scan','TOOL':'Nine MCP tool definitions read from src/mcp/tools.ts'}.get(kind,'Retained by lean test')
        repo['entity_census'][kind]={**repo['entity_census'][kind],'detected':count,'catalogued':count,'reviewed':True,'detection_scope':'semantic source review','lean_review_note':note}
    repo['capabilities']=sorted({c for e in [server,cli,package,add_lang,agent_eval,release,*tool_entities.values()] for c in e['capabilities']})
    repo['categories']=CATEGORIES;repo['studios']=AGENT_STUDIOS;repo['recommendation']='USE DIRECTLY';repo['operational_category']='operational:24'
    repo['entity_count']=sum(counts.values());repo['phases'].update({'entity_extraction':True,'capability_analysis':True})
    repo['state']='NEEDS_REVIEW';repo['next_phase']='CAPABILITY_ANALYSIS'
    repo['semantic_review_progress']={'started_at':r.now(),'completed_at':r.now(),'status':'COMPLETE','review_policy':'LEAN','reviewer':'Claude Code lean static review','final_entity_count':repo['entity_count'],
        'confirmed_entity_ids':[server_id]+[t['id'] for t in tool_entities.values()]+[cli['id'],package['id'],add_lang['id'],agent_eval['id'],release['id']],'confirmed_capabilities':repo['capabilities'],
        'implementation_details_not_catalogued':['src/extraction/languages/* language extractors and src/resolution/frameworks/* framework resolvers (internal to the indexer)','src/db, src/graph, src/search, src/sync, src/context, src/ui internals','__tests__ and scripts/*']}
    r.write(r.repo_file(repo),repo)
    print({'repository':REPOSITORY,'entities':repo['entity_count'],'capabilities':len(repo['capabilities'])})
if __name__=='__main__':main()
