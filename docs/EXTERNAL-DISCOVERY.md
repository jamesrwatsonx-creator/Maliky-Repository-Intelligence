# Read-only external discovery: Every Awesome Repo

**Purpose:** Search Maliky's inspected, owned resources alongside public external discovery leads without merging ownership, registries or verification states.

**External source:** https://github.com/jamesrwatsonx-creator/Every-Awesome-Repo

## Trust boundaries

| Maliky | Every Awesome Repo |
| --- | --- |
| Owned and source-evidenced internal assets, capabilities and clusters | Unverified external collections and candidate discovery tags |
| Existing evidence and review statuses are retained | Always tagged as unverified references, never owned or installed |
| Canonical Maliky registry remains authoritative | Linked outside the canonical registry; no clone, fork or intake |

The adapter uses read-only HTTPS GET for one fixed public JSON index with size limits and schema checks. Search queries are matched **locally**. No private repository identity, owned search results or app-idea query is sent to Every Awesome Repo. It uses no credentials for public discovery.

External suggestions are labeled `source: external:every-awesome-repo`, `kind: external_collection`, `review_status: UNVERIFIED_EXTERNAL_REFERENCE`, `owned: false`. Matching owned repository identities receive only a non-authoritative overlap hint.

## Commands

Maliky's existing search is unchanged and requires no external network:

```bash
python scripts/search_catalog.py "voice assistant"
```

Run both searches from the Maliky checkout, keeping results in separate JSON arrays:

```bash
python scripts/search_with_discovery.py "voice assistant restaurant booking" --external --limit 10 --external-limit 15
python scripts/search_with_discovery.py "geospatial map realtime data" --external
```

Without `--external`, the combined command searches only Maliky. For offline testing, supply a public-index JSON file:

```bash
python scripts/search_with_discovery.py "voice" --external-catalog-file /path/every-awesome-catalog.json
python -m unittest discover -s tests -p "test_external_discovery.py" -v
```

## Application-idea workflow

1. Convert the requested application into actual capabilities and constraints.
2. Search Maliky's owned, source-evidenced catalog first.
3. Where coverage is missing, weak or unverified, opt into external discovery.
4. Open matching curated collections to find the *individual upstream implementations* that could meet a capability.
5. Check license, API availability, documentation, security, maintenance, runtime compatibility, integration effort, and costs before recommending anything.
6. Produce a source-linked solution and flag uncertainties. Separate user-approved intake/install is required to add any new code.

**Search never installs, executes, forks or ingests third-party code.** Inclusion or stars are not proof of safety, compatibility, maintenance or feature support. The source index lists curated collections, not validated downstream components.

## Failure handling and scope

When the external catalog is unreachable, invalid or has a changed schema, owned results are returned as usual and `external_error` explains the failure. No changes are made to either repository. The adapter is a small deterministic, lexical discovery CLI—not a hosted search API, plugin, MCP server or full semantic index.

## Individual tool evidence (optional second external layer)

Every Awesome Repo now separately publishes an individually indexed tool catalog. It is completely usable on its own, including for a data-only application. Maliky can *optionally* consume that read-only index without changing its owned repository/capability registry.

```bash
python scripts/search_with_discovery.py "real time transit data" --external-tools
python scripts/search_with_discovery.py "spatial database" --external --external-tools
```

Results have three separate namespaces: `owned` (Maliky source evidence), `external` (Awesome collections), and `external_tools` (individual candidates linked inside collections). Errors from external requests remain nonfatal to the owned search, exposed as `external_error` or `external_tools_error`.

Each tool result retains the pinned collection line evidence and, when obtained, a pinned literal upstream README statement. `LISTED_ONLY` means **only curated-list inclusion**. `UPSTREAM_DOCUMENTED_NOT_TESTED` means **upstream documentation observed**, not that APIs or deployed behavior were tested, nor that a project has been audited or licensed for your use.

The adapter fetches public `data/tools.json` and matches your query locally. No query, private repo name or owned record is transmitted to Every Awesome Repo. No external records are inserted into Maliky's registry. Offline mode: `--external-tools-file /path/to/tools.json`.

To extend child-tool coverage, work inside Every Awesome Repo with its independent `scripts/index_tools.py` and `scripts/search_tools.py`. Maliky just reads the published index when requested.
