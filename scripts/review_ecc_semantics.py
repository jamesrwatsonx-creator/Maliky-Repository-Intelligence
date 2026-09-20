"""Record the LEAN SEMANTIC REVIEW of ECC (affaan-m/ECC fork) at its existing pinned commit.

The declaration scan catalogued 898 skills and 307 agents, but only 288 skill names and 73 agent
names are distinct: the rest are harness copies (.agents, .kiro, .cursor) and translated copies
under docs/<locale>. One canonical entity is kept per name (canonical folder first) and the
variants are recorded in its metadata. Slash commands, rule packs, CLAUDE.md templates, hooks,
context presets and recommended MCP server configs were missed and are added from source.
Set ECC_TARBALL to the pinned tarball; every file is blob-SHA verified.
"""
from __future__ import annotations
import collections,json,os,re
from lean_review_lib import LeanReview

CATS=['category:skills','category:ai-agents']
STUDIOS=['studio:agent-studio']
PRIORITY=('skills/','agents/','.agents/skills/','.kiro/skills/','.kiro/agents/','.cursor/skills/')
SKILL_GROUPS=[('security','security|hipaa|phi-|defi|evm|keccak|safety-guard|gateguard|compliance|bounty|trading-agent-security'),
              ('agent-orchestration','^agent|agentic|autonomous|loop|^orch-|dmux|^team-|council|devfleet|nanoclaw|^plan-|parallel|dynamic-workflow|continuous|harness|context-budget|token|cost-|unified-memory|hermes|ralphinho|santa|dev-team|blueprint|iterative-retrieval|strategic-compact|config-gc|^skill-|rules-distill|configure-ecc|ecc-|gan-'),
              ('testing-quality','tdd|testing|verification|e2e|eval|benchmark|regression|coding-standards|codehealth|plankton|canary|click-path|quality|repo-scan|production-audit|review|delivery-gate|ck$'),
              ('languages-frameworks','python|django|fastapi|golang|rust|java|springboot|quarkus|kotlin|swift|dart|flutter|cpp|csharp|dotnet|fsharp|perl|laravel|nestjs|nextjs|nuxt|react|vue|vite|angular|bun-|nodejs|jpa|prisma|android|compose|pytorch|tinystruct|hexagonal|frontend-patterns'),
              ('data-and-databases','postgres|mysql|clickhouse|redis|database|scientific|recsys|data-|mle|ml-|pytorch|prediction-market'),
              ('devops-infra-network','docker|kubernetes|deployment|homelab|network|cisco|netmiko|flox|uncloud|windows-desktop|terminal|github|git-workflow|jira|nasiko|ito-'),
              ('design-media-ui','design|frontend|motion|video|manim|remotion|fal-ai|ui-|make-interfaces|taste|blender|ios-icon|accessibility|a11y|liquid|slides|dashboard|brand'),
              ('content-marketing-business','article|content|crosspost|seo|social|marketing|investor|lead|market-research|growth|competitive|product|x-api|customer|carrier|customs|logistics|returns|inventory|scheduling|nonconformance|finance|energy|visa|healthcare|connections'),
              ('documentation-knowledge','doc|knowledge|architecture|code-tour|codebase|living|research|search-first|exa|inherit|api-design|contract-first|backend|error-handling|content-hash|regex|intent|mcp|api-connector|patterns'),
              ('ops-integrations','email|messages|mailtrap|google-workspace|notification|automation|project-flow|workspace|ops')]
SENSITIVE_SKILL=re.compile(r'payment|x402|defi|evm|trading|bounty|hipaa|phi|healthcare|finance|billing|customs|visa|email|messages|social-publisher|x-api|google-workspace|jira|github-ops|terminal-ops|crosspost')
LANG_COMMANDS=re.compile(r'^(cpp|flutter|go|kotlin|python|rust|swift|java|csharp|fastapi|django|laravel|react|typescript|vue|dart|fsharp|perl|php|angular|nuxt|nestjs|springboot|quarkus)-')
KEEP_WORKFLOWS={'CI','Release','Reusable Release Workflow','Reusable Test Workflow','Reusable Validation Workflow','Supply-Chain Watch','SLSA generic generator'}
KEEP_PACKAGES={'ecc-universal','llm-abstraction','skill-comply'}
HOOK_FINDING=('hooks/hooks.json registers hooks on PreToolUse (8), PreCompact (1), SessionStart (2), PostToolUse (2), PostToolUseFailure (2), Stop (7) and SessionEnd (1); each runs an inline `node -e` command that resolves and runs local scripts (some via spawnSync) on every matching agent event, '
              'so installed hooks execute code on the operator\'s machine automatically. Recommended MCP server configs use placeholder credentials (YOUR_*_HERE) and no real secrets were found in mcp-configs/mcp-servers.json. The ecc-install script and rule installers were not audited line by line.')

def group_for(name,groups):
    for group,pattern in groups:
        if re.search(pattern,name): return group
    return 'general'
def priority(path):
    for i,prefix in enumerate(PRIORITY):
        if path.startswith(prefix): return i
    return len(PRIORITY)
def frontmatter(text,key):
    m=re.search(r'^'+key+r':\s*(.+)$',text,flags=re.M)
    return m.group(1).strip().strip('"\'') if m else ''
def heading_and_para(text):
    body=re.sub(r'\A---.*?---\s*','',text,flags=re.S)
    title=next((l[2:].strip() for l in body.splitlines() if l.startswith('# ')),'')
    para=''
    seen=False
    for l in body.splitlines():
        s=l.strip()
        if s.startswith('# '): seen=True;continue
        if seen and s and not s.startswith(('#','|','>','-','*','`','<')): para=s;break
    return title,para
def humanize(text): return re.sub(r'[-_]+',' ',text).strip()

def main():
    from registry import records
    repo=next(x for x in records('repositories') if x['full_name']=='jamesrwatsonx-creator/ECC')
    review=LeanReview('jamesrwatsonx-creator/ECC',repo['inspected_commit'])
    review.load_tarball(os.environ['ECC_TARBALL'],wanted=lambda n:not n.startswith(('docs/','tests/')))
    # ---- skills and agents: one canonical entity per name
    for kind,groups,noun,cap_prefix in (('SKILL',SKILL_GROUPS,'skills','ecc-skills-'),('AGENT',None,'agents','ecc-agents-')):
        by=collections.defaultdict(list)
        for e in review.existing:
            if e['entity_type']==kind: by[e['name']].append(e)
        for name,copies in sorted(by.items()):
            copies.sort(key=lambda e:(priority(e['source']['source_path']),e['source']['source_path']))
            canonical=copies[0]
            translations=sorted({c['source']['source_path'].split('/')[1] for c in copies[1:] if c['source']['source_path'].startswith('docs/')})
            variants=sorted({c['source']['source_path'].split('/')[0] for c in copies[1:] if not c['source']['source_path'].startswith('docs/')})
            group=group_for(name,groups) if groups else ('reviewers' if name.endswith(('reviewer','analyzer','hunter')) else 'build-resolvers' if name.endswith('resolver') else 'planning-architecture' if re.search(r'architect|planner|spec|explorer|chief',name) else 'general')
            extra={}
            if translations: extra['translations']=translations
            if variants: extra['harness_variants']=variants
            if kind=='SKILL' and SENSITIVE_SKILL.search(name): extra['sensitivity']='payments, finance, health data, account access, posting or security-sensitive workflow; review before enabling'
            review.finish(canonical,canonical['description'] or humanize(name),[(cap_prefix+group,'ECC '+noun+' - '+humanize(group),['ECC '+humanize(group)+' '+noun])],'USE EXISTING SKILL' if kind=='SKILL' else 'USE DIRECTLY',
                          'operational:01' if kind=='SKILL' else 'operational:03','SKILL' if kind=='SKILL' else 'MODULE','PARTIAL',['Agent host that loads '+('SKILL.md skills' if kind=='SKILL' else 'agent definitions')],
                          'Same content is shipped for other harnesses and locales (see variants)' if variants or translations else '',CATS,STUDIOS,extra=extra)
            for duplicate in copies[1:]: review.drop(duplicate)
    # ---- slash commands
    commands=sorted(p for p in review.files if re.fullmatch(r'commands/[^/]+\.md',p))
    for path in commands:
        text=review.files[path];stem=path.rsplit('/',1)[1][:-3]
        group='language-workflows' if LANG_COMMANDS.match(stem) else 'epic-management' if stem.startswith('epic-') else 'gan-workflows' if stem.startswith('gan-') else 'general-workflows'
        entity=review.make('WORKFLOW','/'+stem,path)
        review.finish(entity,frontmatter(text,'description') or heading_and_para(text)[0] or 'Slash command /'+stem+'.',[('ecc-commands-'+group,'ECC slash commands - '+humanize(group),['ECC '+humanize(group)+' commands'])],'USE DIRECTLY','operational:20','MODULE','PARTIAL',['Claude Code or compatible slash-command support','ECC skills and agents'],'',CATS,STUDIOS,extra={'kind':'slash command'})
    # ---- rule packs
    packs=sorted({p.split('/')[1] for p in review.files if re.fullmatch(r'rules/[^/]+/[^/]+\.md',p)})
    for pack in packs:
        members=sorted(p for p in review.files if re.fullmatch(r'rules/'+re.escape(pack)+r'/[^/]+\.md',p))
        first=next((p for p in members if p.endswith('coding-style.md')),members[0])
        title,_=heading_and_para(review.files[first])
        entity=review.make('PROMPT_LIBRARY','ecc-rules-'+pack,first)
        review.finish(entity,'ECC '+pack+' rule pack ('+title+' and '+', '.join(m.rsplit('/',1)[1][:-3] for m in members if m!=first)+'); extends the common rules.',[('ecc-language-rule-packs','ECC language rule packs',['coding rules per language','agent rule files for '+pack])],'USE DIRECTLY','operational:24','MODULE','PARTIAL',['Agent host that loads rule files'],'',['category:skills','category:prompt-libraries'],STUDIOS,extra={'rule_files':[m.rsplit('/',1)[1] for m in members]})
    # ---- CLAUDE.md templates and context presets
    for path in sorted(p for p in review.files if re.fullmatch(r'examples/[^/]*CLAUDE\.md',p)):
        title,para=heading_and_para(review.files[path])
        entity=review.make('TEMPLATE','template-'+path.rsplit('/',1)[1][:-3].lower(),path)
        review.finish(entity,(title+'. '+para)[:300] if title else 'ECC CLAUDE.md project template.',[('ecc-claude-md-templates','ECC CLAUDE.md project templates',['project CLAUDE.md starters','agent project instructions templates'])],'USE DIRECTLY','operational:24','MODULE','YES',['Claude Code CLAUDE.md convention'],'',['category:skills'],STUDIOS)
    for path in sorted(p for p in review.files if re.fullmatch(r'contexts/[^/]+\.md',p)):
        title,para=heading_and_para(review.files[path]);stem=path.rsplit('/',1)[1][:-3]
        entity=review.make('PROMPT','context-'+stem,path)
        review.finish(entity,((title+'. '+para) if title else 'ECC '+stem+' context preset.')[:300],[('ecc-context-presets','ECC context presets',['dev research review context modes'])],'USE DIRECTLY','operational:04','MODULE','YES',['Agent host with context injection'],'',['category:prompt-libraries'],STUDIOS)
    # ---- hooks
    hooks=[('hooks/hooks.json','ecc-hooks','Claude Code hooks pack: registers PreToolUse, PreCompact, SessionStart, PostToolUse, PostToolUseFailure, Stop and SessionEnd hooks that run local scripts.'),
           ('hooks/memory-persistence/hooks.json','ecc-memory-persistence-hooks','Session memory persistence hooks.'),('hooks/codex-hooks.json','ecc-codex-hooks','Hook definitions for Codex.')]
    for path,name,description in hooks:
        entity=review.make('PLUGIN',name,path)
        review.finish(entity,description,[('ecc-agent-hooks','ECC agent hooks',['session hooks for agents','tool-use hooks'])],'SECURITY REVIEW REQUIRED','operational:20','MODULE','PARTIAL',['Claude Code or Codex hook support','node'],'',CATS,STUDIOS,extra={'deep_review_finding':HOOK_FINDING})
    # ---- recommended MCP server configs
    servers=json.loads(review.files['mcp-configs/mcp-servers.json'])['mcpServers']
    for key,config in sorted(servers.items()):
        entity=review.make('INTEGRATION','mcp-config-'+key,'mcp-configs/mcp-servers.json')
        env=sorted((config.get('env') or {}).keys())
        launch=' '.join([config.get('command','')]+[str(a) for a in config.get('args',[])[:3]]).strip()
        review.finish(entity,'Recommended MCP server config "'+key+'": '+(config.get('description') or launch or config.get('url','')),[('recommended-mcp-server-configs','Recommended MCP server configs',['MCP server config catalog','mcp-servers.json'])],'REFERENCE ONLY','operational:02','COMPONENT','NO',['MCP client'] +(['env: '+', '.join(env)] if env else []),'',['category:mcp-servers'],STUDIOS,extra={'launch':launch,'required_env':env})
    # ---- packages, CLIs, plugins, workflows
    package=json.loads(review.files['package.json'])
    for entity in sorted(review.existing,key=lambda e:e['id']):
        if entity['id'] in review.out or not os.path.exists(str(__import__('registry').ROOT/'registry/entities'/(entity['id'].split(':')[1]+'.json'))): continue
        kind=entity['entity_type'];path=entity['source']['source_path']
        if kind=='PACKAGE':
            if entity['name'] in KEEP_PACKAGES: review.finish(entity,entity['description'] or entity['name']+' package ('+path+').',[('ecc-agent-operating-system','ECC agent operating system',['ecc harness','cross-harness agent OS'])],'USE AS LIBRARY','operational:03','MODULE','PARTIAL',['Node >=18 or Python'],'',CATS,STUDIOS)
            else: review.drop(entity)
        elif kind=='CLI':
            script=package.get('bin',{}).get(entity['name'])
            description=('`'+entity['name']+'` command ('+script+') of the '+package.get('name','ecc-universal')+' npm package.') if script else (entity['description'] or '`'+entity['name']+'` command.')
            review.finish(entity,description,[('ecc-agent-operating-system','ECC agent operating system',[])],'USE DIRECTLY','operational:24','MODULE','PARTIAL',['Node >=18'],'',CATS,STUDIOS)
        elif kind=='PLUGIN':
            review.finish(entity,entity['description'],[('ecc-agent-operating-system','ECC agent operating system',[])],'USE DIRECTLY','operational:03','MODULE','YES',['Claude Code or Codex plugin support'],'',CATS,STUDIOS)
        elif kind=='WORKFLOW':
            if entity['name'] in KEEP_WORKFLOWS: review.finish(entity,entity['name']+' GitHub Actions workflow.',[('ci-test-and-release-pipeline','CI test and release pipeline',[])],'REFERENCE ONLY','operational:14','COMPONENT','NO',['GitHub Actions'],'',['category:ci-cd'])
            else: review.drop(entity)
        else: review.drop(entity)
    tui=review.make('PACKAGE','ecc-tui','ecc2/Cargo.toml')
    review.finish(tui,'ECC 2.0 - agentic IDE control plane with TUI dashboard (Rust crate, ratatui).',[('ecc-agent-operating-system','ECC agent operating system',[])],'USE AS LIBRARY','operational:24','MODULE','PARTIAL',['Rust toolchain','ratatui'],'',CATS,STUDIOS)
    counts=collections.Counter(e['entity_type'] for e in review.out.values())
    print(review.finalize(CATS,STUDIOS,'USE DIRECTLY','operational:03',
        {'SKILL':'%d unique skills; harness copies (.agents, .kiro, .cursor) and locale translations under docs/ removed as variants and recorded in metadata'%counts['SKILL'],'AGENT':'%d unique agents; variants and translations removed'%counts['AGENT'],'WORKFLOW':'94 slash commands added from commands/ plus 7 CI workflows','PROMPT_LIBRARY':'One entity per rules/<language> pack','TEMPLATE':'CLAUDE.md project templates from examples/','PLUGIN':'Plugin manifests and hook packs','INTEGRATION':'Recommended MCP server configs from mcp-configs/mcp-servers.json','UI_COMPONENT':'Removed 3 Remotion example components inside a skill','PACKAGE':'Retained ecc-universal, llm-abstraction, skill-comply; added ecc-tui; removed a test fixture'},
        deep_review=HOOK_FINDING,details=['docs/ locale translations, tests, scripts/lib internals, legacy command shims, .kiro/.cursor/.opencode harness adapters','install manifests and schemas']))
if __name__=='__main__':main()
