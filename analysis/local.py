"""Independent stdlib implementations inspired by the inspected helper concepts.

These do not claim to run Aider, Continue, RepoAgent, Linguist or Repomix.
"""
import ast
from collections import Counter, defaultdict
import json
from pathlib import PurePosixPath
import re
import tomllib
from .contracts import dependency_identity

VERSION = 'local-static-1'
LANGUAGES = {'.py':'Python','.ts':'TypeScript','.tsx':'TSX','.js':'JavaScript','.jsx':'JSX','.go':'Go','.rs':'Rust','.rb':'Ruby','.kt':'Kotlin','.swift':'Swift','.html':'HTML','.css':'CSS','.md':'Markdown','.json':'JSON','.toml':'TOML','.yml':'YAML','.yaml':'YAML'}

def analyze_file(path, text, detector):
    """Return path-local facts only, enabling content/path/version cache reuse."""
    p=PurePosixPath(path); facts=[]; errors=[]
    def add(kind, description, **kw): facts.append({'type':kind,'path':path,'description':description,**kw})
    generated=bool(re.search(r'(?i)(@generated|automatically generated|do not edit)',text[:2000])) or p.name.endswith(('.min.js','.min.css'))
    vendored=bool(set(p.parts)&{'vendor','vendors','third_party','node_modules'})
    add('file_classification','Conservative extension/header heuristics; not full Linguist',language=LANGUAGES.get(p.suffix,'unknown'),generated=generated,vendored=vendored,documentation=p.suffix in ('.md','.rst'),data_file=p.suffix in ('.json','.csv','.tsv'))
    for f in detector(path,text,errors):
        add('entity_candidate',f['description'],proposed_entity_type=f['type'],symbol=f['symbol'],line_start=f['line'],confidence=0.65)
    if p.name.lower() == 'design.md' and len(p.parts)>1:
        title=re.search(r'^#\s+(.+)',text,re.M)
        add('entity_candidate','Distinct design specification; visual tags require evidence review',proposed_entity_type='DESIGN_REFERENCE',symbol=title[1].strip() if title else p.parent.name,line_start=1,confidence=0.8)
    if p.name=='index.html' and set(p.parts)&{'examples','templates','websites','sites'}:
        title=re.search(r'<title[^>]*>(.*?)</title>',text,re.S|re.I)
        add('entity_candidate','Standalone HTML example candidate; confirm boundary and style',proposed_entity_type='WEBSITE_REFERENCE',symbol=title[1].strip() if title else str(p.parent),line_start=1,confidence=0.55)
    if p.suffix == '.py':
        try:
            tree=ast.parse(text)
            # Keep call evidence bounded and honest. A generic Python call has no
            # reliable target without import/type/dataflow resolution. We record
            # only simple calls to a definition in the same source file.
            local_definitions={node.name for node in ast.walk(tree) if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))}
            class Visitor(ast.NodeVisitor):
                def __init__(self): self.scope=[]
                def definition(self,node):
                    name='.'.join(self.scope+[node.name])
                    add('symbol','Python AST declaration',symbol=name,line_start=node.lineno,line_end=node.end_lineno,symbol_kind=type(node).__name__)
                    self.scope.append(node.name); self.generic_visit(node); self.scope.pop()
                visit_FunctionDef=definition; visit_AsyncFunctionDef=definition; visit_ClassDef=definition
                def visit_Call(self,node):
                    if isinstance(node.func,ast.Name) and node.func.id in local_definitions:
                        add('relationship','Same-file Python call reference; dynamic dispatch is not resolved',symbol='.'.join(self.scope),target=node.func.id,relation='CALL_CANDIDATE',line_start=node.lineno,confidence=0.6)
                    self.generic_visit(node)
                def visit_ImportFrom(self,node):
                    add('relationship','Python import reference',target='.'*node.level+(node.module or ''),relation='IMPORTS',line_start=node.lineno)
                def visit_Import(self,node):
                    for alias in node.names: add('relationship','Python import reference',target=alias.name,relation='IMPORTS',line_start=node.lineno)
            Visitor().visit(tree)
        except (SyntaxError,ValueError,RecursionError) as ex: errors.append({'path':path,'stage':'ast','error':str(ex)[:250]})
    elif p.suffix in ('.ts','.tsx','.js','.jsx'):
        for m in re.finditer(r'(?m)^export\s+(?:default\s+)?(?:async\s+)?(?:function|class|const)\s+(\w+)',text):
            add('symbol','Exported JavaScript/TypeScript declaration heuristic',symbol=m[1],line_start=text[:m.start()].count('\n')+1,confidence=0.5)
        for m in re.finditer(r'\bfrom\s+[\"\x27]([^\"\x27]+)',text):
            add('relationship','JavaScript/TypeScript import reference',target=m[1],relation='IMPORTS',line_start=text[:m.start()].count('\n')+1,confidence=0.5)
    def dep(name,version,ecosystem,scope):
        add('dependency','Declared manifest dependency; range is not a resolved installed version',dependency=dependency_identity(name,version,ecosystem),scope=scope)
    try:
        if p.name=='package.json':
            data=json.loads(text)
            for scope in ('dependencies','devDependencies','peerDependencies','optionalDependencies'):
                for name,version in data.get(scope,{}).items(): dep(name,str(version),'npm',scope)
            if isinstance(data.get('license'),str): add('license','Manifest license declaration',expression=data['license'])
        elif p.name=='pyproject.toml':
            data=tomllib.loads(text); project=data.get('project',{})
            for declaration in project.get('dependencies',[]):
                m=re.match(r'([A-Za-z0-9_.-]+)(.*)',declaration)
                if m: dep(m[1],m[2].strip(),'pypi','runtime')
        elif p.name.startswith('requirements') and p.suffix=='.txt':
            for line in text.splitlines():
                m=re.match(r'^([A-Za-z0-9_.-]+)\s*([<>=!~].*)?$',line.strip())
                if m: dep(m[1],m[2] or '', 'pypi','declared')
        for m in re.finditer(r'SPDX-License-Identifier:\s*([^\r\n*]+)',text):
            add('license','Explicit SPDX identifier in source',expression=m[1].strip(),line_start=text[:m.start()].count('\n')+1)
        if p.name.upper().startswith(('LICENSE','LICENCE','COPYING','NOTICE')):
            add('license','License/notice document exists; absence of detected expression is not absence of license',expression='UNREVIEWED',line_start=1)
    except (ValueError,TypeError,AttributeError) as ex: errors.append({'path':path,'stage':'manifest','error':str(ex)[:250]})
    return {'facts':facts,'errors':errors}

def classify_only(path, text, reason):
    """Preserve an oversized source file in coverage without parsing it."""
    p=PurePosixPath(path)
    generated=bool(re.search(r'(?i)(@generated|automatically generated|do not edit)',text[:2000])) or p.name.endswith(('.min.js','.min.css'))
    vendored=bool(set(p.parts)&{'vendor','vendors','third_party','node_modules'})
    return {'facts':[{'type':'file_classification','path':path,
                      'description':'Static parsing skipped: '+reason,
                      'language':LANGUAGES.get(p.suffix,'unknown'),'generated':generated,'vendored':vendored,
                      'documentation':p.suffix in ('.md','.rst'),'data_file':p.suffix in ('.json','.csv','.tsv'),
                      'static_analysis_skipped':True}], 'errors':[]}

def repository_map(evidence):
    """Aider-inspired reference ranking, deliberately simpler than its PageRank."""
    symbols=defaultdict(list); references=Counter(); imports=Counter()
    for e in evidence:
        f=e['finding']
        if f['type']=='symbol': symbols[f['symbol'].split('.')[-1]].append(f)
        elif f['type']=='relationship':
            if f.get('relation')=='CALL_CANDIDATE': references[f['target'].split('.')[-1]]+=1
            if f.get('relation')=='IMPORTS': imports[f['path']]+=1
    ranked=[]
    for name,defs in symbols.items():
        for f in defs: ranked.append({**f,'reference_count':references[name], 'ambiguity':len(defs)>1})
    ranked.sort(key=lambda f:(-f['reference_count'],f['path'],f['line_start']))
    scores=Counter()
    for f in ranked: scores[f['path']]+=1+f['reference_count']
    return {'method':'symbol-name-reference-ranking; ambiguous names are not resolved call edges',
            'important_symbols':ranked, 'important_files':[{'path':p,'rank':s} for p,s in scores.most_common()],
            'limitations':['Python AST; JS/TS exported declaration heuristics only','No runtime dispatch or whole-program dataflow','Other languages retain static detector evidence and source paths']}
