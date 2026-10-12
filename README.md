# Maliky Repository Intelligence

### Know what you own. Find what it can do. Build with what you already have.

**Maliky Repository Intelligence** is a searchable, capability-first catalog of the GitHub repositories collected and maintained under [jamesrwatsonx-creator](https://github.com/jamesrwatsonx-creator).

Its purpose is to answer a practical question:

> **What technology do I already have access to, where is it, what does it do, and how could I combine it to build something new?**

Instead of treating GitHub as a long list of repositories, Maliky separates those repositories into the **reusable capabilities inside them**: Skills, MCP servers, tools, plugins, agents, frameworks, APIs, SDKs, UI components, design references, models, workflows, services, and more.

A repository is the container. **Its useful internal assets are the things you can find, evaluate, and reuse.**

**Current focus: Catalog V1.** Finish the reliable, categorized, searchable data first. A dedicated website and optional agent/plugin integrations come later. This project is **not** currently a hosted search website, a finished Hermes plugin, or a guarantee that identified code is ready for production.

## Browse the catalog

Start at the [complete browse homepage](browse/README.md), with generated counts and links to every populated section.

**By asset type:** [Skills](browse/types/skills/README.md) · [MCPs](browse/types/mcps/README.md) · [Plugins](browse/types/plugins/README.md) · [Agents](browse/types/agents/README.md) · [Tools](browse/types/tools/README.md) · [APIs](browse/types/apis/README.md) · [SDKs](browse/types/sdks/README.md) · [UI components](browse/types/ui-components/README.md) · [Workflows](browse/types/workflows/README.md) · [Templates](browse/types/templates/README.md) · [Models](browse/types/models/README.md) · [Libraries](browse/types/libraries/README.md) · [Services](browse/types/services/README.md) · [Prompts](browse/types/prompts/README.md) · [Repositories](browse/types/repositories/README.md)

**By purpose:** [Android](browse/topics/android/README.md) · [iOS](browse/topics/ios/README.md) · [React Native](browse/topics/react-native/README.md) · [Expo](browse/topics/expo/README.md) · [Flutter](browse/topics/flutter/README.md) · [Wearables](browse/topics/wearables/README.md) · [Websites](browse/topics/websites/README.md) · [Web apps](browse/topics/web-apps/README.md) · [Website inspiration](browse/topics/website-inspiration/README.md) · [Landing pages](browse/topics/landing-page-inspiration/README.md) · [UI/UX](browse/topics/ui-ux/README.md) · [Design systems](browse/topics/design-systems/README.md) · [Animation](browse/topics/animation-motion/README.md) · [3D/XR](browse/topics/3d-xr/README.md) · [AI agents](browse/topics/ai-agents/README.md) · [Memory](browse/topics/memory/README.md) · [Models/local LLMs](browse/topics/models-local-llms/README.md) · [Search](browse/topics/search-indexing/README.md) · [Browser automation](browse/topics/browser-automation/README.md) · [Voice/STT/TTS](browse/topics/voice-stt-tts/README.md) · [Audio/music](browse/topics/audio-music/README.md) · [Vision/OCR](browse/topics/vision-ocr/README.md) · [Images](browse/topics/images/README.md) · [Video](browse/topics/video/README.md) · [Realtime](browse/topics/realtime/README.md) · [Backend](browse/topics/backend/README.md) · [APIs/SDKs](browse/topics/apis-sdks/README.md) · [Databases/ETL](browse/topics/databases-etl/README.md) · [Security](browse/topics/security-identity/README.md) · [Infrastructure](browse/topics/infrastructure/README.md) · [Deployment](browse/topics/deployment/README.md) · [Testing/developer tools](browse/topics/testing-developer-tools/README.md) · [Business/marketing](browse/topics/business-crm-marketing/README.md) · [Finance/blockchain/crypto](browse/topics/finance-blockchain-crypto/README.md) · [Productivity/automation](browse/topics/productivity-automation/README.md) · [Documentation](browse/topics/documentation/README.md) · [Experiments](browse/topics/experimental/README.md)

**Search:** Use the [catalog query instructions](docs/AGENT-ACCESS.md) and [searchable JSON export](docs/catalog/catalog.json). The browse homepage links to nested topic pages and paginated results.

---

## The problem this solves

A growing collection of forks and repositories can contain thousands of useful assets, but remembering what each project provides is difficult.

A repository that looks like a single project might contain 50 agent Skills, several MCP tools, reusable UI elements, prompts, services, and deployment templates. Simply bookmarking that repository makes those assets difficult to discover again.

Maliky changes how the collection is organized:

- **Discover:** What repositories are in the collection?
- **Describe:** What does each repository actually do?
- **Separate:** Which meaningful assets exist inside it?
- **Classify:** What *kind* of asset is each one, and what *domain* does it serve?
- **Locate:** Where exactly is the source implementation?
- **Search:** Which owned assets could solve a problem?
- **Compose, later:** Which combination of existing assets could support a new app or workflow, and what is still missing?

The immediate goal is useful coverage, not exhaustive analysis or the largest possible number of extracted records.

## Three ways the catalog organizes technology

Each record answers three different questions. These dimensions are deliberately separate.

| Dimension | Question | Example |
| --- | --- | --- |
| **Asset type** | What is it? | Skill, MCP server, agent, API, SDK, UI component |
| **Capability / domain** | What does it help accomplish? | Browser automation, speech recognition, Android UI, search |
| **Attributes and provenance** | What should I know about using it? | Repository, source path, revision, language, dependencies, license, evidence status |

One asset can have more than one category. For example, an Android voice assistant component could be classified under **Mobile / Device Control**, **Voice / Audio**, and **UI / UX** without being duplicated into three separate implementations.

## What gets separated from a repository?

Maliky preserves meaningful internal assets as **independently searchable records** where lightweight source evidence supports them.

| Asset family | Examples of what can be identified |
| --- | --- |
| **Skills** | Agent instruction packages, specialized task skills, reusable skill libraries |
| **MCP servers and tools** | Model Context Protocol servers and the individual tools they expose |
| **Plugins and integrations** | Extensions, connectors, provider adapters and integration modules |
| **AI agents and frameworks** | Specialized agents, multi-agent orchestration, agent runtimes |
| **APIs, SDKs and services** | Endpoints, client libraries, service interfaces, reusable backends |
| **UI / UX and mobile components** | React components, Android/Compose components, design systems, interaction patterns |
| **Voice, audio, vision and models** | STT/TTS modules, audio pipelines, OCR, vision components, model adapters |
| **Memory, data and search** | Context systems, knowledge stores, databases, indexing and retrieval modules |
| **Prompts, templates and workflows** | Reusable prompts, automation sequences, application starters, CI workflows |
| **Infrastructure and deployment** | Container configurations, cloud modules, automation and deployment tooling |
| **Design and media references** | Layout references, websites, animation examples, video/media utilities |

**A repository does not automatically equal one capability.** A library containing 300 genuinely reusable Skills should make those Skills discoverable individually. Conversely, internal helper functions, test fixtures and boilerplate do not need hundreds of meaningless records.

Each useful asset points back to its original repository and, where available, its exact path, inspected commit and supporting evidence.

## The 25 high-level capability categories

These are the broad discovery categories used to organize and browse the collection. They are not mutually exclusive, and they do not replace the catalog's more detailed taxonomy or specific asset types.

| # | Category | What belongs here |
| --- | --- | --- |
| 01 | **Skills** | Reusable AI or agent skills, task instructions and specialized skill collections |
| 02 | **Tools / MCPs / Plugins** | MCP servers, callable tools, extensions and connectors |
| 03 | **AI Agents / Frameworks** | Individual AI agents, orchestrators and multi-agent frameworks |
| 04 | **Memory / Context / Knowledge** | Persistent agent memory, context management, RAG and knowledge systems |
| 05 | **Browser / Computer Use** | Browser automation, browsing agents, scraping and desktop interaction |
| 06 | **Mobile / Device Control** | Android/iOS implementations, device integrations and mobile automation |
| 07 | **Voice / Audio / STT / TTS** | Voice interfaces, speech recognition, transcription, speech generation and audio tooling |
| 08 | **Vision / OCR** | Image understanding, image processing, OCR and visual recognition |
| 09 | **UI / UX / Components** | Reusable interfaces, frontend components, mobile screens and interaction patterns |
| 10 | **Design / References** | Design systems, inspiration websites, visual patterns, fonts, animation and references |
| 11 | **Data / DB / ETL** | Databases, pipelines, storage, transformation and synchronization |
| 12 | **Analytics** | Measurement, reporting, monitoring, metrics and data analysis |
| 13 | **Security / Compliance** | Authentication, authorization, privacy, auditing and security utilities |
| 14 | **Infrastructure / Cloud / CI** | Cloud resources, system infrastructure, continuous integration and operations |
| 15 | **Deployment / Containers** | Docker, deployment templates, packaging and release systems |
| 16 | **APIs / SDKs / Services** | Web services, APIs, software development kits and integration layers |
| 17 | **Models / LLMs** | Language models, inference, model adapters and model-serving components |
| 18 | **Prompts / Workflows** | Prompt libraries, recipes, agent instructions and repeatable automations |
| 19 | **Search / Index** | Search engines, crawlers, indexing, retrieval and ranking systems |
| 20 | **Docs / Guides / Maps** | Technical documentation, learning resources, architecture maps and guides |
| 21 | **Business / Commerce** | CRM, sales, marketing, customer service, marketplaces and commerce systems |
| 22 | **Finance / Trading** | Market analysis, financial tooling, trading research and related integrations |
| 23 | **Productivity / Office** | Email, calendars, document processing, scheduling and office automation |
| 24 | **Video / Media** | Video generation, editing, graphics, streaming and media-processing tools |
| 25 | **Experiments / Playground** | Prototypes, research projects, demonstrations and emerging techniques |

These are **browse families**. The canonical registry also supports detailed categories, technical metadata and specific entity types. A single implementation may appear in several relevant searches while retaining **one canonical source identity**.

## What happens when a new repository is forked or added?

The catalog is designed for **incremental intake**. New repositories should extend what is already known instead of forcing a full rescan.

### Intake pipeline

~~~text
NEW FORK / REPOSITORY
        |
        v
Verify ownership and visibility
        |
        v
Register repository + capture upstream provenance
        |
        v
Read lightweight evidence
(README, manifests, structure, selected source)
        |
        v
Describe the repository and identify reusable assets
        |
        v
Assign asset types + capability categories
        |
        v
Preserve exact links, paths, revisions and evidence status
        |
        v
Check existing records and relevant overlap
        |
        v
Update canonical records + regenerate affected indexes
        |
        v
Validate + save a Git checkpoint
        |
        v
SEARCHABLE CATALOG
~~~

The important rules are:

1. **Do not start over.** Resume from the saved state and reuse existing records.
2. **Do not assume a fork adds an entirely new capability.** Track its upstream source and distinguish overlap from genuinely different assets.
3. **Do not treat detection as proof.** Source-supported candidates remain labeled until verified.
4. **Do not publish private material.** Private repository details require appropriate access controls; public artifacts can contain aggregate private counts without disclosing identities.
5. **Do not execute unknown repository code just to catalog it.** Prefer read-only source inspection.
6. **Do not reprocess everything for one new fork.** Update only new or changed sources and affected indexes.

The repository includes an existing intake entry point at `scripts/intake_repository.py` and an intake policy in [`rules/new-repository-intake.md`](rules/new-repository-intake.md). Automated detection of every future fork without an intake or synchronization trigger is a **future workflow**, not an already-deployed GitHub webhook.

## What can be searched?

The catalog is intended to support searches such as:

- "Show every MCP server and the tools it provides."
- "Which Skills can help with marketing or customer research?"
- "What do I have for Android voice interfaces?"
- "Find browser automation and computer-use frameworks."
- "Which repositories contain reusable authentication components?"
- "Find UI components for an animated mobile onboarding flow."
- "Do I already have a way to search Reddit or analyze app reviews?"
- "Which owned components could be combined into a local business assistant?"

Search results should show **what the asset does**, its **type and categories**, its **parent repository**, and a **direct GitHub source link**. Results should distinguish verified evidence from incomplete candidates.

The existing data layer includes a keyword-based search index and capability composition logic. The current composer uses verified providers; an absent result means a capability **has not been established by the reviewed evidence**, not necessarily that it is absent from every repository.

## From a new app idea to an owned technology stack

The long-term vision is to make the catalog a **capability compiler** for new applications.

~~~text
APP IDEA
   |
   v
Identify the essential features
   |
   v
Convert features into required capabilities
   |
   v
Search the owned catalog first
   |
   v
Select relevant Skills / MCPs / SDKs / UI / services
   |
   v
Compare alternatives and integration constraints
   |
   v
Identify missing or uncertain capabilities
   |
   v
Recommend a realistic MVP architecture
~~~

For example, a voice-enabled business application might require a voice interface, transcription, an agent runtime, website components, search, business integrations and deployment. Maliky should help locate the strongest relevant assets already in the collection rather than designing every part from scratch.

**Reuse is not automatic compatibility.** Dependencies, licenses, security and deployment requirements still need to be checked before integrating a component into a real product.

External research and gap discovery come *after* checking owned coverage. A newly found external project is a candidate, not automatically part of the collection.

## The planned website

**The website is a future product, not the current Catalog V1 deliverable.**

It will provide a visual, searchable interface over these same canonical records instead of creating a competing inventory.

### Planned experience

| Website area | Intended functionality |
| --- | --- |
| **Universal search** | Search repositories, assets and capabilities in plain language |
| **Category explorer** | Navigate the 25 broad capability categories and their detailed subcategories |
| **Asset-type filters** | Browse Skills, MCPs, agents, APIs, SDKs, UI elements, models, workflows and more |
| **Repository profiles** | See what a repository does, its upstream origin and the reusable assets it contains |
| **Capability detail pages** | See functionality, source links, associated assets, evidence status and usage context |
| **Search and comparison** | Compare alternative tools or overlapping implementations before choosing one |
| **Stack / app composition** | Assemble candidate combinations from owned components for a proposed application |
| **Capability gap view** | Identify what is covered, partially covered or not yet established |
| **New-fork activity** | Show newly cataloged repositories and the capabilities they contribute |
| **Build handoff** | Produce a source-linked component shortlist or architecture brief for a coding agent |

The website should answer both **"What do I have?"** and **"What can I build with it?"**

A visual website is optional for using the underlying data. The canonical registry and generated indexes remain the source of truth.

## Future agent and plugin access

After the catalog and website foundation are ready, a separate integration phase can package read-only catalog retrieval and capability matching as a plugin or compatible tool interface.

The goal is to let an authorized assistant, such as Hermes or another coding agent, ask what technologies are available and receive grounded, source-linked answers.

**No Hermes integration, plugin deployment or MCP catalog server is part of the current Catalog V1 scope.**

A later idea-discovery workflow may research Reddit, community complaints, competitor products or other external sources, then consult the owned catalog to suggest useful combinations. Any claim that an app concept is novel or viable requires separate market validation.

## Current development scope

| Stage | Status | Objective |
| --- | --- | --- |
| **1. Catalog V1** | **In progress** | Synchronize owned repositories; describe, categorize and index meaningful assets; validate provenance and search |
| **2. Searchable website** | Planned | Browse and search the catalog visually |
| **3. Optional agent plugin** | Planned | Expose the catalog to authorized external agents, including Hermes |
| **4. Idea discovery and app composition** | Future workflow | Research opportunities, match owned capabilities and report gaps |

**Catalog V1 intentionally does not require** exhaustive semantic review, deep security audits of every repository, universal quality scoring, or every source repository reaching an old strict `COMPLETE` state. Those activities are deferred until a real use case justifies them.

For live checkpoint details, use the machine-readable state rather than hardcoded counts in this README:

- [Catalog statistics](system/statistics.json)
- [Repository discovery manifest](system/discovery-manifest.json)
- [Repository inspection state](system/inspection-state.json)
- [Master inventory](MASTER-INVENTORY.json)

Counts may change as new forks are found and local changes are validated and pushed.

## Canonical data layout

| Path | Purpose |
| --- | --- |
| [`registry/repositories/`](registry/repositories/) | Canonical records for each indexed public repository |
| [`registry/entities/`](registry/entities/) | Individually addressable internal Skills, tools, agents, components and other assets |
| [`registry/capabilities/`](registry/capabilities/) | Capability names, aliases and associated providers |
| [`registry/taxonomy/`](registry/taxonomy/) | Detailed categories and classification vocabulary |
| [`registry/indexes/`](registry/indexes/) | Rebuildable lookup indexes |
| [`search/search-index.jsonl`](search/search-index.jsonl) | Normalized repository, asset and capability search documents |
| [`MASTER-INVENTORY.json`](MASTER-INVENTORY.json) | Generated repository summary |
| [`CAPABILITY-GRAPH.json`](CAPABILITY-GRAPH.json) | Generated nodes and relationships |
| [`system/inspection-state.json`](system/inspection-state.json) | Checkpoint and remaining-work pointer |
| [`system/evidence/`](system/evidence/) | Pinned source evidence and inspection limitations |
| [`rules/new-repository-intake.md`](rules/new-repository-intake.md) | Idempotent new-repository intake policy |

Existing command-line entry points include `scripts/build_indexes.py`, `scripts/validate_registry.py`, `scripts/query_registry.py` and `scripts/compose_idea.py`. Consult their current help and [querying documentation](docs/QUERYING.md) before use; this repository is undergoing the catalog-first scope transition.

The data is designed so future interfaces can consume it **without rediscovering and reclassifying the repositories from scratch**.

## Evidence, ownership and responsible reuse

- **Known:** Supported by repository evidence at an identified revision.
- **Candidate / unverified:** Detected or suggested by lightweight inspection, but not fully established.
- **Unknown:** Not enough evidence to make a claim.

A GitHub fork is not proof of authorship, licensing rights beyond the upstream license, production readiness, or security. Each asset retains its source attribution and license context when available.

Private repositories and sensitive data must not leak into a public registry, published search index or website. Runtime compatibility and operational safety are evaluated when an asset is selected for a build, not presumed during basic cataloging.

---

**The end goal:** One durable, searchable map of the capabilities already available across the GitHub collection, so the next product can begin with **what already exists** instead of starting from zero.

**Find it. Understand it. Reuse it. Combine it. Build.**
