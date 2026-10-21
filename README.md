# Verified recovery Git bundle

Exact local checkpoint: `13e7ef9c9ae159353bbc7729e0059fa541344458`

Prerequisite remote recovery commit: `a5ebaaa128473dc6830223aa5289d615cb3c5dea`

SHA-256: `dafc41e9dd5a6f5e77d16c1172fa83244e55c4af5a949507152b4fcca30c2a7f`

This backup branch is not a registry and must not be merged into main. It preserves exact local history while shell Git cannot push and the connector cannot upload the oversized generated catalog blob.

Restore in a clone containing the prerequisite:

```sh
git fetch origin checkpoints/v1-rebuild
git show origin/checkpoints/v1-rebuild:recovery.bundle > recovery.bundle
git bundle verify recovery.bundle
git fetch recovery.bundle recovery/v1-rebuild
git merge --ff-only FETCH_HEAD
```
