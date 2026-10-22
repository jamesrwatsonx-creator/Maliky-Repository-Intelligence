"""Fast deterministic search over the generated public catalog export."""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CATALOG = ROOT / "docs" / "catalog" / "catalog.json"


def tokens(value):
    return re.findall(r"[a-z0-9]+", (value or "").lower())


def search_catalog(query="", asset_type=None, topic=None, repository=None, status=None, kind="all", limit=20, catalog_path=CATALOG):
    data = json.loads(pathlib.Path(catalog_path).read_text(encoding="utf-8"))
    terms = tokens(query)
    type_value = (asset_type or "").lower()
    topic_value = (topic or "").lower().replace(" ", "-")
    repo_value = (repository or "").lower()
    status_value = (status or "").lower()
    results = []
    for item in data.get("items", []):
        if kind == "assets" and item.get("kind") != "asset":
            continue
        if kind == "repositories" and item.get("kind") != "repository":
            continue
        if type_value and type_value not in {str(item.get("asset_type", "")).lower(), str(item.get("entity_type", "")).lower(), str(item.get("entity_type", "")).lower().replace("_", " ")}:
            continue
        item_topics = {str(x).lower() for x in item.get("topics", [])}
        if topic_value and topic_value not in item_topics:
            continue
        if repo_value and repo_value not in str(item.get("repository", "")).lower():
            continue
        if status_value and status_value not in {str(item.get("review_status", "")).lower(), str(item.get("evidence_status", "")).lower()}:
            continue
        searchable = " ".join(filter(None, [item.get("name", ""), item.get("asset_type", ""), item.get("entity_type", ""), item.get("description", ""), item.get("repository", ""), item.get("source_path", ""), item.get("technology", ""), item.get("language", ""), " ".join(item.get("categories", [])), " ".join(item.get("capabilities", [])), " ".join(item.get("topics", [])), " ".join(item.get("keywords") or []),
                                               " ".join(c['name']+' '+c['description'] for c in item.get('capability_clusters') or []),
                                               " ".join(s['name']+' '+s['purpose'] for s in item.get('important_subsystems') or [])]))
        haystack = tokens(searchable)
        word_set = set(haystack)
        overlap = sum(term in word_set for term in terms)
        if terms and overlap == 0:
            continue
        score = overlap
        if item.get('completion_scope') == 'REPOSITORY_CLUSTERS_V1': score += 2
        name_tokens = set(tokens(item.get("name", "")))
        repo_tokens = set(tokens(item.get("repository", "")))
        score += 4 * sum(term in name_tokens for term in terms)
        score += 2 * sum(term in repo_tokens for term in terms)
        if query and query.lower() in str(item.get("name", "")).lower():
            score += 8
        if query and query.lower() in str(item.get("description", "")).lower():
            score += 2
        results.append((score, item))
    results.sort(key=lambda pair: (-pair[0], str(pair[1].get("name", "")).lower(), pair[1].get("id", "")))
    return [{**item, "match_score": score} for score, item in results[: max(1, limit)]]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="?", default="")
    parser.add_argument("--type", dest="asset_type")
    parser.add_argument("--topic")
    parser.add_argument("--repository")
    parser.add_argument("--status")
    parser.add_argument("--kind", choices=("all", "assets", "repositories"), default="all")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args(argv)
    results = search_catalog(args.query, args.asset_type, args.topic, args.repository, args.status, args.kind, args.limit)
    # Escaping non-ASCII keeps the JSON CLI reliable in Windows legacy consoles.
    print(json.dumps(results, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
