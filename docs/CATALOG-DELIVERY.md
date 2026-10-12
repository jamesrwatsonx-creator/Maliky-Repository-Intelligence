# Practical catalog delivery — 2026-10-12

## Current public coverage

The latest authenticated owner inventory found **579 accessible repositories**: 566 public and 13 private, including 546 public forks. Private identities and evidence remain outside public artifacts. The public registry and browse export contain one repository record for each of the 566 public repositories.

The public catalog currently exposes **8,856 active searchable assets** (7,894 VERIFIED and 962 CANDIDATE), plus 38 preserved historical candidate records that are not promoted into the active catalog. Existing IDs, source paths, pinned revisions, blob SHAs, review states and relationships remain canonical. Repository discoverability does not assert source inspection or runtime readiness.

Generated navigation contains 16 asset-type sections, 42 populated purpose topics and 23 populated views over the established 25-area taxonomy. The current build produces 393 Markdown browse pages with pagination and nested views. The validator checked 397 Markdown files and 4,870 local links. The root README is human-maintained; [`browse/README.md`](../browse/README.md) is the generated, count-bearing catalog homepage. Refreshing generated views leaves the root README unchanged.

All public repositories have a GitHub source link and category routing. **19 repositories are marked NEEDS DESCRIPTION** because available metadata/source evidence does not yet support a useful purpose statement; their pages retain the source link and explicit limitation rather than inventing functionality.

## Search, composition and agent access

Use the deterministic public export search:

```sh
python scripts/search_catalog.py "Android voice" --limit 10
python scripts/search_catalog.py --type MCP_SERVER --limit 20
python scripts/search_catalog.py --topic animation-motion --limit 20
```

For read-only agent search, category/repository filters, composition and a requirements-to-MVP plan, see [`AGENT-CATALOG.md`](AGENT-CATALOG.md). Example:

```sh
python scripts/catalog_agent.py search "voice" --limit 10
python scripts/catalog_agent.py compose --capability capability:queued-speech-generation-submission
python scripts/catalog_agent.py plan --requirement "voice generation" --requirement "appointment booking"
```

Agent output distinguishes verified assets, candidates and repository metadata. It returns source links for selected assets, states unverified compatibility assumptions, and treats missing evidence as a catalog gap—not proof that no owned implementation exists. It is read-only and uses the existing registry/composition function; no hosted service, paid model, vector database or source-code execution is required.

## Incremental refresh and validation

Run `python scripts/refresh_catalog.py` from `recovery/v1-rebuild` after a new fork or repository is added. The existing refresh flow authenticates discovery, reuses stable repository IDs and prior evidence, and inspects only newly discovered public sources with deterministic bounded intake. It does not re-ingest unchanged repositories or promote candidates to VERIFIED. Private identities remain under ignored `.local/` state.

For view-only regeneration and checks:

```sh
python scripts/build_indexes.py
python scripts/build_catalog.py
python scripts/validate_registry.py
python scripts/validate_catalog.py
python -m unittest discover -s tests
python scripts/publication_guard.py
```

Latest completed checks: registry valid (11,256 canonical records); catalog valid (566 repositories, 8,856 active assets, 16 types, 42 topics, 23 populated canonical areas); all 54 tests pass; publication guard passes for all 13 private identities. The generated lightweight browser is at [`docs/catalog/index.html`](catalog/index.html); GitHub Pages account settings are not changed automatically.

The source-review queue and historical semantic `COMPLETE` state remain separate from Catalog V1 readiness. Universal deep review, exhaustive scoring, security review, relationship mapping, a hosted website and an agent plugin are future work.
