"""Generate the human-readable Codex handoff from canonical registry state."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess


ROOT = pathlib.Path(__file__).resolve().parents[1]


def read_json(path: str, default):
    target = ROOT / path
    if not target.exists():
        return default
    return json.loads(target.read_text(encoding="utf-8"))


def records(kind: str):
    folder = ROOT / "registry" / kind
    return [read_json(str(path.relative_to(ROOT)), {}) for path in folder.glob("*.json")]


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, capture_output=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def explicit_deep_review_items(repositories, entities):
    items = []
    for repo in repositories:
        phase = str(repo.get("next_phase", ""))
        progress = repo.get("semantic_review_progress") or {}
        review = repo.get("deep_review") or {}
        triggers = review.get("triggers") or review.get("trigger") or []
        required = review.get("required") is True
        if "DEEP" in phase or progress.get("review_policy") == "DEEP" or required or triggers:
            items.append(repo["full_name"])
    for entity in entities:
        metadata = entity.get("metadata") or {}
        if metadata.get("deep_review_required") is True or metadata.get("review_policy") == "DEEP":
            items.append(entity["id"])
    return sorted(set(items))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current-repository")
    parser.add_argument("--next-action")
    parser.add_argument("--tests-state", default="See system/test-report.json")
    parser.add_argument("--catalog-state", default="See latest validate_catalog.py output")
    parser.add_argument("--checkpoint-state", default="Working tree pending checkpoint")
    parser.add_argument("--blocker", action="append", default=[])
    args = parser.parse_args()

    manifest = read_json("system/discovery-manifest.json", {})
    inspection = read_json("system/inspection-state.json", {})
    statistics = read_json("system/statistics.json", {})
    refresh = read_json("system/catalog-refresh-report.json", {})
    validation = read_json("system/validation-report.json", {})
    publication = read_json("system/publication-report.json", {})
    repositories = records("repositories")
    entities = records("entities")
    capabilities = records("capabilities")
    by_name = {repo["full_name"]: repo for repo in repositories}
    by_id = {repo["id"]: repo for repo in repositories}

    complete = [repo for repo in repositories if repo.get("state") == "COMPLETE"]
    last_complete = max(complete, key=lambda repo: repo.get("inspection_date") or "", default=None)

    refresh_ids = refresh.get("new_repository_ids", [])
    refresh_pending = [
        by_id[repo_id]
        for repo_id in refresh_ids
        if repo_id in by_id and by_id[repo_id].get("state") != "COMPLETE"
    ]
    current = by_name.get(args.current_repository) if args.current_repository else None
    if current is None and refresh_pending:
        current = refresh_pending[0]
    if current is None and inspection.get("next"):
        current = by_name.get(inspection["next"].get("repository"))

    queue = inspection.get("queue", [])
    if refresh_pending:
        prioritized = [
            {
                "repository": repo["full_name"],
                "next_phase": repo.get("next_phase", "STRUCTURE"),
            }
            for repo in refresh_pending
        ]
        prioritized_names = {item["repository"] for item in prioritized}
        queue = prioritized + [
            item for item in queue if item["repository"] not in prioritized_names
        ]
    next_queue = [item for item in queue if not current or item["repository"] != current["full_name"]][:5]
    added = refresh.get("added")
    if added is None:
        added = len(refresh.get("new_repositories", []))

    deep_items = explicit_deep_review_items(repositories, entities)
    counts = manifest.get("counts", {})
    state_counts = statistics.get("repositories_by_state", {})
    decisions = statistics.get("decision_records", {})
    generated_at = dt.datetime.now(dt.timezone.utc).isoformat()
    branch = git("branch", "--show-current")
    head = git("rev-parse", "HEAD")
    pushed = git("rev-parse", "--verify", "@{upstream}")

    current_name = current.get("full_name") if current else "none"
    current_commit = current.get("inspected_commit") if current else None
    current_phase = current.get("next_phase") if current else None
    next_action = args.next_action or (
        f"Resume {current_name} at {current_phase}." if current else "Queue is clear."
    )

    lines = [
        "# Codex resume",
        "",
        "> Generated from canonical registry, discovery, inspection, validation and Git state. Verify against `system/inspection-state.json` before continuing.",
        "",
        "## Durable checkpoint",
        "",
        f"- Canonical branch: `{branch}`",
        f"- Local HEAD at generation: `{head}`",
        f"- Latest known pushed SHA: `{pushed}`",
        f"- Generated at: `{generated_at}`",
        f"- Checkpoint state: {args.checkpoint_state}",
        "",
        "## Live discovery summary",
        "",
        f"- Accessible repositories: {counts.get('owned', 'unknown')}",
        f"- Public repositories: {counts.get('public_owned', 'unknown')}",
        f"- Private repositories: {counts.get('private_owned', 'unknown')}",
        f"- Discovery manifest public records: {len(manifest.get('repositories', []))}",
        f"- Repositories discovered in the latest refresh: {added}",
        f"- Latest refresh repositories semantically complete: {refresh.get('semantic_intake_complete', 0)}",
        "",
        "## Resume pointer",
        "",
        f"- Last repository fully completed: {last_complete['full_name'] if last_complete else 'none'}",
        f"- Repository currently being processed: {current_name}",
        f"- Pinned commit: `{current_commit or 'none'}`",
        f"- Current phase: `{current_phase or 'none'}`",
        f"- Exact next action: {next_action}",
        "- Next repositories in canonical queue:",
    ]
    if next_queue:
        lines.extend(
            f"  - `{item['repository']}` — `{item.get('next_phase', 'STRUCTURE')}`"
            for item in next_queue
        )
    else:
        lines.append("  - none")

    lines.extend([
        "",
        "## Canonical counts",
        "",
        "- Repository states: " + (", ".join(f"{key}={value}" for key, value in sorted(state_counts.items())) or "none"),
        f"- Active entity records: {statistics.get('active_entity_records', 'unknown')}",
        f"- Verified entity records: {statistics.get('verified_entity_records', 'unknown')}",
        f"- Candidate entity records: {statistics.get('candidate_entity_records', 'unknown')}",
        f"- Historical entity records: {statistics.get('historical_entity_records', 'unknown')}",
        f"- Capability records: {len(capabilities)}",
        f"- Search documents: {statistics.get('search_documents', 'unknown')}",
        "- JEV decision records: " + (", ".join(f"{key}={value}" for key, value in sorted(decisions.items())) or "none"),
        f"- Outstanding explicit deep review items: {len(deep_items)}",
    ])
    lines.extend(f"  - `{item}`" for item in deep_items[:20])
    if len(deep_items) > 20:
        lines.append(f"  - plus {len(deep_items) - 20} more")

    lines.extend([
        "",
        "## Validation",
        "",
        f"- Registry validation: {'PASS' if validation.get('valid') else 'FAIL/STALE'} ({validation.get('validated_at', 'timestamp unavailable')})",
        f"- Catalog validation: {args.catalog_state}",
        f"- Unit tests: {args.tests_state}",
        f"- Publication guard: {'PASS' if publication.get('valid') else 'FAIL/STALE'}",
        "",
        "## Blockers",
        "",
    ])
    lines.extend(f"- {blocker}" for blocker in args.blocker)
    if not args.blocker:
        lines.append("- None recorded.")
    lines.extend([
        "",
        "Canonical truth remains in the registry, discovery manifest, inspection state, evidence records and pinned source cache.",
        "",
    ])

    target = ROOT / "docs" / "CODEX-RESUME.md"
    target.write_text("\n".join(lines), encoding="utf-8")
    print(target.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
