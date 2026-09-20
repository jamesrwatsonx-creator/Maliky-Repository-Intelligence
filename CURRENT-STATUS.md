# Current verified status

Lean semantic review has now been recorded for every repository that had reached the semantic
census queue: Voicebox, codegraph, TradingAgents, uAgents, browser-harness, babysitter, pm-skills,
humanizer, github-mcp-server, Google-skills, hermes-agent, ECC, Kimi-K3 and awesome-design-md,
in addition to karpathy-skills. Each is left at `NEEDS_REVIEW` with `next_phase: CAPABILITY_ANALYSIS`;
only karpathy-skills is `COMPLETE`. The declaration scan had missed real assets in several of them
(MCP servers and tools, registered agent tools, process workflows, slash commands, plugin
ecosystems); they were added from pinned source, and duplicates and implementation fragments were
removed. Security-relevant findings are recorded per repository under
`semantic_review_progress.scoped_deep_review`.

434 owned repositories: 422 public, 12 private. Public registry: 8,268 active entity records
(7,792 verified), 578 verified capabilities, 9,268 search documents, 25,301 verified source files
processed.

Still pending: 399 repositories awaiting entity extraction (`PARTIAL` or `STRUCTURE_COMPLETE`),
7 confirmed-empty repositories awaiting a disposition decision, and 1 repository awaiting
structure ingestion. See [the handoff](docs/CLAUDE-CODE-HANDOFF.md) for the exact resume point and
working method.

The original README is retained unchanged and describes historical uncommitted
coverage. Current counts are in [statistics](system/statistics.json); remaining
work is in [inspection-state](system/inspection-state.json).
