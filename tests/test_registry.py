import base64,copy,hashlib,importlib.util,json,pathlib,sys,tempfile,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
import registry as m
import review_extracted_batch as promotion
import build_codex_resume as resume
from unittest import mock

class DetectionTests(unittest.TestCase):
    def test_all_skills_are_detected(self):
        candidates=[m.detect(f'skills/s{i}/SKILL.md',f'---\nname: skill-{i}\ndescription: Does task {i}\n---\n')[0] for i in range(25)]
        self.assertEqual(len(candidates),25)
        self.assertEqual(len({x['symbol'] for x in candidates}),25)
    def test_mcp_and_api_declarations(self):
        text='from mcp.server.fastmcp import FastMCP\nmcp=FastMCP("Example")\n@mcp.tool()\ndef search(query: str):\n    """Search documents."""\n    return query\n@app.get("/health")\ndef health(): return True\n'
        self.assertEqual({x['type'] for x in m.detect('server.py',text)},{'MCP_SERVER','TOOL','API'})
    def test_named_fastmcp_constructor(self):
        self.assertEqual(m.detect('server.py','from fastmcp import FastMCP\nserver=FastMCP(name="voicebox")')[0]['symbol'],'voicebox')
    def test_readme_mentions_are_not_entities(self):
        self.assertEqual(m.detect('README.md','This is a powerful MCP server with 25 skills.'),[])
    def test_readme_named_binary_asset_is_excluded(self):
        self.assertEqual(m.priority({'path':'.github/assets/readme-hero-dark.webp'}),6)
        self.assertEqual(m.priority({'path':'docs/README.fr.md'}),2)
    def test_web_and_mobile_source_is_not_excluded_as_binary(self):
        for path in ['lib/main.dart','index.html','src/tokens.css','theme.scss','scripts/setup.ps1','analysis.R','index.bs','settings.gradle.kts.template']:
            self.assertLess(m.priority({'path':path}),6,path)
    def test_multiline_skill_description(self):
        found=m.detect('SKILL.md','---\nname: editor\ndescription: |\n  Rewrite text.\n  Keep facts intact.\nlicense: MIT\n---\n')[0]
        self.assertEqual(found['description'],'Rewrite text. Keep facts intact.')
    def test_parse_failure_is_recorded(self):
        diagnostics=[]; self.assertEqual(m.detect('package.json','{ broken json',diagnostics),[])
        self.assertEqual(diagnostics[0]['path'],'package.json'); self.assertEqual(diagnostics[0]['stage'],'parse')
    def test_go_tool_declaration(self):
        self.assertEqual(m.detect('tools.go','import "github.com/mark3labs/mcp-go/mcp"\nfunc x() { mcp.NewTool("search_code") }')[0]['symbol'],'search_code')
    def test_stable_entity_identity(self):
        repo={'id':'repository:1','full_name':'owner/repo','url':'https://github.com/owner/repo'}
        entry={'path':'a/SKILL.md','sha':'a'*40}; f={'type':'SKILL','symbol':'test','description':'','line':1}
        self.assertEqual(m.entity_record(repo,'a'*40,entry,f)['id'],m.entity_record(repo,'b'*40,entry,f)['id'])
        self.assertNotEqual(m.entity_record(repo,'a'*40,entry,f)['id'],m.entity_record(repo,'a'*40,{**entry,'path':'b/SKILL.md'},f)['id'])
    def test_local_jsx_export_lists_detect_forward_ref_and_aliases(self):
        text='const Button=React.forwardRef((props,ref)=><button ref={ref} {...props}/>); export { Button }; export type { ButtonProps }; export { Missing } from "./other";'
        self.assertEqual([x['symbol'] for x in m.detect('button.tsx',text)],['Button'])
        self.assertEqual(m.detect('button.tsx',text.replace('export { Button }','export { Button as PrimaryButton }'))[0]['symbol'],'PrimaryButton')
    def test_paths_and_blob_hash(self):
        self.assertFalse(m.safe_path('../escape')); self.assertFalse(m.safe_path('/root')); self.assertFalse(m.safe_path('a\\b'))
        self.assertTrue(m.safe_path('skills/x/SKILL.md'))
        self.assertEqual(m.git_blob(b'hello\n'),'ce013625030ba8dba906f756967f9e9ca394464a')
    def test_owner_and_visibility(self):
        self.assertFalse(m.public_repo({'private':False,'owner':{'login':'unrelated'}}))
        self.assertFalse(m.public_repo({'private':True,'owner':{'login':m.OWNER}}))
        self.assertTrue(m.public_repo({'private':False,'owner':{'login':m.OWNER}}))
    def test_metadata_refresh_preserves_reviewed_description_and_upstream(self):
        meta={'id':1,'name':'test','full_name':m.OWNER+'/test','html_url':'https://github.com/'+m.OWNER+'/test',
              'fork':True,'default_branch':'main','archived':False,'pushed_at':'2026-10-22','description':'GitHub summary','language':'Python'}
        repo=m.blank_repo(meta); repo['description']='Reviewed functional summary'
        repo['semantic_review_progress']={'status':'COMPLETE'}
        repo['metadata']['review_note']='Keep this'; repo['upstream_url']='https://github.com/upstream/test'
        m.merge_public_metadata(repo,meta)
        self.assertEqual(repo['description'],'Reviewed functional summary')
        self.assertEqual(repo['metadata']['github_description'],'GitHub summary')
        self.assertEqual(repo['metadata']['review_note'],'Keep this')
        self.assertEqual(repo['upstream_url'],'https://github.com/upstream/test')
        self.assertEqual(repo['metadata']['pushed_at'],'2026-10-22')
    def test_resume_counts_pending_license_review_but_not_finished_risk_review(self):
        pending={'full_name':'owner/pending','state':'NEEDS_REVIEW','next_phase':'LICENSE_REVIEW'}
        complete={'full_name':'owner/done','state':'COMPLETE','deep_review':{'triggers':['authentication'],'completed':True}}
        self.assertEqual(resume.explicit_deep_review_items([pending,complete],[]),['owner/pending'])

class RegistryIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.original=m.ROOT; self.temp=tempfile.TemporaryDirectory(); m.ROOT=pathlib.Path(self.temp.name)
        for kind in ['repositories','entities','capabilities','studios','ideas','compositions','relationships']: (m.ROOT/'registry'/kind).mkdir(parents=True)
        for path in ['registry/taxonomy/vocabulary.json','registry/taxonomy/categories.json','registry/taxonomy/operational.json']:
            m.write(path,json.loads((self.original/path).read_text()))
        for path in (self.original/'schemas').glob('*.json'): m.write('schemas/'+path.name,json.loads(path.read_text()))
    def tearDown(self): m.ROOT=self.original; self.temp.cleanup()
    def repo(self):
        r=m.blank_repo({'id':1,'name':'test','full_name':m.OWNER+'/test','html_url':'https://github.com/'+m.OWNER+'/test','owner':{'login':m.OWNER},'fork':False,'default_branch':'main','private':False,'archived':False,'pushed_at':'2026-01-01'})
        m.write(m.repo_file(r),r); m.write('system/discovery-manifest.json',{'repositories':[{'id':r['id']}]}); return r
    def test_false_complete_is_rejected(self):
        r=self.repo(); r['state']='COMPLETE'; m.write(m.repo_file(r),r)
        self.assertFalse(m.validate()['valid'])
    def summary_fixture(self):
        repo=self.repo(); repo['inspected_commit']='a'*40
        text=b'# Example\nAn agent instruction package for scoped browser research.\n'; blob=m.git_blob(text)
        entry={'path':'README.md','sha':blob,'type':'blob'}
        m.write(m.cache_path(repo,'a'*40)/'tree.json',{'tree':[entry],'truncated':False})
        path=m.ROOT/m.cache_path(repo,'a'*40)/'blobs'/blob; path.parent.mkdir(); path.write_bytes(text)
        m.write(m.repo_file(repo),repo)
        m.write('system/evidence/1.json',{'inspected_commit':'a'*40,'tree_complete':True,
                'files_read':[{'path':'README.md','blob_sha':blob}], 'unread_source_paths':['later.py'],'errors':[]})
        plan={'repository':repo['full_name'],'commit':'a'*40,'purpose':'Agent instructions for scoped browser research.',
              'categories':['category:skills'],'operational':'operational:01','recommendation':'REFERENCE',
              'reuse_recommendation':'Adapt the instruction package in a trusted agent host.',
              'inspection_scope':'Pinned README and tree; deeper components are inspected on demand.',
              'license_notes':'No license grant established in this fixture.','runtime':['Agent host'],
              'keywords':['browser research'],'risk_notes':['Host permissions remain necessary.'],
              'important_subsystems':[{'name':'Research instructions','purpose':'Guide scoped research.','evidence_paths':['README.md']}],
              'source_review':['README.md'],'asset_presence':{'skills':'PRESENT'},
              'capability_clusters':[{'name':'browser research','description':'Instructions for scoped browser research.','scope':'INSTRUCTIONS'}]}
        return repo,plan
    def test_repository_completion_does_not_require_exhaustive_source_or_promote_candidates(self):
        repo,plan=self.summary_fixture()
        entity=m.entity_record(repo,'a'*40,{'path':'README.md','sha':m.git_blob(b'# Example\nAn agent instruction package for scoped browser research.\n')},
                               {'type':'SKILL','symbol':'candidate','description':'Unreviewed','line':1})
        m.write('registry/entities/test.json',entity)
        repo['entity_census']={'SKILL':{'detected':1,'catalogued':1,'reviewed':False}}; m.write(m.repo_file(repo),repo)
        promotion.apply_repository_plan(plan)
        self.assertTrue(m.validate()['valid'])
        self.assertEqual(m.records('entities'),[entity])
        self.assertFalse(m.read(m.repo_file(repo))['phases']['entity_extraction'])
        m.build(); self.assertIn('browser research',m.query('browser research',kind='REPOSITORY')[0]['text'])
    def test_repository_summary_rejects_unpinned_cluster_evidence(self):
        repo,plan=self.summary_fixture()
        plan['capability_clusters'][0]['evidence_paths']=['not-reviewed.md']
        with self.assertRaisesRegex(ValueError,'unsupported capability cluster'): promotion.apply_repository_plan(plan)
        self.assertEqual(m.read(m.repo_file(repo))['state'],'DISCOVERED')
    def test_repository_summary_preparation_does_not_extract_entities(self):
        repo,plan=self.summary_fixture()
        with mock.patch.object(m,'gh',side_effect=AssertionError('Cached pinned source should be reused')):
            packet=promotion.prepare_repository_summary(repo)
        self.assertEqual(packet['sources'],['README.md'])
        self.assertEqual(m.records('entities'),[])
    def test_empty_repository_summary_requires_fresh_confirmed_disposition(self):
        repo,plan=self.summary_fixture(); repo['inspected_commit']=None
        repo.update({'empty_repository':True,'empty_confirmed_at':m.now()}); m.write(m.repo_file(repo),repo)
        plan.update({'commit':None,'source_review':[],'capability_clusters':[],'important_subsystems':[]})
        promotion.apply_repository_plan(plan)
        self.assertTrue(m.validate()['valid'])
    def test_zero_entity_complete_requires_semantic_disposition(self):
        r=self.repo(); r['state']='COMPLETE'; r['inspected_commit']='a'*40
        r['phases'].update({'structure':True,'entity_extraction':True,'capability_analysis':True,'validation':True})
        r['entity_census']={'SKILL':{'detected':0,'catalogued':0,'reviewed':True}}
        m.write(m.repo_file(r),r)
        m.write('system/evidence/1.json',{'inspected_commit':'a'*40,'tree_complete':True,'files_read':[],'unread_source_paths':[],'errors':[]})
        self.assertTrue(any('zero-entity completion' in error for error in m.validate()['errors']))
    def test_zero_static_entities_are_queued_for_semantic_review(self):
        r=self.repo(); r['inspected_commit']='a'*40; r['unread_source_files']=0
        m.write(m.repo_file(r),r)
        result=promotion.promote(r)
        updated=m.read(m.repo_file(r))
        self.assertEqual(result['review_required'],'zero_static_entities')
        self.assertEqual(updated['state'],'NEEDS_REVIEW')
        self.assertEqual(updated['next_phase'],'SEMANTIC_CENSUS_REVIEW')
    def test_nonzero_static_entities_remain_semantic_candidates(self):
        r=self.repo(); r['inspected_commit']='a'*40; r['unread_source_files']=0
        r['entity_census']={'SKILL':{'detected':1,'catalogued':1,'reviewed':False}}
        m.write(m.repo_file(r),r)
        entity=m.entity_record(r,'a'*40,{'path':'SKILL.md','sha':'b'*40},{'type':'SKILL','symbol':'test','description':'Does work','line':1})
        m.write('registry/entities/'+entity['id'].split(':')[1]+'.json',entity)
        m.write('system/evidence/1.json',{'inspected_commit':'a'*40,'tree_complete':True,
                'files_read':[{'path':'SKILL.md','blob_sha':'b'*40}],'unread_source_paths':[],'errors':[]})
        result=promotion.promote(r)
        updated=m.read(m.repo_file(r)); reviewed=m.records('entities')[0]
        self.assertEqual(result['review_required'],'semantic')
        self.assertEqual(updated['state'],'NEEDS_REVIEW')
        self.assertEqual(updated['next_phase'],'CAPABILITY_ANALYSIS')
        self.assertEqual(reviewed['review_status'],'NEEDS_REVIEW')
        self.assertFalse(updated['entity_census']['SKILL']['reviewed'])
    def test_missing_provenance_schema_is_rejected(self):
        self.repo(); m.write('registry/entities/bad.json',{'id':'entity:'+'b'*24,'entity_type':'SKILL','name':'Bad'})
        report=m.validate(); self.assertFalse(report['valid']); self.assertEqual(report['stage'],'schema')
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
    def test_composition_finds_smallest_cover(self):
        repo=self.repo(); repo['inspected_commit']='a'*40; m.write(m.repo_file(repo),repo)
        for i in range(6): m.write('registry/capabilities/'+str(i)+'.json',{'id':'c:'+str(i),'status':'VERIFIED'})
        # Greedy would choose broad first, requiring three providers; exact cover needs two.
        for name,coverage in [('broad',[0,1,2,3]),('left',[0,1,4]),('right',[2,3,5])]:
            e=m.entity_record(repo,'a'*40,{'path':name+'/SKILL.md','sha':'b'*40},{'type':'SKILL','symbol':name,'description':'','line':1})
            e['capabilities']=['c:'+str(i) for i in coverage]; e['review_status']='VERIFIED'; m.write('registry/entities/'+name+'.json',e)
        result=m.compose(['c:'+str(i) for i in range(6)])
        self.assertEqual({e['name'] for e in result['selected']},{'left','right'}); self.assertEqual(result['missing_capabilities'],[])
    def test_changed_head_preserves_old_entity_and_excludes_it_from_search(self):
        repo=self.repo(); repo['inspected_commit']='b'*40; m.write(m.repo_file(repo),repo)
        old=m.entity_record(repo,'a'*40,{'path':'SKILL.md','sha':'c'*40},{'type':'SKILL','symbol':'old','description':'','line':1})
        m.write('registry/entities/old.json',old); stats=m.build()
        self.assertEqual(stats['historical_entity_records'],1); self.assertEqual(stats['active_entity_records'],0)
        self.assertTrue((m.ROOT/'registry/entities/old.json').exists())
    def test_unchanged_blob_at_new_commit_requires_revalidation(self):
        repo=self.repo(); repo['inspected_commit']='a'*40; m.write(m.repo_file(repo),repo)
        text=b'---\nname: test\ndescription: task\n---\n'; blob=m.git_blob(text)
        old=m.entity_record(repo,'a'*40,{'path':'SKILL.md','sha':blob},{'type':'SKILL','symbol':'test','description':'task','line':1}); old['review_status']='VERIFIED'
        m.write('registry/entities/'+old['id'].split(':')[1]+'.json',old)
        cp=m.cache_path(repo,'b'*40); m.write(cp/'tree.json',{'tree':[{'path':'SKILL.md','type':'blob','sha':blob}],'truncated':False})
        f=m.ROOT/cp/'blobs'/blob; f.parent.mkdir(); f.write_bytes(text)
        metadata={'private':False,'owner':{'login':m.OWNER},'default_branch':'main'}
        with mock.patch.object(m,'gh',side_effect=[metadata,{'sha':'b'*40}]): result=m.ingest(repo['full_name'])
        self.assertNotIn('error',result)
        updated=m.records('entities')[0]; self.assertEqual(updated['review_status'],'STALE'); self.assertEqual(updated['metadata']['prior_review_commit'],'a'*40)
    def test_offline_resume_does_not_repeat_reads(self):
        r=self.repo(); commit='a'*40; text=b'---\nname: test\ndescription: Does a task\n---\n'; blob=m.git_blob(text)
        r['legacy_cache']={'commit':commit}; m.write(m.repo_file(r),r)
        cp=m.cache_path(r,commit); m.write(cp/'tree.json',{'tree':[{'path':'SKILL.md','type':'blob','sha':blob}],'truncated':False})
        path=m.ROOT/cp/'blobs'/blob; path.parent.mkdir(); path.write_bytes(text)
        first=m.ingest(r['full_name'],offline=True); second=m.ingest(r['full_name'],offline=True)
        self.assertEqual(first['files_read'],1); self.assertEqual(second['files_read'],1); self.assertEqual(len(m.records('entities')),1)
        self.assertTrue(m.validate()['valid'])
    def test_pinned_resume_fetches_missing_blob_without_moving_to_live_head(self):
        repo=self.repo(); commit='a'*40
        repo['inspected_commit']=commit; repo['current_commit']='c'*40; m.write(m.repo_file(repo),repo)
        text=b'---\nname: resumed\ndescription: Restore source coverage.\n---\n'; blob=m.git_blob(text)
        m.write(m.cache_path(repo,commit)/'tree.json',{'tree':[{'path':'SKILL.md','type':'blob','sha':blob}],'truncated':False})
        with mock.patch.object(m,'gh',return_value={'encoding':'base64','content':base64.b64encode(text).decode()}) as github:
            result=m.ingest(repo['full_name'],pinned=True)
        github.assert_called_once_with('repos/'+repo['full_name']+'/git/blobs/'+blob)
        self.assertEqual(result['unread'],0)
        updated=m.read(m.repo_file(repo))
        self.assertEqual(updated['inspected_commit'],commit)
        self.assertEqual(updated['current_commit'],'c'*40)
    def test_complete_repository_with_unread_source_resumes_coverage(self):
        repo=self.repo(); commit='a'*40; text=b'---\nname: resumed\ndescription: Resumed skill\n---\n'; blob=m.git_blob(text)
        repo['inspected_commit']=commit; repo['state']='COMPLETE'; repo['phases'].update({'structure':True,'entity_extraction':True,'capability_analysis':True,'validation':True})
        m.write(m.repo_file(repo),repo)
        cp=m.cache_path(repo,commit); m.write(cp/'tree.json',{'tree':[{'path':'SKILL.md','type':'blob','sha':blob}],'truncated':False})
        path=m.ROOT/cp/'blobs'/blob; path.parent.mkdir(); path.write_bytes(text)
        m.write('system/evidence/1.json',{'inspected_commit':commit,'files_read':[],'unread_source_paths':['SKILL.md'],'errors':[]})
        result=m.ingest(repo['full_name'],offline=True)
        self.assertEqual(result['files_read'],1); self.assertEqual(result['unread'],0)
        self.assertEqual(m.records('entities')[0]['name'],'resumed')
    def test_orphan_capability_providers_are_pruned(self):
        repo=self.repo(); repo['inspected_commit']='a'*40; m.write(m.repo_file(repo),repo)
        entity=m.entity_record(repo,'a'*40,{'path':'SKILL.md','sha':'b'*40},{'type':'SKILL','symbol':'test','description':'','line':1})
        entity['capabilities']=['capability:kept']; m.write('registry/entities/test.json',entity)
        for name in ('kept','stale'):
            m.write('registry/capabilities/'+name+'.json',{'id':'capability:'+name,'name':name,'aliases':[name],'status':'VERIFIED','providers':[entity['id']],'evidence':[{'type':'manifest','value':'x'}]})
        result=m.prune_orphan_capabilities()
        self.assertEqual(result,{'updated':0,'removed':1})
        self.assertIsNotNone(m.read('registry/capabilities/kept.json')); self.assertIsNone(m.read('registry/capabilities/stale.json'))

    def review_fixture(self):
        repo=self.repo(); commit='a'*40
        text=b'---\nname: editing\ndescription: Rewrite prose while preserving facts.\n---\nReview the text and correct awkward sentences.\n'
        blob=m.git_blob(text); repo['inspected_commit']=commit; m.write(m.repo_file(repo),repo)
        cp=m.cache_path(repo,commit)
        m.write(cp/'tree.json',{'tree':[{'path':'SKILL.md','type':'blob','sha':blob}],'truncated':False})
        source=m.ROOT/cp/'blobs'/blob; source.parent.mkdir(); source.write_bytes(text)
        m.ingest(repo['full_name'],offline=True)
        item={'type':'SKILL','name':'editing','path':'SKILL.md',
              'description':'Rewrite prose while preserving facts.',
              'capabilities':[['prose-editing','Prose editing',['rewrite prose']]],
              'standalone':'YES','dependencies':['Instruction-following agent'],
              'overlap':'A prompt-based editing workflow, independently reusable from its host repository.',
              'recommendation':'USE DIRECTLY'}
        plan={'repository':repo['full_name'],'commit':commit,'entities':[item],
              'coverage_note':'Full tree has one skill; body confirms the editing workflow.',
              'source_review':['SKILL.md'],'categories':['category:skills'],
              'operational':'operational:01','recommendation':'USE DIRECTLY'}
        return repo,plan,source

    def test_explicit_review_plan_completes_pinned_census(self):
        repo,plan,_=self.review_fixture()
        result=promotion.apply_review_plan(plan)
        self.assertEqual(result['state'],'COMPLETE')
        self.assertEqual(m.records('entities')[0]['review_status'],'VERIFIED')
        self.assertEqual(m.read(m.repo_file(repo))['semantic_review_progress']['reviewer'],'Source-reviewed cohort decision')
        m.build(); self.assertTrue(m.validate()['valid'])

    def test_review_plan_cannot_omit_candidates(self):
        _,plan,_=self.review_fixture(); plan['entities']=[]
        with self.assertRaisesRegex(ValueError,'omits existing candidates'):
            promotion.apply_review_plan(plan)
        self.assertEqual(m.records('entities')[0]['review_status'],'NEEDS_REVIEW')

    def test_review_plan_rejects_corrupted_cached_source_before_writes(self):
        _,plan,source=self.review_fixture(); source.write_bytes(b'changed')
        with self.assertRaisesRegex(RuntimeError,'blob hash mismatch'):
            promotion.apply_review_plan(plan)
        self.assertEqual(m.records('entities')[0]['review_status'],'NEEDS_REVIEW')

    def test_completed_review_reconciliation_only_fills_zero_families(self):
        repo,plan,_=self.review_fixture(); promotion.apply_review_plan(plan)
        repo=m.read(m.repo_file(repo)); repo['state']='NEEDS_REVIEW'; repo['next_phase']='CAPABILITY_ANALYSIS'
        repo['entity_census']['API']={'detected':0,'catalogued':0,'reviewed':False}
        repo['semantic_review_progress']['scoped_deep_review']='Instruction-only workflow; no executable runtime included.'
        result=promotion.reconcile_completed_review(repo)
        self.assertEqual(result['state'],'COMPLETE')
        self.assertTrue(m.read(m.repo_file(repo))['entity_census']['API']['reviewed'])
        repo['state']='NEEDS_REVIEW'; repo['next_phase']='CAPABILITY_ANALYSIS'
        repo['entity_census']['SKILL']['reviewed']=False
        self.assertIsNone(promotion.reconcile_completed_review(repo))

    def test_explicit_plan_replay_keeps_canonical_identity(self):
        _,plan,_=self.review_fixture()
        promotion.apply_review_plan(plan); promotion.apply_review_plan(plan)
        self.assertEqual(len(m.records('entities')),1)
        self.assertEqual(len(m.records('capabilities')),1)

    def test_concise_review_capability_has_stable_identity(self):
        _,plan,_=self.review_fixture(); item=plan['entities'][0]
        item.pop('capabilities'); item['capability']='Prose editing'
        promotion.apply_review_plan(plan)
        self.assertEqual(m.records('entities')[0]['capabilities'],['capability:prose-editing'])

    def test_relationship_names_require_type_when_ambiguous(self):
        repo,plan,_=self.review_fixture(); plugin_path='.claude-plugin/plugin.json'
        data=b'{"name":"editing","description":"Editing skill packaging"}'
        blob=m.git_blob(data); cp=m.cache_path(repo,plan['commit'])
        tree=m.read(cp/'tree.json'); tree['tree'].append({'path':plugin_path,'type':'blob','sha':blob})
        m.write(cp/'tree.json',tree); (m.ROOT/cp/'blobs'/blob).write_bytes(data)
        m.ingest(repo['full_name'],offline=True)
        plan['entities'].append({**plan['entities'][0],'type':'PLUGIN','path':plugin_path})
        edge={'type':'CONTAINS_SKILL','from_name':'editing','to_name':'editing','path':plugin_path}
        plan['relationships']=[edge]
        with self.assertRaisesRegex(ValueError,'Ambiguous or missing relationship endpoint'):
            promotion.apply_review_plan(plan)
        edge.update({'from_type':'PLUGIN','to_type':'SKILL'})
        promotion.apply_review_plan(plan)
        relation=m.records('relationships')[0]
        self.assertNotEqual(relation['from'],relation['to'])

    def test_review_checks_current_source_classifier_against_tree(self):
        repo,plan,_=self.review_fixture(); cp=m.cache_path(repo,plan['commit'])
        tree=m.read(cp/'tree.json'); tree['tree'].append({'path':'index.html','type':'blob','sha':'d'*40})
        m.write(cp/'tree.json',tree)
        with self.assertRaisesRegex(ValueError,'further pinned extraction'):
            promotion.apply_review_plan(plan)

if __name__=='__main__': unittest.main()
