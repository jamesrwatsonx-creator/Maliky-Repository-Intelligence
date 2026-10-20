# Repository operating rules

Read `docs/CODEX-RESUME.md` first when it exists, then verify its summary
against `system/inspection-state.json` before continuing. Regenerate the resume
file from canonical state after every validated logical checkpoint.

Current delivery scope: docs/V1-CATALOG-SCOPE.md records the owner's narrowed
2026-10-12 V1 catalog requirements. Repository discoverability is independent of
the source-inspection COMPLETE gate below. Preserve verified/candidate distinctions.

Read docs/MASTER-SPECIFICATION.md and system/inspection-state.json before work.
Source repositories are read-only. Never execute inspected source code.
Only this intelligence repository may receive commits. Preserve prior records and caches.
Private repository names, IDs, paths, code and evidence belong only in .local/ (ignored).
Public records must pass fresh visibility verification before publication.
One canonical entity per repository/path/type/symbol; categories reference IDs.
Generated indexes are disposable views; registry records are authoritative.
Resume the first incomplete phase at the pinned inspected commit. A changed HEAD
preserves earlier evidence and queues a new revision; never erase it.
V1 COMPLETE requires a full tree, reconciled lean semantic census, verified
provenance, meaningful capabilities and current generated indexes. The ten legacy
scores, tier rationale and universal deep review are not V1 completion gates.
Deep review is scoped and required only for a recorded risk or ambiguity trigger;
see rules/semantic-review.md.
Static detection is candidate evidence, never automatic semantic completion.
Run python scripts/validate_registry.py and python -m unittest discover -s tests.
Run python scripts/build_indexes.py after canonical edits, then validate again.
Checkpoint logical batches and push without force; do not reset, clean or delete.
When a valid repository identity is introduced with language such as "forked",
"add", "intake" or "process", follow rules/new-repository-intake.md immediately.
