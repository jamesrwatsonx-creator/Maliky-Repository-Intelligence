"""Incremental metadata-only catalog refresh from a fresh public GitHub inventory."""
import argparse
import collections
import concurrent.futures
import json
import re
import urllib.request
import registry as r

# Lightweight metadata classification. This is discovery evidence, not source verification.
RULES = [
    ('01', 'skills', r'\bskills?\b'), ('02', 'mcp-servers', r'\bmcp\b'),
    ('07', 'generative-ai', r'\b(voice|audio|speech|tts|stt|whisper)\b'),
    ('09', 'creative-tools', r'\b(video|movie|media|animation)\b'),
    ('05', 'developer-tools', r'\b(browser|computer use|scraping)\b'),
    ('10', 'research-projects', r'\b(research|search|scraper|crawl|intelligence)\b'),
    ('21', 'application-security', r'\b(security|authentication|identity|oauth)\b'),
    ('22', 'commerce-e-commerce', r'\b(blockchain|wallet|crypto|payments)\b'),
    ('19', 'mobile-applications', r'\b(android|ios|mobile|react native|flutter)\b'),
    ('16', 'frontend-applications', r'\b(ui|frontend|react|components|website)\b'),
    ('17', 'design-systems', r'\b(design|figma|css)\b'),
    ('04', 'ai-memory', r'\b(memory|context|rag|knowledge)\b'),
    ('03', 'ai-agents', r'\b(agents?|orchestration)\b'),
    ('15', 'llm-projects', r'\b(llm|model|inference)\b'),
    ('14', 'devops', r'\b(deploy|docker|infrastructure|ci/cd)\b'),
    ('23', 'developer-tools', r'\b(testing|benchmark|evaluation)\b'),
    ('11', 'business-applications', r'\b(business|marketing|crm|sales)\b'),
    ('12', 'apis', r'\b(api|sdk|backend)\b'),
    ('24', 'developer-tools', r'\b(code|coding|developer|programming|terminal|cli)\b'),
    ('20', 'automation-scripting', r'\b(workflow|automation|automate|scheduling)\b'),
]


def readme_description(meta):
    url = 'https://raw.githubusercontent.com/' + meta['full_name'] + '/' + meta['default_branch'] + '/README.md'
    try:
        with urllib.request.urlopen(url, timeout=15) as response: text = response.read(150000).decode('utf-8', 'replace')
        paragraphs = []
        for paragraph in re.split(r'\n\s*\n', text):
            plain = re.sub(r'<[^>]+>', '', paragraph).strip()
            if plain.startswith(('#', '!', '[', '|', '```', '<', '-', '*')): continue
            plain = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', plain)
            plain = ' '.join(plain.split())
            if len(plain) >= 40: paragraphs.append(plain[:500])
        return (paragraphs[0], url) if paragraphs else (None, url)
    except Exception: return None, url


def sync(path):
    metadata = json.loads(open(path).read())
    if any(not r.public_repo(m) for m in metadata): raise ValueError('Input must contain verified public owned repositories only')
    prior = r.records('repositories'); visible = {m['id'] for m in metadata}
    blocked = [x['id'] for x in prior if x['github_id'] not in visible]
    if blocked:
        r.write('.local/visibility-blockers.json', blocked)
        raise RuntimeError('Previously public records are missing from fresh visibility inventory; publication blocked')
    missing = [m for m in metadata if not m.get('description') and not (r.read(r.repo_file({'github_id': m['id']})) or {}).get('description')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        descriptions = dict(zip([m['id'] for m in missing], pool.map(readme_description, missing)))
    taxonomy = r.read('registry/taxonomy/categories.json')
    if not any(x['id'] == 'category:general-other' for x in taxonomy):
        taxonomy.append({'id': 'category:general-other', 'name': 'General / Other', 'family': 'General'})
        r.write('registry/taxonomy/categories.json', taxonomy)
    categories = {x['id'] for x in taxonomy}
    entities = collections.defaultdict(list)
    for entity in r.records('entities'): entities[entity['source']['repository_id']].append(entity)
    for meta in metadata:
        fresh = r.blank_repo(meta); record = r.read(r.repo_file(fresh)) or fresh
        for key in ('name', 'full_name', 'url', 'owner', 'visibility', 'affiliation', 'fork', 'default_branch', 'metadata'):
            record[key] = fresh[key]
        if fresh['description']: record['description'] = fresh['description']
        description, evidence_url = descriptions.get(meta['id'], (None, meta['html_url']))
        if not record['description']:
            record['description'] = description or ('Owned repository ' + meta['name'] + '; purpose is not established by available metadata. Inspect its linked source before recommending reuse.')
        text = record['description'] + ' ' + record['name'].replace('-', ' ').replace('_', ' ')
        matches = [(op, 'category:' + cat) for op, cat, pattern in RULES if re.search(pattern, text, re.I)]
        prior_categories = set(record.get('categories', []))
        prior_categories.update(cat for _, cat in matches if cat in categories)
        for entity in entities[record['id']]: prior_categories.update(entity.get('categories', []))
        record['categories'] = sorted(prior_categories or {'category:general-other'})
        if record.get('operational_category') == 'operational:25' and matches:
            record['operational_category'] = 'operational:' + matches[0][0]
        record['secondary_operational_categories'] = sorted(set(record.get('secondary_operational_categories', [])) | {'operational:' + op for op, _ in matches if 'operational:' + op != record['operational_category']})
        record['visibility_verified_at'] = r.now()
        record['catalog_metadata'] = {'status': 'DISCOVERABLE', 'classification': 'LIGHTWEIGHT_METADATA', 'source_links': [meta['html_url'], evidence_url], 'updated_at': r.now(), 'purpose_established': bool(meta.get('description') or description or not record['description'].startswith('Owned repository '))}
        r.write(r.repo_file(record), record)
    private = [m for m in r.read('.local/discovery-private.json', []) if m.get('private')]
    old_manifest = r.read('system/discovery-manifest.json', {})
    r.write('system/discovery-manifest.json', {**old_manifest, 'discovered_at': r.now(), 'scope': 'Fresh paginated public owner REST inventory reconciled with authenticated connector owner inventory; public pagination exhausted', 'counts': {'owned': len(metadata) + len(private), 'public_owned': len(metadata), 'private_owned': len(private), 'forks_public_owned': sum(m['fork'] for m in metadata)}, 'repositories': [{'id': 'repository:' + str(m['id']), 'github_id': m['id'], 'full_name': m['full_name'], 'visibility': 'public', 'affiliation': 'FORKED_UNDER_USER_ACCOUNT' if m['fork'] else 'OWNED'} for m in metadata]})
    r.write('system/publication-visibility.json', {'verified_at': r.now(), 'valid': True, 'public_registry_records_checked': len(metadata), 'scope': 'Fresh paginated public owner metadata reconciled with authenticated owner connector; no source ingestion', 'public_repository_ids': ['repository:' + str(m['id']) for m in metadata]})
    report = {'public_repositories': len(metadata), 'added': len(metadata)-len(prior), 'preserved_entity_records': sum(map(len, entities.values())), 'unresolved_purposes': sum(not x['catalog_metadata']['purpose_established'] for x in r.records('repositories'))}
    r.write('system/catalog-refresh-report.json', report)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('inventory')
    print(json.dumps(sync(parser.parse_args().inventory)))
