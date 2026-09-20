"""Record the LEAN SEMANTIC REVIEW of hermes-agent at its existing pinned commit.

Core Hermes infrastructure, so a scoped deep review of the trust model, command approval,
credential persistence and gateway authorization was applied (from SECURITY.md and the named
modules). The declaration scan missed the runtime's registered agent tools, the plugin
ecosystem (model providers, memory, messaging platforms, image/browser/dashboard-auth plugins)
and the core services; they are added from source. Set HERMES_TARBALL to the pinned tarball.
"""
from __future__ import annotations
import ast,collections,json,re
from lean_review_lib import LeanReview

CATS=['category:ai-agents','category:agent-frameworks']
STUDIOS=['studio:agent-studio']
SKIP_PREFIXES=('tests/','website/','apps/','ui-tui/','web/','locales/','skills/','optional-skills/','tests-js/','docs/')
SENSITIVE_TOOL=re.compile(r'terminal|code_exec|file|patch|computer|browser|send_message|cron|delegate|credential|shell|process|ssh|docker|kanban|discord|clipboard',re.I)
SENSITIVE_SKILL_CATEGORIES={'finance':'financial data and trading guidance','payments':'payment flows','blockchain':'wallet and blockchain operations','security':'dual-use security content','health':'health data','email':'email account access','social-media':'posting to social accounts'}
KEEP_WORKFLOWS={'CI':'Main CI workflow.','Tests':'Test workflow.','Docker Build, Test, and Publish':'Docker image build, test and publish workflow.','Install & Update E2E':'End-to-end install and update test workflow.','Installer tests':'Installer test workflow.',
                'OSV-Scanner':'OSV-Scanner dependency vulnerability scan workflow.','Nix flake check':'Nix flake check workflow.','Rust tests':'Rust test workflow.','Skills Index Freshness Check':'Checks that the generated skills index is current.','Build Skills Index':'Builds the skills index.',
                'Lint (ruff + ty)':'Python lint and type-check workflow (ruff and ty).','JS Tests':'JavaScript test workflow.','E2E Desktop':'Desktop app end-to-end test workflow.','Deploy Site':'Documentation site deploy workflow.'}
KEEP_PACKAGES={'hermes-agent':'pyproject.toml','@hermes/ink':None,'@hermes/shared':None,'hermes':None,'hermes-tui':None,'@hermes/bootstrap-installer':None,'web':None,'hermes-whatsapp-bridge':None,'@hermes-agent/photon-sidecar':None}
DROP_UI_DIRS=('apps/desktop/src/components/ui/','ui-tui/packages/','apps/desktop/src/app/overlays/','apps/desktop/src/app/contrib/','apps/desktop/src/contrib/','apps/desktop/src/lib/','apps/bootstrap-installer/','web/src/contexts/','web/src/i18n/','web/src/themes/','ui-tui/src/sdk/','ui-tui/src/lib/','apps/desktop/src/i18n/','apps/desktop/src/themes/','website/','apps/desktop/src/app/master-detail.tsx')
UI_KEEP=re.compile(r'(View|Page|Panel|Overlay|Dialog|Picker|Switcher|Board|Drawer|Pane|Editor|Composer|Palette|Modal|Form|Renderer|Terminal|Preview|Card|Tree|Banner|Menu|Manager|Message|Thread|Section|Popover|Bar|Rail|Host|Settings|Tab)$')
UI_APPS=(('apps/desktop/','Hermes desktop app'),('ui-tui/','Hermes terminal UI (Ink)'),('web/','Hermes web dashboard'))
CORE=[('AGENT_FRAMEWORK','AIAgent','run_agent.py',r'^class AIAgent','AI agent with tool calling: manages the conversation flow, tool execution and response handling for function-calling models (run_agent.py AIAgent).','hermes-agent-runtime','Hermes agent runtime',['hermes agent loop','self-improving agent runtime'],'USE AS LIBRARY','operational:03'),
      ('SERVICE','GatewayRunner','gateway/run.py',r'^class GatewayRunner','Main gateway controller (entry point for messaging platform integrations): manages the lifecycle of all platform adapters and routes messages to and from the agent; inbound user authorization lives in gateway/authz_mixin.py.','hermes-messaging-gateway','Hermes messaging gateway',['multi-platform chat gateway for agents'],'INTEGRATE AS SERVICE','operational:12'),
      ('COMPONENT','cron-scheduler','cron/scheduler.py',None,'Cron job scheduler that executes due jobs.','hermes-scheduled-agent-jobs','Hermes scheduled agent jobs',['agent cron jobs'],'EXTRACT COMPONENTS','operational:20'),
      ('SERVICE','acp-server','acp_adapter/server.py',None,'ACP agent server: exposes Hermes Agent via the Agent Client Protocol.','hermes-acp-server','Hermes ACP server',['agent client protocol server'],'INTEGRATE AS SERVICE','operational:24'),
      ('COMPONENT','context-compressor','agent/context_compressor.py',None,'Automatic context window compression for long conversations.','agent-context-compaction','Agent context compaction',['compress conversation context'],'EXTRACT COMPONENTS','operational:04'),
      ('COMPONENT','credential-pool','agent/credential_pool.py',None,'Persistent multi-credential pool for same-provider failover; borrowed secrets are stripped before disk writes (agent/credential_persistence.py).','provider-credential-pooling','Provider credential pooling',['api key rotation pool'],'EXTRACT COMPONENTS','operational:21'),
      ('COMPONENT','dangerous-command-approval','tools/approval.py',None,'Dangerous-command detection, per-session approval state, CLI and gateway prompting, optional auxiliary-LLM smart approval and a persistent allowlist.','agent-dangerous-command-approval','Agent dangerous-command approval',['command approval gate','shell command safety prompts'],'EXTRACT COMPONENTS','operational:21'),
      ('COMPONENT','tool-registry','tools/registry.py',None,'Central registry for all hermes-agent tools; tools register with a name, toolset, schema and handler.','agent-tool-registry','Agent tool registry',['tool registration and toolsets'],'EXTRACT COMPONENTS','operational:03'),
      ('COMPONENT','provider-profile-base','providers/base.py',None,'Provider profile base class for model providers (providers/base.py).','hermes-model-providers-plugins','Hermes model providers plugins',[],'EXTRACT COMPONENTS','operational:15'),
      ('COMPONENT','batch-runner','batch_runner.py',None,'Batch agent runner: parallel processing of dataset prompts with checkpoint/resume, trajectory saving and aggregated tool-usage statistics.','agent-trajectory-batch-generation','Agent trajectory batch generation',['batch agent runs'],'EXTRACT COMPONENTS','operational:23'),
      ('SERVICE','dashboard-web-server','hermes_cli/web_server.py',None,'Hermes Agent web UI server exposing the REST routes catalogued as API entities (sessions, config, skills, MCP, cron, models and system controls).','hermes-dashboard-web-server','Hermes dashboard web server',['agent dashboard API'],'INTEGRATE AS SERVICE','operational:12'),
      ('MCP_SERVER','hermes-mcp-serve','mcp_serve.py',None,'Hermes MCP server: exposes messaging conversations as MCP tools (conversations, messages, events, attachments and approval responses).','hermes-messaging-mcp-server','Hermes messaging MCP server',['Hermes as MCP server'],'INTEGRATE VIA MCP','operational:02')]
TEMPLATES={'api_wrapper':'FastMCP template wrapping an HTTP API as an MCP server.','file_processor':'FastMCP template for a file-processing MCP server.','database_server':'FastMCP template for a database-backed MCP server.'}

def literal_join(text):
    pieces=re.findall(r'(?:[rbfRBF]{0,2})("(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\')',text)
    out=[]
    for piece in pieces:
        try: out.append(ast.literal_eval(piece))
        except Exception: out.append(piece[1:-1])
    return ''.join(out)
def module_doc(text):
    m=re.match(r'\s*(?:#![^\n]*\n)?\s*(?:r?"""|\'\'\')(.*?)(?:"""|\'\'\')',text,flags=re.S)
    if not m: return ''
    lines=[l.strip() for l in m.group(1).strip().splitlines()]
    para=[]
    for l in lines:
        if not l:
            if para: break
            continue
        para.append(l)
    return ' '.join(para)[:300]
def first_paragraph(text,limit=240):
    para=[]
    for l in [x.strip() for x in (text or '').splitlines()]:
        if not l:
            if para: break
            continue
        para.append(l)
    return ' '.join(para)[:limit]
def yaml_value(text,key):
    m=re.search(r'^'+key+r':\s*(.*)$',text,flags=re.M)
    if not m: return ''
    value=m.group(1).strip()
    if value in ('>','|','>-','|-'):
        rest=text[m.end():].splitlines()[1:]
        lines=[]
        for line in rest:
            if line.startswith((' ','\t')): lines.append(line.strip())
            else: break
        return ' '.join(lines)
    return value.strip('"\'')
def kebab(text): return re.sub(r'[^a-z0-9]+','-',text.lower()).strip('-')
def humanize(name): return re.sub(r'(?<=[a-z0-9])(?=[A-Z])',' ',name).replace('_',' ').replace('-',' ')

def main():
    review=LeanReview('jamesrwatsonx-creator/hermes-agent','261a4efb90d7dbe4e71786861858f721b4ab730c')
    import os
    review.load_tarball(os.environ['HERMES_TARBALL'],wanted=lambda n:not n.startswith(SKIP_PREFIXES) or n.startswith(('plugins/',)))
    seen=set()
    # ---- core components
    core={}
    for kind,symbol,path,pattern,description,cap,cap_name,aliases,rec,opcat in CORE:
        text=review.files[path]
        line=next((i for i,l in enumerate(text.splitlines(),1) if pattern and re.match(pattern,l)),1)
        entity=review.make(kind,symbol,path,line)
        review.finish(entity,description,[(cap,cap_name,aliases)],rec,opcat,'CORE' if kind in ('AGENT_FRAMEWORK','SERVICE') else 'MODULE','PARTIAL',['Python >=3.11','Hermes agent runtime'],'',CATS,STUDIOS)
        core[symbol]=entity;seen.add(entity['id'])
    mcp_server=core['hermes-mcp-serve']
    for stem,description in TEMPLATES.items():
        template=review.make('TEMPLATE','fastmcp-'+stem+'-template','optional-skills/mcp/fastmcp/templates/'+stem+'.py')
        review.finish(template,description,[('fastmcp-server-templates','FastMCP server templates',['MCP server scaffolds','FastMCP starter'])],'USE DIRECTLY','operational:02','MODULE','YES',['Python','fastmcp'],'',['category:mcp-servers','category:skills'],STUDIOS)
        seen.add(template['id'])
    # ---- registered agent tools
    tool_count=0;tools=[]
    for path in sorted(review.files):
        if not (path.startswith(('tools/','plugins/','agent/','gateway/')) and path.endswith('.py')): continue
        text=review.files[path]
        for m in re.finditer(r'^\s*registry\.register\(',text,flags=re.M):
            block=text[m.end():m.end()+1600]
            name=re.search(r'name\s*=\s*"([A-Za-z0-9_\-]+)"',block);toolset=re.search(r'toolset\s*=\s*"([A-Za-z0-9_\-]+)"',block);schema=re.search(r'schema\s*=\s*(\w+)',block)
            if not name: continue
            description=''
            if schema:
                d=re.search(r'\b'+re.escape(schema.group(1))+r'\s*=\s*\{',text)
                if d:
                    desc=re.search(r'"description"\s*:\s*((?:\(?\s*[rfb]{0,2}(?:"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\')\s*\)?\s*)+)',text[d.end():d.end()+4000])
                    if desc: description=first_paragraph(literal_join(desc.group(1)),300)
            env=re.search(r'requires_env\s*=\s*\[([^\]]*)\]',block)
            tools.append((path,name.group(1),toolset.group(1) if toolset else 'core',description,re.findall(r'"([A-Z0-9_]+)"',env.group(1)) if env else [],text[:m.start()].count('\n')+1))
    if len({t[1] for t in tools})!=len(tools): raise ValueError('Duplicate registered tool names; inspect before applying')
    for path,name,toolset,description,env,line in tools:
        entity=review.make('TOOL',name,path,line)
        extra={'toolset':toolset}
        if SENSITIVE_TOOL.search(name+' '+toolset): extra['sensitivity']='executes code, changes files or accounts, or drives a browser; gated by the approval system and terminal backend choice'
        review.finish(entity,description or 'Hermes agent tool '+name+' (toolset '+toolset+').',[('hermes-'+kebab(toolset)+'-tools','Hermes '+toolset.replace('_',' ')+' tools',['hermes '+toolset.replace('_',' ')+' toolset'])],'EXTRACT COMPONENTS','operational:03','COMPONENT','NO',['Hermes tool registry']+(['env: '+', '.join(env)] if env else []),'',CATS,STUDIOS,extra=extra)
        seen.add(entity['id']);tool_count+=1
    # ---- plugins
    plugin_count=collections.Counter()
    manifests=sorted(p for p in review.files if re.fullmatch(r'plugins/[^/]+/[^/]+/plugin\.yaml',p) or re.fullmatch(r'plugins/[^/]+/plugin\.yaml',p) or re.fullmatch(r'plugins/[^/]+/dashboard/manifest\.json',p))
    for path in manifests:
        text=review.files[path];parts=path.split('/')
        if path.endswith('.json'):
            data=json.loads(text);name=data.get('name') or parts[1];description=data.get('description') or 'Dashboard plugin '+name;group=parts[1];kind='dashboard-plugin'
        else:
            group=parts[1] if len(parts)==4 else 'core';name=yaml_value(text,'name') or parts[-2];kind=yaml_value(text,'kind');description=first_paragraph(yaml_value(text,'description')) or 'Hermes plugin '+name
        etype='MODEL_ADAPTER' if kind=='model-provider' else 'INTEGRATION' if kind=='platform' else 'PLUGIN'
        cap=('hermes-'+kebab(group)+'-plugins','Hermes '+group.replace('_',' ').replace('-',' ')+' plugins',['hermes '+group.replace('_',' ').replace('-',' ')+' plugin'])
        entity=review.make(etype,name,path)
        deps=re.findall(r'^\s+-\s+(.+)$',text[text.find('pip_dependencies'):text.find('pip_dependencies')+300],flags=re.M) if 'pip_dependencies' in text else []
        review.finish(entity,description,[cap],'USE DIRECTLY' if etype!='PLUGIN' else 'EXTRACT COMPONENTS','operational:15' if etype=='MODEL_ADAPTER' else 'operational:12' if etype=='INTEGRATION' else 'operational:20','MODULE','PARTIAL',['Hermes plugin loader']+deps,'',CATS,STUDIOS,extra={'plugin_group':group,'plugin_kind':kind or group})
        seen.add(entity['id']);plugin_count[etype]+=1
    # builtin gateway platform adapters
    for path in ('gateway/platforms/api_server.py','gateway/platforms/bluebubbles.py','gateway/platforms/msgraph_webhook.py','gateway/platforms/signal.py','gateway/platforms/webhook.py','gateway/platforms/weixin.py','gateway/platforms/whatsapp_cloud.py','gateway/platforms/yuanbao.py'):
        text=review.files[path];name=path.rsplit('/',1)[1][:-3]
        entity=review.make('INTEGRATION','gateway-'+name,path)
        review.finish(entity,module_doc(text) or 'Built-in gateway adapter for '+name.replace('_',' ')+'.',[('hermes-platforms-plugins','Hermes platforms plugins',[])],'USE DIRECTLY','operational:12','MODULE','PARTIAL',['Hermes gateway','platform credentials'],'',CATS,STUDIOS,extra={'plugin_group':'platforms','plugin_kind':'builtin-platform'})
        seen.add(entity['id']);plugin_count['INTEGRATION']+=1
    # ---- existing entities
    kept=collections.Counter();dropped=collections.Counter()
    api_by_path=collections.defaultdict(list)
    for entity in sorted(review.existing,key=lambda e:e['id']):
        if entity['id'] in seen or entity['id'] in review.out: continue
        kind=entity['entity_type'];path=entity['source']['source_path']
        if kind=='SKILL':
            parts=path.split('/');bundle='optional' if parts[0]=='optional-skills' else 'bundled';category=parts[1] if len(parts)>2 else 'general'
            extra={'skill_bundle':bundle,'skill_category':category}
            if category in SENSITIVE_SKILL_CATEGORIES: extra['sensitivity']=SENSITIVE_SKILL_CATEGORIES[category]
            review.finish(entity,entity['description'],[('hermes-'+bundle+'-'+kebab(category)+'-skills','Hermes '+bundle+' '+category.replace('-',' ')+' skills',[category.replace('-',' ')+' skills for Hermes'])],'USE EXISTING SKILL','operational:01','SKILL','PARTIAL',['Agent host that loads SKILL.md skills (Hermes skills hub format)'],'',['category:skills'],extra=extra)
        elif kind=='MCP_SERVER':
            review.drop(entity);dropped['MCP_SERVER']+=1
        elif kind=='TOOL':
            review.finish(entity,first_paragraph(entity['description']) or 'Hermes MCP tool '+entity['name']+'.',[('hermes-messaging-mcp-tools','Hermes messaging MCP tools',['messaging conversations over MCP'])],'INTEGRATE VIA MCP','operational:02','SERVICE','NO',['hermes-mcp-serve','running Hermes gateway'],'',['category:mcp-servers'],STUDIOS)
            review.relate('CONTAINS',mcp_server['id'],entity['id'],path,entity['source'].get('line',1))
        elif kind=='CLI':
            descriptions={'hermes':'`hermes` main command-line interface (hermes_cli.main:main).','hermes-agent':'`hermes-agent` direct agent entry point (run_agent:main).','hermes-acp':'`hermes-acp` Agent Client Protocol entry point (acp_adapter.entry:main).'}
            review.finish(entity,descriptions[entity['name']],[('hermes-agent-runtime','Hermes agent runtime',[])],'USE DIRECTLY','operational:03','CORE','YES',['Python >=3.11'],'',CATS,STUDIOS)
        elif kind=='PACKAGE':
            if entity['name'] in KEEP_PACKAGES and (KEEP_PACKAGES[entity['name']] is None or path==KEEP_PACKAGES[entity['name']]):
                review.finish(entity,entity['description'] or entity['name']+' package ('+path+').',[('hermes-agent-runtime','Hermes agent runtime',[])],'USE AS LIBRARY','operational:03','MODULE','PARTIAL',['Node or Python toolchain'],'',CATS,STUDIOS)
            else: review.drop(entity);dropped['PACKAGE']+=1
        elif kind=='WORKFLOW':
            if entity['name'] in KEEP_WORKFLOWS: review.finish(entity,KEEP_WORKFLOWS[entity['name']],[('ci-test-and-release-pipeline','CI test and release pipeline',[])],'REFERENCE ONLY','operational:14','COMPONENT','NO',['GitHub Actions'],'',['category:ci-cd'])
            else: review.drop(entity);dropped['WORKFLOW']+=1
        elif kind=='API':
            if path.startswith('tests/'): review.drop(entity);dropped['API']+=1;continue
            lines=review.files[path].splitlines() if path in review.files else []
            line=entity['source'].get('line',1);window='\n'.join(lines[max(0,line-8):line])
            route=re.findall(r'@\w+\.(get|post|put|patch|delete)\(\s*"([^"]*)"',window)
            label=(route[-1][0].upper()+' '+route[-1][1]) if route else ''
            existing_text=re.sub(r'^(?:(?:GET|POST|PUT|PATCH|DELETE) \S+ - )+','',entity['description'])  # idempotent on re-runs
            if re.fullmatch(r'(?:GET|POST|PUT|PATCH|DELETE) \S+ endpoint handler \S+|Dashboard API handler \S+|handler \S+',existing_text): existing_text=''
            description=first_paragraph(existing_text) or 'handler '+entity['name']
            group=path.rsplit('/',1)[1][:-3] if '/web_routers/' in path else 'plugins-'+path.split('/')[1] if path.startswith('plugins/') else 'dashboard-core' if path=='hermes_cli/web_server.py' else kebab(path.split('/')[1] if '/' in path else path)
            review.finish(entity,(label+' - ' if label else '')+description,[('hermes-dashboard-'+kebab(group)+'-api','Hermes dashboard '+group.replace('-',' ')+' API',['hermes dashboard '+group.replace('-',' ')+' endpoints'])],'INTEGRATE VIA API','operational:12','SERVICE','NO',['hermes-dashboard-web-server'],'',CATS,STUDIOS,extra={'route':label} if label else None)
        elif kind=='UI_COMPONENT':
            name=entity['name']
            app=next((label for prefix,label in UI_APPS if path.startswith(prefix)),None)
            if app and not path.startswith(DROP_UI_DIRS) and not re.fullmatch(r'[A-Z0-9_]+',name) and UI_KEEP.search(name) and not name.endswith(('Skeleton','Context','Provider')):
                review.finish(entity,app+' React component '+humanize(name)+' ('+path.rsplit('/',1)[-1]+').',[('hermes-ui-components-'+kebab(app.split(' (')[0]),app+' UI components',[app+' components'])],'EXTRACT COMPONENTS','operational:16','COMPONENT','NO',['React','Hermes gateway API'],'',['category:web-applications'],STUDIOS)
            else: review.drop(entity);dropped['UI_COMPONENT']+=1
        else: review.drop(entity);dropped[kind]+=1
    findings=('Trust model (SECURITY.md section 2): single-tenant personal agent; OS-level isolation is the only boundary against an adversarial LLM and the default terminal backend runs commands directly on the host. '
              'tools/approval.py provides dangerous-command detection, per-session approval, optional auxiliary-LLM smart approval and a persistent allowlist; YOLO mode is read from HERMES_YOLO_MODE once at import so skills cannot flip it later. '
              'agent/credential_pool.py persists only whitelisted provider sources to auth.json and strips borrowed secrets at the disk boundary (agent/credential_persistence.py). Inbound messaging is authorized per user and DM policy in gateway/authz_mixin.py. '
              '%d registered agent tools include terminal, code execution, file, browser, computer-use, delegation, cron and messaging tools; those carry a sensitivity flag.')%tool_count
    print(review.finalize(CATS,STUDIOS,'USE DIRECTLY','operational:03',
        {'TOOL':'%d registered agent tools added from registry.register calls, plus 10 MCP messaging tools'%tool_count,'PLUGIN':'plugin.yaml and dashboard manifests','MODEL_ADAPTER':'Model-provider plugins','INTEGRATION':'Messaging platform plugins and built-in gateway adapters','TEMPLATE':'Three FastMCP templates (previously misdetected as MCP servers)','API':'Retained all routes outside tests, with method and path','UI_COMPONENT':'Retained feature-level components (view, page, panel, dialog, overlay, picker, composer, editor, renderer and similar); removed constants, primitives, skeletons, providers, plumbing, installer screens and the Ink package internals','WORKFLOW':'Retained %d of 30 workflows'%len(KEEP_WORKFLOWS),'MCP_SERVER':'Template placeholders replaced by the real hermes MCP server','PACKAGE':'Retained runtime and app packages; removed root, test and site packages'},
        deep_review=findings,details=['agent/, gateway/ and hermes_cli/ internals other than the named core components','tests, docs, website, locales, evals, scripts and native code','skills index cache']))
if __name__=='__main__':main()
