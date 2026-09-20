# Claude Code Handoff

## Durable state

- Repository: `jamesrwatsonx-creator/Maliky-Repository-Intelligence`
- Branch: `main`
- Last validated durable checkpoint before this handoff: `e4c43e1` (previous session)
- Public repositories inventoried: **422**
- Processed and verified source files: **25,301**
- Active entities: **6,958** (Voicebox lean census excluded 52; codegraph review added 10 unlisted MCP server/tool entities)
- Verified entities: **27**
- Candidate entities: **6,931**

Active entity counts by type (after this session's Voicebox lean census):

| Type | Count |
|---|---:|
| `SKILL` | 3,469 |
| `AGENT` | 1,597 |
| `UI_COMPONENT` | 946 |
| `API` | 404 |
| `PACKAGE` | 209 |
| `CLI` | 94 |
| `WORKFLOW` | 84 |
| `DESIGN_REFERENCE` | 74 |
| `TOOL` | 39 |
| `PLUGIN` | 29 |
| `MCP_SERVER` | 11 |
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

## What was completed in the previous session (before this handoff)

The `docs/CLAUDE-CODE-HANDOFF.md` recorded the Voicebox lean census as pending with four remaining tasks:

1. Reconcile 123 HTTP route candidates
2. Review 118 UI component candidates
3. Review 4 Skills, 3 workflows, 7 packages
4. Score, map relationships and complete the independent census

## What was completed in this session

**Voicebox lean semantic census — COMPLETE**

Applied LEAN SEMANTIC REVIEW to all remaining Voicebox candidate families:

### API (HTTP routes): 123 detected → 122 retained

Excluded 1 entity: `health` from `backend/tests/test_cors.py` (test-file duplicate, not a real route).

All 122 real backend routes are retained. They represent the full REST integration surface of the Voicebox Python backend across 14 route modules:
`generations`, `profiles`, `stories`, `effects`, `history`, `captures`, `channels`, `models`, `tasks`, `settings`, `llm`, `mcp_bindings`, `cloud`, `health`.

### UI_COMPONENT: 118 detected → 67 retained

Excluded 51 entities (lean test: not useful to search, reuse, compare, compose, integrate, reference, replace, or extend):
- 1 constant misdetected as component (`MODEL_DISPLAY_NAMES`)
- 1 internal audio lifecycle hack (`AudioKeepAlive`)
- 6 implementation sub-fragments of `ListPane.tsx` (`ListPaneHeader`, `ListPaneScroll`, `ListPaneTitle`, `ListPaneSearch`, `ListPaneActions`, `ListPaneTitleRow`) — `ListPane` itself is retained
- 4 docs site scaffolding components (2 `Layout` routes, `ViewOptionsPopover`, `MarkdownCopyButton`)
- 10 landing page routes (`BlogIndexPage`, `CapturePage`, `CloudPage`, `DownloadPage`, `RootLayout`, `LinuxInstall`, `OgPreview`, `Home`, `PricingPage`, `TokenPage`)
- 26 landing marketing sections (`AgentIntegration`, `ApiSection`, `Banner`, `CaptureHero`, `DictationHero`, `CaptureSection`, `CapturesMockup`, `ControlUI`, `CopyAddress`, `DownloadSection`, `Features`, `Footer`, `Header`, `LandingAudioPlayer`, `Navbar`, `Personalities`, `LinuxIcon`, `WindowsIcon`, `AppleIcon`, `SupportedModels`, `Testimonials`, `TokenSection`, `TokenTeaser`, `TutorialsSection`, `VoiceCreator`)
- 4 generic landing UI primitives (`FeatureCard`, `Hero`, `SectionTitle`, `Section`)

Retained 67 voice-studio components across: audio playback/bars, capture/STT UI, effects chain, profile management, story/multi-clip editing, generation UI, model management, server settings, MCP bindings UI, and generic app framework.

### SKILL (4), WORKFLOW (3), PACKAGE (7), TOOL (4), MCP_SERVER (1), SERVICE (1): all retained

All entities in these types passed the lean test. Descriptions and valid capabilities were added where missing.

### Repository record updated (`registry/repositories/1243146740.json`)

- `capabilities`: set to 4 registered capability IDs (`voice-mcp-server-exposure`, `queued-speech-generation-submission`, `local-audio-transcription`, `voice-capture-history-discovery`, `voice-profile-discovery` — those that already exist in `registry/capabilities/`)
- `categories`: `[category:ai-applications, category:generative-ai, category:mcp-servers, category:desktop-applications, category:full-stack-applications]`
- `recommendation`: `USE DIRECTLY`
- `next_phase`: updated to `CAPABILITY_ANALYSIS` (lean census phase complete)
- `entity_count`: 209
- `entity_census`: catalogued counts updated (API: 122, UI_COMPONENT: 67)

### Indexes rebuilt and registry validated

`python scripts/build_indexes.py` rebuilt all search/capability/browse indexes.
`python scripts/validate_registry.py` returned `valid: true, errors: []`.

## Completed: codegraph lean semantic review (`f366222dbd6b7e43047072a9417289b1b02ae457`)

Retained 15 entities: 1 `MCP_SERVER` (`codegraph`), 9 `TOOL` (`codegraph_search/context/callers/callees/impact/node/explore/status/files`), 1 `CLI`, 1 `PACKAGE`, 2 `SKILL` (`add-lang`, `agent-eval`), 1 `WORKFLOW` (`Release`). The MCP server and its nine tools were missed by the declaration scan and were added from `src/mcp/*` (blob SHAs verified against `system/evidence/1247306274.json`). 13 capabilities were registered; the repository record is `USE DIRECTLY` with `next_phase: CAPABILITY_ANALYSIS`. Language extractors, framework resolvers, db/graph/search/sync internals and tests are implementation details. The source cache was absent, so the nine pinned files reviewed were fetched read-only via `gh api` at the pinned commit. Script: `scripts/review_codegraph_semantics.py`.

## Exact resume point: TradingAgents

The next repository in `system/inspection-state.json` is `jamesrwatsonx-creator/TradingAgents` (`NEEDS_REVIEW`, `SEMANTIC_CENSUS_REVIEW`, pinned `61522e103e61601c553b4544abcd53fa7ebf9f1d`). It is financial (trading), so it triggers scoped deep review under `rules/semantic-review.md`. Use `python scripts/build_semantic_review_packet.py` if a cache exists; otherwise read exact pinned files with `gh api` and follow the `scripts/review_codegraph_semantics.py` pattern.

Voicebox notes that are useful patterns for the next reviews:
- HTTP routes in a backend service: retain all real API routes, exclude test-file duplicates
- UI components: retain domain-specific components, exclude landing pages, docs scaffolding, marketing sections, internal sub-fragments from the same file where the composite is retained
- All capability IDs referenced by entities must exist as files in `registry/capabilities/`; do not invent capability IDs
- Valid recommendations are from `vocab['recommendations']`; `NEEDS DEEPER REVIEW` is always safe
- After lean census, run `python scripts/build_indexes.py` then `python scripts/validate_registry.py`; fix any errors before committing

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

Source repositories are read-only. The `.local/` directory does not exist in this session (source cache was not present). Use `python scripts/build_semantic_review_packet.py <repo>` to attempt to build a review packet from existing caches, but if the cache is missing use the entity records already in `registry/entities/` and the repository record as the evidence base for lean review.

```text
.local/cache/<github_id>/<commit>/
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
python scripts/build_semantic_review_packet.py jamesrwatsonx-creator/codegraph
```

`--max-files` creates a deliberately partial packet and cannot satisfy a census:

```powershell
python scripts/build_semantic_review_packet.py owner/repository --max-files 1000
```

`scripts/verify_publication_visibility.py` performs a fresh GitHub visibility check and may update local visibility evidence; run it only when a fresh remote verification is required.

## Known limits and work that must not restart

- Only one repository has completed semantic review; the remaining queue is intentionally preserved.
- Native analyzer executables are currently unavailable. Local fallbacks are the supported default.
- The `.local/` source cache is absent in this environment; lean review must proceed from entity records already in `registry/entities/` and the repository record.
- Analyzer output requires provenance and source-hash verification and remains evidence rather than canonical truth.
- Runtime behavior has not been executed for every verified entity; source review and exact pinned provenance are the current evidence level where recorded.
- External GitHub discoveries are candidates, not owned assets, until the user forks or imports them and normal ingestion completes.
- Capability IDs referenced in entity records must correspond to files in `registry/capabilities/`; do not add invented capability IDs.

Do **not** rerun discovery, redownload processed source, rebuild the registry, regenerate every repository, reset inspection states, reinstall every analyzer, add new analyzer systems, build the future frontend, add a vector database, add OpenRouter, or restart completed extraction and review. Resume at the repository named under "Exact resume point" above, then advance to the next repository recorded by `system/inspection-state.json` only after it passes its lean completion gate.
