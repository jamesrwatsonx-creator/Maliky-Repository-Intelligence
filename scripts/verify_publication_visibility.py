"""Fresh publication check, without restarting discovery or inspection."""
import json
import registry as r

def verify():
    raw=[];page=1
    while True:
        batch=r.gh(f'user/repos?affiliation=owner&per_page=100&page={page}')
        if not batch:break
        raw.extend(batch);page+=1
    r.write('.local/publication-visibility.json',raw)
    # Preserve historical private identifiers as publication deny-list evidence.
    prior=r.read('.local/discovery-private.json',[])
    retained={x['id']:x for x in prior if x.get('private')}
    retained.update({x['id']:x for x in raw})
    r.write('.local/discovery-private.json',list(retained.values()))
    public={x['id'] for x in raw if r.public_repo(x)}
    records=r.records('repositories');blocked=[x['id'] for x in records if x['github_id'] not in public]
    if blocked:
        r.write('.local/visibility-blockers.json',blocked)
        raise RuntimeError('Public records no longer verified public; publication blocked')
    result={'verified_at':r.now(),'valid':True,'public_registry_records_checked':len(records),'scope':'Fresh paginated authenticated owner metadata; no source ingestion','public_repository_ids':[x['id'] for x in records]}
    r.write('system/publication-visibility.json',result)
    return {'valid':True,'public_registry_records_checked':len(records)}
if __name__=='__main__':print(json.dumps(verify()))
