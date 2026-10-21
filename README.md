# Verified recovery Git bundle

Exact validated checkpoint: `f103f0b801af24988dae4c7a45af2b1b3e0f6740`

Prerequisite durable recovery commit: `a5ebaaa128473dc6830223aa5289d615cb3c5dea`

SHA-256: `c8499f65e8001142513282fdc85b96278c440e0465e308a6510d9d10fa74a5f6`

This is a Git-history backup branch, not a registry or a branch to merge into main. It preserves the local recovery commits while shell push is unauthenticated and a 16 MiB connector limit blocks the generated catalog blob.

Restore from a clone containing the prerequisite (preserve any dirty work first):

```sh
git fetch origin checkpoints/v1-rebuild
git show origin/checkpoints/v1-rebuild:recovery.bundle > recovery.bundle
git bundle verify recovery.bundle
git fetch recovery.bundle recovery/v1-rebuild
git merge --ff-only FETCH_HEAD
```
