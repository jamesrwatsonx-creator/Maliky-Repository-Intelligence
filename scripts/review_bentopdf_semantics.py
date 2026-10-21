"""Lean semantic census of BentoPDF at its pinned intake revision.

The tool index is the source-supported boundary for the browser PDF tools. Each
documented tool remains individually searchable. Repository CI and packaging
declarations are folded into the web application or excluded. Source is read only.
"""
from __future__ import annotations

import json
import re

from lean_review_lib import LeanReview
import registry as r


FULL_NAME = "jamesrwatsonx-creator/bentopdf-edit-website-text-locally.-save-it-connect-it-"
COMMIT = "872a32929e0ee90c67c104e661be31433ff7b4df"
INDEX_PATH = "docs/tools/index.md"

TOOL_PATTERN = re.compile(
    r"^- \[\*\*(?P<name>.+?)\*\*\]\(\./(?P<slug>[^)]+)\)\s+[^A-Za-z0-9]+\s*(?P<description>.+?)\s*$",
    re.MULTILINE,
)

SECURITY_TOOLS = {
    "change-permissions",
    "digital-sign-pdf",
    "edit-pdf",
    "flatten-pdf",
    "protect-pdf",
    "remove-annotations",
    "remove-metadata",
    "remove-restrictions",
    "sanitize-pdf",
    "sign-pdf",
    "unlock-pdf",
    "validate-signature-pdf",
}

VISION_TOOLS = {"ocr-pdf", "deskew-pdf", "extract-tables", "extract-images"}


def complete_scoped(review: LeanReview, result: dict) -> dict:
    repo = review.repo
    repo.update({"state": "COMPLETE", "next_phase": "COMPLETE"})
    repo.setdefault("phases", {}).update(
        {
            "structure": True,
            "entity_extraction": True,
            "capability_analysis": True,
            "deep_review": True,
            "validation": True,
        }
    )
    repo["deep_review"] = {
        "completed": True,
        "reviewer": "Automated scoped static review",
        "evidence": [
            {"type": "source_review", "value": review.url("README.md", 1)},
            {"type": "source_review", "value": review.url("docs/licensing.md", 1)},
            {"type": "source_review", "value": review.url("docs/tools/digital-sign-pdf.md", 1)},
            {"type": "source_review", "value": review.url("docs/tools/sanitize-pdf.md", 1)},
        ],
        "conclusion": (
            "Inventory is complete. Deployments must review AGPL or commercial terms, "
            "third-party AGPL WASM obligations, runtime CDN trust, PDF parser exposure, "
            "digital-signature keys and certificates, CORS proxy configuration, browser "
            "isolation, memory limits, file persistence and the accuracy of redaction, "
            "sanitization, password and signature operations. No PDF, browser code, WASM "
            "module, container or workflow was executed."
        ),
        "runtime_tested": False,
    }
    repo.pop("review_reason", None)
    r.write(r.repo_file(repo), repo)
    return {**result, "state": "COMPLETE", "scoped_review": "COMPLETE"}


def review_bentopdf() -> dict:
    review = LeanReview(FULL_NAME, COMMIT)
    review.load_snapshot(
        wanted=lambda path: path in {"README.md", "package.json", "docs/licensing.md", "chart/README.md", INDEX_PATH}
        or (path.startswith("docs/tools/") and path.endswith(".md"))
    )
    categories = [
        "category:application-security",
        "category:creative-tools",
        "category:full-stack-applications",
        "category:kubernetes-orchestration",
        "category:privacy",
        "category:productivity",
        "category:web-applications",
    ]

    product = review.make("APP", "BentoPDF Web Application", "package.json", 1)
    review.finish(
        product,
        "Self-hostable privacy-first browser application providing a large collection of client-side PDF editing, conversion, organization, extraction, optimization and security tools.",
        [("bentopdf-browser-pdf-toolkit", "BentoPDF browser PDF toolkit", ["BentoPDF", "client-side PDF toolkit"])],
        "LICENSE REVIEW REQUIRED",
        "operational:23",
        "CORE",
        "FULL",
        ["modern browser", "static web hosting or container", "optional runtime-loaded WASM processors"],
        "Top-level application containing the individually documented PDF tools.",
        categories,
        [],
        extra={
            "version": "2.8.8",
            "license": "AGPL-3.0-only or commercial license",
            "processing_model": "client-side browser",
            "server_upload_required": False,
        },
    )

    matches = list(TOOL_PATTERN.finditer(review.files[INDEX_PATH]))
    if len(matches) != 114:
        raise ValueError(f"Expected 114 indexed BentoPDF tools, found {len(matches)}")
    slugs = [match.group("slug") for match in matches]
    if len(set(slugs)) != len(slugs):
        raise ValueError("BentoPDF tool index contains duplicate slugs")

    for match in matches:
        name = match.group("name").strip()
        slug = match.group("slug").strip()
        description = match.group("description").strip()
        path = f"docs/tools/{slug}.md"
        if path not in review.files:
            raise ValueError(f"Indexed BentoPDF tool has no verified document: {path}")
        entity = review.make("TOOL", name, path, 1)
        if slug in SECURITY_TOOLS:
            recommendation = "SECURITY REVIEW REQUIRED"
            operational = "operational:13"
        elif slug in VISION_TOOLS:
            recommendation = "USE DIRECTLY"
            operational = "operational:08"
        elif slug == "pdf-workflow":
            recommendation = "USE DIRECTLY"
            operational = "operational:18"
        else:
            recommendation = "USE DIRECTLY"
            operational = "operational:23"
        review.finish(
            entity,
            description,
            [(f"bentopdf-{slug}", f"BentoPDF {name}", [name, slug.replace("-", " ")])],
            recommendation,
            operational,
            "TOOL",
            "PARTIAL",
            ["BentoPDF web application", "modern browser", "tool-specific JavaScript or WASM dependencies"],
            "Individually documented browser tool provided by the BentoPDF application.",
            categories,
            [],
            extra={
                "license": "AGPL-3.0-only or commercial license",
                "client_side": True,
                "indexed_tool_slug": slug,
            },
        )
        entity["evidence"].append(
            {"type": "source_review", "value": review.url(INDEX_PATH, 1)}
        )
        r.write("registry/entities/" + entity["id"].split(":", 1)[1] + ".json", entity)
        review.relate("PROVIDES", product["id"], entity["id"], INDEX_PATH, 1)

    chart = review.make("INFRASTRUCTURE_MODULE", "BentoPDF Helm Chart", "chart/README.md", 1)
    review.finish(
        chart,
        "Helm deployment package for serving BentoPDF's static frontend from a single NGINX container through a Service, Ingress or Gateway API route.",
        [("bentopdf-helm-chart", "BentoPDF Helm chart", ["BentoPDF Kubernetes chart"])],
        "SECURITY REVIEW REQUIRED",
        "operational:15",
        "DEPLOYMENT",
        "PARTIAL",
        ["Kubernetes", "Helm", "BentoPDF container image", "configured ingress or gateway"],
        "Deployment packaging for the browser application.",
        categories,
        [],
        extra={"license": "AGPL-3.0-only or commercial license"},
    )
    review.relate("COMPLEMENTS", product["id"], chart["id"], "chart/README.md", 1)

    retained = set(review.out)
    for entity in review.existing:
        if entity["id"] not in retained:
            review.drop(entity)

    result = review.finalize(
        categories,
        [],
        "LICENSE REVIEW REQUIRED",
        "operational:23",
        {
            "APP": "Client-side BentoPDF application retained as the product boundary.",
            "TOOL": "All 114 uniquely indexed PDF tools retained as individually searchable capabilities.",
            "INFRASTRUCTURE_MODULE": "Helm deployment package retained.",
            "PACKAGE": "Root package declaration folded into the web application.",
            "WORKFLOW": "Repository CI, deployment, release, scanning, badge and maintenance workflows are not standalone product capabilities.",
        },
        deep_review=(
            "License, sensitive-file and security-operation triggers were reviewed narrowly. BentoPDF is dual licensed, preconfigures runtime CDN URLs for AGPL WASM processors, "
            "handles untrusted documents in a browser, and includes password, permission, sanitization, redaction and cryptographic-signature tools."
        ),
        details=[
            "ten repository CI, deployment, scanning and maintenance workflows",
            "page-level implementation modules represented by their indexed tool",
            "marketing and documentation build scripts",
        ],
    )
    return complete_scoped(review, result)


def main() -> None:
    result = review_bentopdf()
    r.build()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
