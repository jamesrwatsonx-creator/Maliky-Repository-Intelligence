# Current status

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
