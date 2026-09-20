# Current verified status

Analysis acceleration is now checkpointed: nine helper forks have optional adapter
contracts, every helper records native availability and a local fallback, and raw
evidence remains private under `.local/analysis/`. The representative evaluation
created 74 individually searchable design-reference candidates and resumed the
Voicebox review. See [the integration report](docs/ANALYSIS-INTEGRATION-REPORT.md).

Voicebox remains `NEEDS_REVIEW` at `51f49dea198384b4eb6087b72c17057c6eb1c1cd`.
The MCP server and four exposed tools are verified; its remaining HTTP/UI/entity
census is the next semantic-review work.

Recovery and a searchable, resumable registry are checkpointed. Full semantic
review remains partial. Read the [checkpoint report](docs/LATEST-CHECKPOINT.md).

434 owned repositories: 422 public, 12 private. Public registry: 6,925 entity
records, 25,225 verified source files processed, six reviewed atomic capabilities.
Only one repository has passed the full static-review and census gate.

The original README is retained unchanged and describes historical uncommitted
coverage. Current counts are in [statistics](system/statistics.json); remaining
work is in [inspection-state](system/inspection-state.json).
