# Recovery Git-history checkpoint

This backup branch holds a verified incremental Git bundle. It is not a replacement registry or a branch to merge into main.

Checkpoint: `f2bbae858af9a07818a09e63e2ef2758c7a09af5`
Prerequisite durable recovery commit: `a5ebaaa128473dc6830223aa5289d615cb3c5dea`
SHA-256: `f5b9dee4d63921b5b6c9b3453206e5a1aab92de075b43dda2970e3fcace58319`

Restore from a clone containing the prerequisite commit:

```sh
git fetch origin checkpoints/v1-rebuild
git show origin/checkpoints/v1-rebuild:recovery.bundle > recovery.bundle
git bundle verify recovery.bundle
git fetch recovery.bundle recovery/v1-rebuild
git merge --ff-only FETCH_HEAD
```

The canonical recovery branch was not force-updated. Shell push credentials were unavailable; the connector has a 16 MiB per-request limit that blocks the full generated catalog blob. This bundle preserves the exact validated local Git commit and its changes.
