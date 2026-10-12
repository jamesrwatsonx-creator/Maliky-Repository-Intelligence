# App idea research workflow for Hermes

This workflow joins current market evidence with the owned capability catalog. Reddit and competitor findings must come from the connected search tools at the time of the request; the catalog only describes owned technical assets.

For each idea, report:

- The repeated problem, target users and dated links showing demand.
- Existing alternatives and what they offer. Do not say an app does not exist unless current competitor searches support that conclusion.
- The opportunity to differentiate and the required product features.
- Matching owned repositories and specific internal assets, with original GitHub source links and evidence states.
- Known dependencies, assets usable directly or requiring adaptation, and compatibility assumptions that remain unverified.
- Capabilities not established by verified owned assets.
- Technical complexity and the smallest practical MVP.

Suggested agent sequence:

1. Search Reddit and other relevant public sources for repeated complaints. Keep post dates, direct links, and a small quote or faithful paraphrase for each signal.
2. Search current products for each problem and compare feature sets, audience and pricing where public evidence supports it.
3. Turn each promising problem into a short, explicit list of required features and capabilities.
4. Query the local catalog or public JSON export. Search by topic, asset type, repository, source path and description; inspect candidates' source links and review status.
5. Run the existing composition workflow for established capability IDs. State which components are verified, candidate or missing, and list assumptions.
6. Recommend five ideas only if five have adequate demand and asset evidence. Otherwise report the supported number instead of padding the list.

Example catalog checks:

```sh
python scripts/search_catalog.py "voice receptionist" --limit 25
python scripts/search_catalog.py "business CRM voice" --topic voice-stt-tts --limit 50
python scripts/search_catalog.py "browser automation" --type Tool --limit 25
python scripts/registry.py compose --capability capability:queued-speech-generation-submission --capability capability:voice-mcp-server-exposure
```

The catalog is not a market-research database. Refresh external evidence for every research request, and never infer demand or competitor absence from catalog results.
