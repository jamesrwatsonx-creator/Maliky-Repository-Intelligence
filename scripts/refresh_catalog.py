"""Incrementally refresh repository metadata, inspect new entries, and rebuild views."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys

import registry as r
from build_catalog import main as build_catalog
from validate_catalog import check as validate_catalog
from review_extracted_batch import prepare_repository_summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-discovery", action="store_true", help="Use this only when authenticated discovery was already run.")
    parser.add_argument("--max-files", type=int, default=500, help="Maximum source files read for each newly discovered repository.")
    args = parser.parse_args()
    before = {x["id"] for x in r.records("repositories")}
    if not args.skip_discovery:
        r.discover()
    after = r.records("repositories")
    added = [x for x in after if x["id"] not in before]
    inspected = []
    for repo in sorted(added, key=lambda x: x["github_id"]):
        result = prepare_repository_summary(repo, max_files=min(args.max_files, 12))
        inspected.append(result)
    statistics = r.build()
    registry_report = r.validate()
    build_catalog()
    catalog_report = validate_catalog()
    report = {
        "refreshed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "baseline_public_repositories": len(before),
        "public_repositories": len(after),
        "added": len(added),
        "new_repository_ids": [x["id"] for x in added],
        "new_repositories": [x["full_name"] for x in added],
        "new_repository_source_passes": inspected,
        "statistics": statistics,
        "registry_validation": {
            "valid": registry_report["valid"],
            "errors": registry_report.get("errors", [])[:20],
        },
        "catalog_validation": catalog_report,
    }
    r.write("system/catalog-refresh-report.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if registry_report["valid"] and catalog_report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
