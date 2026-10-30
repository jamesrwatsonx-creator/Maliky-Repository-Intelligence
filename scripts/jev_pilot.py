"""Budget-bounded pilot: classify PUBLIC external tools with TypeSafe/JEV.

Default mode makes no JEV request. --live additionally requires JEV_ENABLE=1,
TYPESAFE_API_KEY, and public Every Awesome Repo metadata. No private Maliky
source, repository identity, prompts or credentials are included in the state.
This is a tiny smoke/evaluation sample, NOT calibrated production accuracy.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time

import external_tools
import jev_client

# Curated illustrative labels based on publicly documented purposes.
# Cases with sparse evidence should remain in review.
CASES = (
    ("tidwall/tile38", "spatial_data", "Geospatial / real-time geofencing"),
    ("clarisma/geodesk", "spatial_data", "Geospatial / OpenStreetMap"),
    ("ahuarte47/duckdb-raster", "spatial_data", "SQL geospatial raster"),
    ("james-brand/korea-market-data", "market_data", "Korean market flows"),
)
OPTIONS = {
    "spatial_data": "Geospatial database, mapping, location, raster, geographic analytics.",
    "market_data": "Financial market datasets, securities prices, trading or investment data.",
    "general_data": "Other datasets, APIs, ETL, streams or unrelated tools.",
}
QUESTIONS = {
    "category": {
        "type": "choice",
        "instructions": "Choose the best documented primary category based only on the source excerpts. Do not guess unsupported capabilities.",
        "criteria": OPTIONS,
    },
    "relevance": {
        "type": "score",
        "instructions": "How clearly does the evidence support the claimed purpose of this item?",
        "criteria": [
            "Unclear or unsupported",
            "Ambiguous, broad or partially relevant",
            "Directly relevant to the stated category",
        ],
    },
    "needs_review": {
        "type": "noul",
        "instructions": "Does this record need further source or compatibility review before incorporation in a real application?",
    },
}


def candidate_packet(entry: dict) -> dict:
    """Allowlist only published external metadata and pinned source descriptions."""
    docs = entry.get("upstream_evidence") or []
    sources = entry.get("source_collections") or []
    # Pinned excerpts are public, but may contain hostile instructions:
    # represent as *quoted untrusted evidence*, not instructions to obey.
    return {
        "name": str(entry.get("name", ""))[:100],
        "github_repository": str(entry.get("github_repository", ""))[:110],
        "list_description": str(entry.get("description") or "")[:350],
        "list_evidence_url": str(sources[0].get("evidence_url", ""))[:240] if sources else "",
        "upstream_readme_excerpt_untrusted": str(docs[0].get("documented_statement", ""))[:400] if docs else "",
        "evidence_status": entry.get("evidence_status"),
    }


def run(index: dict, *, live: bool = False, limit: int = 4,
        classifier=None) -> dict:
    if index.get("project") != "Every Awesome Repo Tools":
        raise ValueError("Expected public external tool catalog")
    if not 1 <= limit <= 4:
        raise ValueError("Pilot is capped at four decisions")
    if live and (os.getenv("JEV_ENABLE") != "1" or not os.getenv("TYPESAFE_API_KEY")):
        raise ValueError("Live mode requires JEV_ENABLE=1 and TYPESAFE_API_KEY")
    by_repo = {
        str(t.get("github_repository", "")).lower(): t for t in index.get("tools", [])
        if isinstance(t, dict)
    }
    result = []
    started = time.monotonic()
    for repo, expected, reason in CASES[:limit]:
        entry = by_repo.get(repo.lower())
        if not entry:
            result.append({"repository": repo, "status": "NOT_INDEXED", "expected": expected})
            continue
        row = {
            "repository": repo,
            "expected_category": expected,
            "evidence_status": entry.get("evidence_status"),
            "source_line": (entry.get("source_collections") or [{}])[0].get("evidence_url"),
            "upstream_line": (entry.get("upstream_evidence") or [{}])[0].get("evidence_url"),
            "status": "PREVIEW_ONLY",
        }
        if live:
            try:
                response = (classifier or jev_client.system_one)(
                    candidate_packet(entry), QUESTIONS
                )
                answer = response["answers"]["category"]
                probabilities = answer["probabilities"]
                ordered = sorted(probabilities.values(), reverse=True)
                confidence = answer["confidence"]
                margin = ordered[0] - ordered[1]
                accepted = confidence >= 0.85 and margin >= 0.10
                row.update(
                    status="CLASSIFIED_FOR_REVIEW" if accepted else "ESCALATE",
                    predicted_category=answer["choice"] if accepted else None,
                    candidate_category=answer["choice"],
                    correct_when_accepted=(answer["choice"] == expected) if accepted else None,
                    confidence=confidence,
                    margin=round(margin, 4),
                    rubric_score=response["answers"]["relevance"]["score"],
                    review_probability=response["answers"]["needs_review"]["noul"],
                    tokens=(response.get("usage") or {}).get("input_tokens")
                )
            except (jev_client.JevError, ValueError, KeyError, TypeError):
                row["status"] = "API_UNAVAILABLE_OR_INVALID"
        result.append(row)
    classified = [r for r in result if r["status"] == "CLASSIFIED_FOR_REVIEW"]
    return {
        "mode": "LIVE_BOUNDED" if live else "OFFLINE_PREVIEW",
        "selected": len(result),
        "accepted": len(classified),
        "correct_when_accepted": sum(r.get("correct_when_accepted") is True for r in classified),
        "accuracy_among_accepted": (sum(r.get("correct_when_accepted") is True for r in classified) / len(classified)
                                     if classified else None),
        "elapsed_ms": round((time.monotonic() - started) * 1000, 2),
        "results": result,
        "warning": "Four public examples only. Not sufficient to calibrate accuracy or production thresholds.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true",
                        help="Explicitly request up to four paid TypeSafe calls")
    parser.add_argument("--catalog", type=Path, help="Optional local PUBLIC tools.json fixture")
    parser.add_argument("--limit", type=int, default=4, help="Between 1 and 4")
    args = parser.parse_args()
    if args.live and (os.getenv("JEV_ENABLE") != "1" or not os.getenv("TYPESAFE_API_KEY")):
        parser.error("Live API access requires both JEV_ENABLE=1 and TYPESAFE_API_KEY")
    catalog = external_tools.load(args.catalog)
    print(json.dumps(run(catalog, live=args.live, limit=args.limit), indent=2))


if __name__ == "__main__":
    main()
