# New repository intake

A valid GitHub repository identity introduced with language such as **forked**,
**add**, **intake**, **process**, or **new repository** is an intake event. Do not
ask for another instruction. Run:

```sh
python scripts/intake_repository.py owner/repository
# or
python scripts/intake_repository.py https://github.com/owner/repository
```

The command is idempotent. It resolves ownership and visibility, keeps private
repository identifiers and evidence below `.local/`, captures fork provenance,
pins the inspected revision, reuses an existing canonical record where present,
and resumes the first incomplete phase. It never creates a second registry.

Use deterministic source evidence first: tree, manifests, declarations, pinned
blobs, documentation and dependency files. Extract an independent entity only
when it is useful to search for, reuse, compare, compose, integrate, reference,
replace or extend. Preserve repository, upstream, owner, exact path, blob SHA and
pinned revision. Similar implementations are alternatives, not duplicates.

The decision engine may make bounded routing decisions only when the supported
TypeSafe environment is available. Its results never create canonical facts. If
unavailable, record an auditable deferred decision and continue deterministic
work where source evidence is sufficient. Escalate low-confidence, missing or
conflicting evidence and narrow security, auth, financial, private-data, license,
destructive-execution or privileged-device risks.

After each intake: update relationships and affected indexes, validate the
registry, checkpoint machine state, and make a validated logical commit. Never
publish private source, paths, evidence, metadata or identities.
