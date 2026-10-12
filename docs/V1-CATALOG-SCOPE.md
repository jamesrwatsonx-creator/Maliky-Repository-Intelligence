# Practical searchable V1 scope

The owner's 2026-10-12 instruction narrows delivery to a useful capability catalog.
Preserve extraction, registry IDs, checkpoints and provenance. Discovery completeness
and source-inspection completeness are separate dimensions. Do not mark unreviewed
repositories or assets VERIFIED to satisfy catalog coverage.

Remaining delivery tasks:

1. Reconcile fresh owned inventory with existing records, including recent forks.
2. Make every public repository discoverable with description, categories and links;
   retain all extracted internal assets and their review status. Keep private identities
   and evidence outside the public checkout in ignored, access-controlled storage.
3. Expose capability/purpose, repository and category search and the existing composer
   through a minimal documented read-only JSON CLI usable by Hermes.
4. Test requirements-to-owned-recommendations, source links, gaps and an MVP plan.
5. Validate canonical references, indexes, privacy and tests; checkpoint this branch
   with a verified remote SHA. Do not modify main.

Advanced scoring, exhaustive semantic/security reviews, extensive relationship mapping
and a polished dashboard remain deferred. The old source-inspection COMPLETE gate is
preserved for source audit status; it is not the catalog delivery gate. Metadata-only
classification and lexical recommendations explicitly remain discovery evidence.

The CLI defaults to public records. Explicit `search --private-local` permits authorized
local access to ignored private README metadata. Existing private extracted catalogs are
not available in a fresh public clone and remain in their separately controlled environment.
No claim of private implementation verification or durable private catalog migration is made.
