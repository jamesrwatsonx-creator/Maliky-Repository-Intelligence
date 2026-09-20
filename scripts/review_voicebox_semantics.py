"""Record the first bounded semantic review at Voicebox's existing pinned commit."""
from __future__ import annotations
import hashlib,pathlib,re
import registry as r

REPOSITORY='jamesrwatsonx-creator/voicebox'
BASE='https://github.com/jamesrwatsonx-creator/voicebox/blob/51f49dea198384b4eb6087b72c17057c6eb1c1cd/'

def source_url(path,line): return BASE+path+'#L'+str(line)
def record_capability(identifier,name,aliases,providers,path,line):
    cap={'id':'capability:'+identifier,'name':name,'aliases':aliases,'status':'VERIFIED',
         'verification_scope':'Static source contract; runtime not tested','providers':providers,
         'evidence':[{'type':'source_review','value':source_url(path,line)}]}
    r.write('registry/capabilities/'+identifier+'.json',cap)

def main():
    repo=next(x for x in r.records('repositories') if x['full_name']==REPOSITORY)
    commit=repo['inspected_commit']
    if commit!='51f49dea198384b4eb6087b72c17057c6eb1c1cd': raise ValueError('Voicebox commit changed; preserve this review and queue a new revision')
    tree=r.read(r.cache_path(repo,commit)/'tree.json');entries={e['path']:e for e in tree['tree'] if e['type']=='blob'}
    server_path='backend/mcp_server/server.py';tools_path='backend/mcp_server/tools.py'
    server_text=r.source_text(repo,commit,entries[server_path],True);tools_text=r.source_text(repo,commit,entries[tools_path],True)
    if server_text is None or tools_text is None: raise ValueError('Required Voicebox source is absent from pinned cache')
    server_line=next(i for i,line in enumerate(server_text.splitlines(),1) if 'def build_mcp_server' in line)
    server=r.entity_record(repo,commit,entries[server_path],{'type':'MCP_SERVER','symbol':'voicebox','description':'FastMCP server mounted at the Voicebox /mcp endpoint','line':server_line})
    server['review_status']='VERIFIED';server['operational_category']='operational:02';server['contribution_role']='SERVICE';server['recommendation']='INTEGRATE AS SERVICE'
    server['capabilities']=['capability:voice-mcp-server-exposure'];server['metadata']={'semantic_review':'Verified constructor and mount path; runtime connection was not tested'}
    server['evidence']=[{'type':'source_review','value':source_url(server_path,server_line)},{'type':'source_review','value':source_url(server_path,58)}]
    r.write('registry/entities/'+server['id'].split(':')[1]+'.json',server)
    entities={e['name']:e for e in r.records('entities') if e['source']['repository_id']==repo['id'] and e['source']['inspected_commit']==commit and e['entity_type']=='TOOL'}
    expected={'voicebox_speak':('capability:queued-speech-generation-submission',46),'voicebox_transcribe':('capability:local-audio-transcription',123),'voicebox_list_captures':('capability:voice-capture-history-discovery',180),'voicebox_list_profiles':('capability:voice-profile-discovery',208)}
    if set(entities)!=set(expected): raise ValueError('MCP tool census changed; inspect before applying review')
    for name,(capability,line) in expected.items():
        entity=entities[name];entity['review_status']='VERIFIED';entity['operational_category']='operational:02';entity['contribution_role']='SERVICE';entity['recommendation']='INTEGRATE VIA MCP';entity['capabilities']=[capability]
        entity['metadata']={'semantic_review':'Verified FastMCP tool decorator and source contract; runtime behavior not tested'}
        entity['evidence']=[{'type':'source_review','value':source_url(tools_path,line)}]
        r.write('registry/entities/'+entity['id'].split(':')[1]+'.json',entity)
    record_capability('voice-mcp-server-exposure','Voice MCP server exposure',['voice input/output MCP server','Voicebox MCP endpoint'],[server['id']],server_path,58)
    record_capability('local-audio-transcription','Local audio transcription',['audio to text','Whisper transcription','speech to text'],[entities['voicebox_transcribe']['id']],tools_path,115)
    record_capability('voice-capture-history-discovery','Voice capture history discovery',['list voice captures','voice capture listing'],[entities['voicebox_list_captures']['id']],tools_path,173)
    record_capability('voice-profile-discovery','Voice profile discovery',['list voice profiles','voice listing'],[entities['voicebox_list_profiles']['id']],tools_path,201)
    queued=r.read('registry/capabilities/queued-speech-generation-submission.json');queued['providers']=sorted(set(queued['providers']+[entities['voicebox_speak']['id']]));r.write('registry/capabilities/queued-speech-generation-submission.json',queued)
    census=repo['entity_census'];census['MCP_SERVER']={'detected':1,'catalogued':1,'detection_scope':'semantic source review of FastMCP named constructor and mount','reviewed':True}
    census['TOOL']={**census['TOOL'],'reviewed':True,'detection_scope':'semantic source review of four FastMCP decorators'}
    census['SERVICE']={**census['SERVICE'],'reviewed':True}
    repo['semantic_review_progress']={'started_at':r.now(),'reviewer':'Codex static semantic review','confirmed_entity_ids':[server['id']]+[entities[name]['id'] for name in expected],
                                      'confirmed_capabilities':['capability:voice-mcp-server-exposure','capability:queued-speech-generation-submission','capability:local-audio-transcription','capability:voice-capture-history-discovery','capability:voice-profile-discovery'],
                                      'pending':['Reconcile 123 HTTP route candidates, excluding tests and generated clients where appropriate','Review 118 UI component candidates for reusable boundaries','Review 4 Skills, 3 workflows and 7 packages','Score, map relationships and complete the independent census']}
    repo['state']='NEEDS_REVIEW';repo['next_phase']='SEMANTIC_CENSUS_REVIEW';repo['phases']['entity_extraction']=False;repo['phases']['capability_analysis']=False;repo['phases']['deep_review']=False;repo['phases']['validation']=False
    r.write(r.repo_file(repo),repo)
    lines=['# Voicebox semantic review checkpoint','',f'Pinned commit: `{commit}`. Static source review only; no target code was executed.','',
           '## Confirmed source contracts','',f'- [Voicebox MCP server]({source_url(server_path,server_line)}) is constructed with `FastMCP(name="voicebox")` and mounted at `/mcp`.','- Four decorated MCP tools are independently catalogued: `voicebox.speak`, `voicebox.transcribe`, `voicebox.list_captures`, and `voicebox.list_profiles`.','- `voicebox.speak` delegates to the existing queued generation endpoint; it does not prove streaming inference.','- `voicebox.transcribe` accepts base64 audio or a loopback-only absolute local path, with a 200 MB guard.','', '## Still pending','', '- 123 HTTP route candidates, 118 UI component candidates, Skills, workflows, packages, scores, mappings and the independent census remain unreviewed.','- This checkpoint keeps Voicebox in `NEEDS_REVIEW`; it does not mark the repository complete.']
    (r.ROOT/'docs/VOICEBOX-SEMANTIC-REVIEW.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print({'repository':REPOSITORY,'mcp_server':server['id'],'verified_tools':len(expected),'state':repo['state']})
if __name__=='__main__':main()
