# Practical V1 catalog scope and completion

## Current owner directive — 2026-10-21

This directive supersedes the earlier exhaustive semantic-completion standard.
The primary unit is **repository + capability clusters**. Existing detailed
entities remain preserved and searchable as bonus intelligence.

For each repository, inspect bounded pinned evidence (README, package/skill/plugin
manifests, tree structure and strategically relevant source as needed). Record what
it actually does, primary/secondary capability areas, important top-level reusable
subsystems, major asset-family observations, runtime/language, upstream/revision/blob
provenance, license/risk notes, concise reuse guidance and useful search keywords.
Distinguish implementations from instructions, configuration, design-only material
and external references. NOT_OBSERVED means absent from bounded review, not a proof
of absence from every source file.

Practical completion is recorded as `completion_scope: REPOSITORY_CLUSTERS_V1`
and `repository_intelligence.status: COMPLETE`. It does not promote existing
candidate entities, erase detailed review state, claim production readiness, or
require exhaustive source reads and asset census reconciliation. A freshly
confirmed empty repository can be dispositioned without inventing a commit or
software capability. About 3–15 clusters suits ordinary repositories; avoid padding
single-purpose projects and do not invent clusters for empty repositories.

App Ideation searches/ranks repository summaries first. Deeply inspect the strongest
selected candidates only when a build needs exact components, APIs, Skills or MCPs.
An uninspected exact component is an on-demand inspection task, not a proven missing
capability. Risk notes guide that review; catalog completion is not deployment approval.

Use the existing `run_bulk_intake.py --repository-summaries` evidence preparation
and `review_extracted_batch.py --repository-plan` review application entrypoints.
Canonical source and review data stay in the existing registry/evidence architecture;
raw compact source packets remain ignored under `.local/analysis/repository-packets/`.

## Historical delivery scope

Catalog V1 is a lightweight, evidence-aware view over the existing Maliky registry. It prioritizes public inventory coverage, basic descriptions, searchable internal assets, provenance, browse navigation and a read-only agent workflow. It does not require exhaustive source review or change the meaning of historical inspection states.

## Delivered

- Authenticated inventory: 579 accessible repositories (566 public, 13 private); all 566 public repositories have canonical records and GitHub links.
- 8,856 active searchable assets remain individually represented. VERIFIED, CANDIDATE and historical records remain distinct and preserve canonical IDs and provenance.
- 16 asset-type sections, 42 populated purpose sections, 23 populated views over the established 25-area taxonomy, and 393 generated Markdown browse pages.
- Deterministic local JSON search, topic/type filtering, repository/category queries, read-only agent search, existing capability composition and requirements-to-MVP planning.
- Incremental refresh instructions, registry/catalog validation and private-publication checks.
- 19 repositories explicitly need better purpose descriptions because available evidence is insufficient; their records remain linked and discoverable without fabricated claims.

See [`CATALOG-DELIVERY.md`](CATALOG-DELIVERY.md) for current checks and exact usage examples, [`CATALOG-REFRESH.md`](CATALOG-REFRESH.md) for incremental updates, and [`AGENT-CATALOG.md`](AGENT-CATALOG.md) for the read-only interface.

## Preserved distinctions and privacy

Do not mark unreviewed repositories or assets VERIFIED to satisfy catalog coverage. Metadata-only classification and lexical search results are leads, not source verification. `NEEDS DESCRIPTION` is separate from historical `COMPLETE` inspection status. Private names, source code and evidence stay outside public artifacts; publication guard validation is required before publishing.

## Deferred by design

Universal deep review, exhaustive quality/security scoring, extensive relationship mapping, a hosted search service, dashboard polish and a dedicated agent plugin remain future work. Catalog ownership does not mean an asset is installed, compatible, secure, licensed for every use, or production-ready.
