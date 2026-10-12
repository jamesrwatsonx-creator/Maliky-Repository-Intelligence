# Practical catalog delivery — 2026-10-12

Baseline: `6297ad83e03872490c8440aa87b4c9e5e10178af`, branch `recovery/v1-rebuild`.
Fresh authenticated owner inventory: 579 repositories, 566 public and 13 private.
Public owner REST pagination was exhausted and reconciled with that inventory.
Added 144 public repository records without restarting extraction or deleting records.

Preserved 8,844 independently searchable extracted assets: 7,894 VERIFIED and
950 candidates. Existing canonical provenance, source audit states and composition
remain intact. All public repositories now have descriptions, category routing and
source links. Empty repositories are described explicitly. General / Other is used
when more specific lightweight classification is not established.

`scripts/catalog_agent.py` is a standard-library read-only JSON CLI for capability
and purpose search, repository/category filters, existing composition and a requirements
planner. See AGENT-CATALOG.md. No hosted service, LLM API or dashboard is required.
Private README metadata is ignored locally and available only with explicit local
search; it is not present in public GitHub checkpoints. Durable private catalogs and
private asset extraction remain in separately authorized storage/environments.

The tested speech app workflow maps queued speech-generation submission and serial
speech-job scheduling to one verified provider; appointment booking remains an explicit
evidence gap. `system/catalog-workflow-test.json` contains the recommendations,
provenance, missing requirements and MVP steps. Lexical leads are not proof of coverage.

Validation: canonical registry validator, all 54 unit tests and publication guard pass.
The publication guard checks all 13 known private repository identities. No source
repository was changed. Source audit queues remain pending independently of this
catalog delivery; metadata coverage does not assert exhaustive implementation verification.

Later: enrich broad categories where useful; incrementally inspect new forks; add
runtime compatibility evidence, richer requirements mapping, hosted authenticated API,
advanced scoring or dashboard only when an actual workflow needs them.
