# Voicebox semantic review checkpoint

Pinned commit: `51f49dea198384b4eb6087b72c17057c6eb1c1cd`. Static source review only; no target code was executed.

## Confirmed source contracts

- [Voicebox MCP server](https://github.com/jamesrwatsonx-creator/voicebox/blob/51f49dea198384b4eb6087b72c17057c6eb1c1cd/backend/mcp_server/server.py#L25) is constructed with `FastMCP(name="voicebox")` and mounted at `/mcp`.
- Four decorated MCP tools are independently catalogued: `voicebox.speak`, `voicebox.transcribe`, `voicebox.list_captures`, and `voicebox.list_profiles`.
- `voicebox.speak` delegates to the existing queued generation endpoint; it does not prove streaming inference.
- `voicebox.transcribe` accepts base64 audio or a loopback-only absolute local path, with a 200 MB guard.

## Still pending

- 123 HTTP route candidates, 118 UI component candidates, Skills, workflows, packages, scores, mappings and the independent census remain unreviewed.
- This checkpoint keeps Voicebox in `NEEDS_REVIEW`; it does not mark the repository complete.
