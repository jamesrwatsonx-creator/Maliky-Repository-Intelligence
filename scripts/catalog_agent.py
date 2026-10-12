"""Read-only JSON interface over the existing public registry and composer."""
import argparse
import json
import re
import registry as r


def normalized(text):
    return ' '.join(re.findall(r'[a-z0-9]+', text.lower()))


def search(text='', repository=None, category=None, kind=None, verified=False, limit=10, private_local=False):
    docs = [json.loads(line) for line in (r.ROOT/'search/search-index.jsonl').read_text(encoding='utf-8').splitlines()]
    canonical = {x['id']: x for group in ('repositories', 'entities', 'capabilities') for x in r.records(group)}
    if private_local:
        for item in r.read('.local/private-catalog.json', []):
            canonical[item['id']] = item
            docs.append({**item, 'entity_type': 'REPOSITORY', 'repository': item['name'], 'text': item['name']+' '+item['description'], 'state': 'CANDIDATE', 'capabilities': []})
    terms = set(re.findall(r'[a-z0-9]+', text.lower()))
    caps = {c['id'] for c in r.records('capabilities') if normalized(text) in [normalized(a) for a in [c['id'], c['name']] + c.get('aliases', [])]} if text else set()
    found = []
    for d in docs:
        source = canonical[d['id']]
        if repository and repository.lower() not in d.get('repository', '').lower(): continue
        if kind and d['entity_type'] != kind: continue
        categories = source.get('categories', []) + [source.get('operational_category', '')] + source.get('secondary_operational_categories', [])
        if category and category not in categories: continue
        # A repository marked COMPLETE is not itself a verified reusable asset.
        status = 'VERIFIED' if d['state'] == 'VERIFIED' else 'CANDIDATE'
        if d['entity_type'] == 'REPOSITORY': status = 'REPOSITORY_METADATA'
        if verified and status != 'VERIFIED': continue
        score = len(terms & set(re.findall(r'[a-z0-9]+', d['text'].lower())))
        if caps & set(d.get('capabilities', [])): score += 10
        if terms and not score: continue
        found.append({**d, 'catalog_status': status, 'categories': categories, 'match_score': score})
    return sorted(found, key=lambda d: (-d['match_score'], d['id']))[:limit]


def plan(requirements, limit=5):
    mapped = []
    capability_ids = set()
    for requirement in requirements:
        verified = search(requirement, verified=True, limit=limit)
        candidates = [x for x in search(requirement, limit=limit*3) if x['catalog_status'] != 'VERIFIED'][:limit]
        exact = [c['id'] for c in r.records('capabilities') if c['status'] == 'VERIFIED' and normalized(requirement) in [normalized(a) for a in [c['id'], c['name']] + c.get('aliases', [])]]
        capability_ids.update(exact)
        mapped.append({'requirement': requirement, 'verified_recommendations': verified, 'discovery_candidates': candidates, 'exact_capability_ids': exact, 'gap': 'NO_EXACT_VERIFIED_CAPABILITY' if not exact else None})
    composition = r.compose(sorted(capability_ids))
    composition_gaps = set(composition.get('missing_capabilities', []))
    missing = [x['requirement'] for x in mapped
               if x['gap'] or composition_gaps.intersection(x['exact_capability_ids'])]
    return {'requirements': mapped, 'composition': composition,
            'missing_components': missing,
            'unprovided_capabilities': sorted(composition_gaps),
            'mvp_plan': [
                'Confirm one customer workflow and acceptance criteria for each requirement.',
                'Inspect linked verified recommendations; confirm licenses, dependencies and runtime compatibility.',
                'Integrate the selected providers for exact capability matches; investigate candidates for remaining requirements.',
                'Implement only confirmed gaps, then test the complete workflow with one user.'],
            'limitations': 'Lexical recommendations are leads, not proof that a feature is satisfied. Missing means not established in this catalog. No model, source execution, credentials, or writes are used.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['search', 'compose', 'plan'])
    p.add_argument('text', nargs='?', default='')
    p.add_argument('--repository'); p.add_argument('--category'); p.add_argument('--kind')
    p.add_argument('--verified', action='store_true'); p.add_argument('--limit', type=int, default=10)
    p.add_argument('--private-local', action='store_true', help='Include ignored private metadata accessible to this local OS user, for search only')
    p.add_argument('--requirement', action='append', default=[])
    p.add_argument('--capability', action='append', default=[])
    a = p.parse_args()
    if a.limit < 1 or a.limit > 100: p.error('--limit must be 1..100')
    if a.private_local and a.command != 'search': p.error('--private-local is supported only by search')
    if a.command == 'search': result = search(a.text, a.repository, a.category, a.kind, a.verified, a.limit, a.private_local)
    elif a.command == 'compose': result = r.compose(a.capability or a.text)
    else:
        if not a.requirement: p.error('plan requires at least one --requirement')
        result = plan(a.requirement, a.limit)
    # Escaped JSON is portable through Windows PowerShell's legacy code pages.
    print(json.dumps({'schema_version': 1, 'result': result}, ensure_ascii=True))


if __name__ == '__main__': main()
