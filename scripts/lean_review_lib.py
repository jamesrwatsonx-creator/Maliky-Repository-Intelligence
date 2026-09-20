"""Shared helpers for LEAN SEMANTIC REVIEW scripts (review_<repository>_semantics.py).

A review script builds a LeanReview for one repository at its existing pinned commit, reviews
existing entities and adds newly discovered ones with `finish`, drops entities that fail the lean
test with `drop`, then calls `finalize`. Every source file read is verified against the git blob
SHA recorded in system/evidence/<github_id>.json. No target code is executed.
"""
from __future__ import annotations
import hashlib,os,tarfile
import registry as r

NOTE='Verified from pinned source; runtime not tested'

class LeanReview:
    def __init__(self,full_name,commit,tarball_env=None):
        self.repo=next(x for x in r.records('repositories') if x['full_name']==full_name)
        self.commit=commit;self.full_name=full_name
        if self.repo['inspected_commit']!=commit: raise ValueError(full_name+' commit changed; preserve this review and queue a new revision')
        evidence=r.read('system/evidence/'+str(self.repo['github_id'])+'.json')
        self.verified={p['path']:p['blob_sha'] for p in evidence['files_read']}
        self.tree={e['path']:e for e in evidence['tree_entries']}
        self.base='https://github.com/'+full_name+'/blob/'+commit+'/'
        self.existing=[e for e in r.records('entities') if e['source']['repository_id']==self.repo['id'] and e['source']['inspected_commit']==commit]
        self.files={};self.caps={};self.out={};self.removed=[];self.edges=[];self.seen_sha={}
        if tarball_env: self.load_tarball(os.environ[tarball_env])

    def url(self,path,line=1): return self.base+path+'#L'+str(line)
    def entry(self,path):
        if self.verified.get(path)!=self.tree[path]['sha']: raise ValueError('Verified evidence missing for '+path)
        return self.tree[path]
    def load_tarball(self,tarball,wanted=lambda name:True):
        with tarfile.open(tarball) as archive:
            for member in archive:
                if not member.isfile(): continue
                name=member.name.split('/',1)[1]
                if name in self.tree and wanted(name):
                    data=archive.extractfile(member).read()
                    if r.git_blob(data)!=self.tree[name]['sha']: raise ValueError('Tarball file does not match pinned blob: '+name)
                    self.files[name]=data.decode('utf-8','replace')
    def make(self,kind,symbol,path,line=1):
        return r.entity_record(self.repo,self.commit,self.entry(path),{'type':kind,'symbol':symbol,'description':'','line':line})
    def find(self,kind,name=None,path=None):
        return [e for e in self.existing if e['entity_type']==kind and (name is None or e['name']==name) and (path is None or e['source']['source_path']==path)]

    def finish(self,entity,description,caps,recommendation,opcat,role,standalone,deps,overlap='',categories=(),studios=(),ideas=(),extra=None):
        """caps: list of (capability slug, name, aliases)."""
        cap_ids=[]
        for cap,name,aliases in caps:
            cap_ids.append('capability:'+cap)
            info=self.caps.setdefault(cap,{'name':name,'aliases':set(),'providers':[],'path':entity['source']['source_path']});info['aliases'].update(aliases);info['providers'].append(entity['id'])
        path=entity['source']['source_path']
        entity.update({'description':description,'capabilities':cap_ids,'recommendation':recommendation,'operational_category':opcat,'contribution_role':role,'review_status':'VERIFIED','categories':list(categories),'studios':list(studios),'ideas':list(ideas),
                       'evidence':[{'type':'source_review','value':self.url(path,entity['source'].get('line',1))}],
                       'metadata':{'semantic_review':NOTE,'review_policy':'LEAN','standalone':standalone,'dependencies':list(deps),'overlap':overlap,**(extra or {})}})
        r.write('registry/entities/'+entity['id'].split(':')[1]+'.json',entity);self.out[entity['id']]=entity
        return entity
    def drop(self,entity):
        (r.ROOT/'registry/entities'/(entity['id'].split(':')[1]+'.json')).unlink();self.removed.append(entity['id'])
    def duplicate_of(self,entity):
        sha=entity['source']['blob_sha'];first=self.seen_sha.setdefault(sha,entity['source']['source_path'])
        return {'duplicate_of':first} if first!=entity['source']['source_path'] else {}
    def relate(self,kind,source,target,path,line=1):
        identifier='relationship:'+hashlib.sha256('\0'.join([kind,source,target]).encode()).hexdigest()[:24]
        r.write('registry/relationships/'+identifier.split(':')[1]+'.json',{'id':identifier,'type':kind,'from':source,'to':target,'evidence':[{'type':'source_review','value':self.url(path,line)}]})
    def peer(self,name):
        return next((x for x in r.records('repositories') if x['full_name'].split('/')[1]==name),None)

    def write_capabilities(self):
        for cap,info in self.caps.items():
            file='registry/capabilities/'+cap+'.json';record=r.read(file)
            kept=[x for x in (record['providers'] if record else []) if 'capability:'+cap in (r.read('registry/entities/'+x.split(':')[1]+'.json') or {}).get('capabilities',[])]  # drop stale providers on re-runs
            providers=sorted(set(info['providers'])|set(kept));aliases=sorted(info['aliases']|set(record['aliases'] if record else []))
            if record: r.write(file,{**record,'providers':providers,'aliases':aliases})
            else: r.write(file,{'id':'capability:'+cap,'name':info['name'],'aliases':aliases or [info['name'].lower()],'status':'VERIFIED','verification_scope':'Static source contract; runtime not tested','providers':providers,'evidence':[{'type':'source_review','value':self.url(info['path'])}]})

    def prune_orphan_capabilities(self):
        """Drop capability providers whose entity no longer lists the capability; delete capabilities left without providers."""
        import pathlib
        for file in sorted((r.ROOT/'registry/capabilities').glob('*.json')):
            record=r.read('registry/capabilities/'+file.name)
            kept=[x for x in record['providers'] if 'capability:'+file.name[:-5] in (r.read('registry/entities/'+x.split(':')[1]+'.json') or {}).get('capabilities',[])]
            if kept==record['providers']: continue
            if kept: r.write('registry/capabilities/'+file.name,{**record,'providers':kept})
            else: file.unlink()

    def finalize(self,categories,studios,recommendation,operational,notes,deep_review='',details=(),ideas=()):
        self.write_capabilities();self.prune_orphan_capabilities()
        by_kind={}
        for e in self.out.values(): by_kind[e['entity_type']]=by_kind.get(e['entity_type'],0)+1
        repo=self.repo
        for kind,count in by_kind.items():
            census=repo['entity_census'].get(kind,{'detected':0,'catalogued':0,'detection_scope':'semantic source review','reviewed':False})
            repo['entity_census'][kind]={**census,'detected':max(census['detected'],count),'catalogued':count,'reviewed':True,'detection_scope':'semantic source review','lean_review_note':notes.get(kind,'Retained by lean test')}
        for kind,census in repo['entity_census'].items():
            if kind not in by_kind and census['catalogued']: repo['entity_census'][kind]={**census,'catalogued':0,'reviewed':True,'lean_review_note':notes.get(kind,'All candidates removed by lean test')}
        repo['capabilities']=sorted({c for e in self.out.values() for c in e['capabilities']})
        repo['categories']=list(categories);repo['studios']=list(studios);repo['ideas']=list(ideas);repo['recommendation']=recommendation;repo['operational_category']=operational
        repo['entity_count']=len(self.out);repo['phases'].update({'entity_extraction':True,'capability_analysis':True})
        repo['state']='NEEDS_REVIEW';repo['next_phase']='CAPABILITY_ANALYSIS'
        progress={'started_at':r.now(),'completed_at':r.now(),'status':'COMPLETE','review_policy':'LEAN','reviewer':'Claude Code lean static review','final_entity_count':len(self.out),'removed_entity_ids':self.removed,
                  'confirmed_capabilities':repo['capabilities'],'implementation_details_not_catalogued':list(details)}
        if deep_review: progress['scoped_deep_review']=deep_review
        repo['semantic_review_progress']=progress
        r.write(r.repo_file(repo),repo)
        return {'repository':self.full_name,'entities':len(self.out),'by_type':by_kind,'removed':len(self.removed),'capabilities':len(repo['capabilities'])}
