# Maliky Repository Intelligence

## Purpose

This repository is the canonical intelligence system for meaningful reusable assets across the user's repositories. It must answer what the user owns, where each asset lives, what it does, which capabilities and dependencies it has, whether it runs independently, what overlaps with it, how it maps to Studios, Ideas, and categories, which owned assets can compose a requested app or workflow, which capabilities are missing, and what targeted GitHub search could fill those gaps.

Before continuing any work, read [`docs/CLAUDE-CODE-HANDOFF.md`](docs/CLAUDE-CODE-HANDOFF.md).

## Preserve the canonical architecture

Do not replace, rebuild, or bypass:

```text
registry/
MASTER-INVENTORY.json
CAPABILITY-GRAPH.json
search/
system/inspection-state.json
analysis/
```

Reuse existing caches, evidence, schemas, taxonomy, identifiers, provenance, inspection states, and generated indexes. Do not restart completed discovery, extraction, or review.

## Review mode

Use **LEAN SEMANTIC REVIEW** by default. For each meaningful reusable entity, establish only:

1. identity and type;
2. exact source repository, path, and commit;
3. what it actually does;
4. capabilities;
5. dependencies;
6. standalone status: `YES`, `NO`, or `PARTIAL`;
7. meaningful overlap, duplicate, alternative, or complement;
8. category, Studio, and Idea mappings where relevant;
9. recommended use: `USE DIRECTLY`, `EXTRACT`, `WRAP`, `COMBINE`, `REFERENCE`, `SUPERSEDED`, or `IGNORE FOR BUILD COMPOSITION`.

Do not deeply analyze every implementation detail. Escalate to deep review only when lean evidence is insufficient or the asset is security-sensitive, strategically critical, materially ambiguous, financial, authentication-related, private-data-related, or otherwise risky. Follow [`rules/semantic-review.md`](rules/semantic-review.md).

## Entity principle

Every meaningful reusable asset remains independently searchable. If there are 6,000 legitimate Skills, preserve approximately 6,000 searchable Skill records. Apply the same principle to MCPs, agents, APIs, workflows, components, models, design references, websites, and other supported types.

Use this test: **Would this asset be useful to search for, reuse, compare, compose, integrate, reference, replace, or extend?** If yes, preserve it as a meaningful entity. If no, it may remain an implementation detail.

## Capability-first composition

```text
Idea
-> features
-> required capabilities
-> search owned registry
-> compose owned assets
-> determine coverage: COVERED / PARTIALLY_COVERED / MISSING
```

Search owned assets first. If a capability remains missing or materially weak, run a targeted GitHub search and create an `EXTERNAL_CANDIDATE` after lightweight evaluation. External results are never owned automatically; the user may choose to fork or import one, after which it follows normal ingestion. Follow [`rules/capability-gap-discovery.md`](rules/capability-gap-discovery.md).

## Analysis helpers and safety

Aider, Continue, Semgrep, ScanCode Toolkit, Linguist, Repomix, RepoAgent, Syft, and CodeQL provide supporting evidence only. Their output is never canonical truth, and review must continue through local fallbacks when native executables are unavailable.

Do not execute arbitrary repository code unnecessarily, expose credentials, publish private source or raw evidence, modify source repositories, install every analyzer runtime, or force-push. Commit and push small validated checkpoints to `main`.
