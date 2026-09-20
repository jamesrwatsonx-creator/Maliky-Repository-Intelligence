import copy,hashlib,importlib.util,json,pathlib,sys,tempfile,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
import registry as m

class DetectionTests(unittest.TestCase):
    def test_all_skills_are_detected(self):
        candidates=[m.detect(f'skills/s{i}/SKILL.md',f'---\nname: skill-{i}\ndescription: Does task {i}\n---\n')[0] for i in range(25)]
        self.assertEqual(len(candidates),25)
        self.assertEqual(len({x['symbol'] for x in candidates}),25)
    def test_mcp_and_api_declarations(self):
        text='from mcp.server.fastmcp import FastMCP\nmcp=FastMCP("Example")\n@mcp.tool()\ndef search(query: str):\n    """Search documents."""\n    return query\n@app.get("/health")\ndef health(): return True\n'
        self.assertEqual({x['type'] for x in m.detect('server.py',text)},{'MCP_SERVER','TOOL','API'})
    def test_readme_mentions_are_not_entities(self):
        self.assertEqual(m.detect('README.md','This is a powerful MCP server with 25 skills.'),[])
    def test_stable_entity_identity(self):
        repo={'id':'repository:1','full_name':'owner/repo','url':'https://github.com/owner/repo'}
        entry={'path':'a/SKILL.md','sha':'a'*40}; f={'type':'SKILL','symbol':'test','description':'','line':1}
        self.assertEqual(m.entity_record(repo,'a'*40,entry,f)['id'],m.entity_record(repo,'b'*40,entry,f)['id'])
        self.assertNotEqual(m.entity_record(repo,'a'*40,entry,f)['id'],m.entity_record(repo,'a'*40,{**entry,'path':'b/SKILL.md'},f)['id'])
    def test_paths_and_blob_hash(self):
        self.assertFalse(m.safe_path('../escape')); self.assertFalse(m.safe_path('/root')); self.assertFalse(m.safe_path('a\\b'))
        self.assertTrue(m.safe_path('skills/x/SKILL.md'))
        self.assertEqual(m.git_blob(b'hello\n'),'ce013625030ba8dba906f756967f9e9ca394464a')
    def test_owner_and_visibility(self):
        self.assertFalse(m.public_repo({'private':False,'owner':{'login':'unrelated'}}))
        self.assertFalse(m.public_repo({'private':True,'owner':{'login':m.OWNER}}))
        self.assertTrue(m.public_repo({'private':False,'owner':{'login':m.OWNER}}))

class RegistryIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.original=m.ROOT; self.temp=tempfile.TemporaryDirectory(); m.ROOT=pathlib.Path(self.temp.name)
        for kind in ['repositories','entities','capabilities','studios','ideas','compositions','relationships']: (m.ROOT/'registry'/kind).mkdir(parents=True)
        for path in ['registry/taxonomy/vocabulary.json','registry/taxonomy/categories.json','registry/taxonomy/operational.json']:
            m.write(path,json.loads((self.original/path).read_text()))
    def tearDown(self): m.ROOT=self.original; self.temp.cleanup()
    def repo(self):
        r=m.blank_repo({'id':1,'name':'test','full_name':m.OWNER+'/test','html_url':'https://github.com/'+m.OWNER+'/test','owner':{'login':m.OWNER},'fork':False,'default_branch':'main','private':False,'archived':False,'pushed_at':'2026-01-01'})
        m.write(m.repo_file(r),r); m.write('system/discovery-manifest.json',{'repositories':[{'id':r['id']}]}); return r
    def test_false_complete_is_rejected(self):
        r=self.repo(); r['state']='COMPLETE'; m.write(m.repo_file(r),r)
        self.assertFalse(m.validate()['valid'])
    def test_census_mismatch_rejected(self):
        r=self.repo(); r['entity_census']={'SKILL':{'detected':25,'catalogued':5,'reviewed':False}}; m.write(m.repo_file(r),r)
        self.assertTrue(any('census count mismatch' in s for s in m.validate()['errors']))
    def test_dangling_edge_rejected(self):
        self.repo(); m.write('registry/relationships/bad.json',{'id':'edge:bad','type':'PROVIDES','from':'repository:1','to':'missing','evidence':[{'type':'manifest','value':'x'}]})
        self.assertFalse(m.validate()['valid'])
    def test_composition_excludes_candidates(self):
        r=self.repo(); r['inspected_commit']='a'*40; m.write(m.repo_file(r),r)
        e=m.entity_record(r,'a'*40,{'path':'SKILL.md','sha':'b'*40},{'type':'SKILL','symbol':'skill','description':'','line':1}); e['capabilities']=['cap:test']
        m.write('registry/entities/test.json',e); m.write('registry/capabilities/test.json',{'id':'cap:test','status':'VERIFIED'})
        self.assertEqual(m.compose(['cap:test'])['selected'],[])
        e['review_status']='VERIFIED'; m.write('registry/entities/test.json',e)
        self.assertEqual(len(m.compose(['cap:test'])['selected']),1)
        self.assertEqual(m.compose(['cap:missing'])['missing_capabilities'],['cap:missing'])
    def test_offline_resume_does_not_repeat_reads(self):
        r=self.repo(); commit='a'*40; text=b'---\nname: test\ndescription: Does a task\n---\n'; blob=m.git_blob(text)
        r['legacy_cache']={'commit':commit}; m.write(m.repo_file(r),r)
        cp=m.cache_path(r,commit); m.write(cp/'tree.json',{'tree':[{'path':'SKILL.md','type':'blob','sha':blob}],'truncated':False})
        path=m.ROOT/cp/'blobs'/blob; path.parent.mkdir(); path.write_bytes(text)
        first=m.ingest(r['full_name'],offline=True); second=m.ingest(r['full_name'],offline=True)
        self.assertEqual(first['files_read'],1); self.assertEqual(second['files_read'],1); self.assertEqual(len(m.records('entities')),1)
        self.assertTrue(m.validate()['valid'])

if __name__=='__main__': unittest.main()
