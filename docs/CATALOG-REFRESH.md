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
