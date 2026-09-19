# Maliky Repository Intelligence

**What do I already own that can help build what I am imagining?**

A machine-readable capability intelligence system for the GitHub ecosystem curated by `jamesrwatsonx-creator`. A repository is a container: its internal Skills, MCP servers, tools, agents, packages, components and services are independent reusable entities with exact source provenance.

This is not a bookmarks list, a directory of README summaries, or an instruction to install every discovered project.

The model connects **Ideas ↔ Requirements ↔ Capabilities ↔ Entities ↔ Repositories**, with dependencies, infrastructure, Studios and composition recipes attached through typed references.

## Three independent dimensions

| Dimension | Question | Examples |
|---|---|---|
| Entity type | What IS it? | Skill, MCP server, component, SDK, model |
| Capability / category | What can it DO / what domain? | Screenshot hierarchy detection, voice cloning, CRM |
| Metadata | What attributes describe it? | Python, MIT, active, self-hosted, React, unreviewed security |

## Current coverage

See [`system/statistics.json`](system/statistics.json), [`system/discovery-manifest.json`](system/discovery-manifest.json) and [`system/inspection-state.json`](system/inspection-state.json) for exact counts and status. Discovery and structural extraction do **not** mean deep review is complete. Unknown scores and unsupported capabilities remain unset.

Authenticated connector discovery found **430 accessible repositories**, including **419 public and 11 private**, across pages of 100, 100, 100, 100, 30 and 0. This repository is public; private-source details are withheld from publication. Coverage refers to the active connection, not inaccessible repositories whose existence cannot be observed.

## Working with the registry

Python 3.11+:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python scripts/discover_repositories.py jamesrwatsonx-creator
# Use GITHUB_TOKEN in your environment for authenticated discovery:
python scripts/discover_repositories.py --all-accessible
python scripts/ingest_repository.py owner/repository
python scripts/reinspect_repository.py owner/repository
python scripts/build_indexes.py
python scripts/validate_registry.py
python scripts/report_status.py
python scripts/query_registry.py 'UI screenshot inspection'
python scripts/compose_idea.py idea:android-competitor-intelligence
```

The client makes GitHub GET requests only. It statically inspects source text; it does not install dependencies or execute repository code. Runtime behavior is unverified unless a separate review records otherwise. API failures remain visible and return failure status. Use `--offline` for cached evidence and `--max-files` only for an explicitly partial, resumable pass.

## Canonical records and generated views

| Location | Purpose |
|---|---|
| `registry/repositories/` | One profile per source repository |
| `registry/entities/` | First-class internal assets, one record per identity |
| `registry/capabilities/` | Atomic actions, synonyms and provider references |
| `registry/taxonomy/` | 110 seeded categories, 11 domain families, independent metadata vocabulary |
| `registry/studios/`, `registry/ideas/` | Multi-mapping destinations and product requirements |
| `registry/relationships/`, `registry/compositions/` | Evidence-backed edges and implementation recipes |
| `registry/indexes/` | Regeneratable lookup views across 13 dimensions |
| `MASTER-INVENTORY.json` | Lightweight repository overview |
| `CAPABILITY-GRAPH.json` | Normalized nodes and typed edges |
| `search/search-index.jsonl` | Normalized retrieval documents for a future app |
| `system/evidence/` | Source path/SHA coverage, unread files, parse errors and review candidates |

## Inspection and continuous ingestion

Discovery exhausts pagination. Inspection pins a commit, enumerates architecture, reads manifests and implementations, extracts explicit asset definitions, and records pending semantic review. An agent then verifies capabilities, scores, license implications, security, overlaps, complements and Studio/Idea mappings. Complete records require the deep-review checklist in `AGENTS.md`.

Scoring is evidence-based and independent for repositories and entities. An excellent internal Skill can exist in an otherwise weak repository. Fork identities remain traceable without counting unchanged upstream code as a separate implementation.

Capability search retrieves across entity types. Idea composition maps feature requirements to reviewed providers, compares alternatives and explicitly reports gaps. The initial composer uses a conservative set-cover heuristic; missing means **not established in the reviewed registry**, not necessarily absent from the account.

## Future application

The normalized JSONL index can feed SQLite, Postgres, a lexical search engine or later embeddings. A future OpenRouter interface can retrieve records and recommend architectures without parsing arbitrary files at query time. No graphical app, vector database or hosted model is required for the foundation.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`docs/INGESTION.md`](docs/INGESTION.md), [`docs/QUERYING.md`](docs/QUERYING.md) and [`docs/MASTER-SPECIFICATION.md`](docs/MASTER-SPECIFICATION.md).
