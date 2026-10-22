# Current status

## Active V1 checkpoint — 2026-10-21

The current strategy indexes each repository by pinned purpose, major capability
clusters, provenance, reuse guidance and tags. Existing detailed entity records
are preserved as bonus intelligence. The latest authenticated refresh reports 731
accessible/owned repositories (717 public, 14 private). The public manifest
contains 717 repositories, so inventory is reconciled; the refresh found no new
public repositories. Private identities and evidence remain local-only.

The canonical catalog has 653 repository-intelligence summaries complete, 57
DISCOVERED repositories, and 7 NEEDS_REVIEW empty-source dispositions. It contains
9,945 active entities (8,395 verified and 1,550 candidates), 2,402 capabilities,
13,064 search documents, 1,608 capability clusters and 1,633 repository/cluster
assignments. The pending queue is 64 repositories. This run completed 43
source-reviewed summaries across PRAW/social-research and mobile/Android cohorts,
without changing detailed entity records.

The latest 50-repository preparation attempt could not retrieve pinned source for
its selected cohort because GitHub REST connections were refused; those entries
remain uncompleted. The Git remote remains reachable. `gh auth status` reports an
invalid keyring token, although the repository discovery path completed this
refresh successfully. JEV decisions remain deferred where the decision engine is
unavailable. Resume from `docs/CODEX-RESUME.md` and
`system/inspection-state.json`; do not mark source-unavailable entries complete.
Registry, catalog, 73 unit tests and publication guard passed on 2026-10-22.

The historical sections below describe earlier checkpoints, not current counts.

## Verified interruption checkpoint — 2026-10-12

The latest completed recovery checkpoint before this work was `6297ad83e03872490c8440aa87b4c9e5e10178af` on `recovery/v1-rebuild`. An authenticated discovery refresh then completed and found 579 accessible repositories: 566 public and 13 private. The private identities and raw inventory remain under ignored `.local/`; the public manifest contains aggregate private counts only.

The refresh's bounded intake phase was stopped after `aider` completed its static source pass and while `continue` was being inspected. `aider` is pinned at `5dc9490bb35f9729ef2c95d00a19ccd30c26339c` with 12 unreviewed candidate assets. `continue` remains `DISCOVERED`; 38 unreviewed candidate entity files from `5522c6f44ca0ac3528b37244818fbfa39b5af470` are preserved but are not active in the search/catalog index because the repository inspection record and evidence manifest were not completed before interruption. No further repository pass was started.

The recovered public catalog reflects the current discovery and active registry: 566 repository records and 8,856 active assets, organized into 16 browse-by-type sections and 42 populated purpose sections across 389 Markdown browse pages. The current catalog readiness milestone is distinct from the historical semantic `COMPLETE` inspection state; no repository was mass-promoted.

Registry validation, catalog validation (4,832 local links), publication guard (13 private identifiers checked), and all 48 unit tests passed before checkpointing. See [the interruption handoff](docs/RECOVERY-HANDOFF-2026-10-12.md) for the exact resume pointer and remaining consistency notes.

## Recovery checkpoint

On 2026-10-12, workspace maintenance removed the checkout that contained the
locally validated V1 history through `e57ed8e1c812890ca8437d9628b6997dda3865e8`
and a later uncommitted batch. Exact object recovery was attempted before any
rebuild. No matching object, descendant, reflog, worktree, alternate object
database, bundle, archive or canonical-state snapshot was found.

The current working branch is `recovery/v1-rebuild`, rooted at published remote
commit `0728b37b50addec86aa1919467c971799bad8a49`. It is a reconstruction base,
not evidence that the lost local state was recovered. The prior workspace copy
is retained only as an obsolete source of scripts and deterministic evidence.
The surviving private `.local/` area is not copied, published or overwritten.

## Reconstructed first batch

The recovered pipeline completed its first deterministic live-source batch:
`jamesrwatsonx-creator/gauntlet-loop` reached `COMPLETE` from a pinned public
revision. Its entity, capability, search document, source evidence, and a
deferred decision record were rebuilt and passed validation. This confirms the
rebuild can now proceed in small checkpointed batches.

## Next safe action

Use `python scripts/run_bulk_intake.py --all --resume --limit 25 --priority
--snapshot` in small validated batches. Do not recreate state from historical
counts. After every validated logical checkpoint, run
`python scripts/create_checkpoint_bundle.py` when push is unavailable.
