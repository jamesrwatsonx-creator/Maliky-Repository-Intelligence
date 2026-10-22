# Repository operating rules

Read `docs/CODEX-RESUME.md` first when it exists, then verify its summary
against `system/inspection-state.json` before continuing. Regenerate the resume
file from canonical state after every validated logical checkpoint.

Current delivery scope: docs/V1-CATALOG-SCOPE.md records the owner's 2026-10-21
repository-first V1 requirements. Repository summaries and capability clusters are
the primary search unit. Preserve all detailed records and verified/candidate distinctions.

Read docs/MASTER-SPECIFICATION.md and system/inspection-state.json before work.
Source repositories are read-only. Never execute inspected source code.
Only this intelligence repository may receive commits. Preserve prior records and caches.
Private repository names, IDs, paths, code and evidence belong only in .local/ (ignored).
Public records must pass fresh visibility verification before publication.
One canonical entity per repository/path/type/symbol; categories reference IDs.
Generated indexes are disposable views; registry records are authoritative.
Resume the first incomplete phase at the pinned inspected commit. A changed HEAD
preserves earlier evidence and queues a new revision; never erase it.
Practical V1 COMPLETE with completion_scope REPOSITORY_CLUSTERS_V1 requires pinned
source evidence, an accurate purpose, major capability clusters, important reusable
subsystems, asset-family observations, runtime/license/risk notes, classification,
reuse guidance and current search views. It does not require reading every source
file or splitting every component/endpoint/class. Ordinary repositories normally
need about 3-15 clusters, fewer when genuinely single-purpose or empty.
Detailed extraction/deep inspection is demand-driven after App Ideation selects
strong candidates. Historic detailed-census completion remains distinguishable.
Static detection is candidate evidence, never automatic asset verification.
Run python scripts/validate_registry.py and python -m unittest discover -s tests.
Run python scripts/build_indexes.py after canonical edits, then validate again.
Checkpoint logical batches and push without force; do not reset, clean or delete.
When a valid repository identity is introduced with language such as "forked",
"add", "intake" or "process", follow rules/new-repository-intake.md immediately.
