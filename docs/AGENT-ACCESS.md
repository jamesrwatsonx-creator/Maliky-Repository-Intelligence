# Read-only catalog access for agents

The GitHub registry is the canonical source. The generated public export contains only public repository records and active assets; it excludes the private inventory and local evidence. Evidence status distinguishes `VERIFIED` assets from `NEEDS_REVIEW` candidates. Ownership does not imply that a project is installed, running, compatible or production-ready.

## Hermes, Codex, Claude Code or a local agent

For local work, use the deterministic CLI:

```sh
python scripts/search_catalog.py "Android voice interface" --limit 20
python scripts/search_catalog.py "MCP server" --type "MCP Server" --limit 100
python scripts/search_catalog.py "animation" --topic animation-motion --kind assets
python scripts/search_catalog.py "mobile UI" --repository android --status VERIFIED
```

The output is JSON. Each asset includes its name, description, type, verification state, originating repository, exact source path, pinned source URL, categories, topics, known capabilities and source revision. Repository results include the GitHub repository link and a link to the canonical registry record.

Agents without a checkout can read the public export directly:

```text
https://raw.githubusercontent.com/jamesrwatsonx-creator/Maliky-Repository-Intelligence/recovery/v1-rebuild/docs/catalog/catalog.json
```

It contains one `items` array (filter `kind` for repositories or assets), plus `capabilities`, `topics`, `asset_types` and summary counts. The export stores each item once. This is a read-only static file; clients should refresh it when they begin a research session rather than keeping their own database.

## Compose an application idea

Try a small composition from two established speech capabilities:

```sh
python scripts/registry.py compose --capability capability:queued-speech-generation-submission --capability capability:voice-mcp-server-exposure
```

The composer returns verified owned providers, their source records, known dependency relationships, alternatives and requirements not covered by verified providers. “Missing” means the catalog does not establish a verified provider; it is not proof that no asset exists. Runtime compatibility and production readiness require separate validation.

For a new idea, first search the catalog for each required capability. Pass the resulting canonical capability IDs to `scripts/registry.py compose --capability capability:id` (repeat the flag for more requirements). Review the returned source links and assumptions before selecting an architecture. The composition engine does not install, execute or acquire repositories. The existing `idea:voice-websites` registry record is currently `UNMAPPED` with no requirements, so do not treat it as a completed architecture recipe.

## Future static website and catalog clients

`docs/catalog/catalog.json` is the versioned public-data interface. `docs/catalog/index.html` provides a local and GitHub Pages-compatible search view over the same export. A future website should consume these generated records and continue to treat `registry/` as the source of truth.
