"""Requeue repositories completed only by static declaration promotion.

Pinned evidence and candidate entities are preserved.  Generated capabilities
are downgraded to candidates until a lean semantic review verifies them.
"""
from __future__ import annotations

import json

import registry as r


REVIEWER = "deterministic source-declaration promotion"


def main() -> None:
    repositories = r.records("repositories")
    entities = r.records("entities")
    capabilities = {cap["id"]: cap for cap in r.records("capabilities")}
    requeued = []

    for repo in repositories:
        progress = repo.get("semantic_review_progress", {})
        if repo.get("state") != "COMPLETE" or progress.get("reviewer") != REVIEWER:
            continue

        active = [
            entity
            for entity in entities
            if entity["source"]["repository_id"] == repo["id"]
            and entity["source"]["inspected_commit"] == repo.get("inspected_commit")
        ]
        unresolved = []
        evidence = r.read("system/evidence/" + str(repo["github_id"]) + ".json", {})
        unresolved = [
            error for error in evidence.get("errors", []) if not error.get("review_resolution")
        ]

        for entity in active:
            entity["review_status"] = "NEEDS_REVIEW"
            entity["recommendation"] = "NEEDS DEEPER REVIEW"
            entity.setdefault("metadata", {}).update(
                {
                    "semantic_review": "Static source-declaration candidate; semantic review pending.",
                    "review_policy": "LEAN",
                }
            )
            r.write("registry/entities/" + entity["id"].split(":", 1)[1] + ".json", entity)
            for capability_id in entity.get("capabilities", []):
                capability = capabilities.get(capability_id)
                if capability and entity["id"] in capability.get("providers", []):
                    capability["status"] = "CANDIDATE"
                    capability["verification_scope"] = "Pinned source declaration; semantic review pending"
                    r.write("registry/capabilities/" + capability_id.split(":", 1)[1] + ".json", capability)

        counts = __import__("collections").Counter(entity["entity_type"] for entity in active)
        for kind, census in repo.get("entity_census", {}).items():
            repo["entity_census"][kind] = {
                **census,
                "detected": max(census.get("detected", 0), counts[kind]),
                "catalogued": counts[kind],
                "reviewed": False,
                "detection_scope": "pinned source declarations; semantic review pending",
            }
        repo.update(
            {
                "state": "NEEDS_REVIEW",
                "next_phase": "SOURCE_EVIDENCE_REVIEW" if unresolved else "CAPABILITY_ANALYSIS",
                "recommendation": "NEEDS DEEPER REVIEW",
                "review_reason": "Prior completion used static declarations without a semantic census; lean review required.",
                "semantic_review_progress": {
                    "status": "PENDING",
                    "review_policy": "LEAN",
                    "reason": "source_parse_errors" if unresolved else "static_candidates_require_semantic_review",
                    "candidate_entity_count": len(active),
                    "source_errors": unresolved,
                    "requeued_at": r.now(),
                },
            }
        )
        repo.setdefault("phases", {}).update(
            {"entity_extraction": False, "capability_analysis": False, "validation": False}
        )
        r.write(r.repo_file(repo), repo)
        requeued.append({"repository": repo["full_name"], "entities": len(active), "source_errors": len(unresolved)})

    statistics = r.build()
    print(json.dumps({"requeued": requeued, "count": len(requeued), "statistics": statistics}, indent=2))


if __name__ == "__main__":
    main()
