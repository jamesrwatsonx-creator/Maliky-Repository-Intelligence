# Claude Code Handoff

## Durable state

- Repository: `jamesrwatsonx-creator/Maliky-Repository-Intelligence`
- Branch: `main`
- Last validated durable checkpoint before this handoff: `e4c43e1` (previous session)
- Public repositories inventoried: **422**
- Processed and verified source files: **25,301**
- Active entities: **9,191** (net of lean-review exclusions and additions)
- Verified entities: **5,976**
- Candidate entities: **3,215**

Active entity counts by type (after this session's Voicebox lean census):

| Type | Count |
|---|---:|
| `SKILL` | 3,591 |
| `WORKFLOW` | 2,250 |
| `AGENT` | 1,610 |
| `UI_COMPONENT` | 850 |
| `API` | 402 |
| `PACKAGE` | 206 |
| `CLI` | 94 |
| `DESIGN_REFERENCE` | 74 |
| `TOOL` | 49 |
| `PLUGIN` | 29 |
| `COMPONENT` | 9 |
| `INTEGRATION` | 6 |
| `MCP_SERVER` | 6 |
| `CONNECTOR` | 4 |
| `AGENT_FRAMEWORK` | 2 |
| `SDK` | 2 |
| `SERVICE` | 2 |
| `DOCUMENTATION_ASSET` | 1 |
| `INFRASTRUCTURE_MODULE` | 1 |
| `LIBRARY` | 1 |
| `MODEL_ADAPTER` | 1 |
| `TEMPLATE` | 1 |

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

## Completed: TradingAgents lean semantic review (`61522e103e61601c553b4544abcd53fa7ebf9f1d`)

Retained 30 entities: 1 `AGENT_FRAMEWORK` (`TradingAgentsGraph`), 12 `AGENT` (4 analysts, bull/bear researchers, research manager, trader, 3 risk debaters, portfolio manager), 9 `TOOL` (LangChain data tools), 4 `CONNECTOR` (yfinance, Alpha Vantage, StockTwits, Reddit), 1 `MODEL_ADAPTER` (`create_llm_client`), 1 `COMPONENT` (`TradingMemoryLog`), `CLI`, `PACKAGE`. `create_social_media_analyst` is a deprecated alias and was excluded. 16 capabilities were registered. Scoped deep review (financial): no order placement, broker/exchange client, wallet or private-key code exists; output is an advisory five-tier rating, and the README says research use only. Residual risks: LLM keys via env vars, unauthenticated Reddit/StockTwits endpoints, non-deterministic LLM output. Relationships include ALTERNATIVE_TO AutoHedge/Vibe-Trading/AI-Trader/FinMem and COMPLEMENTS freqtrade/ccxt/hummingbot (all unreviewed peers). Script: `scripts/review_tradingagents_semantics.py`.

## Completed: uAgents lean semantic review (`9f6a18bd1e8356be834d6d6e78533c47c609e8d1`)

Retained 24 entities: `AGENT_FRAMEWORK` `Agent`, `AGENT` `ChatAgent`, 5 `COMPONENT` (`Bureau`, `Protocol`, `Dialogue`, `QuotaProtocol`, `ChitChatDialogue`), 6 `INTEGRATION` (MCP, A2A single/multi/inbound, LangChain, CrewAI adapters), 2 `SDK` (Agentverse A2A and LangGraph), 1 `INFRASTRUCTURE_MODULE` (Helm chart), 4 `PACKAGE`, 2 `CLI`, 2 `WORKFLOW` (CI, release). Removed 2 test-example `API` entities and 2 boilerplate workflows. 16 capabilities registered. Scoped deep review (keys/wallet): `get_or_create_private_keys` (`python/src/uagents/storage/__init__.py:130-150`) returns one wallet key but persists a different one, stores keys as plaintext `private_keys.json` in the cwd, and `Agent` defaults to `network="mainnet"`; the framework and repository are therefore `SECURITY REVIEW REQUIRED` (use the `seed` argument or an external key store for funded agents). Script: `scripts/review_uagents_semantics.py`.

## Completed: browser-harness lean semantic review (`41108b8676d4bdb58b26ab3b079c0b7b0f8f3926`)

Retained 133 entities (5 existing + 128 added): 123 `SKILL` (root skill, 104 domain-skill playbooks, 18 interaction-skill playbooks; each per-site file is its own searchable skill, description derived from its title and first paragraph; folder READMEs and companion `.py` scripts folded in), `CLI`, `PACKAGE`, `PLUGIN`, `WORKFLOW` (release), `LIBRARY` (`helpers`), `SERVICE` (`daemon`), 3 `COMPONENT` (`recorder`, `video`, `browser_use_cloud_auth`), `TEMPLATE` (`agent_helpers`). 13 capabilities registered; playbooks group under three capabilities (scraping, automation, interaction techniques). Scoped deep review: **telemetry is opt-out** and `run.py:251` sends the stdin script (up to 20,000 chars), stdout tail, steps and errors to PostHog EU, so the CLI, package and repository are `SECURITY REVIEW REQUIRED` until telemetry is disabled (`browser-harness telemetry disable` or `BH_TELEMETRY=0`). `profile-sync` and `cookies` skills are `SECURITY REVIEW REQUIRED` (real cookies to a cloud browser); account-acting and checkout skills carry a `sensitivity` metadata flag (checkout skills stop before purchase). Overlap: ALTERNATIVE_TO playwright-mcp, chrome-devtools-mcp, stagehand, browser-use, agent-browser (all unreviewed). Script: `scripts/review_browser_harness_semantics.py` (needs `BH_SOURCE_DIR` with the pinned files; blob SHAs are verified).

## Completed: babysitter lean semantic review (`d97a2e46a84cbc3ca4589050a9bddbcbf792a785`)

Retained 5,638 entities: 2,099 `SKILL`, 1,289 `AGENT`, 2,134 `WORKFLOW`, 76 `UI_COMPONENT`, 15 `TOOL`, 1 `MCP_SERVER`, 11 `PACKAGE`, 11 `CLI`, 2 `PLUGIN`. The declaration scan had missed the library's process definitions, so 2,131 JS files with an `@process` header (each with `@description`, `@inputs`, `@outputs`) were added as `WORKFLOW` entities (12 shared/helper JS files skipped); 3 CI workflows were kept. Bulk skills, agents and processes are grouped under 330 per-specialization capabilities (`babysitter-library-<area>-skills|agents|processes`). Removed 109 entities: 5 test-file MCP misdetections, 5 generic CI workflows, 80 UI route/layout/primitive/fragment/video components, and monorepo root, video and example packages. Scoped deep review: `run_create`/`run_iterate` load a process `entrypoint` with a dynamic `import()` (`packages/sdk/src/runtime/orchestrateIteration.ts`), so a connected MCP client can execute local JavaScript; the MCP server and those two tools are `SECURITY REVIEW REQUIRED`. Security-research and cryptography areas carry a `sensitivity` metadata flag. Script: `scripts/review_babysitter_semantics.py` (needs `BS_TARBALL`, the pinned tarball from `gh api repos/<repo>/tarball/<commit>`; blob SHAs are verified). Library skill/agent descriptions come from their frontmatter as previously extracted; they were not individually re-read.

## Completed: pm-skills lean semantic review (`18468a95b427e70e258b51389796367c6f684e7d`)

Retained 122 entities: 68 `SKILL`, 9 `PLUGIN`, 44 `WORKFLOW` (42 slash commands added from the `commands/` folders plus 2 CI workflows), 1 `TOOL` (`validate_plugins.py`, a plugin-collection validator added from source). 11 capabilities registered, one per PM plugin domain plus the validator. No deep-review triggers (prompt/markdown content only). Shared helper: `scripts/lean_review_lib.py` (`LeanReview`) now underlies new review scripts; script: `scripts/review_pm_skills_semantics.py` (needs `PM_TARBALL`).

## Completed: humanizer lean semantic review (`e2e92e7b4b8229253ed5c8e81dc65463fdeddda5`)

Retained 3 entities: the already-VERIFIED `SKILL` (unchanged), the `PLUGIN` manifest, and the `Check package` `WORKFLOW` (CI reference). `scripts/validate-package.py` and `agents/openai.yaml` are packaging details of this single skill and were not catalogued. 3 capabilities on the repository (two pre-existing writing capabilities plus the shared CI capability). Script: `scripts/review_humanizer_semantics.py`.

## Exact resume point: github-mcp-server

The next repository in `system/inspection-state.json` is `jamesrwatsonx-creator/github-mcp-server` (`NEEDS_REVIEW`, `SEMANTIC_CENSUS_REVIEW`, pinned `eb088dfe9d854dab6453a8d4ae5871a5ced20974`). The `.local/` cache is absent: read exact pinned files with `gh api -H "Accept: application/vnd.github.raw" "repos/<owner>/<repo>/contents/<path>?ref=<commit>"` (strip `` from path lists on Windows), follow the `scripts/review_*_semantics.py` pattern (set `PYTHONUTF8=1`), and check that new entity source paths exist in `files_read` with matching blob SHAs. Git needs a one-off identity: `git -c user.name=jamesrwatsonx-creator -c user.email=272351518+jamesrwatsonx-creator@users.noreply.github.com commit`.

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
