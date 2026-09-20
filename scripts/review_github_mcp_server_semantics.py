"""Record the LEAN SEMANTIC REVIEW of github-mcp-server at its existing pinned commit.

The declaration scan found only workflows, a UI package and three components; the MCP server
itself and its 109 Go-defined tools were missed and are added from pkg/github/*.go.
Scoped deep review: the server acts with the caller's GitHub credentials, so write-capable
tools, token handling and available narrowing flags were checked.
Set GH_TARBALL to the pinned tarball; every file is blob-SHA verified.
"""
from __future__ import annotations
import re
from lean_review_lib import LeanReview

CATS=['category:mcp-servers','category:developer-tools']
STUDIOS=['studio:integrations-api-infrastructure']
KEEP_WORKFLOWS={'AI Issue Assessment':'AI-assisted issue assessment workflow.','AI Moderator':'AI-assisted moderation workflow.','CodeQL':'CodeQL code-scanning workflow.','Docker':'Docker image publish workflow.',
                'Build and Test Go Project':'Go build and test workflow.','GoReleaser Release':'GoReleaser release workflow.','golangci-lint':'golangci-lint workflow.','MCP Server Diff':'Workflow comparing MCP server output (tools/schemas) between revisions.','Publish to MCP Registry':'Workflow publishing the server to the MCP Registry.'}
KEEP_UI={'MarkdownEditor'}
APPS={'get-me':'GetMeApp','issue-write':'IssueWriteApp','pr-edit':'PrEditApp','pr-write':'PrWriteApp'}

def go_strings(text):
    out=[];i=0
    while i<len(text):
        c=text[i]
        if c=='"':
            j=i+1;buf=[]
            while text[j]!='"':
                if text[j]==chr(92): buf.append(text[j+1]);j+=2
                else: buf.append(text[j]);j+=1
            out.append(''.join(buf));i=j+1
        elif c=='`':
            j=text.index('`',i+1);out.append(text[i+1:j]);i=j+1
        elif c==')': break
        else: i+=1
    return ''.join(out)

def parse_tools(source):
    tools=[]
    for m in re.finditer(r'mcp\.Tool\{',source):
        after=source[m.end():m.end()+4000]
        name=re.match(r'\s*Name:\s*"([A-Za-z0-9_]+)"',after)
        if not name: continue
        desc=re.search(r'Description:\s*t\("[A-Z0-9_]+",\s*',after)
        toolset=re.findall(r'NewTool\w*\(\s*(?:Toolset(?:Metadata)?)(\w+),',source[max(0,m.start()-200):m.start()])
        title=re.search(r'Title:\s*t\("[A-Z0-9_]+",\s*',after)
        scopes=re.search(r'\[\]scopes\.Scope\{([^}]*)\}',after)
        tools.append({'name':name.group(1),'description':go_strings(after[desc.end():]) if desc and after[desc.end()]=='"' else (go_strings(after[title.end():]) if title else ''),'read_only':'ReadOnlyHint: true' in after.split('InputSchema')[0],
                      'toolset':toolset[-1] if toolset else None,'scopes':[s.strip().replace('scopes.','') for s in scopes.group(1).split(',') if s.strip()] if scopes else [],'line':source[:m.start()].count('\n')+1})
    return tools

def kebab(camel): return re.sub(r'(?<!^)(?=[A-Z])','-',camel).lower()

def package_doc(text):
    lines=[]
    for line in text.splitlines():
        if line.startswith('// Package'): lines.append(line[3:])
        elif lines and line.startswith('//'): lines.append(line[2:].strip())
        elif lines: break
    return ' '.join(lines)

def yaml_field(text,key):
    m=re.search(r'^'+key+r':\s*(.+)$',text,flags=re.M)
    return m.group(1).strip().strip('"\'') if m else ''

def main():
    review=LeanReview('jamesrwatsonx-creator/github-mcp-server','eb088dfe9d854dab6453a8d4ae5871a5ced20974','GH_TARBALL')
    tools=[]
    for path in sorted(review.files):
        if path.startswith('pkg/github/') and path.endswith('.go') and not path.endswith('_test.go'):
            for tool in parse_tools(review.files[path]): tool['path']=path;tools.append(tool)
    names=[t['name'] for t in tools]
    if len(names)!=len(set(names)) or len(tools)<100: raise ValueError('Unexpected tool census: %d tools, %d unique'%(len(names),len(set(names))))
    writers=[t['name'] for t in tools if not t['read_only']]
    finding=('The server acts with the caller\'s GitHub credentials (PAT via GITHUB_PERSONAL_ACCESS_TOKEN, or OAuth); %d of %d tools lack a ReadOnlyHint and can mutate GitHub state (repositories, issues, pull requests, gists, workflows and more). '
             'Narrow exposure with --read-only, --toolsets and --exclude-tools (cmd/github-mcp-server/main.go); HTTP mode adds token, PAT-scope and scope-challenge middleware (pkg/http/middleware). '
             'No token persistence to disk was found in internal/oauth (no file-write calls).')%(len(writers),len(tools))
    server_path='internal/ghmcp/server.go'
    line=next((i for i,l in enumerate(review.files[server_path].splitlines(),1) if l.startswith('func New')),1)
    server=review.make('MCP_SERVER','github-mcp-server',server_path,line)
    review.finish(server,'GitHub\'s official MCP server (Go): %d tools across GitHub toolsets over stdio or HTTP, with toolset selection, read-only mode, lockdown mode, tool exclusion, insiders features and OAuth or PAT authentication.'%len(tools),
                  [('github-mcp-server-exposure','GitHub MCP server exposure',['GitHub MCP server','official GitHub MCP','GitHub tools for agents'])],'SECURITY REVIEW REQUIRED','operational:02','SERVICE','PARTIAL',['GitHub account credentials (PAT or OAuth)','Go binary or Docker image','GitHub API access'],
                  'Wraps the GitHub API; complements git/CI skills in this registry',CATS,STUDIOS,extra={'deep_review_finding':finding})
    tool_ids={}
    for tool in tools:
        entity=review.make('TOOL',tool['name'],tool['path'],tool['line'])
        toolset=kebab(tool['toolset']) if tool['toolset'] else 'core'
        cap=('github-'+toolset+'-mcp-tools','GitHub '+toolset.replace('-',' ')+' MCP tools',['GitHub '+toolset.replace('-',' ')+' tools','github '+toolset.replace('-',' ')+' via MCP'])
        review.finish(entity,tool['description'] or 'GitHub MCP tool '+tool['name']+'.',[cap],'INTEGRATE VIA MCP','operational:02','SERVICE','NO',['github-mcp-server','GitHub API access'+(' with scopes: '+', '.join(tool['scopes']) if tool['scopes'] else '')],'',CATS,STUDIOS,
                      extra={'read_only':tool['read_only'],'toolset':toolset,'required_scopes':tool['scopes'],**({'write_capable':True,'deep_review_finding':'Can mutate GitHub state; enable only with --read-only off and a scoped token.'} if not tool['read_only'] else {})})
        tool_ids[tool['name']]=entity['id'];review.relate('CONTAINS',server['id'],entity['id'],tool['path'],tool['line'])

    def component(kind,symbol,path,description,cap,name,aliases,rec,opcat,standalone,deps,categories=CATS):
        entity=review.make(kind,symbol,path)
        return review.finish(entity,description,[(cap,name,aliases)],rec,opcat,'MODULE',standalone,deps,'',categories,STUDIOS)
    cli=component('CLI','github-mcp-server','cmd/github-mcp-server/main.go','`github-mcp-server` command: stdio and HTTP serving with toolset, read-only, lockdown, exclude-tools, insiders and OAuth options; also documentation/scope listing helpers.','github-mcp-server-exposure','GitHub MCP server exposure',[],'USE DIRECTLY','operational:02','YES',['Go binary or Docker image','GitHub credentials'])
    review.relate('EXPOSES_MCP',cli['id'],server['id'],'cmd/github-mcp-server/main.go',1)
    mcpcurl_readme=review.files.get('cmd/mcpcurl/README.md','')
    mcpcurl_desc=next((l.strip() for l in mcpcurl_readme.splitlines()[1:] if l.strip() and not l.startswith('#')),'')
    component('CLI','mcpcurl','cmd/mcpcurl/main.go','mcpcurl: '+(mcpcurl_desc or 'curl-like command-line client for calling MCP server tools.'),'mcp-server-command-line-client','MCP server command-line client',['call MCP tools from the shell','mcp curl'],'EXTRACT COMPONENTS','operational:02','YES',['Go','a running MCP server'])
    for symbol,path,fallback,cap,name,aliases in [('inventory','pkg/inventory/registry.go','Tool, resource and prompt inventory with toolset filtering and instruction generation.','mcp-tool-inventory-and-toolset-filtering','MCP tool inventory and toolset filtering',['compose MCP toolsets','filter MCP tools']),
                                                   ('scopes','pkg/scopes/scopes.go','Mapping between GitHub token scopes and tool requirements.','github-token-scope-mapping','GitHub token scope mapping',['PAT scope to tool mapping']),
                                                   ('oauth','internal/oauth/oauth.go','OAuth authorization manager (browser and device flows) for the server.','oauth-browser-and-device-login-flow','OAuth browser and device login flow',['OAuth PKCE login','device flow login'])]:
        component('LIBRARY',symbol,path,package_doc(review.files[path]) or fallback,cap,name,aliases,'EXTRACT COMPONENTS','operational:12' if symbol!='oauth' else 'operational:21','NO',['Go','github-mcp-server module'])
    module=review.make('PACKAGE','github-mcp-server (Go module)','go.mod')
    review.finish(module,'Go module github.com/github/github-mcp-server providing the server, CLI and reusable pkg/ libraries.',[('github-mcp-server-exposure','GitHub MCP server exposure',[])],'USE AS LIBRARY','operational:02','CORE','YES',['Go'],'',CATS,STUDIOS)

    for entity in sorted(review.existing,key=lambda e:e['id']):
        if entity['id'] in review.out: continue
        kind=entity['entity_type'];path=entity['source']['source_path']
        if kind=='WORKFLOW':
            if entity['name'] in KEEP_WORKFLOWS: review.finish(entity,KEEP_WORKFLOWS[entity['name']],[('ci-test-and-release-pipeline','CI test and release pipeline',[])],'REFERENCE ONLY','operational:14','COMPONENT','NO',['GitHub Actions'],'',['category:ci-cd'])
            else: review.drop(entity)
        elif kind=='AGENT':
            review.finish(entity,entity['description'],[('mcp-tool-migration-agent','MCP tool migration agent',['migrate MCP tools between Go SDKs'])],'REFERENCE ONLY','operational:24','MODULE','NO',['GitHub Copilot agent support','this repository\'s pkg/github layout'],'',['category:ai-agents'])
        elif kind=='PACKAGE':
            review.finish(entity,'@github/mcp-server-ui: MCP App UIs for github-mcp-server built with Primer React and Vite.',[('mcp-app-ui-for-github-tools','MCP App UI for GitHub tools',['MCP apps UI','interactive GitHub tool forms'])],'USE AS LIBRARY','operational:16','MODULE','NO',['Node','React','Primer React','github-mcp-server (MCP Apps)'],'',CATS,STUDIOS)
        elif kind=='UI_COMPONENT':
            if entity['name'] in KEEP_UI: review.finish(entity,'Markdown editor React component used by the write-issue and write-PR apps.',[('mcp-app-ui-for-github-tools','MCP App UI for GitHub tools',[])],'EXTRACT COMPONENTS','operational:16','COMPONENT','NO',['React','Primer React'],'',['category:web-applications'])
            else: review.drop(entity)
        else: review.drop(entity)
    for folder,symbol in APPS.items():
        path='ui/src/apps/'+folder+'/App.tsx'
        entity=review.make('UI_COMPONENT',symbol,path)
        review.finish(entity,'MCP App UI (Primer React) for the '+folder.replace('-',' ')+' flow of github-mcp-server, rendered by MCP Apps-capable clients.',[('mcp-app-ui-for-github-tools','MCP App UI for GitHub tools',[])],'INTEGRATE VIA MCP','operational:16','COMPONENT','NO',['React','Primer React','github-mcp-server tools'],'',CATS,STUDIOS)
    for path in sorted(p for p in review.files if p.startswith('.github/prompts/') and p.endswith('.prompt.yml')):
        entity=review.make('PROMPT',path.rsplit('/',1)[1][:-len('.prompt.yml')],path)
        review.finish(entity,(yaml_field(review.files[path],'name') or 'Issue review prompt')+' (GitHub Models prompt used by the AI issue assessment workflow).',[('github-issue-review-prompts','GitHub issue review prompts',['issue triage prompt','bug report review prompt'])],'REFERENCE ONLY','operational:20','COMPONENT','YES',['GitHub Models prompt format'],'',['category:prompt-libraries'])
    print(review.finalize(CATS,STUDIOS,'INTEGRATE VIA MCP','operational:02',
        {'MCP_SERVER':'The server and 109 Go-defined tools were missed by the declaration scan and added from pkg/github and internal/ghmcp','TOOL':'%d tools, %d read-only and %d write-capable'%(len(tools),len(tools)-len(writers),len(writers)),'WORKFLOW':'Retained 9 of 13; removed close-inactive, docs-check, issue-labeler, license-check','UI_COMPONENT':'Kept MarkdownEditor; removed AppProvider and FeedbackFooter as glue; added four MCP App UIs','PROMPT':'Two issue-review prompts retained'},
        deep_review=finding,details=['pkg/github helpers, internal/githubv4mock, toolsnaps, pkg/http internals, docs and installation guides','tests and e2e']))
if __name__=='__main__':main()
