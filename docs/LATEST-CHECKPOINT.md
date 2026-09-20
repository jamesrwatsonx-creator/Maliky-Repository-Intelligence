# Recovery and current checkpoint

The canonical registry is recovered, checkpointed, searchable and ready for further
incremental ingestion. **The full semantic inventory is not complete.**

## Recovery result

The initial workspace had no checkout. Remote main contained only README.md at
`975418eedfafdb3fc55c323958eaa6b13a8ac457`. That README remains unchanged.

The later claimed 430 / 409 / 411 / 75,406 / 10,606 run was not recovered from
available local files. An older August 27 inventory survives unchanged: 278 owned
repositories, 278 tree cache records and 1,968 cached source files. Of these,
252 records still match currently public owned repositories; 6 legacy private
records and 20 records with no current public match remain isolated locally.
251 reusable repository caches yielded 1,668 blob-hash-verified files. Another
105 candidate files failed hash verification and were not trusted.

## Verified current scope

| Measure | Count |
|---|---:|
| Accessible repositories | 434 |
| Owned by jamesrwatsonx-creator | 434 |
| Owned forks | 404 |
| Public owned | 422 |
| Private owned, excluded from public details | 12 |
| Other accessible / private other-access | 0 / 0 |
| Complete nonempty source trees | 414 |
| Confirmed empty source repositories | 7 |
| Canonical registry itself, excluded from recursive ingestion | 1 |
| Verified source files processed | 25,225 |
| Canonical entity records | 6,925 |
| Reviewed entity records / candidates | 7 / 6,918 |
| Reviewed atomic capabilities | 6 |
| Search documents | 7,353 |
| Repositories passing full static review and census | 1 |

The entity records include 3,469 Skills, 1,597 agents, 997 UI components, 405 APIs,
209 packages, 94 CLIs, 84 workflows, 30 tools, 29 plugins, 9 MCP servers,
one service and one documentation asset. These are source-backed records; the
candidate label remains until semantic review confirms each classification.

## Implemented and checked

- 110 detailed categories, 25 operational categories, 35 entity types, Studio and
  Idea records, independent metadata and scoring vocabularies.
- Commit-pinned discovery, source hashes, resumable extraction, per-type censuses,
  stale-revision handling, private-data separation and publication checks.
- Normalized search, alias expansion, relationship graph, thirteen lookup indexes,
  dependency-aware output and a first-class composition recipe.
- Exact minimum provider count for up to 16 requirements and 60 viable providers;
  disclosed greedy fallback for larger problems. Unverified providers are excluded.
- Schema/reference/provenance/census/score validation and 18 passing tests.

Full raw source caches and complete raw tree manifests remain local and ignored.
The public evidence keeps read-file provenance, complete counts, full-tree hashes
and explicitly labelled previews of unread paths. This reduced the public
checkpoint from about 247 MB to about 34 MB without discarding recovered evidence.

## Review examples

The nine-file `andrej-karpathy-skills` repository has a reconciled census of one
canonical Skill, one plugin wrapper and one worked-example documentation asset.
Equivalent root-prompt and Cursor-rule versions reference the same Skill. Its ten
scores and qualitative B tier record the lack of behavioral benchmarks and a
standalone license file. COMPLETE describes the inspection, not production approval.

Voicebox's `stream_speech` generates a complete WAV before chunking its HTTP
response. The capability is therefore **generated WAV response delivery**, not
streaming inference. Its queued submission API has an explicit dependency edge
to the serial generation queue. Runtime behavior was not tested.

## What remains and exact resume point

Entity extraction, semantic review, scoring and mappings remain partial across the
broader inventory. 231 repositories are PARTIAL, 169 STRUCTURE_COMPLETE,
20 NEEDS_REVIEW (including the seven empty repositories), one COMPLETE and the
canonical registry itself DISCOVERED. All source repositories remained read-only.

Next: **semantic census review of `jamesrwatsonx-creator/voicebox`** at
`51f49dea198384b4eb6087b72c17057c6eb1c1cd`. Its 496 eligible text files were
already processed. Reuse the cached source and existing entities; inspect remaining
service/model/component definitions, reconcile its census, then review capabilities,
scores and mappings. Do not repeat its source download.

The machine-readable queue is [inspection-state](../system/inspection-state.json).
Usage and future one-repository intake are documented in [INGESTION](INGESTION.md)
and [QUERYING](QUERYING.md). The future hosted/OpenRouter UI is not implemented.

Durable checkpoints: foundation `2770cd2`, extraction and initial review `29fb40f`.
Further validation and documentation updates follow on main.
