import copy,json,pathlib,sys,tempfile,unittest
from unittest import mock
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from analysis import contracts as c
from analysis.adapters import normalize
from analysis.local import analyze_file
from analysis.pipeline import analyze,build_packet,local_output,r
from analysis.runner import run_static,clean_environment
from analysis.availability import statuses

REPO={'id':'repository:1','github_id':1,'full_name':'owner/example','visibility':'public','inspected_commit':'a'*40,'entity_census':{}}

class ContractTests(unittest.TestCase):
    def test_every_helper_has_explicit_optional_availability(self):
        with mock.patch('shutil.which',return_value=None):
            state=statuses();self.assertEqual(len(state),9)
            for item in state.values():
                self.assertFalse(item['available']);self.assertTrue(item['unavailable']);self.assertTrue(item['fallback_available']);self.assertTrue(item['integration_mode']);self.assertFalse(item['installation_required'])
    def test_tool_registry_publishes_every_availability_field(self):
        tools=r.read('analysis/tools.yaml')['tools'];self.assertEqual(len(tools),9)
        for item in tools:
            for field in ('available','unavailable','fallback_available','integration_mode'):
                self.assertIn(field,item)
    def test_evidence_stable_and_commit_sensitive(self):
        f={'type':'symbol','path':'a.py','symbol':'x','line_start':1}
        a=c.evidence(REPO,'test','1',f,'blob:abc');b=c.evidence(REPO,'test','1',f,'blob:abc')
        self.assertEqual(a['evidence_id'],b['evidence_id'])
        self.assertNotEqual(a['evidence_id'],c.evidence({**REPO,'inspected_commit':'b'*40},'test','1',f,'blob:abc')['evidence_id'])
        a['review_status']='VERIFIED'
        with self.assertRaises(ValueError):c.validate(a)
    def test_paths_confidence_and_line_guards(self):
        for path in ('../x','/x','C:/x','a\\b','x/../a','./x'):
            with self.assertRaises(ValueError):c.source_path(path)
        for confidence in (-1,2,float('nan'),True):
            with self.assertRaises(ValueError):c.evidence(REPO,'x','1',{'type':'symbol','path':'a.py','confidence':confidence},'blob:x')
    def test_dependency_dedup_preserves_evidence(self):
        items=[c.evidence(REPO,t,'1',{'type':'dependency','path':'requirements.txt','dependency':{'name':n,'version':'1.0','ecosystem':eco}},'raw:'+t) for t,n,eco in [('syft','Foo_Bar','python'),('scancode','foo-bar','pypi')]]
        merged=c.merge_dependencies(items);self.assertEqual(len(merged),1);self.assertEqual(len(merged[0]['evidence_ids']),2)
        items.append(c.evidence(REPO,'syft','1',{'type':'dependency','path':'requirements.txt','dependency':{'name':'foo-bar','version':'>=1.0','ecosystem':'pypi'}},'raw:x'))
        self.assertEqual(len(c.merge_dependencies(items)),2)

class AdapterTests(unittest.TestCase):
    def convert(self,tool,payload,paths=('app.py','package.json','requirements.txt')):return normalize(tool,payload,REPO,'test-version','raw:test',paths)
    def test_native_semgrep_and_unknown_rule(self):
        f={'check_id':'maliky-mcp-tool','path':'app.py','start':{'line':3},'extra':{'message':'candidate','metadata':{'entity_type':'TOOL'},'metavars':{'$NAME':{'abstract_content':'search'}}}}
        e=self.convert('semgrep',{'results':[f]})[0];self.assertEqual(e['finding']['symbol'],'search');self.assertEqual(e['review_status'],'UNREVIEWED')
        f['check_id']='external-rule';self.assertEqual(self.convert('semgrep',{'results':[f]})[0]['finding']['type'],'security')
    def test_native_scancode_and_syft(self):
        scan=self.convert('scancode',{'files':[{'path':'package.json','detected_license_expression_spdx':'MIT','package_data':[{'name':'lib','version':'1','type':'npm'}]}]})
        syft=self.convert('syft',{'artifacts':[{'name':'lib','version':'1','type':'npm','locations':[{'path':'package.json'}]}]})
        self.assertEqual(len(c.merge_dependencies(scan+syft)),1)
        self.assertEqual(scan[0]['finding']['expression'],'MIT')
    def test_native_linguist_file_and_breakdown(self):
        e=self.convert('linguist',{'app.py':{'language':'Python','generated':True,'vendored':True}})[0]
        self.assertTrue(e['finding']['generated']);self.assertTrue(e['finding']['vendored'])
        self.assertEqual(self.convert('linguist',{'Python':{'files':['app.py']}})[0]['finding']['language'],'Python')
    def test_sarif_and_repomix(self):
        sarif={'version':'2.1.0','runs':[{'results':[{'ruleId':'py/test','message':{'text':'review'},'locations':[{'physicalLocation':{'artifactLocation':{'uri':'app.py'},'region':{'startLine':2}}}]}]}]}
        self.assertEqual(self.convert('codeql',sarif)[0]['finding']['line_start'],2)
        self.assertEqual(self.convert('repomix','<files><file path="app.py">print(1)</file></files>')[0]['finding']['type'],'context')
        with self.assertRaises(ValueError):self.convert('repomix','<!DOCTYPE x><files/>')
    def test_outside_tree_rejected(self):
        with self.assertRaises(ValueError):self.convert('linguist',{'secret.py':{'language':'Python'}})
    def test_imports_never_execute_target(self):
        with mock.patch('subprocess.run',side_effect=AssertionError('execution')):
            result=analyze_file('app.py','import os\ndef f():\n    os.system("do-not-run")\n',r.detect)
        self.assertTrue(any(f['type']=='relationship' for f in result['facts']))
    def test_call_evidence_is_limited_to_same_file_definitions(self):
        result=analyze_file('app.py','def local(): pass\ndef f():\n    local()\n    external()\n    module.dynamic()\n',r.detect)
        calls=[f for f in result['facts'] if f['type']=='relationship' and f.get('relation')=='CALL_CANDIDATE']
        self.assertEqual([f['target'] for f in calls],['local'])
    def test_generated_vendor_flags_do_not_drop_candidates(self):
        result=analyze_file('vendor/tool.py','# automatically generated\n@mcp.tool()\ndef search(): pass\n',r.detect)
        self.assertTrue(any(f['type']=='entity_candidate' for f in result['facts']))
    def test_large_files_remain_covered_without_static_parsing(self):
        from analysis.local import classify_only
        result=classify_only('generated.ts','// automatically generated\n'+'x'*2_000_000,'file exceeds limit')
        self.assertTrue(result['facts'][0]['static_analysis_skipped']);self.assertTrue(result['facts'][0]['generated'])
    def test_visual_examples_are_individual_candidates(self):
        facts=[analyze_file(f'examples/{i}/DESIGN.md',f'# Design {i}',r.detect)['facts'] for i in range(200)]
        self.assertEqual(sum(f['type']=='entity_candidate' for fs in facts for f in fs),200)

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.old=r.ROOT;self.temp=tempfile.TemporaryDirectory();r.ROOT=pathlib.Path(self.temp.name)
        (r.ROOT/'scripts').mkdir();(r.ROOT/'scripts/registry.py').write_text('detector-version-1')
        self.repo=copy.deepcopy(REPO);self.cache('a'*40,{'a.py':'def work():\n    return 1\n','package.json':'{"name":"x","dependencies":{"lib":"^1"}}'})
    def tearDown(self):r.ROOT=self.old;self.temp.cleanup()
    def cache(self,commit,files):
        cp=r.cache_path(self.repo,commit);entries=[]
        for name,text in files.items():
            data=text.encode();sha=r.git_blob(data);p=r.ROOT/cp/'blobs'/sha;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);entries.append({'type':'blob','mode':'100644','path':name,'sha':sha})
        r.write(cp/'tree.json',{'tree':entries,'truncated':False})
    def test_repeat_reuses_and_changed_commit_rebinds(self):
        first,_=analyze(self.repo);second,_=analyze(self.repo)
        self.assertEqual(first['cache']['computed'],2);self.assertEqual(second['cache']['reused'],2)
        self.cache('b'*40,{'a.py':'def work():\n    return 1\n','new.py':'def newer(): pass\n'})
        self.repo['inspected_commit']='b'*40;third,_=analyze(self.repo)
        self.assertEqual(third['cache']['reused'],1);self.assertEqual(third['cache']['computed'],1)
        self.assertTrue(all(e['repository']['commit']=='b'*40 for e in third['evidence']))
        self.assertFalse(any(e['finding']['path']=='package.json' for e in third['evidence']))
        self.assertTrue((r.ROOT/'.local/analysis/normalized/1'/('a'*40)/'evidence.json').exists())
    def test_bounded_run_discloses_omitted_files(self):
        result,_=analyze(self.repo,max_files=1)
        self.assertEqual(result['coverage']['eligible_tree_files'],2);self.assertEqual(result['coverage']['selected_tree_files'],1)
        self.assertEqual(result['coverage']['not_selected_for_this_run'],1)
    def test_algorithm_change_invalidates_cache(self):
        analyze(self.repo);(r.ROOT/'scripts/registry.py').write_text('detector-version-2')
        result,_=analyze(self.repo);self.assertEqual(result['cache']['computed'],2)
    def test_packet_actual_size_bound_and_no_canonical_writes(self):
        result,sources=analyze(self.repo);packet,path=build_packet(self.repo,result,sources,10000)
        self.assertLessEqual(path.stat().st_size,10000);self.assertEqual(path.stat().st_size,packet['packet_bytes'])
        self.assertFalse((r.ROOT/'registry').exists());self.assertFalse((r.ROOT/'system').exists())
    def test_wrong_commit_report_fails_without_stopping(self):
        f=r.ROOT/'.local/wrong.json';r.write(f,{'repository_id':self.repo['id'],'commit':'b'*40,'payload':{'results':[]}})
        result,_=analyze(self.repo,[('semgrep','1',f)])
        self.assertEqual(result['adapter_status']['semgrep']['status'],'FAILED');self.assertTrue(result['evidence'])
    def test_corrupt_source_is_not_trusted(self):
        cp=r.ROOT/r.cache_path(self.repo,'a'*40)/'blobs';next(cp.iterdir()).write_bytes(b'corrupt')
        result,_=analyze(self.repo);self.assertEqual(len(result['coverage']['errors']),1)
    def test_private_output_and_execution_boundary(self):
        self.repo['visibility']='private';result,_=analyze(self.repo)
        self.assertTrue(all(e['repository']['visibility']=='private' for e in result['evidence']))
        self.assertEqual(run_static(self.repo,'syft')['status'],'SKIPPED')
        with self.assertRaises(ValueError):local_output(r.ROOT/'analysis/public.json')
        with mock.patch.dict('os.environ',{'GH_TOKEN':'secret','OPENAI_API_KEY':'secret','GITHUB_TOKEN':'secret'}):
            env=clean_environment(r.ROOT/'.local/home');self.assertFalse(any(k in env for k in ('GH_TOKEN','GITHUB_TOKEN','OPENAI_API_KEY')))
    def test_unavailable_tool_does_not_block_review(self):
        with mock.patch('shutil.which',return_value=None):self.assertEqual(run_static(self.repo,'semgrep')['status'],'UNAVAILABLE')

if __name__=='__main__':unittest.main()
