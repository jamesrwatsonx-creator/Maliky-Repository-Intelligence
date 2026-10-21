# Refresh the public catalog

Run from the repository checkout on `recovery/v1-rebuild`:

```sh
python scripts/refresh_catalog.py
```

The command uses authenticated GitHub pagination once, reuses stable GitHub repository IDs, refreshes current public metadata, and retains existing repository, entity, evidence and review records. A repository that becomes inaccessible or private blocks the refresh so its existing public record is not silently published. Private identities and raw discovery data stay under ignored `.local/` state.

Only newly discovered public repositories receive a source pass (up to 500 priority-selected files) at their pinned current revision. The pass is deterministic and does not execute source code or promote candidates to `VERIFIED`. Existing repositories are not re-ingested. New candidates retain their review status; use the ordinary scoped review process only where stronger evidence is needed.

The operation rebuilds search, graph, registry indexes and inspection statistics, regenerates the Markdown browse sections and JSON/static-search export, then validates the registry and catalog links. It is safe to run twice: stable IDs and source identity prevent duplicate records, while generated pages are replaced from canonical state.

For an already refreshed registry, regenerate only the public views with:

```sh
python scripts/build_indexes.py
python scripts/build_catalog.py
python scripts/validate_registry.py
python scripts/validate_catalog.py
python -m unittest discover -s tests
python scripts/publication_guard.py
```

Review `system/validation-report.json` and the printed refresh summary, then make a normal commit and push to `origin/recovery/v1-rebuild`. The static search page is prepared at `docs/catalog/`; enabling GitHub Pages with the `recovery/v1-rebuild` branch and `/docs` folder is an account setting and is not changed by this script.

## Pinned extraction and cohort semantic review

Resume unfinished revisions with archive-backed reads rather than moving them to
live HEAD:

```sh
python scripts/run_bulk_intake.py --priority --pinned --snapshot --limit 25
```

Extraction prepares candidates. To finish a reviewed cohort, write explicit
decisions using the examples under `system/semantic-reviews/`, then run:

```sh
python scripts/review_extracted_batch.py --plan system/semantic-reviews/2026-10-21-cohort-001.json --dry-run
python scripts/review_extracted_batch.py --plan system/semantic-reviews/2026-10-21-cohort-001.json
```

Each plan pins its repository and commit, records architecture/census coverage,
lists reviewed source paths, retains independently useful assets with lean fields,
and explains every excluded candidate. Shared entity defaults and explicit path
exclusion groups keep repetitive decisions compact. New assets may be added when
source review finds boundaries the detector missed. Capability names or explicit
capability tuples are supported; relationships use retained asset names. Sensitive
surfaces receive a scoped review with source paths and a concrete conclusion.

The entrypoint verifies the complete source coverage, cached blob hashes, taxonomy
references and candidate dispositions before applying a plan. Excluded records are
preserved in the ignored pinned cache and in Git history. Replaying a plan preserves
entity identity. Rebuild and run the checks above after applying a logical cohort;
keep canonical writes sequential while validating a checkpoint.
