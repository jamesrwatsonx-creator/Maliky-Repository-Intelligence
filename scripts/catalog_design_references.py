"""Create source-backed DESIGN_REFERENCE candidates from cached DESIGN.md files."""
from __future__ import annotations
import pathlib,re
import registry as r

TARGET='jamesrwatsonx-creator/awesome-design-md'
STYLE_TERMS={
    'luxury':r'\bluxury\b|quietly expensive', 'editorial':r'\beditorial\b|\bmagazine\b',
    'dark':r'\bdark\b|black canvas|near-pure black|deep navy', 'minimal':r'\bminimal\b|\baustere\b',
    'black-and-white':r'black.*white|white.*black', 'gradient-led':r'\bgradient\b',
    'typography-led':r'\btypography\b|\btypeface\b|display headlines', 'serif-led':r'\bserif\b',
    'fintech':r'financial[- ]infrastructure|\bfintech\b|\bmoney\b', 'automotive':r'\bautomotive\b|\bcar\b',
}
LAYOUT_TERMS={'landing-page':r'marketing page|landing page','dashboard':r'\bdashboard\b','editorial-layout':r'\bmagazine\b|long-form'}
FEATURE_TERMS={'oversized typography':r'large|display headline|oversized','gradient mesh':r'gradient mesh','photography-led':r'photography|photo','cards':r'\bcards?\b','grid':r'\bgrid\b','animation':r'\banimation\b|\bmotion\b','3d':r'\b3d\b|three-dimensional'}

def terms(text, mapping):
    return [name for name,pattern in mapping.items() if re.search(pattern,text,re.I)]

def first_body_paragraph(text):
    """Fallback for older documents that use headings instead of frontmatter."""
    lines=text.splitlines();paragraph=[]
    for line in lines:
        if not line.strip() or line.lstrip().startswith('#'):
            if paragraph: break
            continue
        paragraph.append(line.strip())
    return ' '.join(paragraph)

def main():
    repo=next((x for x in r.records('repositories') if x['full_name']==TARGET),None)
    if not repo: raise ValueError('Target repository is absent from the public registry')
    commit=repo['inspected_commit'];tree=r.read(r.cache_path(repo,commit)/'tree.json')
    if not tree or tree.get('truncated',True): raise ValueError('A complete pinned tree is required')
    entries={e['path']:e for e in tree['tree'] if e['type']=='blob'}
    paths=sorted(path for path in entries if path.startswith('design-md/') and path.endswith('/DESIGN.md'))
    if not paths: raise ValueError('No independent design documents found')
    created=[]
    for path in paths:
        entry=entries[path];text=r.source_text(repo,commit,entry,True)
        if text is None: raise ValueError('Cached source missing: '+path)
        frontmatter=r.frontmatter(text);description=frontmatter.get('description','').strip() or first_body_paragraph(text)
        if not description: raise ValueError('No source description: '+path)
        symbol=pathlib.PurePosixPath(path).parent.name
        entity=r.entity_record(repo,commit,entry,{'type':'DESIGN_REFERENCE','symbol':symbol,'description':description,'line':1})
        title=re.search(r'^#\s+(.+)',text,re.M)
        entity['name']=frontmatter.get('name',title[1] if title else symbol).strip()
        entity['operational_category']='operational:17';entity['secondary_operational_categories']=['operational:16']
        entity['recommendation']='REFERENCE ONLY';entity['contribution_role']='REFERENCE'
        visual_style=terms(description,STYLE_TERMS);layout=terms(description,LAYOUT_TERMS);features=terms(description,FEATURE_TERMS)
        entity.update({'visual_style':visual_style,'layout':layout,'visual_features':features,'technologies':[],'best_for':[],
                       'visual_evidence':[{'field':field,'value':value,'source_path':path,'basis':'source-description'} for field,values in [('visual_style',visual_style),('layout',layout),('visual_features',features)] for value in values],
                       'metadata':{'reference_kind':'source design-system document','visual_metadata_basis':'source-description only'}})
        entity['evidence']=[{'type':'source_path','value':path},{'type':'source_description','value':'frontmatter.description'}]
        r.write('registry/entities/'+entity['id'].split(':')[1]+'.json',entity);created.append(entity)
    all_types=r.read('registry/taxonomy/vocabulary.json')['entity_types']
    counts={kind:sum(e['entity_type']==kind for e in created) for kind in all_types}
    repo['entity_census']={kind:{'detected':counts[kind],'catalogued':counts[kind],
                                 'detection_scope':'source DESIGN.md documents' if kind=='DESIGN_REFERENCE' else 'source review; no candidate detected',
                                 'reviewed':False} for kind in all_types if kind!='REPOSITORY'}
    repo['entity_count']=len(created);repo['state']='NEEDS_REVIEW';repo['next_phase']='SEMANTIC_CENSUS_REVIEW'
    repo['phases']['entity_extraction']=False
    r.write(r.repo_file(repo),repo)
    print({'repository':TARGET,'commit':commit,'design_references':len(created)})
if __name__=='__main__':main()
