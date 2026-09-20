# Claude Code Handoff

## Durable state

- Repository: `jamesrwatsonx-creator/Maliky-Repository-Intelligence`
- Branch: `main`
- Current implementation commit when this handoff began: `7b00768ccaae88cd2e159bf975f1766209f218fe`
- Last validated durable checkpoint before the handoff documentation: `7b00768`
- Public repositories inventoried: **422**
- Processed and verified source files: **25,301**
- Active entities: **7,000**
- Verified entities: **12**
- Candidate entities: **6,988**

Active entity counts by type:

| Type | Count |
|---|---:|
| `SKILL` | 3,469 |
| `AGENT` | 1,597 |
| `UI_COMPONENT` | 997 |
| `API` | 405 |
| `PACKAGE` | 209 |
| `CLI` | 94 |
| `WORKFLOW` | 84 |
| `DESIGN_REFERENCE` | 74 |
| `TOOL` | 30 |
| `PLUGIN` | 29 |
| `MCP_SERVER` | 10 |
| `SERVICE` | 1 |
| `DOCUMENTATION_ASSET` | 1 |

`system/inspection-state.json` currently records:

| State | Repositories |
|---|---:|
| `COMPLETE` | 1 |
| `NEEDS_REVIEW` | 21 |
| `PARTIAL` | 231 |
| `STRUCTURE_COMPLETE` | 168 |
| `DISCOVERED` | 1 |

The only fully reviewed repository is `jamesrwatsonx-creator/andrej-karpathy-skills`, pinned at `2c606141936f1eeef17fa3043a72095b4765b9c2`.

## Review policy now in force

> The previous exhaustive semantic-review philosophy is superseded by LEAN SEMANTIC REVIEW by default.

> Do not revisit completed work merely because it predates the lean-review policy.

> The objective is to understand every meaningful reusable asset deeply enough for search, reuse, composition, capability coverage and capability-gap discovery — not to exhaustively explain every implementation detail.

The canonical lean and deep-review rules are in `rules/semantic-review.md`. The capability-gap and GitHub discovery policy is in `rules/capability-gap-discovery.md`.

## Exact resume point: Voicebox

The next repository in `system/inspection-state.json` is `jamesrwatsonx-creator/voicebox`:

- State: `NEEDS_REVIEW`
- Next phase: `SEMANTIC_CENSUS_REVIEW`
- Pinned commit: `51f49dea198384b4eb6087b72c17057c6eb1c1cd`
- Source files already read: **496**
- Catalogued entities: **260**

Verified Voicebox entities include:

- MCP server: `voicebox`
- MCP tools: `voicebox_speak`, `voicebox_transcribe`, `voicebox_list_captures`, `voicebox_list_profiles`
- APIs: `generate_speech`, `stream_speech`

Resume Voicebox with **LEAN SEMANTIC REVIEW**. The exact next semantic item is to reconcile the detected HTTP route candidates with the catalogue, retaining only routes that are meaningful searchable, reusable, composable, integrable, comparable, replaceable, or extensible assets. Do not deeply review every route.

Then apply the same lean test to the remaining Voicebox families:

- 123 detected HTTP route candidates, excluding tests and generated clients where appropriate;
- 118 UI component candidates, retaining meaningful reusable boundaries rather than implementation fragments;
- 4 Skills;
- 3 workflows;
- 7 packages;
- capability, relationship, score, Studio, Idea, and category mappings needed for retained meaningful entities;
- final count reconciliation and validation.

Voicebox must remain `NEEDS_REVIEW` until those lean requirements pass. Do not expand the semantic-review queue before completing it. Fetch exact pinned source from the existing cache when review packets are insufficient.

## Analysis adapters and fallbacks

The normalized evidence contracts, adapters, importers, local fallbacks, and representative validation are already present. Analyzer evidence is advisory and cannot write canonical records directly. Review does not depend on installing external executables.

| Helper | `available` | `unavailable` | `fallback_available` | `integration_mode` |
|---|---|---|---|---|
| Aider | `false` | `true` | `true` | `ADAPT ALGORITHM` |
| Continue | `false` | `true` | `true` | `ADAPT ALGORITHM` |
| Semgrep | `false` | `true` | `true` | `SUBPROCESS ADAPTER` |
| ScanCode Toolkit | `false` | `true` | `true` | `SUBPROCESS ADAPTER` |
| Linguist | `false` | `true` | `true` | `ADAPT ALGORITHM` |
| Repomix | `false` | `true` | `true` | `ADAPT ALGORITHM` |
| CodeQL | `false` | `true` | `true` | `REFERENCE IMPLEMENTATION ONLY` |
| RepoAgent | `false` | `true` | `true` | `ADAPT ALGORITHM` |
| Syft | `false` | `true` | `true` | `SUBPROCESS ADAPTER` |

Only add installation automation when a tool demonstrably improves review quality. Keep local fallbacks operational in all cases. See `analysis/tools.yaml` and `analysis/README.md` for the contracts and usage.

## Local and private evidence

Source repositories are read-only. Reuse exact pinned source and analysis evidence from these ignored local paths:

```text
.local/cache/<github_id>/<commit>/
.local/cache/1243146740/51f49dea198384b4eb6087b72c17057c6eb1c1cd/  # Voicebox
.local/analysis/
.local/evidence-manifests/
.local/legacy-profiles/
.local/history/
.local/discovery-private.json
.local/publication-visibility.json
```

Never publish those paths or raw private evidence. Public evidence manifests belong under `system/evidence/` and must contain only publication-safe provenance.

## Established commands

Run the smallest checks relevant to each change:

```powershell
python scripts/validate_registry.py
python -m unittest discover -s tests
python scripts/publication_guard.py
git diff --check
git status --short
```

Rebuild generated indexes only after canonical registry changes:

```powershell
python scripts/build_indexes.py
python scripts/validate_registry.py
```

Build a full semantic packet from already cached source:

```powershell
python scripts/build_semantic_review_packet.py jamesrwatsonx-creator/voicebox
```

`--max-files` creates a deliberately partial packet and cannot satisfy a census:

```powershell
python scripts/build_semantic_review_packet.py owner/repository --max-files 1000
```

Import a native analyzer report without making the native executable mandatory:

```powershell
python scripts/build_semantic_review_packet.py owner/repository --report semgrep VERSION .local/report.json
python scripts/run_analysis_tool.py jamesrwatsonx-creator/voicebox semgrep
```

`scripts/verify_publication_visibility.py` performs a fresh GitHub visibility check and may update local visibility evidence; run it only when a fresh remote verification is required.

## Known limits and work that must not restart

- Only one repository has completed semantic review; the remaining queue is intentionally preserved.
- Native analyzer executables are currently unavailable. Local fallbacks are the supported default.
- Analyzer output requires provenance and source-hash verification and remains evidence rather than canonical truth.
- Bounded semantic packets are incomplete by design.
- Runtime behavior has not been executed for every verified entity; source review and exact pinned provenance are the current evidence level where recorded.
- External GitHub discoveries are candidates, not owned assets, until the user forks or imports them and normal ingestion completes.

Do **not** rerun discovery, redownload processed source, rebuild the registry, regenerate every repository, reset inspection states, reinstall every analyzer, add new analyzer systems, build the future frontend, add a vector database, add OpenRouter, or restart completed extraction and review. Continue at the Voicebox resume point above, then advance to the next repository recorded by `system/inspection-state.json` only after Voicebox passes its lean completion gate.
