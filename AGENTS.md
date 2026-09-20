# Repository operating rules

Read docs/MASTER-SPECIFICATION.md and system/inspection-state.json before work.
Source repositories are read-only. Never execute inspected source code.
Only this intelligence repository may receive commits. Preserve prior records and caches.
Private repository names, IDs, paths, code and evidence belong only in .local/ (ignored).
Public records must pass fresh visibility verification before publication.
One canonical entity per repository/path/type/symbol; categories reference IDs.
Generated indexes are disposable views; registry records are authoritative.
Resume the first incomplete phase at the pinned inspected commit. A changed HEAD
preserves earlier evidence and queues a new revision; never erase it.
COMPLETE requires full tree, reconciled independently reviewed census, verified
provenance, capabilities, all ten justified scores, tier rationale and deep review.
Static detection is candidate evidence, never automatic semantic completion.
Run python scripts/validate_registry.py and python -m unittest discover -s tests.
Run python scripts/build_indexes.py after canonical edits, then validate again.
Checkpoint logical batches and push without force; do not reset, clean or delete.
