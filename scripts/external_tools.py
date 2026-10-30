"""Read-only external individual-tool discovery from Every Awesome Repo.

Search terms are matched locally. A pinned list mention is a research lead;
an upstream README statement is documentation evidence, not runtime validation.
No write, clone, installation or owned-registry enrichment occurs here.
"""
from __future__ import annotations
import json
from pathlib import Path
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PUBLIC_TOOL_INDEX = (
    "https://raw.githubusercontent.com/"
    "jamesrwatsonx-creator/Every-Awesome-Repo/main/data/tools.json"
)
SOURCE = "external:every-awesome-repo:individual-tools"
MAX_BYTES = 12_000_000
MAX_TOOLS = 30_000
STOPWORDS = {"an", "and", "app", "application", "create", "build", "for",
             "from", "i", "in", "of", "on", "or", "the", "to", "using", "with"}
ALIASES = {
    "map": ("maps", "geospatial", "gis"),
    "realtime": ("streaming", "real", "time"),
    "live": ("realtime", "streaming"),
    "data": ("api", "datasets", "database"),
    "transport": ("transit", "traffic", "rail", "train"),
    "finance": ("market", "stock", "financial"),
    "reservation": ("booking", "calendar"),
    "voice": ("speech", "audio", "tts"),
}


class ToolIndexError(ValueError):
    """External index unavailable or structurally unsafe to consume."""


def tokenize(value: str) -> set[str]:
    return {x for x in re.findall(r"[a-z0-9]+", (value or "").lower())
            if len(x) > 1 and x not in STOPWORDS}


def validate(payload: object) -> dict:
    if not isinstance(payload, dict):
        raise ToolIndexError("Individual tool index must be a JSON object")
    if payload.get("project") != "Every Awesome Repo Tools":
        raise ToolIndexError("Unexpected external tool index identity")
    if payload.get("schema_version") != "1.0.0":
        raise ToolIndexError("Unsupported individual tool index version")
    if not isinstance(payload.get("tools"), list):
        raise ToolIndexError("Missing individual tools array")
    if len(payload["tools"]) > MAX_TOOLS:
        raise ToolIndexError("Individual tools array exceeds the limit")
    return payload


def load(path: str | Path | None = None, *, timeout: float = 12.0) -> dict:
    if path is None:
        request = Request(PUBLIC_TOOL_INDEX, headers={
            "Accept": "application/json",
            "User-Agent": "Maliky-ReadOnly-Tool-Discovery"
        }, method="GET")
        try:
            with urlopen(request, timeout=timeout) as response:
                if response.geturl() != PUBLIC_TOOL_INDEX:
                    raise ToolIndexError("Unexpected index redirect")
                raw = response.read(MAX_BYTES + 1)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise ToolIndexError(f"Cannot fetch public tool index: {exc}") from exc
    else:
        try:
            with Path(path).open("rb") as stream:
                raw = stream.read(MAX_BYTES + 1)
        except OSError as exc:
            raise ToolIndexError(f"Cannot read local tool index: {exc}") from exc
    if len(raw) > MAX_BYTES:
        raise ToolIndexError("Individual tool index exceeds maximum size")
    try:
        return validate(json.loads(raw.decode("utf-8")))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ToolIndexError("Malformed public tool index JSON") from exc


def search(index: dict, query: str, *, limit: int = 20) -> list[dict]:
    validate(index)
    wanted = tokenize(query)
    expanded = set(wanted)
    for term in wanted:
        expanded.update(ALIASES.get(term, ()))
    matches = []
    seen = set()
    for item in index["tools"]:
        if not isinstance(item, dict):
            continue
        identity = item.get("id")
        if not isinstance(identity, str) or not identity.startswith("tool:"):
            continue
        if identity in seen:
            continue
        seen.add(identity)
        status = item.get("evidence_status")
        if status not in ("LISTED_ONLY", "UPSTREAM_DOCUMENTED_NOT_TESTED"):
            continue
        sources = item.get("source_collections")
        if not isinstance(sources, list) or not sources:
            continue
        evidence = [s for s in sources if isinstance(s, dict)
                    and isinstance(s.get("evidence_url"), str)
                    and s["evidence_url"].startswith("https://github.com/")]
        if not evidence:
            continue
        upstream = [s for s in item.get("upstream_evidence", [])
                    if isinstance(s, dict)
                    and isinstance(s.get("evidence_url"), str)
                    and s["evidence_url"].startswith("https://github.com/")]
        if status == "UPSTREAM_DOCUMENTED_NOT_TESTED" and not upstream:
            # Never promote source-less or unsupported "documented" claims.
            status = "LISTED_ONLY"
        name = tokenize(item.get("name") if isinstance(item.get("name"), str) else "")
        desc = tokenize(item.get("description") if isinstance(item.get("description"), str) else "")
        topics = tokenize(" ".join(x for x in item.get("topics", []) if isinstance(x, str)))
        docs = tokenize(" ".join(x.get("documented_statement", "") for x in upstream
                                 if isinstance(x.get("documented_statement"), str)))
        direct = wanted & (name | desc | topics | docs)
        related = expanded & (name | desc | topics | docs)
        score = (9 * len(direct & name) + 5 * len(direct & desc)
                 + 3 * len(direct & topics) + 4 * len(direct & docs)
                 + len(related - direct))
        if score < 1:
            continue
        matches.append({
            "id": identity,
            "kind": "external_individual_tool",
            "source": SOURCE,
            "owned": False,
            "name": item.get("name"),
            "url": item.get("url"),
            "github_repository": item.get("github_repository"),
            "description": item.get("description"),
            "topics": item.get("topics"),
            "evidence_status": status,
            "list_evidence": evidence[:8],
            "upstream_documentation": upstream[:4],
            "license_spdx_id": item.get("license_spdx_id") if upstream else None,
            "last_documentation_review": item.get("last_documentation_review") if upstream else None,
            "match_score": score,
            "matched_terms": sorted(related),
            "disclaimer": "External research lead, not an owned, installed or execution-verified tool."
        })
    matches.sort(key=lambda r: (-r["match_score"],
                                r["evidence_status"] != "UPSTREAM_DOCUMENTED_NOT_TESTED",
                                str(r["name"]).lower(), str(r["url"])))
    return matches[:max(0, min(int(limit), 100))]
