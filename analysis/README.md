# Analysis evidence layer

Source cache → optional analyzers → normalized evidence → independent semantic
review → existing canonical registry. Analysis never writes canonical entities,
censuses, completion flags, scores or inspection queue state.

`tools.yaml` records all nine fork commits, upstreams, licenses and integration
decisions; it uses JSON syntax, a valid YAML 1.2 subset. See `INSPECTION.md` for
the actual modules read and limitations. No third-party implementation is vendored.

## Commands

From the repository root:

```
python scripts/build_semantic_review_packet.py jamesrwatsonx-creator/voicebox
python scripts/run_analysis_tool.py jamesrwatsonx-creator/voicebox semgrep
python scripts/build_semantic_review_packet.py owner/repo --report semgrep VERSION .local/report.json
```

All evidence, raw native reports, reusable file artifacts and packets are written
only below ignored `.local/analysis/`. Private inputs are supported by the Python
API but never registered publicly. The public CLI selects existing registry repos.
No command redownloads already inspected source. Missing cache entries and parser
failures are explicit coverage gaps. Source bytes are verified against Git blobs.

Native report import requires an envelope with `repository_id`, exact `commit`
and `payload` containing the original tool output. Import reports only from a
known pinned scan: the envelope is an assertion, not cryptographic proof of scanner
execution. All reported paths must belong to that pinned tree. Semgrep/ScanCode/
Syft/Linguist JSON, CodeQL SARIF 2.1.0 and Repomix XML are supported. Absolute
paths are rejected; configure the scanner to emit relative paths. Unsupported
formats fail per adapter without stopping local analysis. Native scanner errors
are retained as PARTIAL status, never presented as a clean scan.

## Optional runtime and fallbacks

- Aider concepts: reference-count repository map, with ambiguous symbols labelled.
- RepoAgent concepts: Python AST definitions and syntactic calls, without LLM calls
  or documentation writes. JavaScript/TypeScript exports use labelled heuristics.
- Continue concepts: repository/path/blob/algorithm content keys; unchanged files
  reuse artifacts, changed/deleted files rebuild the current view, old evidence stays.
- Linguist concepts: conservative language/generated/vendor flags. No file is
  discarded because of these flags. Native JSON can improve them.
- Repomix concepts: bounded UTF-8 review packet, with omissions and full evidence
  reference. Excerpts never replace exact source. No false token-count precision.
- Semgrep: local conservative candidate rules, JSON importer and opt-in static CLI.
- ScanCode/Syft: optional static CLI and native importers; dependencies deduplicate
  by ecosystem/name/version while keeping every source evidence ID. Version ranges
  are preserved separately from resolved versions. Inventory is not proof of a
  direct dependency. Manifest fallback does not claim full SBOM or license coverage.
- CodeQL: reference-only selective SARIF import. No database builds or target-code
  execution. Query repository license does not establish rights to the separate CLI.

The fixed CLI runner stages verified cached text, strips inherited credentials,
uses a clean home, disables known telemetry/update options, applies timeouts and
never installs packages or invokes build hooks. It is **not an OS network sandbox**;
private repositories cannot use it. CodeQL should be considered for authentication,
payments, health/private data, exposed network services, production candidates or
complex dataflow, with a separately prepared database and appropriate execution
isolation. Unavailable scanners leave existing review functional.

## Review and publication

Every finding has a stable evidence ID, tool/version, pinned source, provenance,
confidence and UNREVIEWED state. Deterministic findings remain candidates. Compare
overlapping symbol/dependency evidence, investigate disagreements, and create one
canonical entity per repository/path/type/symbol only after review. A packet does
not satisfy the independent census gate and cannot mark a repository COMPLETE.

Visual entity types are additive. `visual_style`, `layout`, `visual_features`,
`technologies` and `best_for` are searchable. Store `visual_evidence` showing whether
a tag comes from a source description or a rendered observation; do not invent
appearance from a filename. Canonical JSON files stay in their existing locations.
Type directories contain paginated links to those files, preserving individual
browsability without duplicating canonical records.

Run registry validation, unit tests, rebuild indexes and publication guard before
commits. Fresh visibility verification is required before publication. Raw analysis
never belongs in a public commit, even for currently public source.
