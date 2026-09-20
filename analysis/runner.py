"""Opt-in static scanner runner. Never installs tools or runs target code.

Scans a disposable, hash-verified copy, outside the source repository. Only fixed
argument lists are allowed. This is process hygiene, not an OS network sandbox.
"""
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
from .pipeline import r, local_output
from .contracts import source_path,digest

def clean_environment(home):
    env={k:v for k,v in os.environ.items() if k.upper() in ('SYSTEMROOT','WINDIR','PATH','PATHEXT','COMSPEC','TEMP','TMP','LANG','LC_ALL')}
    env.update({'HOME':str(home),'USERPROFILE':str(home),'APPDATA':str(home),'LOCALAPPDATA':str(home),
                'XDG_CONFIG_HOME':str(home),'XDG_CACHE_HOME':str(home),'SEMGREP_SEND_METRICS':'off','SEMGREP_ENABLE_VERSION_CHECK':'0','SYFT_CHECK_FOR_APP_UPDATE':'false'})
    return env

def run_static(repo,tool,timeout=120):
    if tool not in ('semgrep','scancode','syft'): raise ValueError('Only fixed static scan commands are supported; CodeQL accepts prebuilt SARIF only')
    # A sanitized environment does not enforce no-network; private runs are excluded.
    if repo.get('visibility')!='public': return {'status':'SKIPPED','reason':'Private source uses local stdlib analysis or offline report import only'}
    executable=shutil.which(tool)
    if not executable: return {'status':'UNAVAILABLE','reason':'Executable not installed; fallback remains available'}
    root=local_output(r.ROOT/'.local/analysis/runs');root.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=root,prefix=tool+'-') as tmp:
        home=pathlib.Path(tmp)/'home';home.mkdir();target=pathlib.Path(tmp)/'source';target.mkdir()
        tree=r.read(r.cache_path(repo,repo['inspected_commit'])/'tree.json')
        entries=[e for e in tree['tree'] if e['type']=='blob' and r.priority(e)<=5]
        staged=[];missing=[]
        for entry in entries:
            path=source_path(entry['path'])
            if entry.get('mode')=='120000': missing.append(path);continue
            try:text=r.source_text(repo,repo['inspected_commit'],entry,True)
            except (UnicodeError,RuntimeError): missing.append(path);continue
            if text is None: missing.append(path);continue
            dest=(target/path).resolve()
            if not dest.is_relative_to(target): raise ValueError('Escaping staging directory')
            dest.parent.mkdir(parents=True,exist_ok=True)
            # Exact bytes, including BOM, from the verified cache.
            dest.write_bytes((r.ROOT/r.cache_path(repo,repo['inspected_commit'])/'blobs'/entry['sha']).read_bytes());staged.append(path)
        if missing: return {'status':'SKIPPED','reason':'Incomplete static snapshot','missing_files':len(missing)}
        env=clean_environment(home);out=pathlib.Path(tmp)/'report.json'
        config=home/'syft.yaml';config.write_text('check-for-app-update: false\n',encoding='utf-8')
        commands={
            'semgrep':[executable,'scan','--config',str(r.ROOT/'analysis/rules/entities.yaml'),'--json','--metrics=off','--disable-version-check','--no-git-ignore','--output',str(out),'.'],
            'scancode':[executable,'--license','--copyright','--package','--strip-root','--json-pp',str(out),'.'],
            'syft':[executable,'scan','--config',str(config),'dir:.','-o','syft-json='+str(out)]}
        try:
            version=subprocess.run([executable,'--version' if tool!='syft' else 'version'],cwd=home,env=env,capture_output=True,text=True,timeout=15,encoding='utf-8',errors='replace')
            p=subprocess.run(commands[tool],cwd=target,env=env,capture_output=True,text=True,timeout=timeout,encoding='utf-8',errors='replace')
            if p.returncode or not out.exists(): return {'status':'FAILED','returncode':p.returncode,'reason':p.stderr[:300]}
            envelope={'repository_id':repo['id'],'commit':repo['inspected_commit'],'payload':json.loads(out.read_text(encoding='utf-8')),'staged_paths':staged}
            report=local_output(root/(digest(envelope)+'.json'));r.write(report,envelope)
            return {'status':'EXECUTED','tool':tool,'version':version.stdout.strip() or 'unknown','report':str(report),'staged_files':len(staged)}
        except subprocess.TimeoutExpired:return {'status':'FAILED','reason':'timeout'}
        except (OSError,ValueError) as ex:return {'status':'FAILED','reason':str(ex)[:300]}
