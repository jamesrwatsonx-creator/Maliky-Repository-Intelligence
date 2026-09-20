# Analysis helper inspection decisions

All nine public forks were inspected at pinned commits through read-only GitHub metadata and selected source blobs. Raw source stays in `.local/analysis/helper-inspection/`. No upstream code was copied into the implementation. ScanCode NOTICE was checked directly because the metadata API returned NOASSERTION. Truncated recursive trees for ScanCode and CodeQL are explicitly not claimed as full coverage.

| Helper | Pinned commit | Upstream | Mode | License |
|---|---|---|---|---|
| aider | `5dc9490bb35f9729ef2c95d00a19ccd30c26339c` | Aider-AI/aider | ADAPT ALGORITHM | Apache-2.0 |
| continue | `5522c6f44ca0ac3528b37244818fbfa39b5af470` | continuedev/continue | ADAPT ALGORITHM | Apache-2.0 |
| semgrep | `0516c0f23a3dceac5c8f5ff3fecd402af4450182` | semgrep/semgrep | SUBPROCESS ADAPTER | LGPL-2.1 |
| scancode-toolkit | `5e8448ecf2397c6eb7e7eb50326c8c880d9b598b` | aboutcode-org/scancode-toolkit | SUBPROCESS ADAPTER | Apache-2.0 AND CC-BY-4.0 |
| linguist | `ee4fb24d13cb21a0eb43b30b52f5cde17fbba8ae` | github-linguist/linguist | ADAPT ALGORITHM | MIT |
| repomix | `f444a651f7cd1ce17aa290b5c0df9bc730f350ab` | yamadashy/repomix | ADAPT ALGORITHM | MIT |
| codeql | `e7bc1c6fb69fab063bb862a57336c69dc33723d0` | github/codeql | REFERENCE IMPLEMENTATION ONLY | MIT |
| RepoAgent | `825d988127d7bfd757237d9c4e8678d9104030f0` | OpenBMB/RepoAgent | ADAPT ALGORITHM | Apache-2.0 |
| syft | `b49f0172f636fca01282eb12a411de6b0e26e633` | anchore/syft | SUBPROCESS ADAPTER | Apache-2.0 |

## analyzer:aider
Source: https://github.com/jamesrwatsonx-creator/aider/blob/5dc9490bb35f9729ef2c95d00a19ccd30c26339c/aider/repomap.py
Role: repository symbol/reference ranking. Runtime: Python; upstream tree-sitter/networkx omitted.
Independent reference-count ranking; not Aider PageRank. No chat/edit/LLM execution.

## analyzer:continue
Source: https://github.com/jamesrwatsonx-creator/continue/blob/5522c6f44ca0ac3528b37244818fbfa39b5af470/core/indexing/refreshIndex.ts
Role: content-addressed incremental indexing. Runtime: Python stdlib; no Continue service.
Reuse path/blob/algorithm-version artifacts; always rebind evidence to the inspected commit. No embedding backend.

## analyzer:semgrep
Source: https://github.com/jamesrwatsonx-creator/semgrep/blob/0516c0f23a3dceac5c8f5ff3fecd402af4450182/cli/src/semgrep/commands/scan.py
Role: structural candidate detection. Runtime: Separately installed Semgrep CLI.
JSON importer plus local rules and controlled static CLI runner. Rules remain candidates. CLI not installed on validation host.

## analyzer:scancode-toolkit
Source: https://github.com/jamesrwatsonx-creator/scancode-toolkit/blob/5e8448ecf2397c6eb7e7eb50326c8c880d9b598b/src/scancode/cli.py
Role: license and package evidence. Runtime: Separately installed ScanCode CLI and native dependencies.
Native JSON importer. Code Apache-2.0, data CC-BY-4.0, bundled third-party licenses vary. Never infer legal clearance.

## analyzer:linguist
Source: https://github.com/jamesrwatsonx-creator/linguist/blob/ee4fb24d13cb21a0eb43b30b52f5cde17fbba8ae/lib/linguist/blob_helper.rb
Role: language and generated/vendor classification. Runtime: Python stdlib fallback; Ruby/Rugged needed for native Linguist.
Conservative extension/header flags plus native JSON importer. Generated/vendor files remain visible. Not complete Linguist parity.

## analyzer:repomix
Source: https://github.com/jamesrwatsonx-creator/repomix/blob/f444a651f7cd1ce17aa290b5c0df9bc730f350ab/src/core/file/fileProcess.ts
Role: bounded semantic review context. Runtime: Python stdlib fallback; native Repomix requires Node >=22.
Bounded evidence packets plus XML importer; exact source remains canonical. No remote URL/package execution.

## analyzer:codeql
Source: https://github.com/jamesrwatsonx-creator/codeql/blob/e7bc1c6fb69fab063bb862a57336c69dc33723d0/python/ql/src/codeql-suites/python-security-and-quality.qls
Role: security/dataflow evidence. Runtime: Separately distributed CodeQL CLI, databases, query packs.
Selective SARIF importer only. This fork is queries/libraries, not CLI. No auto-build or target execution; binary license/eligibility must be checked before use.

## analyzer:repoagent
Source: https://github.com/jamesrwatsonx-creator/RepoAgent/blob/825d988127d7bfd757237d9c4e8678d9104030f0/repo_agent/file_handler.py
Role: Python AST declarations and syntactic call references. Runtime: Python stdlib; no LLM/documentation service.
Independent AST visitor; Python only, names may be ambiguous. No generated descriptions, source writes or automatic documentation.

## analyzer:syft
Source: https://github.com/jamesrwatsonx-creator/syft/blob/b49f0172f636fca01282eb12a411de6b0e26e633/syft/format/syftjson/model/document.go
Role: SBOM package inventory. Runtime: Separately installed Syft Go executable.
Native Syft JSON importer; optional CLI. No container pulling; normalize package identity without treating every package as a direct dependency.
