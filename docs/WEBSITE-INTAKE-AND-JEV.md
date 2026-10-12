# Website intake and optional JEV decision adapter

Status: **implementation contract / staged integration**. This file does **not** claim that the website, an authenticated intake endpoint, or a TypeSafe deployment is live.

## Objective

Let the future Maliky website accept a GitHub repository URL, invoke the **existing** Repository Intelligence intake engine, and show newly discovered repositories and their meaningful reusable assets in the canonical browser/search catalog. Keep all canonical state and provenance in `registry/`; the website is only a client.

The independently available backend pieces already exist:

- `scripts/intake_repository.py`: normalize owned GitHub URL, register public repo, ingest source, prepare candidate entities, rebuild registry, validate.
- `scripts/refresh_catalog.py`: update discovery and derived views.
- `scripts/build_catalog.py` and `scripts/validate_catalog.py`: generate and check browse pages and public JSON.
- `scripts/search_catalog.py` and `scripts/registry.py compose`: read-only query and selection of verified capabilities.
- `docs/catalog/catalog.json`: **public-only, read-only** website consumption format.

Do **not** rewrite those components or duplicate the capability database.

## Required first website workflow

1. A **signed-in owner** enters a GitHub URL in **Add Repository**.
2. The backend validates that it is a normal `https://github.com/OWNER/REPO` URL without query, fragment, credentials, redirects to arbitrary hosts, or embedded shell syntax. The backend checks actual GitHub ownership and visibility, not just the string.
3. It returns an intake job ID promptly. Never run a potentially lengthy source scan in a synchronous web request.
4. A **single serialized backend worker** uses a current, isolated checkout/worktree of the authorized canonical branch and invokes `scripts/intake_repository.py` for a single public owned repository. Preserve uncommitted work; do not run alongside a Codex registry writer.
5. Use the existing conservative extraction flow. Existing assets remain canonical; newly identified assets preserve source repo, path, pinned revision and `VERIFIED` vs `NEEDS_REVIEW` distinction. For a large repo, support a cheap basic-description pass plus optional deferred deepening, without falsely marking unfinished extraction complete.
6. Run `scripts/build_catalog.py`, `scripts/validate_catalog.py`, registry validation and the private-data publication guard.
7. Prepare a normal Git checkpoint / reviewable proposed change. On publication, verify the actual remote SHA. Do not force-push or silently modify `main`. If the worker cannot safely publish, preserve the exact local state and return a review-required status.
8. The website refreshes its read-only generated catalog after a successful verified checkpoint. It shows the repository, actual extracted assets, updated topic listings and any unresolved candidates.

Existing `DISCOVERED` records remain visible in the catalog, but presence alone must never be represented as completed internal extraction.

## Future website API contract (not deployed yet)

The API is intentionally small and implementation-agnostic; a signed-in server or authorized agent may implement it later.

- `POST /api/intake` with `{"repository_url":"https://github.com/jamesrwatsonx-creator/example","mode":"normal"}` -> HTTP 202 `{"job_id":"...","status":"queued"}`.
- `GET /api/intake/{job_id}` -> `queued | inspecting | validating | review_required | published | failed`, with safe, redacted error/status details, processed counts and a verified commit only after publication.
- `GET /api/catalog` or direct static fetch of `docs/catalog/catalog.json` for public browse/search.
- App composition uses the existing catalog query/composition functions; it must not grant code-execution access to anonymous users.

No provider API key, GitHub write credential, raw private repository metadata or unredacted trace may be sent to the browser or included in the public catalog.

## Where JEV fits

**JEV is an optional backend decision provider, not a required component of browsing or intake.** Keep the deterministic classification/indexing path as the default, with no paid model dependency.

Relevant owned sources:

- `jamesrwatsonx-creator/Jev-For-Dummies`: an HTTP wrapper for TypeSafe **Choice**, **Noul**, and **Score**; useful as a reference for an adapter. Its example interface uses GET parameters containing the input text, which may appear in URL logs: do **not** send sensitive or private source text via those GET URLs.
- `jamesrwatsonx-creator/jev-ultrafast`: a separate browser-interaction agent using TypeSafe decisions and a small text model. It is **not** a generic bulk code-extraction or classification tool; do not deploy its browser harness to power basic catalog search.
- `jamesrwatsonx-creator/awesome-jev`: reference gallery, not a production runtime.

Potential optional classifications:

1. **Choice**: select one or more candidate topical categories supplied from the established taxonomy (validate selected IDs).
2. **Noul**: decide whether a description is sufficiently clear to avoid a more expensive analysis step, with conservative thresholds.
3. **Score**: rank *already retrieved* assets for an app requirement, without replacing evidence-backed search results.

JEV outputs are suggestions, **not evidence**. Never promote source candidates to VERIFIED based on a model score, confidence or probability. Record provider, timestamp, input digest, candidate set, result and whether a deterministic fallback was used. Require explicit opt-in and a server-side TypeSafe credential before enabling. Apply per-intake call and cost limits; stop and fall back to existing rules on failure or ambiguous judgment. No sending private repository contents without separately designed authorization and disclosure.

A TypeSafe API key is **not required to finish catalog V1 or launch basic website browsing**. Adding JEV incurs its own service usage and operational dependencies and is separate from a Codex/ChatGPT subscription.

## Release sequence

1. Finish and verify the current simplified catalog checkpoint. Reconcile the preserved interrupted `continue` evidence without re-running already completed discovery.
2. Implement authenticated, serialized, auditable website intake **around the existing CLI**. Unit-test owner/visibility checks, URL rejection, duplicate intake, retry, interrupted job, private-data guard, index refresh and publishing conflicts.
3. Test the website with one previously catalogued repo (idempotency) and one small, newly added public fork (new assets). Verify actual links and remote SHA.
4. Build the website's Library, Add Repository and Create Application views using the existing static export.
5. Add and measure optional JEV-assisted category triage **only if it materially improves coverage or reduces total cost**. Compare against deterministic baseline on labeled repositories; disable if it fails.

**Current boundary:** this document is an integration design committed on a separate feature branch to avoid modifying the active `recovery/v1-rebuild` checkpoint. It does not establish that the intake worker, website, TypeSafe connection, or plugin has been deployed.
