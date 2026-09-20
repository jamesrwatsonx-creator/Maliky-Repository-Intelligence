"""Record the LEAN SEMANTIC REVIEW of browser-harness at its existing pinned commit.

Each domain-skill and interaction-skill playbook is an independently searchable SKILL entity;
core modules that would be reused, compared or composed are catalogued individually.
Scoped deep review covered telemetry, cloud auth, cookie/profile sync and account-acting skills.

Source: set BH_SOURCE_DIR to a directory holding the exact pinned files (same relative paths);
each file's git blob SHA is verified against system/evidence/1249678565.json before use.
"""
from __future__ import annotations
import hashlib,os,pathlib,re
import registry as r

REPOSITORY='jamesrwatsonx-creator/browser-harness'
COMMIT='41108b8676d4bdb58b26ab3b079c0b7b0f8f3926'
BASE='https://github.com/jamesrwatsonx-creator/browser-harness/blob/'+COMMIT+'/'
SRC='src/browser_harness/'
DS='agent-workspace/domain-skills/'
IS='interaction-skills/'
CATS=['category:skills','category:automation-scripting','category:ai-agents']
PY=['Python >=3.11','browser-harness CLI and daemon','Chrome/Chromium with remote debugging enabled or a Browser Use cloud browser']
NOTE='Verified from pinned source; runtime not tested'
TELEMETRY_FINDING=('Telemetry is opt-out (enabled by default): run.py:251 sends the script read from stdin (up to 20,000 chars), the stdout tail, traced helper steps and error text to PostHog EU '
                   '(telemetry.py capture_cli_event, POSTHOG_HOST eu.i.posthog.com) with an install id; the forbidden-key filter applies only to the generic capture() path. Because the tool drives the user\'s real logged-in browser and scripts routinely print page content, '
                   'disable it with `browser-harness telemetry disable` or BH_TELEMETRY=0 before use.')
SENSITIVE_KEYS={'aa/checkout':'drives a checkout to the card-entry form; source stops before purchase','alaska/checkout':'drives a checkout to a filled payment form; source says stop before Book now','bigbang-hr/checkout':'checkout and payment-step flow','qbo/report-export':'acts inside a logged-in QuickBooks Online account (financial data)','tasksquad-ai/auth':'authentication flow','x/posting':'posts from a logged-in account and covers login','linkedin/invitation-manager':'bulk-accepts or ignores invitations on a logged-in account','gmail/compose':'composes and sends mail from a logged-in account','tiktok/upload':'publishes from a logged-in account','hubspot/private-app-webhooks':'edits webhook subscriptions of a private app','browser-use-cloud/cloud':'uses a BROWSER_USE_API_KEY and starts billable cloud browsers','facebook/groups':'acts on a logged-in account','facebook/pages':'acts on a logged-in account'}
EXTRACT_WORDS=('scrap','search','discover','hotel','pricing','multi-source','shopping','hydration','enumeration','npm','indeed','export','read','navigation','overview')

def url(path,line): return BASE+path+'#L'+str(line)
def capability(identifier,name,aliases,providers,path,line):
    r.write('registry/capabilities/'+identifier+'.json',{'id':'capability:'+identifier,'name':name,'aliases':sorted(aliases),'status':'VERIFIED','verification_scope':'Static source contract; runtime not tested','providers':sorted(providers),'evidence':[{'type':'source_review','value':url(path,line)}]})
def relationship(kind,source,target,path,line):
    identifier='relationship:'+hashlib.sha256('\0'.join([kind,source,target]).encode()).hexdigest()[:24]
    r.write('registry/relationships/'+identifier.split(':')[1]+'.json',{'id':identifier,'type':kind,'from':source,'to':target,'evidence':[{'type':'source_review','value':url(path,line)}]})

def describe(text,fallback):
    title=None;para=None;in_code=False
    for line in text.splitlines():
        s=line.strip()
        if s.startswith('```'): in_code=not in_code;continue
        if in_code or not s: continue
        if title is None and s.startswith('# '): title=s[2:].strip();continue
        if title is not None and para is None and not s.startswith(('#','|','-','*','>','<','`')): para=re.sub(r'[`*_]|\[([^\]]*)\]\([^)]*\)',lambda m:m.group(1) or '',s);break
    out=(title or fallback)+('. '+para if para else '')
    return out[:300]

def main():
    repo=next(x for x in r.records('repositories') if x['full_name']==REPOSITORY)
    if repo['inspected_commit']!=COMMIT: raise ValueError('browser-harness commit changed; preserve this review and queue a new revision')
    source_dir=pathlib.Path(os.environ['BH_SOURCE_DIR'])
    evidence=r.read('system/evidence/'+str(repo['github_id'])+'.json')
    verified={p['path']:p['blob_sha'] for p in evidence['files_read']}
    tree={e['path']:e for e in evidence['tree_entries']}
    def entry(path):
        if verified.get(path)!=tree[path]['sha']: raise ValueError('Verified evidence missing for '+path)
        return tree[path]
    def text(path):
        data=(source_dir/path).read_bytes()
        if r.git_blob(data)!=tree[path]['sha']: raise ValueError('Fetched file does not match pinned blob: '+path)
        return data.decode('utf-8')
    existing={(e['entity_type'],e['name']):e for e in r.records('entities') if e['source']['repository_id']==repo['id'] and e['source']['inspected_commit']==COMMIT}
    caps={};entities={};skill_ids=[]
    def finish(entity,description,cap_specs,recommendation,opcat,role,standalone,deps,overlap,refs,categories=CATS,extra=None):
        cap_ids=[]
        for cap,cap_name,aliases in cap_specs:
            cap_ids.append('capability:'+cap)
            info=caps.setdefault(cap,{'name':cap_name,'aliases':set(),'providers':[],'path':refs[0][0],'line':refs[0][1]});info['aliases'].update(aliases);info['providers'].append(entity['id'])
        metadata={'semantic_review':NOTE,'review_policy':'LEAN','standalone':standalone,'dependencies':deps,'overlap':overlap,**(extra or {})}
        entity.update({'description':description,'capabilities':cap_ids,'recommendation':recommendation,'operational_category':opcat,'contribution_role':role,'review_status':'VERIFIED','categories':categories,'studios':[],'ideas':[],
                       'evidence':[{'type':'source_review','value':url(p,l)} for p,l in refs],'metadata':metadata})
        r.write('registry/entities/'+entity['id'].split(':')[1]+'.json',entity);entities[(entity['entity_type'],entity['name'])]=entity
    def make(kind,symbol,path,line=1): return r.entity_record(repo,COMMIT,entry(path),{'type':kind,'symbol':symbol,'description':'','line':line})

    cli=existing[('CLI','browser-harness')];package=existing[('PACKAGE','browser-harness')];plugin=existing[('PLUGIN','browser-harness')];root=existing[('SKILL','browser-harness')];release=existing[('WORKFLOW','release')]
    core_cap=('browser-cdp-control-via-python-helpers','Browser CDP control via Python helpers',['control real Chrome from an agent','CDP browser automation harness','browser automation CLI'])
    finish(cli,'`browser-harness` CLI: reads a Python script from stdin, ensures the CDP daemon, and runs it with pre-imported browser helpers; also doctor, auth, telemetry, mac-approve and cloud commands.',[core_cap],'SECURITY REVIEW REQUIRED','operational:05','CORE','YES',PY,'ALTERNATIVE_TO playwright-mcp, chrome-devtools-mcp, stagehand, browser-use and agent-browser (this registry); differs by attaching to the user\'s own running Chrome and letting agents edit helpers',[('pyproject.toml',32),(SRC+'run.py',233)],extra={'deep_review_finding':TELEMETRY_FINDING})
    finish(package,'PyPI-style package browser-harness 0.1.9 (MIT): helpers, daemon, recorder, video, cloud auth and telemetry; depends on cdp-use, fetch-use, pillow and websockets.',[core_cap],'SECURITY REVIEW REQUIRED','operational:05','CORE','YES',['Python >=3.11','cdp-use==1.4.5','websockets==15.0.1','pillow','fetch-use'],'Same distribution as the browser-harness CLI entity',[('pyproject.toml',7)],extra={'deep_review_finding':TELEMETRY_FINDING})
    finish(root,'Root agent skill (SKILL.md): tells any coding agent to use browser-harness for all web interaction, with usage, local-Chrome connection, design constraints and gotchas; domain skills load only when BH_DOMAIN_SKILLS=1.',[('browser-control-agent-skill','Browser control agent skill',['use browser for web tasks','agent skill for browser automation'])],'USE DIRECTLY','operational:05','SKILL','PARTIAL',['browser-harness CLI install'],'',[('SKILL.md',1)])
    finish(plugin,'Claude Code plugin manifest exposing the browser-harness skill; requires the one-time CLI install.',[('browser-control-agent-skill','Browser control agent skill',[])],'USE DIRECTLY','operational:05','MODULE','PARTIAL',['browser-harness CLI install'],'',[('.claude-plugin/plugin.json',1)])
    finish(release,'Release workflow for the browser-harness package.',[('python-package-release-workflow','Python package release workflow',['PyPI release GitHub Action'])],'REFERENCE ONLY','operational:14','COMPONENT','NO',['GitHub Actions','PyPI credentials'],'',[('.github/workflows/release.yml',1)],categories=['category:ci-cd'])

    for kind,symbol,path,line,description,cap_specs,rec,opcat,standalone,deps in [
        ('LIBRARY','helpers',SRC+'helpers.py',130,'Python helper API pre-imported into scripts: goto_url, new_tab/switch_tab/close_tab, page_info, click_at_xy, type_text, fill_input, press_key, scroll, capture_screenshot, wait_for_load/element/network_idle, js, upload_file, http_get and raw cdp(); loads agent_helpers.py.',[core_cap],'USE AS LIBRARY','operational:05','PARTIAL',PY),
        ('SERVICE','daemon',SRC+'daemon.py',211,'Long-lived process holding one CDP websocket to local Chrome or a Browser Use cloud browser and relaying commands over a local IPC socket (Unix socket, or TCP loopback on Windows); one daemon per BU_NAME.',[('persistent-cdp-browser-session-daemon','Persistent CDP browser session daemon',['CDP websocket holder','browser session daemon'])],'INTEGRATE AS SERVICE','operational:05','PARTIAL',['Python >=3.11','cdp-use','websockets','running Chrome or cloud browser']),
        ('COMPONENT','recorder',SRC+'recorder.py',1,'Session recorder: one screenshot plus one JSONL trace line per traced action into a recordings folder, toggled with start_recording/stop_recording; failures never break the run.',[('browser-session-recording','Browser session recording',['record browser actions as frames'])],'EXTRACT COMPONENTS','operational:05','PARTIAL',['helpers trace hook','pillow']),
        ('COMPONENT','video',SRC+'video.py',1,'Initialises, compiles, reviews and exports browser-harness recordings into videos (with video_render.py).',[('browser-recording-video-rendering','Browser recording video rendering',['make video from browser recording'])],'EXTRACT COMPONENTS','operational:09','PARTIAL',['recorder output','pillow']),
        ('COMPONENT','browser_use_cloud_auth',SRC+'auth.py',1,'Browser Use Cloud login for the CLI: OAuth PKCE with a loopback callback, device flow or API key on stdin; stores the credential in a private (chmod 600) JSON file.',[('browser-use-cloud-oauth-login','Browser Use Cloud OAuth login',['OAuth PKCE CLI login','device flow login'])],'EXTRACT COMPONENTS','operational:21','PARTIAL',['Browser Use Cloud account','python stdlib http.server']),
        ('TEMPLATE','agent_helpers',('agent-workspace/agent_helpers.py'),1,'Empty agent-editable helper module loaded by helpers.py when BH_AGENT_WORKSPACE points at it: the place where an agent adds task-specific browser primitives (the self-healing pattern).',[('agent-extensible-browser-helpers','Agent-extensible browser helpers',['agent-written helper workspace','self-healing browser helpers'])],'USE DIRECTLY','operational:05','YES',['browser-harness helpers'])]:
        entity=make(kind,symbol,path,line)
        finish(entity,description,cap_specs,rec,opcat,'MODULE',standalone,deps,'',[(path,line)])
    ids={n:entities[k]['id'] for k,n in [(('LIBRARY','helpers'),'helpers'),(('SERVICE','daemon'),'daemon'),(('COMPONENT','recorder'),'recorder'),(('COMPONENT','video'),'video'),(('COMPONENT','browser_use_cloud_auth'),'auth'),(('TEMPLATE','agent_helpers'),'template')]}

    counts_by_group={'extraction':0,'automation':0,'interaction':0}
    for path in sorted(tree):
        domain=path.startswith(DS) and path.endswith('.md') and not path.endswith('/README.md')
        interaction=path.startswith(IS) and path.endswith('.md')
        if not (domain or interaction): continue
        body=text(path);entry(path)
        if domain:
            site,stem=path[len(DS):-3].split('/',1) if '/' in path[len(DS):] else (path[len(DS):-3],'')
            key=site+'/'+stem;name=key;prefix='Domain skill'
            group='extraction' if any(w in stem for w in EXTRACT_WORDS) else 'automation'
            opcat='operational:10' if group=='extraction' else 'operational:05'
        else:
            key='interaction/'+path[len(IS):-3];name=key;prefix='Interaction skill';group='interaction';opcat='operational:05'
        counts_by_group[group]+=1
        cap={'extraction':('site-specific-web-scraping-playbooks','Site-specific web scraping playbooks',['website scraping recipe','browser-harness domain skill']),
             'automation':('site-specific-web-automation-playbooks','Site-specific web automation playbooks',['website automation recipe','logged-in site workflow playbook']),
             'interaction':('browser-interaction-technique-playbooks','Browser interaction technique playbooks',['iframes shadow DOM dialogs uploads techniques','CDP interaction technique'])}[group]
        cap_specs=[cap]
        sensitive=SENSITIVE_KEYS.get(key);rec='USE EXISTING SKILL'
        if key in ('interaction/profile-sync','interaction/cookies'):
            rec='SECURITY REVIEW REQUIRED';sensitive='handles real cookies/sessions'
            if key=='interaction/profile-sync': cap_specs.append(('local-browser-profile-cookie-sync','Local browser profile cookie sync',['upload local Chrome cookies to cloud browser','profile sync']))
        if key=='browser-use-cloud/cloud': cap_specs.append(('remote-cloud-browser-session-management','Remote cloud browser session management',['Browser Use cloud browsers API','stop zombie cloud browsers']))
        entity=make('SKILL',name,path,1)
        extra={'playbook_group':group}
        if sensitive: extra['sensitivity']=sensitive;extra['guard']='Run only with an explicitly user-authorised session'
        finish(entity,prefix+': '+describe(body,key),cap_specs,rec,opcat,'SKILL','NO',['browser-harness CLI'] + (['BH_DOMAIN_SKILLS=1'] if domain else []),'',[(path,1)],extra=extra)
        skill_ids.append(entity['id'])
    for cap,info in caps.items(): capability(cap,info['name'],info['aliases'],info['providers'],info['path'],info['line'])

    for target in ('helpers','daemon','recorder','video','auth'): relationship('CONTAINS',package['id'],ids[target],'pyproject.toml',7)
    relationship('CONTAINS',package['id'],cli['id'],'pyproject.toml',32)
    relationship('DEPENDS_ON',cli['id'],ids['daemon'],SRC+'run.py',233)
    relationship('DEPENDS_ON',plugin['id'],cli['id'],'.claude-plugin/plugin.json',4)
    relationship('DEPENDS_ON',root['id'],cli['id'],'SKILL.md',7)
    relationship('DEPENDS_ON',ids['video'],ids['recorder'],SRC+'video.py',1)
    peers={x['full_name'].split('/')[1]:x for x in r.records('repositories')}
    for name in ('playwright-mcp','chrome-devtools-mcp','stagehand','browser-use','Ghl-and-voice-idea-agent-browser'):
        if name in peers: relationship('ALTERNATIVE_TO',repo['id'],peers[name]['id'],'SKILL.md',1)

    counts={};[counts.__setitem__(e['entity_type'],counts.get(e['entity_type'],0)+1) for e in entities.values()]
    notes={'SKILL':'Root skill plus %d domain playbooks and %d interaction playbooks (README index and companion .py scripts folded into their skills)'%(counts_by_group['extraction']+counts_by_group['automation'],counts_by_group['interaction']),'LIBRARY':'helpers read from source','SERVICE':'daemon read from source','COMPONENT':'recorder, video and cloud auth retained; telemetry is a finding, not an entity','TEMPLATE':'agent_helpers workspace retained'}
    for kind,count in counts.items():
        census=repo['entity_census'][kind]
        repo['entity_census'][kind]={**census,'detected':max(census['detected'],count),'catalogued':count,'reviewed':True,'detection_scope':'semantic source review','lean_review_note':notes.get(kind,'Retained by lean test')}
    repo['capabilities']=sorted({c for e in entities.values() for c in e['capabilities']})
    repo['categories']=CATS;repo['recommendation']='SECURITY REVIEW REQUIRED';repo['operational_category']='operational:05'
    repo['entity_count']=len(entities);repo['phases'].update({'entity_extraction':True,'capability_analysis':True})
    repo['state']='NEEDS_REVIEW';repo['next_phase']='CAPABILITY_ANALYSIS'
    repo['semantic_review_progress']={'started_at':r.now(),'completed_at':r.now(),'status':'COMPLETE','review_policy':'LEAN','reviewer':'Claude Code lean static review','final_entity_count':len(entities),
        'confirmed_entity_ids':[e['id'] for e in entities.values()],'confirmed_capabilities':repo['capabilities'],
        'scoped_deep_review':'Telemetry, cloud auth, cookie/profile sync and account-acting skills reviewed. '+TELEMETRY_FINDING+' Cloud auth stores its credential in a private file; profile-sync uploads real cookies to a cloud browser and must be user-authorised; checkout skills stop before purchase.',
        'implementation_details_not_catalogued':['admin.py install/doctor/cloud management, macos.py, paths.py, _ipc.py, run.py internals','README index files inside domain-skill folders and companion .py scripts (folded into their skills)','tests, docs and issue templates']}
    r.write(r.repo_file(repo),repo)
    print({'repository':REPOSITORY,'entities':len(entities),'by_type':counts,'groups':counts_by_group,'capabilities':len(repo['capabilities'])})
if __name__=='__main__':main()
