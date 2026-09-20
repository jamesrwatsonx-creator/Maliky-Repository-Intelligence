# Semantic Review Policy

## Lean review is the default

Review each meaningful reusable entity only deeply enough to establish:

1. **Identity:** stable name and entity type.
2. **Provenance:** exact source repository, path, inspected commit, and supporting evidence.
3. **Actual function:** a source-supported account of what the entity does.
4. **Capabilities:** the useful outcomes it provides.
5. **Dependencies:** material runtime, service, framework, model, data, and parent-system requirements.
6. **Standalone status:** `YES`, `NO`, or `PARTIAL`, with a short reason when the answer is not obvious.
7. **Meaningful overlap:** duplicates, alternatives, superseded assets, and complementary assets that affect selection or composition.
8. **Mappings:** relevant category, Studio, and Idea relationships.
9. **Composition use:** one of `USE DIRECTLY`, `EXTRACT`, `WRAP`, `COMBINE`, `REFERENCE`, `SUPERSEDED`, or `IGNORE FOR BUILD COMPOSITION`.

An implementation detail becomes an entity only when it would be useful to search for, reuse, compare, compose, integrate, reference, replace, or extend. Normal completion does not require exhaustive route, function, class, file, or line-by-line analysis.

Prefer exact pinned source and existing local evidence. Analyzer output may strengthen evidence, but it does not replace source verification or write canonical truth. When a packet is insufficient, read the exact source from the existing pinned cache rather than redownloading or executing the repository.

## Deep review only when needed

Escalate from lean review when any of these conditions applies:

- material ambiguity;
- conflicting evidence;
- security-sensitive behavior;
- authentication or authorization;
- payments, wallets, trading, or other financial behavior;
- private or sensitive data;
- core Hermes or Maliky infrastructure;
- a strategic shared component;
- source behavior contradicts documentation;
- lean evidence cannot establish the capability safely.

Deep review is scoped to the uncertainty or risk that triggered it. It does not convert the whole repository to exhaustive review.

## Completion

Reconcile detected and catalogued counts by entity family, recording why candidates were retained, merged, excluded, or treated as implementation details. A repository completes semantic review when every meaningful reusable entity meets the lean fields above, triggered deep reviews are resolved, relationships and mappings are valid, generated indexes are current, and the established validation and publication checks pass.

Do not reopen completed work merely because it predates this policy. Resume the queue from `system/inspection-state.json` and preserve pinned commits and prior validated evidence.
