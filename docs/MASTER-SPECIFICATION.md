# MALIKY REPOSITORY INTELLIGENCE

## RECOVERY, CHECKPOINT, RESUME, AND COMPLETION MASTER PROMPT

You are operating inside the existing canonical repository:

`jamesrwatsonx-creator/Maliky-Repository-Intelligence`

This is NOT a fresh initialization.

A previous Codex run performed substantial repository discovery, source inspection, structural extraction, and entity extraction, but most of that work may exist only in the local workspace and may not have been committed to GitHub.

Your first responsibility is therefore:

**RECOVER → VERIFY → CHECKPOINT → RESUME**

Do NOT restart completed work.

Do NOT discard partial work.

Do NOT assume GitHub HEAD represents everything produced by the previous run.

Do NOT run destructive Git commands.

Do NOT use `git reset --hard`, `git clean`, destructive checkout commands, or delete untracked files.

---

# 1. KNOWN REMOTE GITHUB STATE

At the beginning of this recovery task, the known remote state is:

Repository:

`jamesrwatsonx-creator/Maliky-Repository-Intelligence`

Known remote branch:

`main`

Known remote commit:

`975418eedfafdb3fc55c323958eaa6b13a8ac457`

Known remote commit message:

`Initialize Maliky Repository Intelligence purpose and operating model`

At that remote commit, only `README.md` was committed.

Files referenced by the README such as:

```text
AGENTS.md
MASTER-INVENTORY.json
CAPABILITY-GRAPH.json
system/statistics.json
system/discovery-manifest.json
system/inspection-state.json
registry/
schemas/
scripts/
search/
docs/
```

were NOT verified as committed to remote GitHub.

Therefore, inspect the LOCAL working tree before doing anything else.

---

# 2. HISTORICAL PREVIOUS-RUN CHECKPOINT

The previous run reported approximately:

```text
Accessible repositories discovered: 430
Public repositories: 419
Private repositories: 11

Public repository snapshots retrieved: 409

Nonempty public repository trees reported complete: 411

Source files read: 75,406

Extracted asset/entity records with repository/path/commit provenance:
10,606
```

The previous run also reportedly created or began creating:

* 110 detailed taxonomy categories
* approximately 35 entity types
* Studio records
* Idea records
* schemas
* validation tooling
* repository inspection infrastructure
* source snapshots/caches
* provenance records
* structural extraction records

However:

**These historical numbers are recovery hints, not automatically authoritative truth.**

Verify them against actual local files.

If local artifacts support them, preserve them.

If local artifacts contradict them, trust the artifacts and report the discrepancy.

If the artifacts are gone, explicitly state that the previous work cannot be recovered rather than pretending that it still exists.

---

# 3. FIRST ACTION: RECOVERY AUDIT

Before discovery, ingestion, or repository inspection, inspect the current local workspace.

Determine:

```text
current branch
HEAD commit
remote configuration
git status
tracked files
modified files
staged files
untracked files
ignored files
local branches
local commits not pushed
stashes if any
generated registry files
cached repository snapshots
inspection state
discovery manifests
entity records
capability records
source evidence
temporary inspection output
logs
errors
partial records
```

Inspect the entire workspace structure.

Do not assume untracked files are disposable.

Untracked files may contain the majority of the previous run.

---

# 4. RECOVERY REPORT

Before resuming large-scale work, produce a concise factual checkpoint report.

Report:

```text
REMOTE HEAD:
LOCAL HEAD:

LOCAL AHEAD/BEHIND:

TRACKED CHANGES:
UNTRACKED FILES:

RECOVERED DISCOVERY MANIFEST:
yes/no

RECOVERED INSPECTION STATE:
yes/no

RECOVERED REPOSITORY RECORDS:
<count>

RECOVERED ENTITY RECORDS:
<count>

RECOVERED SKILLS:
<count>

RECOVERED MCP SERVERS:
<count>

RECOVERED AGENTS:
<count>

RECOVERED TOOLS:
<count>

RECOVERED COMPONENTS:
<count>

RECOVERED SERVICES:
<count>

RECOVERED APIS/SDKS:
<count>

RECOVERED MODELS:
<count>

RECOVERED CAPABILITIES:
<count>

RECOVERED SOURCE SNAPSHOTS:
<count>

RECOVERED SOURCE FILES:
<count>

LAST CONFIRMED COMPLETED PHASE:

PARTIAL PHASE:

NEXT SAFE STEP:
```

Do not estimate values that can be calculated.

---

# 5. DO NOT RESTART COMPLETED REPOSITORY INSPECTIONS

This rule is mandatory.

For every repository, recover and examine its existing inspection state.

Possible states include:

```text
NOT_STARTED
DISCOVERED
QUEUED
IN_PROGRESS
PARTIAL
STRUCTURE_COMPLETE
ENTITY_EXTRACTION_COMPLETE
CAPABILITY_ANALYSIS_COMPLETE
DEEP_REVIEW_COMPLETE
COMPLETE
STALE
ACCESS_RESTRICTED
FAILED
NEEDS_REVIEW
```

If an inspection is already valid for the repository's current inspected commit:

**DO NOT RESTART IT.**

Resume only the incomplete phase.

Examples:

```text
STRUCTURE_COMPLETE
→ continue with entity extraction

ENTITY_EXTRACTION_COMPLETE
→ continue with capability analysis

CAPABILITY_ANALYSIS_COMPLETE
→ continue with semantic/deep review

DEEP_REVIEW_COMPLETE
→ continue with scoring/relationships/validation
```

If the source repository HEAD has changed since `inspected_commit`, evaluate whether reinspection is required.

Do not automatically throw away valid prior evidence.

---

# 6. ENTITY CENSUS COMPLETION GATE

This requirement is critical.

A repository is a container.

A repository is NOT automatically one capability.

One repository may contain:

```text
25 Skills
7 MCP servers
4 agents
15 tools
30 UI components
8 workflows
6 services
3 SDKs
models
prompts
connectors
infrastructure
```

Every meaningful first-class internal asset must be independently catalogued.

Before a repository can receive `COMPLETE`, produce an entity census.

Example:

```yaml
entity_census:
  skills:
    detected: 25
    catalogued: 25

  mcp_servers:
    detected: 7
    catalogued: 7

  agents:
    detected: 4
    catalogued: 4

  tools:
    detected: 15
    catalogued: 15

  components:
    detected: 30
    catalogued: 30
```

If:

```text
detected != catalogued
```

the repository MUST remain:

```text
PARTIAL
```

or:

```text
NEEDS_REVIEW
```

Do not sample 5 Skills from a repository containing 25 and declare the repository complete.

---

# 7. DEEP INSPECTION REQUIREMENT

README-only analysis is prohibited.

For every repository, inspect enough of its architecture to determine what it really contains.

Inspect when present:

```text
README*
docs/
src/
lib/
packages/
apps/
services/
skills/
agents/
.agent/
.agents/
mcp/
mcps/
servers/
tools/
plugins/
extensions/
components/
workflows/
prompts/
models/
connectors/
integrations/
api/
sdk/
scripts/
infra/
infrastructure/
docker/
deploy/
examples/
tests/
.github/
```

Inspect manifests and configuration such as:

```text
package.json
pnpm-workspace.yaml
yarn workspaces
pyproject.toml
requirements.txt
uv.lock
Cargo.toml
go.mod
build.gradle
settings.gradle
pom.xml
Dockerfile
docker-compose*
MCP manifests
Skill manifests
plugin manifests
model configs
agent configs
exports
entry points
API route definitions
```

Do not depend entirely on directory names.

Internal assets may be defined through code, registries, manifests, imports, exports, decorators, configuration, or documentation.

---

# 8. FIRST-CLASS ENTITY TYPES

Support at minimum:

```text
REPOSITORY
SKILL
MCP_SERVER
MCP_CLIENT
TOOL
PLUGIN
AGENT
AGENT_FRAMEWORK
WORKFLOW
COMPONENT
UI_COMPONENT
MOBILE_COMPONENT
DESIGN_SYSTEM
PROMPT
PROMPT_LIBRARY
SERVICE
API
SDK
LIBRARY
PACKAGE
MODEL
MODEL_ADAPTER
DATASET
BENCHMARK
DATABASE
CONNECTOR
INTEGRATION
AUTOMATION
CLI
APP
INFRASTRUCTURE_MODULE
TEMPLATE
REFERENCE_IMPLEMENTATION
DOCUMENTATION_ASSET
OTHER
```

Do not artificially cap the number of entities extracted from a repository.

---

# 9. PROVENANCE

Every extracted entity must point back to its origin.

At minimum:

```yaml
source:
  repository_id:
  repository_name:
  repository_url:
  upstream_url:
  source_path:
  inspected_commit:
  inspection_date:
```

Also preserve supporting evidence when available:

```yaml
evidence:
  - type: source_path
    value:

  - type: manifest
    value:

  - type: exported_symbol
    value:

  - type: documentation
    value:
```

The system must always be able to answer:

> Which repo contains this?

and:

> Where inside the repo is it?

---

# 10. CANONICAL RECORD RULE

One entity receives ONE canonical record.

Do not duplicate a Skill because it belongs to:

```text
AI
Research
Marketing
Agents
Search
```

Instead:

```text
one canonical Skill record
+
multiple category references/indexes
```

Generated indexes are not sources of truth.

---

# 11. THREE INDEPENDENT DIMENSIONS

Keep these separate.

## ENTITY TYPE

What is it?

Examples:

```text
Skill
MCP
Agent
Component
Repository
SDK
Model
```

## CAPABILITY / DOMAIN

What can it do?

Examples:

```text
UI screenshot inspection
browser navigation
voice cloning
Google Play review retrieval
sentiment analysis
CRM
```

## METADATA

What describes it?

Examples:

```text
Python
MIT
active
self-hosted
production-ready
React
high dependency weight
```

Do not mix these into one flat tag pile.

---

# 12. OPERATIONAL CAPABILITY TAXONOMY

Maintain the following high-level operational taxonomy:

1. Skills
2. Tools / MCPs / Plugins
3. AI Agents / Agent Frameworks
4. Memory / Context / Knowledge
5. Browser / Computer Use
6. Mobile / Device Control
7. Voice / Audio / STT / TTS
8. Vision / OCR / Image Understanding
9. Video / Media Generation & Editing
10. Research / Search / Scraping / Intelligence
11. Business / Sales / CRM / Leads
12. Backend / APIs / Services
13. Databases / Search / Storage / Data
14. Infrastructure / Docker / Deployment / CI
15. Models / Inference / Model Routing
16. Frontend / UI / Components
17. Design Systems / Motion / Animation
18. 3D / Graphics / XR / Rendering
19. Mobile Apps / Android / iOS Components
20. Automation / Workflows / Orchestration
21. Security / Authentication / Identity
22. Payments / Blockchain / Wallets
23. Testing / Evaluation / QA
24. Developer Tools / Codegen / Build Systems
25. General / Other

A repository or entity may have:

```text
one primary operational category
unlimited secondary categories
```

---

# 13. DETAILED TAXONOMY

Preserve the detailed taxonomy previously created.

It should contain approximately 110 functional categories spanning:

## AI / Agents

* AI applications
* Machine-learning models
* LLM projects
* Generative AI
* AI agents
* Agent frameworks
* Agent workflows
* Skills
* MCP servers
* MCP clients/SDKs
* GPTs/GPs
* Prompt libraries
* RAG
* Vector search
* AI memory
* AI orchestration
* AI evaluation
* AI safety/alignment
* AI observability
* AI infrastructure

## Maps / Knowledge

* Maps
* Technology maps
* Dependency maps
* Capability maps
* Architecture maps
* Knowledge graphs
* Ontologies/taxonomies
* Documentation maps
* Organization maps
* Workflow maps

## Applications

* Web applications
* Mobile applications
* Desktop applications
* Backend services
* Frontend applications
* Full-stack applications
* APIs
* SDKs/client libraries
* CLI tools
* Libraries/packages
* Frameworks
* Plugins/extensions
* Developer tools
* Templates/boilerplates
* Reference implementations

## Data / Research

* Databases
* Data engineering
* ETL/ELT
* Data science
* Data visualization
* Datasets
* Data labeling
* Analytics
* Scientific computing
* Research projects
* Benchmarks
* Robotics
* IoT

## Infrastructure

* Cloud infrastructure
* DevOps
* CI/CD
* Infrastructure as code
* Containers
* Kubernetes/orchestration
* Serverless
* Networking
* Distributed systems
* Message/event systems
* Monitoring/observability
* Reliability engineering
* Automation/scripting
* Release engineering

## Security

* Cybersecurity
* Application security
* IAM
* Cryptography
* Privacy
* Secrets management
* Compliance/governance
* Security testing
* Blockchain/Web3 security

## Business / Industry

* Business applications
* Productivity
* Project management
* Finance/accounting
* Commerce/e-commerce
* CRM
* HR
* Healthcare
* Education
* Legal/policy
* Government/civic tech
* Marketing/communications
* Media/publishing
* Real estate/geospatial
* Transportation/logistics
* Manufacturing
* Energy/utilities
* Agriculture/environment

## Documentation / Community / Creative

* Documentation
* Knowledge bases
* Specifications/standards
* Tutorials/examples
* Open-source communities
* Developer communities
* Localization
* Accessibility
* Design systems
* Creative tools
* Games/interactive experiences

Preserve stable category IDs if they already exist locally.

Do not recreate them under different IDs.

---

# 14. METADATA DIMENSIONS

Keep these as metadata instead of ordinary functional categories:

```text
Primary purpose
Repository maturity
Maintenance status
Audience
Deployment model
License
Contribution model
Programming language
Framework ecosystem
Storage technology
Integration type
Execution pattern
Data sensitivity
Scalability profile
Testing profile
Documentation quality
Operational readiness
Dependency profile
Security posture
Repository relationship
```

---

# 15. BROAD DOMAIN FAMILIES

Maintain broad domain-family organization approximately around:

```text
AI
Application
Infrastructure
Data
Security
Business
Documentation
Research
Community
Marketing / Media
UI / UX / Design
```

Do not use these broad families to replace the detailed taxonomy.

They are higher-level navigation.

---

# 16. CAPABILITIES MUST BE ATOMIC

Bad:

```text
AI system
software platform
developer tool
```

Good:

```text
UI screenshot hierarchy detection
OCR text extraction
Google Play review retrieval
voice cloning
speaker diarization
browser click execution
DOM extraction
semantic search
agent memory persistence
competitor monitoring
sentiment classification
Compose animation rendering
OAuth authentication
```

The future system will compose products from these atomic capabilities.

---

# 17. ALIASES AND SYNONYMS

Preserve synonyms.

Example:

```text
UI inspection
UI image inspection
screenshot inspection
screen analysis
visual audit
interface analysis
design inspection
```

Search should connect those phrases to relevant capability records.

---

# 18. CONTRIBUTION ROLES

Use:

```text
CORE
MODULE
COMPONENT
SKILL
SERVICE
REFERENCE
```

Meaning:

### CORE

Could power a major part of a product.

### MODULE

Reusable subsystem.

### COMPONENT

Smaller reusable implementation.

### SKILL

Best exposed directly as an agent/Hermes capability.

### SERVICE

Best integrated through API/MCP/service boundary.

### REFERENCE

Useful architecture/code/design to learn from but generally not import directly.

---

# 19. SCORING

Repository scoring should include:

```text
Capability Value
Code Quality
Reusability
Production Readiness
Maintenance Health
Future Relevance
Strategic Value
Documentation Quality
Security Posture
Integration Ease
```

Use 1–10.

Each score requires evidence/reasoning.

Do not score primarily on stars.

Important internal entities may have their own independent scores.

A B-tier repository may contain an S-tier Skill.

---

# 20. TIERS

Use:

```text
S
A
B
C
D
```

Do not mechanically calculate tiers from averages.

Strategic relevance matters.

---

# 21. RECOMMENDATIONS

Support recommendations such as:

```text
USE DIRECTLY
EXTRACT COMPONENTS
TURN INTO SKILL
USE EXISTING SKILL
INTEGRATE VIA MCP
INTEGRATE VIA API
INTEGRATE AS SERVICE
USE AS LIBRARY
REFERENCE ONLY
SUPERSEDED
ARCHIVE
NEEDS DEEPER REVIEW
AVOID FOR PRODUCTION
LICENSE REVIEW REQUIRED
SECURITY REVIEW REQUIRED
```

---

# 22. RELATIONSHIP GRAPH

Support explicit relationships including:

```text
CONTAINS
PROVIDES
IMPLEMENTS
DEPENDS_ON
REQUIRES
CALLS
WRAPS
EXTENDS
FORK_OF
DERIVED_FROM
OVERLAPS
COMPLEMENTS
REPLACES
REPLACED_BY
ALTERNATIVE_TO
INTEGRATES_WITH
USED_BY
SUITABLE_FOR
MAPS_TO_STUDIO
MAPS_TO_IDEA
USES_MODEL
USES_API
EXPOSES_MCP
CONTAINS_SKILL
CONTAINS_AGENT
CONTAINS_COMPONENT
```

Do not leave important relationships buried only in prose.

---

# 23. COMPOSITION RECIPES

Maintain first-class composition records.

The system should know not only which things exist, but which combinations solve problems.

Example:

```text
Google Play scraper
+
review ingestion
+
sentiment model
+
topic clustering
+
Compose dashboard
=
Android Competitor Intelligence
```

Store reusable compositions.

---

# 24. MALIKY MAPPINGS

Allow multi-mapping to:

```text
Vibe Studio
Trading Studio
Video Studio
Idea Studio
GHL Studio
Agent Studio
Voice Studio
Design Studio
Hermes App Builder Studio
Pulse
Hermes 3D Office
Components / UX
Office / Docs
Voice / Communications
Integrations / API Infrastructure
Deployment / CI
```

A repository/entity may map to multiple Studios.

---

# 25. IDEA MAPPING

Support existing and future Ideas, including:

```text
Voice Websites
Go Native
Personalized Search
Trading Studio
Voice Middleware
```

Do not force mappings without evidence.

---

# 26. CAPABILITY-FIRST BUILD RULE

When a future product requires something, use this order:

```text
Need
↓
Existing shared Maliky capability?
↓
Existing Skill?
↓
Existing MCP/tool?
↓
Existing service?
↓
Existing reusable component?
↓
Existing SDK/API?
↓
Existing reference implementation?
↓
Build new functionality only if necessary
```

Do not recommend installing whole repositories merely because they are relevant.

---

# 27. SMALLEST STRONG COMPOSITION

When an idea requires 20 capabilities and 40 repositories contain related functionality, do not recommend all 40.

Determine the smallest strong composition satisfying the requirements.

Return alternatives separately.

---

# 28. DISCOVERY SCOPE MUST BE CORRECTED AND VERIFIED

The previous run reported:

`430 accessible repositories`

This is NOT automatically equivalent to:

`430 repositories owned by jamesrwatsonx-creator`

During recovery, distinguish:

```text
OWNED
FORKED_UNDER_USER_ACCOUNT
COLLABORATOR_ACCESS
ORGANIZATION_ACCESS
OTHER_ACCESSIBLE
```

The primary canonical personal inventory should prioritize:

```text
owner == jamesrwatsonx-creator
```

including forks owned by that account.

Do not silently absorb unrelated repositories merely because the GitHub integration can access them.

Report:

```text
repositories owned by target account
forks owned by target account
other accessible repositories
private owned repositories
private other-access repositories
```

---

# 29. PRIVATE REPOSITORY SAFETY

`Maliky-Repository-Intelligence` is currently PUBLIC.

Therefore:

**DO NOT COMMIT PRIVATE REPOSITORY SOURCE CODE OR SENSITIVE PRIVATE-REPOSITORY DETAILS INTO THIS PUBLIC REGISTRY.**

Do not publish:

* private source code
* secrets
* credentials
* proprietary prompts
* sensitive internal documents
* confidential file contents

For private repositories, use public-safe/sanitized metadata in the public registry.

Detailed evidence from private sources should remain:

* local and gitignored, or
* in an explicitly private storage/repository if one is later created.

Never leak private-source material merely because the GitHub connector can read it.

---

# 30. SOURCE REPOSITORIES ARE READ-ONLY

Do not modify source repos.

No commits.

No PRs.

No issue creation.

No settings changes.

No branch changes.

No deletion.

Repository Intelligence observes them.

---

# 31. RESUMABILITY

The entire pipeline must be:

```text
incremental
idempotent
resumable
auditable
```

If processing terminates at repository 317:

* previous work remains intact
* state records repository 318 as next
* complete repositories are skipped
* partial repositories resume at their incomplete stage

---

# 32. SEARCH INDEX

Maintain normalized searchable records such as:

`search/search-index.jsonl`

Search should retrieve across:

```text
repositories
Skills
MCPs
agents
tools
components
models
APIs
SDKs
services
workflows
capabilities
```

Do not require the future application to scan arbitrary source YAML files for every query.

---

# 33. FUTURE SEARCH APPLICATION

The registry should eventually support a UI with:

```text
search bar
OpenRouter API
conversational search
repository explorer
Skill explorer
MCP explorer
capability explorer
Idea composer
relationship graph
side-by-side comparisons
```

Example:

> I need UI image inspection.

Return all relevant:

```text
Skills
MCPs
models
repos
components
agents
tools
APIs
```

Example:

> I want to build an app that monitors competing Android apps, analyzes reviews, detects complaints, discovers gaps and displays market intelligence.

The system should derive:

```text
features
↓
capabilities
↓
existing entities
↓
recommended composition
↓
alternatives
↓
missing capabilities
```

---

# 34. VALIDATION

Before any repository is considered complete, validate:

```text
record syntax
entity IDs
repository IDs
source paths
commit provenance
category IDs
capability references
Studio references
Idea references
relationship edges
score values
inspection state
entity census
```

A repository with unresolved entity-census discrepancies cannot be `COMPLETE`.

---

# 35. RECOVER BEFORE REBUILDING

After the recovery audit:

If the previous generated files exist locally:

**KEEP THEM.**

Validate them.

Repair them where necessary.

Continue from their checkpoint.

If the files exist but schemas have evolved, migrate the records rather than discarding them.

If files are partially generated, preserve valid portions.

If cached repository snapshots exist, reuse them when their inspected commit matches the source repository commit.

Do not make thousands of redundant source requests just because this prompt is new.

---

# 36. IF PREVIOUS LOCAL WORK IS MISSING

If the previous run's local/generated work cannot be found:

Report explicitly:

```text
Previous historical run was recorded, but its generated working data is unavailable in this workspace and was not committed to GitHub.
```

Then:

1. preserve the existing README
2. construct the canonical foundation
3. perform correctly scoped owner discovery
4. begin inspection
5. checkpoint frequently
6. commit durable registry work in logical batches so this problem does not happen again

Do not claim the lost previous inspections remain usable.

---

# 37. CHECKPOINTING POLICY

Do not allow another massive run to remain entirely uncommitted.

Create logical durable checkpoints.

Examples:

```text
foundation complete
discovery manifest complete
inspection batch 001
inspection batch 002
entity extraction batch
capability normalization
indexes generated
validation pass
```

Do not commit temporary caches, private evidence, credentials, giant unnecessary raw files, or unsafe data.

But durable canonical registry records and state files should not exist only in an ephemeral Codex session.

---

# 38. REQUIRED INITIAL RESPONSE

Before performing substantial new inspection, report:

1. what existing local work was recovered
2. exact last completed phase
3. what is partial
4. what remains
5. whether the historical 430/409/411/75,406/10,606 figures are supported by local artifacts
6. owned-repository count versus merely-accessible count
7. whether private data is safely isolated
8. exact next operation

Then resume automatically.

Do NOT stop merely to ask permission unless an irreversible/destructive operation would be required.

---

# 39. FINAL OBJECTIVE

The finished system must answer:

> What do I already own that can help build what I am imagining?

It must answer at the level of:

```text
repository
exact Skill
exact MCP
exact component
exact agent
exact API
exact SDK
exact workflow
exact model
exact source path
exact inspected commit
capability supplied
dependencies
alternatives
overlap
Studio mapping
Idea mapping
recommended role
```

The ultimate output should support:

```text
Idea
→ Features
→ Requirements
→ Capabilities
→ Existing Assets
→ Best Composition
→ Missing Pieces
```

This is a private software capability intelligence layer, not merely a repository list.

---

# 40. BEGIN NOW

Perform the recovery audit first.

Recover previous local work before initiating any broad discovery or reinspection.

Do not restart a completed repository inspection.

Do not discard partial entity extraction.

Do not trust historical counts without validating them.

Do not confuse accessible repositories with repositories owned by the target account.

Do not expose private repository material through this public registry.

Once the checkpoint is verified, resume from the first genuinely incomplete stage and continue until the Repository Intelligence system is structurally complete, validated, searchable, resumable, and ready for continuous future repository ingestion.
