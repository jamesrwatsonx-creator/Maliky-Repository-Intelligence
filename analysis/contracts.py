"""Versioned evidence boundary. Raw reports and packets stay under .local."""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import PurePosixPath
from datetime import datetime, timezone
import re

VERSION = '1.0'
KINDS = {'entity_candidate', 'symbol', 'relationship', 'dependency', 'license', 'security', 'file_classification', 'context'}

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()

def source_path(value):
    if not isinstance(value, str) or not value or '\\' in value or ':' in value or '\x00' in value:
        raise ValueError('Expected a repository-relative POSIX path')
    p = PurePosixPath(value)
    if p.is_absolute() or '..' in p.parts or str(p) != value or value == '.':
        raise ValueError('Unsafe source path')
    return value

def validate(e):
    if e.get('schema_version') != VERSION or e.get('review_status') != 'UNREVIEWED':
        raise ValueError('Analysis evidence must remain unreviewed')
    for key in ('source_tool', 'source_tool_version', 'created_at'):
        if not isinstance(e.get(key), str) or not e[key]: raise ValueError('Missing '+key)
    r = e['repository']
    for key in ('id', 'owner', 'name'):
        if not isinstance(r.get(key), str) or not r[key]: raise ValueError('Missing repository '+key)
    if not re.fullmatch('[0-9a-f]{40}', r.get('commit', '')): raise ValueError('Unpinned evidence')
    if r.get('visibility') not in ('public', 'private'): raise ValueError('Unknown visibility')
    f = e['finding']
    if f.get('type') not in KINDS: raise ValueError('Unknown evidence type')
    if not isinstance(f.get('description'), str): raise ValueError('Missing description')
    source_path(f['path'])
    for field in ('line_start', 'line_end'):
        if f.get(field) is not None and (type(f[field]) is not int or f[field] < 1): raise ValueError('Invalid line')
    if f.get('line_end', f.get('line_start', 1)) < f.get('line_start', 1): raise ValueError('Reversed lines')
    if type(f.get('confidence')) not in (float, int) or not math.isfinite(f['confidence']) or not 0 <= f['confidence'] <= 1:
        raise ValueError('Invalid confidence')
    if f['type'] == 'entity_candidate' and not f.get('proposed_entity_type'): raise ValueError('Missing candidate type')
    if not e.get('evidence', {}).get('raw_reference'): raise ValueError('Missing raw reference')
    if e['evidence_id'] != 'evidence:'+digest({k:v for k,v in e.items() if k not in ('evidence_id','created_at')}):
        raise ValueError('Evidence identity mismatch')
    return e

def evidence(repo, tool, version, finding, raw_reference, **support):
    e = {'schema_version':VERSION, 'source_tool':tool, 'source_tool_version':version,
         'repository':{'id':repo['id'], 'owner':repo['full_name'].split('/')[0], 'name':repo['full_name'].split('/')[1],
                       'commit':repo['inspected_commit'], 'visibility':repo.get('visibility', 'private')},
         'finding':{'confidence':0.6, 'description':'', **finding},
         'evidence':{'raw_reference':raw_reference, **support}, 'review_status':'UNREVIEWED'}
    e['evidence_id'] = 'evidence:'+digest(e)
    e['created_at'] = datetime.now(timezone.utc).isoformat()
    return validate(e)

def dependency_identity(name, version, ecosystem):
    ecosystem = {'python':'pypi', 'python-pkg':'pypi', 'javascript':'npm', 'js':'npm', 'rust':'cargo', 'go-module':'golang'}.get(ecosystem, ecosystem)
    name = re.sub('[-_.]+', '-', name).lower() if ecosystem == 'pypi' else name
    return {'name':name, 'version':version or '', 'ecosystem':ecosystem or 'unknown'}

def merge_dependencies(items):
    merged = {}
    for e in items:
        if e['finding']['type'] != 'dependency': continue
        d = e['finding']['dependency']; identity = dependency_identity(d['name'], d.get('version'), d.get('ecosystem'))
        key = digest(identity)
        record = merged.setdefault(key, {**identity, 'evidence_ids':[], 'sources':[]})
        if e['evidence_id'] not in record['evidence_ids']: record['evidence_ids'].append(e['evidence_id'])
        if e['source_tool'] not in record['sources']: record['sources'].append(e['source_tool'])
    return list(merged.values())
