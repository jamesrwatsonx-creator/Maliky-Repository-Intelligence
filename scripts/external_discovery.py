"""Read-only external discovery of public Awesome-list repositories.

This module does not use Maliky's registry, ingest sources, execute upstream code,
save results, or send a user's search query to a remote service. It downloads a
public JSON index and scores records locally. Records are suggestions, NEVER
verified or owned capabilities.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

CATALOG_URL = (
    "https://raw.githubusercontent.com/"
    "jamesrwatsonx-creator/Every-Awesome-Repo/main/data/catalog.json"
)
SOURCE_ID = "external:every-awesome-repo"
MAX_CATALOG_BYTES = 5 * 1024 * 1024
MAX_RECORDS = 100_000
STOPWORDS = {
    "a", "an", "and", "app", "application", "build", "create", "for", "i", "in",
    "into", "me", "my", "of", "on", "or", "the", "to", "that", "this",
    "using", "want", "with",
}
ALIASES = {
    "voice": ("speech", "tts", "audio", "conversational"),
    "assistant": ("agent", "agents", "ai"),
    "booking": ("scheduling", "calendar", "automation", "workflows"),
    "reservation": ("booking", "scheduling", "calendar"),
    "restaurant": ("commerce", "ecommerce", "payments", "customer"),
    "map": ("maps", "geospatial", "gis"),
    "maps": ("map", "geospatial", "gis"),
    "location": ("geospatial", "maps", "gis"),
    "website": ("frontend", "web", "ui", "design"),
    "mobile": ("android", "ios", "cross", "platform"),
    "dashboard": ("visualization", "analytics", "ui"),
    "realtime": ("streaming", "real", "time"),
    "chatbot": ("llm", "voice", "conversational"),
    "customer": ("crm", "commerce", "marketing"),
    "payment": ("payments", "fintech", "commerce"),
    "shopping": ("ecommerce", "commerce"),
    "auth": ("authentication", "identity", "security"),
    "automation": ("workflow", "orchestration"),
    "video": ("creative", "media", "generative"),
}


class ExternalCatalogError(ValueError):
    """Public catalog unavailable or does not match the accepted schema."""


def tokens(value: str) -> set[str]:
    return {
        term
        for term in re.findall(r"[a-z0-9]+", (value or "").lower())
        if len(term) > 1 and term not in STOPWORDS
    }


def canonical_repository(repo: str, url: str) -> str | None:
    """Accept only matching public github.com owner/name links, never arbitrary URLs."""
    if not isinstance(repo, str) or not re.fullmatch(
        r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo
    ):
        return None
    if not isinstance(url, str):
        return None
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc.lower() != "github.com":
        return None
    if parsed.query or parsed.fragment or parsed.params:
        return None
    if parsed.path.strip("/").lower() != repo.lower():
        return None
    return repo


def validate_catalog(payload: object) -> dict:
    if not isinstance(payload, dict):
        raise ExternalCatalogError("External catalog root must be an object")
    if payload.get("project") != "Every Awesome Repo":
        raise ExternalCatalogError("Unexpected catalog identity")
    if not isinstance(payload.get("repositories"), list):
        raise ExternalCatalogError("Missing repositories array")
    if len(payload["repositories"]) > MAX_RECORDS:
        raise ExternalCatalogError("Catalog exceeds maximum record count")
    if not isinstance(payload.get("categories"), list):
        raise ExternalCatalogError("Missing categories array")
    if not isinstance(payload.get("schema_version"), str):
        raise ExternalCatalogError("Missing catalog schema_version")
    if payload["schema_version"].split(".")[0] != "1":
        raise ExternalCatalogError("Unsupported catalog schema version")
    return payload


def load_catalog(path: str | Path | None = None, *, timeout: float = 12.0) -> dict:
    """Load file fixture or HTTPS-only public JSON, with a strict maximum size."""
    if path is not None:
        try:
            with Path(path).open("rb") as handle:
                raw = handle.read(MAX_CATALOG_BYTES + 1)
        except OSError as exc:
            raise ExternalCatalogError(f"Cannot read external catalog file: {exc}") from exc
    else:
        request = Request(
            CATALOG_URL,
            headers={
                "User-Agent": "Maliky-External-Discovery/1.0",
                "Accept": "application/json",
            },
            method="GET",
        )
        try:
            with urlopen(request, timeout=timeout) as response:
                # A redirect to any other host would not be our fixed public source.
                if response.geturl() != CATALOG_URL:
                    raise ExternalCatalogError("Unexpected external catalog redirect")
                raw = response.read(MAX_CATALOG_BYTES + 1)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise ExternalCatalogError(f"Cannot fetch public catalog: {exc}") from exc
    if len(raw) > MAX_CATALOG_BYTES:
        raise ExternalCatalogError("Public catalog is larger than the allowed limit")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ExternalCatalogError("Invalid public catalog JSON") from exc
    return validate_catalog(payload)


def search_catalog(
    query: str,
    catalog: dict,
    *,
    limit: int = 20,
    exclude_repositories: set[str] | None = None,
) -> list[dict]:
    """Score linked collection records; never import them into the owned registry."""
    validate_catalog(catalog)
    wanted = tokens(query)
    expanded = set(wanted)
    for term in wanted:
        expanded.update(ALIASES.get(term, ()))
    seen = set()
    matches = []
    owned = {str(r).lower() for r in (exclude_repositories or set())}
    for item in catalog["repositories"]:
        if not isinstance(item, dict):
            continue
        repo = item.get("repository")
        url = item.get("url")
        identity = canonical_repository(repo, url)
        if not identity or identity.lower() in seen:
            continue
        seen.add(identity.lower())
        categories = item.get("categories")
        tags = item.get("discovery_tags")
        if not isinstance(categories, list) or not isinstance(tags, list):
            continue
        categories = [s for s in categories if isinstance(s, str)][:30]
        tags = [s for s in tags if isinstance(s, str)][:60]
        desc = item.get("description") if isinstance(item.get("description"), str) else ""
        name_terms = tokens(identity)
        tag_terms = tokens(" ".join(tags))
        category_terms = tokens(" ".join(categories))
        desc_terms = tokens(desc[:2000])
        direct = wanted & (name_terms | tag_terms | category_terms | desc_terms)
        related = expanded & (name_terms | tag_terms | category_terms | desc_terms)
        score = (
            10 * len(direct & name_terms)
            + 6 * len(direct & tag_terms)
            + 4 * len(direct & category_terms)
            + 2 * len(direct & desc_terms)
            + len(related - direct)
        )
        if score < 1:
            continue
        stars = item.get("stars", 0)
        if not isinstance(stars, int) or isinstance(stars, bool) or stars < 0:
            stars = 0
        matches.append({
            "source": SOURCE_ID,
            "kind": "external_collection",
            "review_status": "UNVERIFIED_EXTERNAL_REFERENCE",
            "owned": False,
            "repository": identity,
            "url": url,
            "categories": categories,
            "discovery_tags": tags,
            "description": desc or None,
            "stars_snapshot": stars,
            "stars_checked_at": item.get("stars_checked_at"),
            "catalog_snapshot_date": catalog.get("snapshot_date"),
            "original_screenshot": item.get("original_screenshot") is True,
            "possible_owned_identity_overlap": identity.lower() in owned,
            "match_score": score,
            "matched_terms": sorted(related),
        })
    matches.sort(
        key=lambda m: (-m["match_score"], -m["stars_snapshot"], m["repository"].lower())
    )
    return matches[:max(0, min(int(limit), 100))]
