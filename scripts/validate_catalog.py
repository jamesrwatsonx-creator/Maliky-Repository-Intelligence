"""Validate catalog coverage, provenance links, and generated Markdown links."""
from __future__ import annotations

import json
import pathlib
import re
import sys
from urllib.parse import unquote, urlsplit

import registry as r

ROOT = r.ROOT


def check():
    failures = []
    catalog_path = ROOT / "docs/catalog/catalog.json"
    if not catalog_path.is_file():
        return {"valid": False, "errors": ["missing docs/catalog/catalog.json"]}
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    items = data.get("items", [])
    ids = [x.get("id") for x in items]
    if len(ids) != len(set(ids)):
        failures.append("duplicate public catalog item ids")
    if len(items) != data.get("counts", {}).get("all_items"):
        failures.append("item count mismatch")
    repos = [x for x in items if x.get("kind") == "repository"]
    assets = [x for x in items if x.get("kind") == "asset"]
    canonical_repos = [x for x in r.records("repositories") if x.get("visibility") == "public"]
    canonical_entities = r.records("entities")
    active_entity_ids = {e["id"] for e in canonical_entities if any(repo["id"] == e["source"].get("repository_id") and repo.get("inspected_commit") == e["source"].get("inspected_commit") for repo in canonical_repos)}
    if {x["id"] for x in repos} != {x["id"] for x in canonical_repos}:
        failures.append("public repository coverage differs from canonical repository registry")
    if {x["id"] for x in assets} != active_entity_ids:
        failures.append("active asset coverage differs from canonical entity registry")
    exported_repos = {x['id']: x for x in repos}
    for repo in canonical_repos:
        info = repo.get('repository_intelligence', {})
        if info.get('status') == 'COMPLETE':
            exported = exported_repos.get(repo['id'], {})
            for field in ('capability_clusters', 'keywords', 'important_subsystems', 'asset_presence', 'runtime', 'license_notes', 'risk_notes', 'reuse_recommendation', 'source_evidence'):
                if exported.get(field) != info.get(field): failures.append(repo['id']+': summary export mismatch '+field)
            if exported.get('completion_scope') != r.SUMMARY_POLICY: failures.append(repo['id']+': summary scope missing')
    for item in assets:
        required = ("id", "name", "repository", "repository_url", "source_path", "source_url", "review_status", "evidence_status", "inspected_commit", "blob_sha")
        missing = [key for key in required if not item.get(key)]
        if missing:
            failures.append(f"{item.get('id')}: missing export fields {','.join(missing)}")
        if item.get("review_status") not in ("VERIFIED", "NEEDS_REVIEW"):
            failures.append(f"{item.get('id')}: unknown review status")
    for item in repos:
        if not item.get("description"):
            failures.append(f"{item.get('id')}: blank repository description")
        if item.get("description_status") == "NEEDS_DESCRIPTION" and "NEEDS DESCRIPTION" not in item.get("description", ""):
            failures.append(f"{item.get('id')}: unresolved description is not labeled")
    if len(data.get("topics", [])) < 1:
        failures.append("no populated purpose topics")
    if len(data.get("asset_types", [])) < 1:
        failures.append("no populated asset types")

    # Validate local Markdown targets in all generated navigation and documentation.
    markdown_files = [ROOT / "README.md", *((ROOT / "browse").rglob("*.md"))]
    markdown_files += [ROOT / p for p in ("docs/AGENT-ACCESS.md", "docs/APP-IDEA-RESEARCH.md", "docs/CATALOG-REFRESH.md") if (ROOT / p).exists()]
    links_checked = 0
    link_re = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
    for file in markdown_files:
        content = file.read_text(encoding="utf-8", errors="replace")
        for raw in link_re.findall(content):
            target = raw.strip().split()[0].strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or target.startswith("//") or not parsed.path:
                continue
            links_checked += 1
            local = (file.parent / unquote(parsed.path)).resolve()
            try:
                local.relative_to(ROOT.resolve())
            except ValueError:
                failures.append(f"{file.relative_to(ROOT)}: local link escapes repository: {target}")
                continue
            if not local.exists():
                failures.append(f"{file.relative_to(ROOT)}: broken link: {target}")
    generated = [ROOT / "README.md", ROOT / "browse/README.md", ROOT / "docs/catalog/index.html", ROOT / "docs/catalog/app.js", ROOT / "docs/catalog/styles.css"]
    missing_generated = [x.relative_to(ROOT).as_posix() for x in generated if not x.is_file()]
    failures.extend("missing generated page: " + x for x in missing_generated)
    return {"valid": not failures, "errors": failures, "repositories": len(repos), "assets": len(assets), "asset_types": len(data.get("asset_types", [])), "topics": len(data.get("topics", [])), "capabilities": len(data.get("capabilities", [])), "markdown_files_checked": len(markdown_files), "local_links_checked": links_checked}


if __name__ == "__main__":
    report = check()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if report["valid"] else 1)
