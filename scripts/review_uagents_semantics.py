"""Record the LEAN SEMANTIC REVIEW of uAgents at its existing pinned commit.

The framework holds agent identity keys and a ledger wallet (default network mainnet), so a
scoped deep review covered key generation, persistence and registration. Evidence base:
system/evidence/1247318224.json plus the exact pinned source files named in each
source_review evidence URL. No code was executed.
"""
from __future__ import annotations
import hashlib,os
import registry as r

REPOSITORY='jamesrwatsonx-creator/uAgents'
COMMIT='9f6a18bd1e8356be834d6d6e78533c47c609e8d1'
BASE='https://github.com/jamesrwatsonx-creator/uAgents/blob/'+COMMIT+'/'
P='python/'
SRC=P+'src/uagents/'
ADP=P+'uagents-adapter/src/uagents_adapter/'
CORE=P+'uagents-core/uagents_core/'
CATS=['category:ai-agents','category:agent-frameworks']
STUDIO=['studio:agent-studio']
DEPS=['Python >=3.10','pydantic','uvicorn']
NOTE='Verified from pinned source; runtime not tested'
KEY_FINDING=('get_or_create_private_keys (python/src/uagents/storage/__init__.py:130) returns one freshly generated wallet key but persists a second, different PrivateKey().private_key '
             '(line 149), so name-only agents get a wallet on first run that is never saved; keys are stored as plaintext private_keys.json in the current working directory; Agent defaults to network="mainnet". '
             'Use the seed argument or an external key store for any funded agent.')

def url(path,line): return BASE+path+'#L'+str(line)
def capability(identifier,name,aliases,providers,path,line):
    r.write('registry/capabilities/'+identifier+'.json',{'id':'capability:'+identifier,'name':name,'aliases':sorted(aliases),'status':'VERIFIED','verification_scope':'Static source contract; runtime not tested','providers':sorted(providers),'evidence':[{'type':'source_review','value':url(path,line)}]})
def relationship(kind,source,target,path,line):
    identifier='relationship:'+hashlib.sha256('\0'.join([kind,source,target]).encode()).hexdigest()[:24]
    r.write('registry/relationships/'+identifier.split(':')[1]+'.json',{'id':identifier,'type':kind,'from':source,'to':target,'evidence':[{'type':'source_review','value':url(path,line)}]})

# (type, symbol, path, line, description, [(capability, capability name, aliases)], recommendation, opcat, role, standalone, deps, overlap, categories)
NEW=[
 ('AGENT_FRAMEWORK','Agent',SRC+'agent.py',222,'Core uAgents Agent: typed message handlers and intervals, protocols, key-value storage, identity and ledger wallet, Almanac registration, Agentverse mailbox and an HTTP endpoint. Defaults to mainnet.',
  [('typed-agent-messaging-framework','Typed agent messaging framework',['uAgents framework','decentralized agent framework','typed agent protocols']),('almanac-agent-registration','Almanac agent registration',['register agent on Almanac','agent discovery registration']),('agentverse-mailbox-connectivity','Agentverse mailbox connectivity',['agent mailbox','Agentverse hosted mailbox'])],
  'SECURITY REVIEW REQUIRED','operational:03','CORE','YES',DEPS+['cosmpy','uagents-core','Fetch.ai ledger/Almanac for registration'],'Alternative to other agent frameworks in this registry (LangGraph-style graphs, AutoGen-style chat); different model: addressable message-passing agents',CATS),
 ('COMPONENT','Bureau',SRC+'agent.py',1514,'Manages a collection of Agents and orchestrates their execution together in one process and server port.',[('multi-agent-bureau-hosting','Multi-agent bureau hosting',['run multiple agents in one process'])],'EXTRACT COMPONENTS','operational:03','MODULE','NO',DEPS,'',CATS),
 ('COMPONENT','Protocol',SRC+'protocol.py',18,'Reusable protocol container: supported message models, allowed replies and message handlers with a digest, mountable on any Agent.',[('typed-agent-messaging-framework','Typed agent messaging framework',[])],'EXTRACT COMPONENTS','operational:03','MODULE','NO',DEPS,'',CATS),
 ('COMPONENT','Dialogue',SRC+'experimental/dialogues/__init__.py',103,'Experimental Protocol subclass that models a multi-step conversation as a validated state machine of nodes and edges.',[('state-machine-agent-dialogue','State-machine agent dialogue',['agent dialogue protocol','conversation state machine'])],'EXTRACT COMPONENTS','operational:03','MODULE','NO',DEPS,'Basis of ChitChatDialogue in uagents-ai-engine',CATS),
 ('COMPONENT','QuotaProtocol',SRC+'experimental/quota/__init__.py',106,'Experimental Protocol that rate-limits message handlers per sender using agent storage and applies allow/block access-control lists.',[('agent-message-rate-limiting-and-acl','Agent message rate limiting and ACL',['rate limit agent handlers','agent access control list'])],'EXTRACT COMPONENTS','operational:21','MODULE','NO',DEPS,'',CATS),
 ('AGENT','ChatAgent',SRC+'experimental/chat_agent/__init__.py',12,'Experimental Agent subclass that answers chat messages with an LLM (llm_config, instructions) and registered tools; stores message history.',[('llm-tool-calling-chat-agent','LLM tool-calling chat agent',['LLM chat agent for uAgents'])],'EXTRACT COMPONENTS','operational:03','MODULE','PARTIAL',DEPS+['litellm','LLM provider API key'],'',CATS),
 ('INTEGRATION','MCPServerAdapter',ADP+'mcp/adapter.py',41,'Wraps a Model Context Protocol server as a uAgent so its tools can be reached by natural-language chat; routes tool selection through ASI1 (asi1_api_key, model).',[('mcp-server-to-agent-bridge','MCP server to agent bridge',['expose MCP server as uAgent'])],'INTEGRATE VIA API','operational:02','MODULE','PARTIAL',DEPS+['MCP server instance','ASI1 API key (external LLM service)'],'',CATS+['category:mcp-servers']),
 ('INTEGRATION','SingleA2AAdapter',ADP+'a2a_outbound/adapter.py',97,'Bridges one A2A agent into the uAgent chat protocol.',[('a2a-outbound-agent-orchestration','A2A outbound agent orchestration',['A2A to uAgent bridge','route queries to A2A agents'])],'INTEGRATE VIA API','operational:03','MODULE','PARTIAL',DEPS+['a2a-sdk','A2A agent server'],'',CATS),
 ('INTEGRATION','MultiA2AAdapter',ADP+'a2a_outbound/adapter.py',438,'Orchestrates several A2A agents behind one uAgent: discovery, query routing, fallback and health checks.',[('a2a-outbound-agent-orchestration','A2A outbound agent orchestration',[])],'INTEGRATE VIA API','operational:03','MODULE','PARTIAL',DEPS+['a2a-sdk','A2A agent servers','LLM for routing'],'',CATS),
 ('INTEGRATION','A2ARegisterTool',ADP+'a2a_inbound/adapter.py',19,'Registers a uAgent, by address, as an A2A HTTP endpoint (agent card and skills) so A2A clients can reach it.',[('a2a-inbound-agent-exposure','A2A inbound agent exposure',['expose Agentverse agent over A2A'])],'INTEGRATE VIA API','operational:03','MODULE','PARTIAL',DEPS+['a2a-sdk','Agentverse agent'],'',CATS),
 ('INTEGRATION','LangchainRegisterTool',ADP+'langchain/tools.py',75,'Registers a LangChain agent or chain as a uAgent on Agentverse so it is discoverable and callable by messages.',[('langchain-agent-agentverse-registration','LangChain agent Agentverse registration',['register LangChain agent on Agentverse'])],'INTEGRATE VIA API','operational:03','MODULE','PARTIAL',DEPS+['langchain','Agentverse API key'],'',CATS),
 ('INTEGRATION','CrewaiRegisterTool',ADP+'crewai/tools.py',125,'Registers a CrewAI crew as a uAgent on Agentverse with parameter extraction from chat text.',[('crewai-agent-agentverse-registration','CrewAI agent Agentverse registration',['register CrewAI crew on Agentverse'])],'INTEGRATE VIA API','operational:03','MODULE','PARTIAL',DEPS+['crewai','Agentverse API key'],'',CATS),
 ('SDK','AgentverseA2AStarletteApplication',CORE+'agentverse/sdk/a2a/agentverse_sdk.py',65,'Starlette A2A application that registers with Agentverse and serves agent cards and messages.',[('a2a-inbound-agent-exposure','A2A inbound agent exposure',[])],'USE AS LIBRARY','operational:03','MODULE','PARTIAL',['starlette','a2a-sdk','Agentverse API key'],'',CATS),
 ('SDK','AgentverseLangGraphApplication',CORE+'agentverse/sdk/langchain/agentverse_sdk.py',128,'Hosts a LangGraph application as an Agentverse agent (registration, session-to-thread mapping); launched by the langgraph-av CLI.',[('langgraph-agent-agentverse-hosting','LangGraph agent Agentverse hosting',['host LangGraph app on Agentverse'])],'USE AS LIBRARY','operational:03','MODULE','PARTIAL',['langgraph-api','langgraph-cli','starlette','Agentverse API key'],'',CATS),
 ('COMPONENT','ChitChatDialogue',P+'uagents-ai-engine/src/ai_engine/chitchat.py',81,'Predefined chit-chat Dialogue graph (default, init, chatting and end states) whose message contents are supplied at runtime; used by Agentverse AI Engine to converse with uAgents.',[('state-machine-agent-dialogue','State-machine agent dialogue',[])],'EXTRACT COMPONENTS','operational:03','MODULE','NO',DEPS+['uagents Dialogue'],'',CATS),
 ('INFRASTRUCTURE_MODULE','uagent-helm-chart',P+'deployment/helm/uagent/Chart.yaml',1,'Helm chart for running a uAgent on Kubernetes: deployment, service, ingress, HPA, config, secrets and service account templates.',[('kubernetes-agent-deployment','Kubernetes agent deployment',['helm chart for agent','deploy uAgent on Kubernetes'])],'EXTRACT COMPONENTS','operational:14','MODULE','PARTIAL',['Kubernetes','Helm','container image of the agent'],'',['category:devops']),
]
# (existing type, existing name, description, capability list, recommendation, opcat, role, standalone, deps, evidence, categories)
KEEP=[
 ('PACKAGE','uagents','uagents 0.25.1 (Apache-2.0): the core framework package (Agent, Bureau, Protocol, storage, registration, mailbox, experimental modules).',[('typed-agent-messaging-framework','Typed agent messaging framework',[])],'USE AS LIBRARY','operational:03','CORE','YES',DEPS+['uagents-core','cosmpy'],[(P+'pyproject.toml',3)],CATS),
 ('PACKAGE','uagents-core','uagents-core 0.4.5: identity, envelopes, Agentverse SDKs and the av / langgraph-av CLIs.',[('agentverse-agent-lifecycle-cli','Agentverse agent lifecycle CLI',['Agentverse CLI','agent registration troubleshooting'])],'USE AS LIBRARY','operational:03','MODULE','YES',['Python >=3.10','pydantic','httpx, starlette (extras)'],[(P+'uagents-core/pyproject.toml',3)],CATS),
 ('PACKAGE','uagents-adapter','uagents-adapter 0.6.2: adapters connecting uAgents to LangChain, CrewAI, MCP and A2A.',[('mcp-server-to-agent-bridge','MCP server to agent bridge',[])],'USE AS LIBRARY','operational:03','MODULE','PARTIAL',DEPS+['uagents >=0.22.3','optional langchain, crewai, mcp, a2a-sdk'],[(P+'uagents-adapter/pyproject.toml',4)],CATS),
 ('PACKAGE','uagents-ai-engine','uagents-ai-engine: message and dialogue types for Agentverse AI Engine integration (ChitChatDialogue, UAgentResponse).',[('state-machine-agent-dialogue','State-machine agent dialogue',[])],'USE AS LIBRARY','operational:03','MODULE','PARTIAL',DEPS+['uagents'],[(P+'uagents-ai-engine/pyproject.toml',1)],CATS),
 ('CLI','av','`av` (uagents_core.agentverse.cli): inspect and troubleshoot Agentverse agents (Almanac registration, search record, endpoint connectivity, profile).',[('agentverse-agent-lifecycle-cli','Agentverse agent lifecycle CLI',[])],'USE DIRECTLY','operational:24','MODULE','PARTIAL',['Python >=3.10','uagents-core','Agentverse API access'],[(P+'uagents-core/pyproject.toml',48)],CATS),
 ('CLI','langgraph-av','`langgraph-av`: launches a LangGraph app as an Agentverse agent via the AgentverseLangGraphApplication SDK.',[('langgraph-agent-agentverse-hosting','LangGraph agent Agentverse hosting',[])],'USE DIRECTLY','operational:24','MODULE','PARTIAL',['uagents-core[langgraph extras]','langgraph-cli'],[(P+'uagents-core/pyproject.toml',49)],CATS),
 ('WORKFLOW','CI','CI workflow for the Python monorepo (tests, with a coverage-comment step).',[('ci-test-and-release-pipeline','CI test and release pipeline',['python monorepo CI'])],'REFERENCE ONLY','operational:14','COMPONENT','NO',['GitHub Actions'],[('.github/workflows/ci-tests.yml',1)],['category:ci-cd']),
 ('WORKFLOW','Check and release','Check-and-release workflow for the monorepo packages.',[('ci-test-and-release-pipeline','CI test and release pipeline',[])],'REFERENCE ONLY','operational:14','COMPONENT','NO',['GitHub Actions','PyPI credentials'],[('.github/workflows/release.yml',1)],['category:ci-cd']),
]
REMOVE=[('WORKFLOW','Post coverage comment'),('WORKFLOW','Lint PR Title'),('API','healthcheck'),('API','handle_message')]

def main():
    repo=next(x for x in r.records('repositories') if x['full_name']==REPOSITORY)
    if repo['inspected_commit']!=COMMIT: raise ValueError('uAgents commit changed; preserve this review and queue a new revision')
    evidence=r.read('system/evidence/'+str(repo['github_id'])+'.json')
    verified={p['path']:p['blob_sha'] for p in evidence['files_read']}
    tree={e['path']:e for e in evidence['tree_entries']}
    def entry(path):
        if verified.get(path)!=tree[path]['sha']: raise ValueError('Verified evidence missing for '+path)
        return tree[path]
    existing={(e['entity_type'],e['name']):e for e in r.records('entities') if e['source']['repository_id']==repo['id'] and e['source']['inspected_commit']==COMMIT}
    caps={};entities={}
    def finish(entity,description,cap_specs,recommendation,opcat,role,standalone,deps,overlap,refs,categories,extra=''):
        cap_ids=[]
        for cap,cap_name,aliases in cap_specs:
            cap_ids.append('capability:'+cap)
            info=caps.setdefault(cap,{'name':cap_name,'aliases':set(),'providers':[],'path':refs[0][0],'line':refs[0][1]});info['aliases'].update(aliases);info['providers'].append(entity['id'])
        metadata={'semantic_review':NOTE,'review_policy':'LEAN','standalone':standalone,'dependencies':deps,'overlap':overlap}
        if extra: metadata['deep_review_finding']=extra
        entity.update({'description':description,'capabilities':cap_ids,'recommendation':recommendation,'operational_category':opcat,'contribution_role':role,'review_status':'VERIFIED','categories':categories,'studios':STUDIO if 'operational:14' != opcat else [],'ideas':[],
                       'evidence':[{'type':'source_review','value':url(p,l)} for p,l in refs],'metadata':metadata})
        r.write('registry/entities/'+entity['id'].split(':')[1]+'.json',entity);entities[(entity['entity_type'],entity['name'])]=entity
    for kind,symbol,path,line,description,cap_specs,recommendation,opcat,role,standalone,deps,overlap,categories in NEW:
        entity=r.entity_record(repo,COMMIT,entry(path),{'type':kind,'symbol':symbol,'description':'','line':line})
        finish(entity,description,cap_specs,recommendation,opcat,role,standalone,deps,overlap,[(path,line)],categories,KEY_FINDING if symbol=='Agent' else '')
    for kind,name,description,cap_specs,recommendation,opcat,role,standalone,deps,refs,categories in KEEP:
        finish(existing[(kind,name)],description,cap_specs,recommendation,opcat,role,standalone,deps,'',refs,categories)
    for cap,info in caps.items(): capability(cap,info['name'],info['aliases'],info['providers'],info['path'],info['line'])

    removed=[]
    for key in REMOVE:
        entity=existing[key];os.remove(r.ROOT/'registry/entities'/(entity['id'].split(':')[1]+'.json'));removed.append(entity['id'])
    E=lambda kind,name: entities[(kind,name)]['id']
    for target in ('Agent','Bureau','Protocol'): relationship('CONTAINS',E('PACKAGE','uagents'),E('AGENT_FRAMEWORK' if target=='Agent' else 'COMPONENT',target),SRC+('agent.py' if target!='Protocol' else 'protocol.py'),1)
    relationship('DEPENDS_ON',E('PACKAGE','uagents'),E('PACKAGE','uagents-core'),P+'pyproject.toml',15)
    relationship('DEPENDS_ON',E('PACKAGE','uagents-adapter'),E('PACKAGE','uagents'),P+'uagents-adapter/pyproject.toml',11)
    for kind,name in (('CLI','av'),('CLI','langgraph-av'),('SDK','AgentverseA2AStarletteApplication'),('SDK','AgentverseLangGraphApplication')): relationship('CONTAINS',E('PACKAGE','uagents-core'),E(kind,name),P+'uagents-core/pyproject.toml',47)
    for name in ('MCPServerAdapter','SingleA2AAdapter','MultiA2AAdapter','A2ARegisterTool','LangchainRegisterTool','CrewaiRegisterTool'): relationship('CONTAINS',E('PACKAGE','uagents-adapter'),E('INTEGRATION',name),P+'uagents-adapter/pyproject.toml',4)
    relationship('EXTENDS',E('AGENT','ChatAgent'),E('AGENT_FRAMEWORK','Agent'),SRC+'experimental/chat_agent/__init__.py',12)
    relationship('EXTENDS',E('COMPONENT','Dialogue'),E('COMPONENT','Protocol'),SRC+'experimental/dialogues/__init__.py',103)
    relationship('EXTENDS',E('COMPONENT','ChitChatDialogue'),E('COMPONENT','Dialogue'),P+'uagents-ai-engine/src/ai_engine/chitchat.py',81)
    relationship('EXTENDS',E('COMPONENT','QuotaProtocol'),E('COMPONENT','Protocol'),SRC+'experimental/quota/__init__.py',106)
    relationship('MAPS_TO_STUDIO',E('AGENT_FRAMEWORK','Agent'),'studio:agent-studio',SRC+'agent.py',222)
    relationship('COMPLEMENTS',E('INTEGRATION','MCPServerAdapter'),E('AGENT_FRAMEWORK','Agent'),ADP+'mcp/adapter.py',41)

    counts={};[counts.__setitem__(e['entity_type'],counts.get(e['entity_type'],0)+1) for e in entities.values()]
    notes={'API':'Removed 2 API entities: both are handlers in a test example (python/tests/examples/40-external-agent), not part of the framework surface','WORKFLOW':'Retained CI and release; removed coverage-comment and PR-title-lint as generic boilerplate','AGENT_FRAMEWORK':'Agent read from source; not found by declaration scan','COMPONENT':'Bureau, Protocol, Dialogue, QuotaProtocol, ChitChatDialogue retained','INTEGRATION':'Six adapters retained','SDK':'Two Agentverse SDK entry points retained','INFRASTRUCTURE_MODULE':'Helm chart retained'}
    for kind in set(counts)|{'API'}:
        count=counts.get(kind,0);census=repo['entity_census'][kind]
        repo['entity_census'][kind]={**census,'detected':max(census['detected'],count),'catalogued':count,'reviewed':True,'detection_scope':'semantic source review','lean_review_note':notes.get(kind,'Retained by lean test')}
    repo['capabilities']=sorted({c for e in entities.values() for c in e['capabilities']})
    repo['categories']=CATS;repo['studios']=STUDIO;repo['recommendation']='SECURITY REVIEW REQUIRED';repo['operational_category']='operational:03'
    repo['entity_count']=len(entities);repo['phases'].update({'entity_extraction':True,'capability_analysis':True})
    repo['state']='NEEDS_REVIEW';repo['next_phase']='CAPABILITY_ANALYSIS'
    repo['semantic_review_progress']={'started_at':r.now(),'completed_at':r.now(),'status':'COMPLETE','review_policy':'LEAN','reviewer':'Claude Code lean static review','final_entity_count':len(entities),
        'confirmed_entity_ids':[e['id'] for e in entities.values()],'removed_entity_ids':removed,'confirmed_capabilities':repo['capabilities'],
        'scoped_deep_review':'Key and wallet handling reviewed. '+KEY_FINDING,
        'implementation_details_not_catalogued':['python/src/uagents internals: context, dispatch, resolver, registration policies, network/Almanac contract, asgi, storage, setup, crypto','experimental mobility and search modules','python/docs API markdown, python/tests, scripts (do_release, upgrade, generate_api_docs), hello-agent example and issue/PR templates']}
    r.write(r.repo_file(repo),repo)
    print({'repository':REPOSITORY,'entities':len(entities),'by_type':counts,'capabilities':len(repo['capabilities']),'removed':len(removed)})
if __name__=='__main__':main()
