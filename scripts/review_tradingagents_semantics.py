"""Record the LEAN SEMANTIC REVIEW of TradingAgents at its existing pinned commit.

Financial domain, so a scoped deep review was applied: source was searched for order
execution, broker/exchange clients, wallets and key handling. None exist; the framework
emits advisory five-tier ratings only. Evidence base: system/evidence/1247317639.json plus
the exact pinned source files named in each source_review evidence URL. No code was executed.
"""
from __future__ import annotations
import hashlib
import registry as r

REPOSITORY='jamesrwatsonx-creator/TradingAgents'
COMMIT='61522e103e61601c553b4544abcd53fa7ebf9f1d'
BASE='https://github.com/jamesrwatsonx-creator/TradingAgents/blob/'+COMMIT+'/'
AG='tradingagents/agents/'
CATS=['category:ai-agents','category:agent-frameworks','category:llm-projects','category:finance-accounting']
STUDIO=['studio:trading-studio'];IDEA=['idea:trading-studio']
PY_DEPS=['Python >=3.10','langgraph','langchain-core','LLM provider API key']
NOTE='Verified from pinned source; runtime not tested'

def url(path,line): return BASE+path+'#L'+str(line)
def capability(identifier,name,aliases,providers,path,line):
    r.write('registry/capabilities/'+identifier+'.json',{'id':'capability:'+identifier,'name':name,'aliases':sorted(aliases),'status':'VERIFIED','verification_scope':'Static source contract; runtime not tested','providers':sorted(providers),'evidence':[{'type':'source_review','value':url(path,line)}]})
def relationship(kind,source,target,path,line):
    identifier='relationship:'+hashlib.sha256('\0'.join([kind,source,target]).encode()).hexdigest()[:24]
    r.write('registry/relationships/'+identifier.split(':')[1]+'.json',{'id':identifier,'type':kind,'from':source,'to':target,'evidence':[{'type':'source_review','value':url(path,line)}]})

# (type, symbol, path, line, description, capability, recommendation, operational, role, standalone, dependencies, overlap)
AGENTS=[('create_market_analyst',AG+'analysts/market_analyst.py',11,'Market (technical) analyst node: pulls price history and technical indicators through tools and writes a market report.','technical-market-analysis-agent','Technical market analysis agent',['technical analysis agent','stock indicator analyst']),
        ('create_fundamentals_analyst',AG+'analysts/fundamentals_analyst.py',14,'Fundamentals analyst node: reads company fundamentals, balance sheet, cash flow and income statement through tools and writes a fundamentals report.','fundamental-company-analysis-agent','Fundamental company analysis agent',['fundamentals analyst','company financial analysis agent']),
        ('create_news_analyst',AG+'analysts/news_analyst.py',11,'News analyst node: reads company and global news through tools and writes a news report.','financial-news-analysis-agent','Financial news analysis agent',['news analyst','macro and company news agent']),
        ('create_sentiment_analyst',AG+'analysts/sentiment_analyst.py',38,'Grounded sentiment analyst: pre-fetches Yahoo Finance news, StockTwits messages and Reddit posts into the prompt (no tool calling) so the report is grounded rather than recalled.','grounded-social-sentiment-analysis-agent','Grounded social sentiment analysis agent',['sentiment analyst','retail investor sentiment agent']),
        ('create_bull_researcher',AG+'researchers/bull_researcher.py',4,'Bull-case researcher: argues for investing in the debate over the analyst reports.','bull-bear-investment-debate','Bull/bear investment debate',['investment thesis debate','bull vs bear agents']),
        ('create_bear_researcher',AG+'researchers/bear_researcher.py',4,'Bear-case researcher: argues against investing in the debate over the analyst reports.','bull-bear-investment-debate','Bull/bear investment debate',[]),
        ('create_research_manager',AG+'managers/research_manager.py',16,'Research manager: judges the bull/bear debate and produces a structured investment plan.','bull-bear-investment-debate','Bull/bear investment debate',[]),
        ('create_trader',AG+'trader/trader.py',20,'Trader agent: turns the investment plan into a structured trade proposal.','trade-proposal-generation','Trade proposal generation',['trader agent','investment plan to trade proposal']),
        ('create_aggressive_debator',AG+'risk_mgmt/aggressive_debator.py',4,'Aggressive risk debater: argues for higher-risk execution of the trade proposal.','multi-perspective-risk-debate','Multi-perspective risk debate',['risk management debate agents']),
        ('create_conservative_debator',AG+'risk_mgmt/conservative_debator.py',4,'Conservative risk debater: argues for capital preservation on the trade proposal.','multi-perspective-risk-debate','Multi-perspective risk debate',[]),
        ('create_neutral_debator',AG+'risk_mgmt/neutral_debator.py',4,'Neutral risk debater: balances the aggressive and conservative positions.','multi-perspective-risk-debate','Multi-perspective risk debate',[]),
        ('create_portfolio_manager',AG+'managers/portfolio_manager.py',24,'Portfolio manager: synthesises the risk debate into a typed PortfolioDecision with a five-tier rating (Buy, Overweight, Hold, Underweight, Sell); advisory text only, no order placement.','portfolio-rating-decision','Portfolio rating decision',['final trade decision agent','five-tier rating'])]
TOOLS=[('get_stock_data','tradingagents/agents/utils/core_stock_tools.py',7,'OHLCV price history for a symbol and date range, routed to the configured vendor.','stock-price-and-indicator-retrieval','Stock price and indicator retrieval',['stock price data','OHLCV lookup']),
       ('get_indicators','tradingagents/agents/utils/technical_indicators_tools.py',6,'Technical indicator values for a symbol, routed to the configured vendor.','stock-price-and-indicator-retrieval','Stock price and indicator retrieval',['technical indicators']),
       ('get_fundamentals','tradingagents/agents/utils/fundamental_data_tools.py',7,'Company fundamentals snapshot for a ticker.','company-fundamentals-retrieval','Company fundamentals retrieval',['company financials','fundamental data']),
       ('get_balance_sheet','tradingagents/agents/utils/fundamental_data_tools.py',24,'Balance sheet statements for a ticker.','company-fundamentals-retrieval','Company fundamentals retrieval',[]),
       ('get_cashflow','tradingagents/agents/utils/fundamental_data_tools.py',43,'Cash flow statements for a ticker.','company-fundamentals-retrieval','Company fundamentals retrieval',[]),
       ('get_income_statement','tradingagents/agents/utils/fundamental_data_tools.py',62,'Income statements for a ticker.','company-fundamentals-retrieval','Company fundamentals retrieval',[]),
       ('get_news','tradingagents/agents/utils/news_data_tools.py',6,'Company-specific news for a ticker and date window.','financial-news-and-insider-retrieval','Financial news and insider retrieval',['stock news','company news lookup']),
       ('get_global_news','tradingagents/agents/utils/news_data_tools.py',24,'Global macro news for a date window.','financial-news-and-insider-retrieval','Financial news and insider retrieval',['macro news']),
       ('get_insider_transactions','tradingagents/agents/utils/news_data_tools.py',46,'Insider transactions for a ticker.','financial-news-and-insider-retrieval','Financial news and insider retrieval',['insider trading data'])]
CONNECTORS=[('yfinance','tradingagents/dataflows/y_finance.py',9,'Yahoo Finance vendor implementation (via yfinance and stockstats) of every data method: prices, indicators, fundamentals, statements, news, insider transactions.','multi-vendor-market-data-routing','Multi-vendor market data routing',['yfinance data vendor','free market data'],['yfinance','stockstats','pandas']),
            ('alpha_vantage','tradingagents/dataflows/alpha_vantage_common.py',10,'Alpha Vantage vendor implementation of the same data methods; requires ALPHA_VANTAGE_API_KEY and is the fallback partner of yfinance in route_to_vendor.','multi-vendor-market-data-routing','Multi-vendor market data routing',['Alpha Vantage data vendor'],['requests','ALPHA_VANTAGE_API_KEY']),
            ('stocktwits','tradingagents/dataflows/stocktwits.py',30,'StockTwits public symbol-stream fetcher: no key, returns formatted per-ticker retail messages with user-labelled bullish/bearish tags; degrades to a placeholder on failure.','social-ticker-discussion-retrieval','Social ticker discussion retrieval',['StockTwits fetch','retail trader posts'],['requests','public unauthenticated endpoint (rate and terms limits)']),
            ('reddit','tradingagents/dataflows/reddit.py',59,'Reddit public-JSON search fetcher over finance subreddits for ticker posts (~10 requests/min/IP, no key); degrades to a placeholder on failure.','social-ticker-discussion-retrieval','Social ticker discussion retrieval',['Reddit ticker search'],['requests','public unauthenticated endpoint (rate and terms limits)'])]

def main():
    repo=next(x for x in r.records('repositories') if x['full_name']==REPOSITORY)
    if repo['inspected_commit']!=COMMIT: raise ValueError('TradingAgents commit changed; preserve this review and queue a new revision')
    evidence=r.read('system/evidence/'+str(repo['github_id'])+'.json')
    verified={p['path']:p['blob_sha'] for p in evidence['files_read']}
    tree={e['path']:e for e in evidence['tree_entries']}
    def entry(path):
        if verified.get(path)!=tree[path]['sha']: raise ValueError('Verified evidence missing for '+path)
        return tree[path]
    existing={(e['entity_type'],e['name']):e for e in r.records('entities') if e['source']['repository_id']==repo['id'] and e['source']['inspected_commit']==COMMIT}
    caps={};entities=[]
    def finish(entity,type_,description,cap_ids,recommendation,opcat,role,standalone,dependencies,overlap,evidence_refs,*,categories=CATS,studios=STUDIO,ideas=IDEA):
        entity.update({'description':description,'capabilities':cap_ids,'recommendation':recommendation,'operational_category':opcat,'contribution_role':role,'review_status':'VERIFIED','categories':categories,'studios':studios,'ideas':ideas,
                       'evidence':[{'type':'source_review','value':url(p,l)} for p,l in evidence_refs],'metadata':{'semantic_review':NOTE,'review_policy':'LEAN','standalone':standalone,'dependencies':dependencies,'overlap':overlap}})
        r.write('registry/entities/'+entity['id'].split(':')[1]+'.json',entity);entities.append(entity)
    def add_cap(cap,name,aliases,entity,path,line):
        info=caps.setdefault(cap,{'name':name,'aliases':set(),'providers':[],'path':path,'line':line});info['aliases'].update(aliases);info['providers'].append(entity['id'])
    def make(type_,symbol,path,line):
        return r.entity_record(repo,COMMIT,entry(path),{'type':type_,'symbol':symbol,'description':'','line':line})

    graph=make('AGENT_FRAMEWORK','TradingAgentsGraph','tradingagents/graph/trading_graph.py',50)
    finish(graph,'AGENT_FRAMEWORK','LangGraph pipeline mirroring a trading firm: analyst team, bull/bear research debate, research manager, trader, three-way risk debate and portfolio manager; propagate(ticker, date) returns a five-tier advisory rating. Includes SQLite checkpoint resume, a reflection step and a persistent decision log. It never places orders.',
           ['capability:multi-agent-trading-decision-pipeline'],'USE AS LIBRARY','operational:03','CORE','YES',PY_DEPS+['yfinance or Alpha Vantage data','optional SQLite checkpoints'],
           'ALTERNATIVE_TO AutoHedge, Vibe-Trading, AI-Trader and FinMem-LLM-StockTrading (unreviewed); COMPLEMENTS execution engines (freqtrade, ccxt, hummingbot) that it does not replace',
           [('tradingagents/graph/trading_graph.py',50),('main.py',13)])
    add_cap('multi-agent-trading-decision-pipeline','Multi-agent trading decision pipeline',['multi-agent LLM trading framework','trading firm agent graph','stock research agent team'],graph,'tradingagents/graph/trading_graph.py',50)
    agent_entities=[]
    for symbol,path,line,description,cap,cap_name,aliases in AGENTS:
        agent=make('AGENT',symbol,path,line)
        finish(agent,'AGENT',description,['capability:'+cap],'EXTRACT COMPONENTS','operational:03','MODULE','NO',PY_DEPS+['TradingAgentsGraph state and tool nodes'],'',[(path,line)])
        add_cap(cap,cap_name,aliases,agent,path,line);agent_entities.append(agent)
    tool_entities=[]
    for symbol,path,line,description,cap,cap_name,aliases in TOOLS:
        tool=make('TOOL',symbol,path,line)
        finish(tool,'TOOL',description+' Reads market data only.',['capability:'+cap],'EXTRACT COMPONENTS','operational:10','COMPONENT','NO',['langchain-core @tool','dataflows route_to_vendor','yfinance or Alpha Vantage'],'',[(path,line)])
        add_cap(cap,cap_name,aliases,tool,path,line);tool_entities.append(tool)
    connector_entities={}
    for symbol,path,line,description,cap,cap_name,aliases,deps in CONNECTORS:
        connector=make('CONNECTOR',symbol,path,line)
        finish(connector,'CONNECTOR',description,['capability:'+cap],'EXTRACT COMPONENTS','operational:10','COMPONENT','PARTIAL',deps,'',[(path,line)])
        add_cap(cap,cap_name,aliases,connector,path,line);connector_entities[symbol]=connector
    adapter=make('MODEL_ADAPTER','create_llm_client','tradingagents/llm_clients/factory.py',15)
    finish(adapter,'MODEL_ADAPTER','Lazy-importing factory returning a BaseLLMClient for OpenAI-compatible providers, Anthropic, Google or Azure OpenAI; used for the deep-thinking and quick-thinking model roles.',['capability:multi-provider-llm-client-factory'],'EXTRACT COMPONENTS','operational:15','MODULE','PARTIAL',['langchain provider packages','provider API key env vars'],'Complements any OpenRouter-style router in this registry',[('tradingagents/llm_clients/factory.py',15)],categories=['category:llm-projects','category:ai-orchestration'],studios=[],ideas=[])
    add_cap('multi-provider-llm-client-factory','Multi-provider LLM client factory',['LLM provider factory','OpenAI Anthropic Google Azure client switch'],adapter,'tradingagents/llm_clients/factory.py',15)
    memory=make('COMPONENT','TradingMemoryLog','tradingagents/agents/utils/memory.py',10)
    finish(memory,'COMPONENT','Markdown decision log that stores each decision, later resolves it against realised returns with a reflection, and injects same- and cross-ticker past context into new runs; optional entry cap.',['capability:trading-decision-memory-and-reflection'],'EXTRACT COMPONENTS','operational:04','MODULE','PARTIAL',['local filesystem log path','LLM for reflection'],'Comparable to FinMem-LLM-StockTrading layered memory (unreviewed)',[('tradingagents/agents/utils/memory.py',10)],categories=['category:ai-memory','category:finance-accounting'],studios=STUDIO,ideas=IDEA)
    add_cap('trading-decision-memory-and-reflection','Trading decision memory and reflection',['agent decision memory log','outcome reflection memory'],memory,'tradingagents/agents/utils/memory.py',10)
    cli=existing[('CLI','tradingagents')];package=existing[('PACKAGE','tradingagents')]
    finish(cli,'CLI','`tradingagents` Typer/Rich CLI (cli.main:app): interactive provider, model, ticker and analyst selection, live progress, saved reports; prompts for and exports the chosen LLM provider API key into the process environment.',['capability:multi-agent-trading-decision-pipeline'],'USE DIRECTLY','operational:03','CORE','YES',['Python >=3.10','typer, rich, questionary','LLM provider API key'],'',[('pyproject.toml',1),('cli/utils.py',477)])
    finish(package,'PACKAGE','PyPI-style package tradingagents 0.2.5 (Apache-2.0) bundling the graph, agents, dataflows and LLM clients plus the cli package.',['capability:multi-agent-trading-decision-pipeline'],'USE AS LIBRARY','operational:03','MODULE','YES',PY_DEPS+['pandas','yfinance'],'Same distribution as the tradingagents CLI entity; not a separate product',[('pyproject.toml',1)])
    add_cap('multi-agent-trading-decision-pipeline','',[],cli,'pyproject.toml',1);add_cap('multi-agent-trading-decision-pipeline','',[],package,'pyproject.toml',1)
    for cap,info in caps.items(): capability(cap,info['name'],info['aliases'],info['providers'],info['path'],info['line'])

    for agent in agent_entities: relationship('CONTAINS_AGENT',graph['id'],agent['id'],agent['source']['source_path'],int(agent['source']['line']))
    relationship('DEPENDS_ON',graph['id'],adapter['id'],'tradingagents/graph/trading_graph.py',50)
    relationship('DEPENDS_ON',graph['id'],memory['id'],'tradingagents/graph/trading_graph.py',50)
    relationship('CONTAINS',package['id'],cli['id'],'pyproject.toml',1)
    relationship('MAPS_TO_STUDIO',graph['id'],'studio:trading-studio','main.py',13)
    relationship('MAPS_TO_IDEA',graph['id'],'idea:trading-studio','main.py',13)
    sentiment=next(a for a in agent_entities if a['name']=='create_sentiment_analyst')
    relationship('DEPENDS_ON',sentiment['id'],connector_entities['reddit']['id'],AG+'analysts/sentiment_analyst.py',30)
    relationship('DEPENDS_ON',sentiment['id'],connector_entities['stocktwits']['id'],AG+'analysts/sentiment_analyst.py',30)
    peers={x['full_name'].split('/')[1]:x for x in r.records('repositories')}
    for name in ('AutoHedge','Vibe-Trading','AI-Trader','FinMem-LLM-StockTrading'):
        if name in peers: relationship('ALTERNATIVE_TO',repo['id'],peers[name]['id'],'README.md',66)
    for name in ('freqtrade','ccxt','hummingbot'):
        if name in peers: relationship('COMPLEMENTS',repo['id'],peers[name]['id'],AG+'managers/portfolio_manager.py',24)

    counts={};[counts.__setitem__(e['entity_type'],counts.get(e['entity_type'],0)+1) for e in entities]
    notes={'AGENT':'Twelve role agents retained; create_social_media_analyst is a deprecated alias of create_sentiment_analyst and is not catalogued','TOOL':'Nine LangChain data tools retained','CONNECTOR':'Vendor/data connectors retained','AGENT_FRAMEWORK':'TradingAgentsGraph read from source; not found by declaration scan','MODEL_ADAPTER':'LLM client factory read from source','COMPONENT':'TradingMemoryLog read from source'}
    for kind,count in counts.items():
        repo['entity_census'][kind]={**repo['entity_census'][kind],'detected':count,'catalogued':count,'reviewed':True,'detection_scope':'semantic source review','lean_review_note':notes.get(kind,'Retained by lean test')}
    repo['capabilities']=sorted({c for e in entities for c in e['capabilities']})
    repo['categories']=CATS;repo['studios']=STUDIO;repo['ideas']=IDEA;repo['recommendation']='USE AS LIBRARY';repo['operational_category']='operational:03'
    repo['entity_count']=len(entities);repo['phases'].update({'entity_extraction':True,'capability_analysis':True})
    repo['state']='NEEDS_REVIEW';repo['next_phase']='CAPABILITY_ANALYSIS'
    repo['semantic_review_progress']={'started_at':r.now(),'completed_at':r.now(),'status':'COMPLETE','review_policy':'LEAN','reviewer':'Claude Code lean static review','final_entity_count':len(entities),
        'confirmed_entity_ids':[e['id'] for e in entities],'confirmed_capabilities':repo['capabilities'],
        'scoped_deep_review':'Financial domain: searched pinned source for order placement, broker/exchange clients, wallets and private-key handling; none found. Output is an advisory five-tier rating; README states research use only, not financial advice. Remaining risk: LLM API keys read from env vars, unauthenticated Reddit/StockTwits endpoints, non-deterministic outputs.',
        'implementation_details_not_catalogued':['graph setup, conditional logic, propagation, signal processing, reflection and checkpointer internals','dataflows utilities, config and per-endpoint Alpha Vantage modules','agent state, schemas, rating parser and structured-output helpers','tests, docker-compose and scripts/smoke_structured_output.py']}
    r.write(r.repo_file(repo),repo)
    print({'repository':REPOSITORY,'entities':len(entities),'by_type':counts,'capabilities':len(repo['capabilities'])})
if __name__=='__main__':main()
