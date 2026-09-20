# Architecture

Canonical records live in registry/. Stable repository IDs use GitHub numeric IDs.
Entity IDs hash repository ID, exact path, type and declared symbol. Categories,
capabilities and descriptive metadata are independent. The 110 detailed categories,
25 operational categories and 35 entity types are reconstructed from the supplied
specification because no prior canonical taxonomy files were recovered.

Repository records hold resumable phases and entity censuses. Evidence manifests
record commit-pinned paths, blob hashes, successfully read files and unread paths.
Only the GitHub CLI GET client contacts source repositories. No source is executed.
The intelligence repository alone receives commits.

Search JSONL, inventory, graph and thirteen dimension indexes are derived views.
Capabilities have aliases and explicit provider IDs. Reviewed entities can be
selected by the idea composer; candidates cannot silently become recommendations.
The composer uses exact minimum provider count for up to 16 requirements and 60 viable providers, with an explicitly disclosed greedy fallback, and reports alternatives and gaps.
It does not claim runtime compatibility or optimal dependency closure.

## Trust and privacy

Private repository identities and source evidence remain in ignored .local/ storage.
Public discovery exposes aggregate private counts only. A visibility change blocks
publication until affected records have been reviewed and moved to private storage.
Legacy narratives are kept locally until separately reviewed. Public source text
is cached locally, while committed evidence contains paths and hashes, not snapshots.
Revisions remain in local history and previously published Git history.

## Deliberate limits

Detectors identify explicit skills, packages, CLIs, plugins, workflows, selected
agent manifests, MCP constructors/tool registrations, Python routes and exported
JSX components. They are not an exhaustive semantic parser. The remaining entity
types are supported as canonical records but require deeper inspection/adapters.
No repository is automatically COMPLETE merely because detectors ran. Static
verification does not establish production readiness or security.
