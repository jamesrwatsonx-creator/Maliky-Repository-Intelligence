# Ingestion and recovery

Requirements: Python 3.11+, Git and authenticated GitHub CLI (`gh auth login`).
No dependency installation or source execution is required.

```sh
python scripts/discover_repositories.py jamesrwatsonx-creator
python scripts/ingest_repository.py jamesrwatsonx-creator/REPOSITORY --structure-only
python scripts/ingest_repository.py jamesrwatsonx-creator/REPOSITORY --max-files 100
python scripts/ingest_repository.py jamesrwatsonx-creator/REPOSITORY --offline
python scripts/build_indexes.py
python scripts/validate_registry.py
python -m unittest discover -s tests
```

`--max-files` counts additional files this run, never total allowed entities.
It deliberately leaves a partial checkpoint. Repeated invocations skip already
read blob hashes at the inspected commit. Omitting it processes all eligible text.
`--offline` only uses commit-pinned, hash-verified cached source; it never asserts
freshness against current remote HEAD. `--structure-only` inventories paths without
claiming semantic extraction. A changed HEAD archives prior state locally and
keeps old records until new evidence is available. No destructive Git commands.

For continuous ingestion, run discovery and inspect only new/changed repositories.
The batch runner (`python scripts/registry.py batch --structure-only --workers 4`)
persists each repository independently. Exit status is nonzero for fetch failures.
The canonical intelligence repo is excluded from broad batches to avoid recursive
indexing; it may be inspected explicitly. Rebuild indexes after interruptions.

Before COMPLETE, a reviewer must reconcile every first-class entity type against
architecture, manifests, registries, source definitions and exports. The census
must be independently reviewed, not inferred from successful extraction alone.
Confirm source coverage and record capabilities, dependencies, all ten justified
scores, tier rationale, mappings when supported, and deep-review evidence.
Unresolved census discrepancies must remain PARTIAL or NEEDS_REVIEW.

Checkpoint with explicit paths, validate and push ordinary fast-forward commits.
Run the publication guard before staging. Never stage .local/, secrets or snapshots.

Use `--snapshot` to stream a public commit archive into the local content-addressed
cache. No archive member is extracted as an executable path. Files above 10 MB
are left to individual blob ingestion. Truncated GitHub trees use a bare filtered
Git fetch at the exact commit. Raw manifests stay local; public previews carry
explicit full counts and a tree-manifest hash.
