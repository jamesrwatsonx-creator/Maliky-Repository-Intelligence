"""Import native scanner outputs, without trusting their classifications."""
from .contracts import evidence, source_path, dependency_identity
from urllib.parse import unquote
import xml.etree.ElementTree as ET

TOOLS = ('semgrep', 'scancode', 'syft', 'linguist', 'codeql', 'repomix')

def normalize(tool, payload, repo, version, raw_reference, known_paths):
    if tool not in TOOLS: raise ValueError('No native-output adapter for '+tool)
    result = []
    def emit(kind, path, description='', **fields):
        source_path(path)
        if path not in known_paths: raise ValueError('Report references a path outside the pinned source tree: '+path)
        result.append(evidence(repo, tool, version, {'type':kind, 'path':path, 'description':description, **fields}, raw_reference))
    def package(p, path):
        name = p.get('name')
        if not name: return
        ecosystem = p.get('type') or p.get('ecosystem') or 'unknown'
        if p.get('purl', '').startswith('pkg:'): ecosystem = p['purl'][4:].split('/')[0]
        namespace = p.get('namespace')
        if namespace: name = namespace.rstrip('/')+'/'+name
        emit('dependency', path, 'Scanner package inventory; dependency role requires review',
             dependency=dependency_identity(name, p.get('version'), ecosystem), purl=p.get('purl'))
    if tool == 'semgrep':
        if not isinstance(payload.get('results'), list): raise ValueError('Expected Semgrep results')
        for f in payload['results']:
            extra=f.get('extra', {}); meta=extra.get('metadata', {})
            kind = meta.get('entity_type')
            # Only local, deliberately authored rules can propose entity types.
            typ = 'entity_candidate' if f.get('check_id', '').split('.')[-1].startswith('maliky-') and kind else 'security'
            emit(typ, f['path'], extra.get('message', ''), line_start=f['start']['line'],
                 symbol=extra.get('metavars', {}).get('$NAME', {}).get('abstract_content', f['check_id']),
                 proposed_entity_type=kind if typ == 'entity_candidate' else None, rule=f['check_id'])
    elif tool == 'scancode':
        if not isinstance(payload.get('files'), list): raise ValueError('Expected ScanCode files')
        for f in payload['files']:
            if f.get('type') == 'directory': continue
            path=f['path']
            expression=f.get('detected_license_expression_spdx') or f.get('detected_license_expression')
            if expression: emit('license', path, 'Detected license expression; obligations need review', expression=expression)
            for p in f.get('package_data', []): package(p, path)
            for p in f.get('licenses', []):
                if p.get('spdx_license_key'): emit('license', path, 'Legacy ScanCode license match', expression=p['spdx_license_key'])
    elif tool == 'syft':
        if not isinstance(payload.get('artifacts'), list): raise ValueError('Expected Syft artifacts')
        for p in payload['artifacts']:
            for location in p.get('locations', []):
                path=location.get('path') or location.get('accessPath')
                if path and path.startswith('./'): path=path[2:]
                if path: package(p, path)
    elif tool == 'linguist':
        for key, value in payload.items():
            if 'files' in value:
                for path in value['files']: emit('file_classification', path, 'Linguist language breakdown', language=key)
            else:
                language=value.get('language')
                emit('file_classification', key, 'Linguist file classification', language=language,
                     generated=value.get('generated', False), vendored=value.get('vendored', False))
    elif tool == 'codeql':
        if payload.get('version') != '2.1.0' or not isinstance(payload.get('runs'), list): raise ValueError('Expected SARIF 2.1.0')
        for run in payload['runs']:
            for f in run.get('results', []):
                for location in f.get('locations', []):
                    physical=location['physicalLocation']; artifact=physical['artifactLocation']
                    uri=artifact.get('uri')
                    if uri is None: uri=run['artifacts'][artifact['index']]['location']['uri']
                    emit('security', unquote(uri), f.get('message', {}).get('text', ''),
                         line_start=physical.get('region', {}).get('startLine', 1), rule=f.get('ruleId', 'unknown'))
    elif tool == 'repomix':
        if not isinstance(payload, str) or '<!DOCTYPE' in payload or '<!ENTITY' in payload: raise ValueError('Expected plain Repomix XML')
        root=ET.fromstring('<packet>'+payload+'</packet>')
        for f in root.iter('file'):
            emit('context', f.attrib['path'], 'Compressed review context; reopen exact source before confirming behavior',
                 excerpt=''.join(f.itertext())[:8000])
    return result
