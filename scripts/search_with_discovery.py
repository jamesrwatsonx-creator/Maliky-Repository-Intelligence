"""Combined, non-mutating search of Maliky's owned catalog and external discovery.

Owned results stay separate from unverified external suggestions. External mode is
opt-in; external GitHub data is never treated as part of Maliky's canonical registry.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import external_discovery
import search_catalog as maliky_search

ROOT = Path(__file__).resolve().parents[1]


def search_both(
    query: str,
    *,
    owned_catalog: str | Path | None = None,
    external: bool = False,
    external_catalog: str | Path | None = None,
    limit: int = 20,
    external_limit: int = 20,
) -> dict:
    """Return separate owned and external result groups with explicit provenance."""
    if external_catalog is not None:
        external = True
    if owned_catalog is None:
        owned_catalog = maliky_search.CATALOG
    if not Path(owned_catalog).is_file():
        raise FileNotFoundError(f"Maliky public catalog not found: {owned_catalog}")
    owned = maliky_search.search_catalog(
        query, limit=max(1, min(int(limit), 100)),
        catalog_path=owned_catalog,
    )
    # Repo-level overlap is an annotation only; it does not change ownership.
    owned_repos = {
        str(item.get("repository", "")).lower()
        for item in owned
        if item.get("repository")
    }
    external_matches = []
    external_error = None
    if external:
        try:
            catalog = external_discovery.load_catalog(external_catalog)
            external_matches = external_discovery.search_catalog(
                query, catalog, limit=external_limit,
                exclude_repositories=owned_repos,
            )
        except external_discovery.ExternalCatalogError as exc:
            external_error = str(exc)
    return {
        "query": query,
        "sources": {
            "owned": "Maliky public catalog (read only)",
            "external": external_discovery.SOURCE_ID if external else None,
        },
        "owned": owned,
        "external": external_matches,
        "external_error": external_error,
        "disclaimer": (
            "Owned records retain their Maliky evidence status. External entries "
            "are unverified curated-list leads, not owned, installed or vetted "
            "tools. Inspect upstream implementations and licenses before use."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Application idea or desired capabilities")
    parser.add_argument("--external", action="store_true",
                        help="Opt in to fetch the public Every Awesome Repo catalog")
    parser.add_argument("--external-catalog-file", type=Path,
                        help="Use a local external JSON file (also enables external search)")
    parser.add_argument("--owned-catalog-file", type=Path,
                        help="Override the Maliky public catalog for offline testing")
    parser.add_argument("--limit", type=int, default=20, help="Maximum owned results")
    parser.add_argument("--external-limit", type=int, default=20,
                        help="Maximum external suggestions")
    args = parser.parse_args(argv)
    if args.limit < 1 or args.external_limit < 0:
        parser.error("--limit must be positive and --external-limit nonnegative")
    try:
        result = search_both(
            args.query,
            owned_catalog=args.owned_catalog_file,
            external=args.external,
            external_catalog=args.external_catalog_file,
            limit=args.limit,
            external_limit=args.external_limit,
        )
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(f"Search error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=True, indent=2))
    # An unavailable external index is deliberately non-fatal: owned search works.
    return 0


if __name__ == "__main__":
    sys.exit(main())
