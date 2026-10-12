# Practical V1 catalog scope and completion

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
