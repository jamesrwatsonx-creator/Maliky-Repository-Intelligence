"""Representative offline comparison; evidence counts are not accuracy claims."""
import argparse,collections,json,pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from analysis.pipeline import analyze,build_packet,r
from analysis.runner import run_static

REPRESENTATIVES={'voicebox':'saved semantic checkpoint','pm-skills':'skill-heavy','babysitter':'multiple MCP entities and skill monorepo','hermes-agent':'UI/component-heavy mixed repository','awesome-design-md':'website/design collection','ECC':'large mixed agent/skill monorepo'}

def evaluate(only=()):
    rows=[];repos=r.records('repositories');entities=r.records('entities')
    selected={name:role for name,role in REPRESENTATIVES.items() if not only or name in only}
    unknown=set(only)-set(REPRESENTATIVES)
    if unknown: raise ValueError('Unknown representative: '+', '.join(sorted(unknown)))
    for name,role in selected.items():
        repo=next(x for x in repos if x['name']==name)
        before=[e for e in entities if e['source']['repository_id']==repo['id'] and e['source']['inspected_commit']==repo['inspected_commit']]
        analysis_limit=1000 if repo.get('files_read',0)>1000 else None
        result,sources=analyze(repo,max_files=analysis_limit);packet,path=build_packet(repo,result,sources)
        candidates=[e['finding'] for e in result['evidence'] if e['finding']['type']=='entity_candidate']
        old={(e['entity_type'],e['source']['source_path'],e['name']) for e in before}
        new={(e['proposed_entity_type'],e['path'],e.get('symbol','')) for e in candidates}
        row={'repository':repo['full_name'],'commit':repo['inspected_commit'],'role':role,
             'previous_entities':len(before),'previous_types':dict(collections.Counter(e['entity_type'] for e in before)),
             'candidate_findings':len(candidates),'candidate_types':dict(collections.Counter(e['proposed_entity_type'] for e in candidates)),
             'new_candidate_identities':len(new-old),'existing_not_redetected':len(old-new),
             'new_candidate_preview':[{'type':t,'path':p,'symbol':s} for t,p,s in sorted(new-old)[:15]],
             'analysis_file_limit':analysis_limit,'coverage':{k:v for k,v in result['coverage'].items() if k not in ('missing','errors')},
             'missing_cached_files':len(result['coverage']['missing']),'parse_errors':len(result['coverage']['errors']),
             'dependency_identities':len(result['dependencies']),'license_findings':sum(e['finding']['type']=='license' for e in result['evidence']),
             'cache':result['cache'],'elapsed_seconds':result['elapsed_seconds'],'packet_bytes':path.stat().st_size,
             'packet_reduction_percent':packet['source_to_packet_reduction_percent'],
             'excerpted_files':len(packet['excerpts']),'direct_review_remaining':'Unmeasured; packets do not discharge census review',
             'false_positive_rate':None,'accuracy_note':'No independent ground truth across these repos; do not equate more findings with better accuracy'}
        rows.append(row);print(json.dumps(row),flush=True)
    # Repeat a small complete sample to prove reuse in a real cache.
    repo=next(x for x in repos if x['name']=='pm-skills');again,_=analyze(repo)
    report={'evaluated_at':r.now(),'representatives':rows,'incremental_repeat':{'repository':repo['full_name'],'cache':again['cache']},
            'native_runtime_validation':'External executables unavailable; native formats covered by unit fixtures only. No install automation.',
            'native_availability':{t:run_static(repo,t) for t in ('semgrep','scancode','syft')},
            'rollout':'Representative evaluation only; no full-inventory analyzer rollout'}
    r.write('.local/analysis/representative-evaluation.json',report)
    return report
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--only',action='append',choices=sorted(REPRESENTATIVES))
    evaluate(parser.parse_args().only or ())
