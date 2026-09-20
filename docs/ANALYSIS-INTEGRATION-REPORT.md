# Analysis engine integration report

The analysis layer improves source review without changing the canonical registry
model. Its output is private, pinned evidence. Only a reviewer creates or verifies
canonical entities, capabilities, relationships and completion state.

## Helper decisions

All nine helper forks were inspected at pinned commits. `analysis/tools.yaml`
records each source, upstream, license, integration mode, runtime availability and
fallback. At this checkpoint all nine native executables are unavailable on the
validation host; all nine local fallbacks remain available. No installation
automation was added.

| Result | Count | Helpers |
|---|---:|---|
| Inspected | 9 / 9 | aider, continue, semgrep, scancode-toolkit, linguist, repomix, codeql, RepoAgent, syft |
| Integrated with an adapter or local fallback | 8 | aider, continue, semgrep, scancode-toolkit, linguist, repomix, RepoAgent, syft |
| Reference-only deep-analysis path | 1 | codeql, through optional pinned SARIF import |
| Native-runtime adapter failures | 0 | Native tools were not installed or requested |

The local fallbacks are: symbol/reference ranking inspired by Aider; content/path/
blob/version cache reuse inspired by Continue; conservative file classification
inspired by Linguist; bounded packets inspired by Repomix; and Python AST
definitions with same-file calls inspired by RepoAgent. Semgrep, ScanCode and Syft
have native-output importers and optional fixed-command runners. CodeQL never
builds a database or executes target code here; a separately prepared SARIF report
is the only import path.

## Representative evaluation

| Repository | Purpose | Scope | Candidate result | Packet reduction |
|---|---|---|---|---:|
| `voicebox` | saved semantic checkpoint | 500 cached text files, full eligible selection | 259 structural candidates; one MCP server was then found by semantic review | 98.38% |
| `pm-skills` | skill-heavy census | 140 cached text files, full eligible selection | 68 Skills, 9 plugins and 2 workflows, matching existing candidates | 86.26% |
| `babysitter` | MCP-heavy mixed monorepo | 9,121 cached text files, full eligible selection | 3,616 candidates, matching existing candidates | 99.91% |
| `hermes-agent` | UI/component-heavy repository | bounded 1,000 of 9,082 eligible files | 291 candidates; 8,082 files explicitly left for later review | 99.42% |
| `awesome-design-md` | design collection | all 76 cached text files | 74 distinct design references | 96.39% |
| `ECC` | large mixed monorepo | bounded 1,000 of 3,400 eligible files | 924 candidates; 2,400 files explicitly left for later review | 99.10% |

Candidate counts are not accuracy scores. The representative set has no independent
ground truth for a false-positive rate, so the report records it as unmeasured.
The bounded cases are validation samples, not census completion. They demonstrate
that a packet can focus review without pretending to have analysed every file.

## Resulting registry changes

- `awesome-design-md` now has 74 individually searchable `DESIGN_REFERENCE`
  records. Visual metadata comes only from each source document's description and
  says so in `visual_evidence`; no rendered appearance was inferred.
- Voicebox review added the missing `voicebox` MCP server and verified its four
  decorated tools. It also added source-backed capabilities for MCP exposure, local
  audio transcription, voice profile discovery and capture-history discovery.
- Voicebox remains `NEEDS_REVIEW`. Its 123 HTTP route candidates, 118 UI component
  candidates, four Skills, three workflows, seven packages, scores, mappings and
  independent census still require review.

The last fully reviewed repository remains `andrej-karpathy-skills`. The next
semantic-review work is the remaining Voicebox census at commit
`51f49dea198384b4eb6087b72c17057c6eb1c1cd`.

## Validation

The registry validator, 42 unit tests, index build and publication guard passed.
Private source, raw analyzer reports, packet contents and reusable file evidence
remain under ignored `.local/analysis/`.
