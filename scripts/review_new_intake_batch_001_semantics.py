"""Lean semantic review for the first repositories in the 2026-10-20 intake.

All decisions use the pinned, blob-verified source evidence produced by the
intake pipeline.  Inspected repository code is never imported or executed.
"""
from __future__ import annotations

import json

from lean_review_lib import LeanReview
import registry as r


def one(review: LeanReview, kind: str, *, path: str):
    found = review.find(kind, path=path)
    if len(found) != 1:
        raise ValueError(f"Expected one {kind} at {path}, found {len(found)}")
    return found[0]


def complete_scoped(
    review: LeanReview,
    result: dict,
    evidence: list[tuple[str, int]],
    conclusion: str,
) -> dict:
    """Complete inventory work while preserving a scoped deployment warning."""
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
            {"type": "source_review", "value": review.url(path, line)}
            for path, line in evidence
        ],
        "conclusion": conclusion,
        "runtime_tested": False,
    }
    repo.pop("review_reason", None)
    r.write(r.repo_file(repo), repo)
    return {**result, "state": "COMPLETE", "scoped_review": "COMPLETE"}


def review_phone_harness() -> dict:
    review = LeanReview(
        "jamesrwatsonx-creator/phone-harness",
        "8ad9a8b764c59a4bebe2a50ca457e50e557ee550",
    )
    categories = [
        "category:automation-scripting",
        "category:cli-tools",
        "category:developer-tools",
        "category:mobile-applications",
        "category:plugins-extensions",
        "category:skills",
    ]

    package = one(review, "PACKAGE", path="pyproject.toml")
    review.finish(
        package,
        "Python device-automation runtime exposing one API for local iPhone Mirroring, Android over adb, hosted Android and remote iPhone control.",
        [
            (
                "cross-platform-phone-automation-runtime",
                "Cross-platform phone automation runtime",
                ["phone-harness", "iPhone and Android automation"],
            )
        ],
        "SECURITY REVIEW REQUIRED",
        "operational:06",
        "CORE",
        "FULL",
        ["Python 3.10+", "adb for local Android", "macOS Vision and Accessibility APIs for iPhone Mirroring"],
        "Shared transport and helper implementation used by the CLI, skill and Hermes integration.",
        categories,
        [],
        extra={"license": "MIT", "privileged_device_access": True},
    )

    cli = one(review, "CLI", path="pyproject.toml")
    review.finish(
        cli,
        "Command-line entry point for device setup, diagnostics, skill installation and fresh-interpreter Python scripts with phone-control helpers preloaded.",
        [
            (
                "phone-control-script-runner",
                "Phone-control script runner",
                ["phone-harness CLI", "agent phone script execution"],
            )
        ],
        "SECURITY REVIEW REQUIRED",
        "operational:06",
        "INTERFACE",
        "PARTIAL",
        ["phone-harness Python package", "configured phone transport"],
        "Executes caller-supplied Python against the selected device runtime.",
        categories,
        [],
        extra={"arbitrary_code_execution": True},
    )

    skill = one(review, "SKILL", path="SKILL.md")
    review.finish(
        skill,
        "Agent skill documenting a consistent screen, OCR, tap, typing, navigation, scrolling, application and multi-device control workflow.",
        [
            (
                "agent-phone-control-skill",
                "Agent phone-control skill",
                ["phone-harness skill", "mobile device control skill"],
            )
        ],
        "SECURITY REVIEW REQUIRED",
        "operational:06",
        "SKILL",
        "PARTIAL",
        ["phone-harness package", "paired or hosted device", "required host permissions"],
        "Instruction surface for agents using the package helpers; it does not provide a device transport by itself.",
        categories,
        [],
    )

    plugin = review.make(
        "PLUGIN", "Phone Harness Hermes Plugin", "integrations/hermes/__init__.py", 1
    )
    review.finish(
        plugin,
        "Hermes Agent plugin that installs the phone-harness runtime and skill, registers confirmation hooks and exposes phone script execution.",
        [
            (
                "phone-harness-hermes-plugin",
                "Phone Harness Hermes plugin",
                ["Hermes phone plugin", "phone-harness integration"],
            )
        ],
        "SECURITY REVIEW REQUIRED",
        "operational:06",
        "INTEGRATION",
        "PARTIAL",
        ["Hermes Agent", "phone-harness", "configured phone transport"],
        "Packages the skill and provides the phone_exec tool represented separately.",
        categories,
        [],
        extra={"default_confirmation_hook": True},
    )

    tool = review.make("TOOL", "phone_exec", "integrations/hermes/__init__.py", 1)
    review.finish(
        tool,
        "Hermes tool that runs model-supplied Python in a fresh child interpreter with phone helpers pre-imported and returns bounded output and screenshots.",
        [
            (
                "hermes-phone-script-execution",
                "Hermes phone script execution",
                ["phone_exec", "Hermes device control tool"],
            )
        ],
        "SECURITY REVIEW REQUIRED",
        "operational:06",
        "TOOL",
        "PARTIAL",
        ["Phone Harness Hermes plugin", "phone-harness", "user-approved device access"],
        "The plugin asks before calls by default; classifier-only auto-run is opt-in and explicitly described as bypassable.",
        categories,
        [],
        extra={"arbitrary_code_execution": True, "privileged_device_access": True},
    )

    for entity in review.existing:
        if entity["entity_type"] == "WORKFLOW":
            review.drop(entity)

    review.relate("DEPENDS_ON", cli["id"], package["id"], "pyproject.toml", 1)
    review.relate("COMPLEMENTS", skill["id"], package["id"], "SKILL.md", 1)
    review.relate("PROVIDES", plugin["id"], tool["id"], "integrations/hermes/__init__.py", 1)
    review.relate("DEPENDS_ON", tool["id"], package["id"], "integrations/hermes/__init__.py", 1)

    result = review.finalize(
        categories,
        [],
        "SECURITY REVIEW REQUIRED",
        "operational:06",
        {
            "PACKAGE": "Cross-device automation runtime retained.",
            "CLI": "Device setup and caller-supplied script runner retained.",
            "SKILL": "Agent operating instructions retained.",
            "PLUGIN": "Hermes integration retained.",
            "TOOL": "Hermes phone_exec surface retained.",
            "WORKFLOW": "Repository CI and publication workflows are not standalone catalog capabilities.",
        },
        deep_review="Privileged-device and arbitrary-execution trigger reviewed narrowly. The runtime can observe and operate real or hosted phones, while its CLI and Hermes tool run caller/model-supplied Python. Hermes requests approval by default and scrubs likely credential variables, but classifier-only auto-run is opt-in and heuristic.",
        details=["project CI workflow", "package publication workflow", "backend-specific transport internals"],
    )
    return complete_scoped(
        review,
        result,
        [("README.md", 1), ("SKILL.md", 1), ("integrations/hermes/__init__.py", 1)],
        "Inventory is complete. Deployment requires explicit confirmation, trusted script generation, least-privilege host/device permissions, protected cloud-phone credentials and isolation appropriate for arbitrary Python execution; no device or script was run.",
    )


def review_superdesign() -> dict:
    review = LeanReview(
        "jamesrwatsonx-creator/superdesign-Front-end",
        "49e2b9dd9615c6dae936b326b1ddb85d4f1d6f19",
    )
    categories = [
        "category:ai-agents",
        "category:creative-tools",
        "category:design-systems",
        "category:developer-tools",
        "category:plugins-extensions",
    ]

    for entity in review.existing:
        review.drop(entity)

    plugin = review.make("PLUGIN", "SuperDesign IDE Extension", "package.json", 1)
    review.finish(
        plugin,
        "Historical VS Code-compatible extension for generating UI mockups, reusable components and wireframes from natural-language prompts inside an IDE.",
        [
            (
                "ide-native-ai-design-extension",
                "IDE-native AI design extension",
                ["SuperDesign IDE extension", "AI UI design plugin"],
            )
        ],
        "SECURITY REVIEW REQUIRED",
        "operational:03",
        "CORE",
        "PARTIAL",
        ["VS Code 1.90+", "model-provider credentials", "Node.js extension host"],
        "The upstream README marks this 2025 extension historical and no longer actively maintained.",
        categories,
        [],
        extra={"maintenance_status": "historical; no longer actively maintained"},
    )

    agent = review.make(
        "AGENT", "SuperDesign Custom Design Agent", "src/services/customAgentService.ts", 1
    )
    review.finish(
        agent,
        "Model-provider-backed design agent with workspace read, write, edit, search, listing, theme and shell tools for producing and revising interface artifacts.",
        [
            (
                "tool-using-ui-design-agent",
                "Tool-using UI design agent",
                ["SuperDesign agent", "IDE design agent"],
            )
        ],
        "SECURITY REVIEW REQUIRED",
        "operational:03",
        "CORE",
        "PARTIAL",
        ["Vercel AI SDK", "OpenAI, Anthropic or OpenRouter credentials", "writable IDE workspace"],
        "Runs inside the extension and can mutate workspace files or invoke shell commands.",
        categories,
        [],
        extra={"arbitrary_command_execution": True, "workspace_mutation": True},
    )

    review.relate("CONTAINS", plugin["id"], agent["id"], "src/extension.ts", 1)

    result = review.finalize(
        categories,
        [],
        "SECURITY REVIEW REQUIRED",
        "operational:03",
        {
            "PLUGIN": "IDE extension retained as the product integration surface.",
            "AGENT": "Design agent retained as a separate tool-using capability.",
            "PACKAGE": "Extension package declaration folded into the plugin entity.",
            "UI_COMPONENT": "Generic icon glyphs are implementation fragments rather than standalone reusable capabilities.",
            "WORKFLOW": "Extension publication CI is repository-specific.",
        },
        deep_review="Credential, workspace-mutation and arbitrary-command triggers reviewed narrowly. The custom agent connects to configured model providers and registers file mutation plus shell tools. The shell helper checks a short unsafe-pattern list, which is not a complete command sandbox, and the upstream README says the extension is no longer maintained.",
        details=["generic icon components", "extension publication workflow", "provider and webview implementation internals"],
    )
    return complete_scoped(
        review,
        result,
        [("README.md", 1), ("src/services/customAgentService.ts", 1), ("src/tools/bash-tool.ts", 1)],
        "Inventory is complete. Use requires protected provider credentials, explicit workspace and command boundaries, review of generated shell/file operations and acceptance of the extension's unmaintained status; no provider or command was invoked.",
    )


def review_one_time() -> dict:
    review = LeanReview(
        "jamesrwatsonx-creator/1time.io",
        "69c7c5da0d223c257d3079ecf2c05abea030fcee",
    )
    categories = [
        "category:application-security",
        "category:backend-services",
        "category:cli-tools",
        "category:plugins-extensions",
        "category:privacy",
        "category:web-applications",
    ]

    cli = one(review, "CLI", path="cli/package.json")
    review.finish(
        cli,
        "Node.js command-line client that encrypts text or files locally, creates self-destructing links, and decrypts one-time links for terminal workflows.",
        [
            (
                "encrypted-one-time-secret-cli",
                "Encrypted one-time secret CLI",
                ["1time CLI", "terminal secret sharing"],
            )
        ],
        "SECURITY REVIEW REQUIRED",
        "operational:13",
        "INTERFACE",
        "PARTIAL",
        ["Node.js 20+", "1time-compatible service endpoint"],
        "Published as @1time/cli; the duplicate package declaration is folded into this executable surface.",
        categories,
        [],
        extra={"distribution_package": "@1time/cli", "sensitive_data": True},
    )

    extension = review.make("PLUGIN", "1time Chrome Extension", "extension/package.json", 1)
    review.finish(
        extension,
        "Chrome extension that encrypts selected page text locally and copies a one-time link while keeping the decryption key in the URL fragment.",
        [
            (
                "browser-selected-text-secret-sharing",
                "Browser selected-text secret sharing",
                ["1time Chrome extension", "encrypted selection sharing"],
            )
        ],
        "SECURITY REVIEW REQUIRED",
        "operational:13",
        "INTEGRATION",
        "PARTIAL",
        ["Chromium extension APIs", "1time-compatible service endpoint", "host permission for the selected endpoint"],
        "Uses extension-owned clipboard and session storage surfaces and supports self-hosted service origins.",
        categories,
        [],
        extra={"sensitive_data": True, "encryption_claim": "AES-256-GCM client-side"},
    )

    service = review.make("SERVICE", "1time Secret Sharing Service", "backend/main.go", 1)
    review.finish(
        service,
        "Self-hostable Go, Redis and file-storage service for bounded-view ciphertext and encrypted-file payloads used by browser, CLI and integration clients.",
        [
            (
                "zero-knowledge-one-time-secret-service",
                "Zero-knowledge one-time secret service",
                ["1time.io", "self-destructing encrypted links"],
            )
        ],
        "SECURITY REVIEW REQUIRED",
        "operational:13",
        "CORE",
        "PARTIAL",
        ["Go 1.25", "Redis", "writable file storage", "TLS reverse proxy for remote deployment"],
        "Stores encrypted payloads and bounded read counts; encryption and decryption occur in clients.",
        categories,
        [],
        extra={"sensitive_data": True, "server_plaintext_claim": False},
    )

    zapier = review.make("INTEGRATION", "1time Zapier Integration", "zap/package.json", 1)
    review.finish(
        zapier,
        "Zapier Platform integration that packages the shared 1time protocol for creating encrypted one-time secret links in automation workflows.",
        [
            (
                "zapier-encrypted-secret-sharing",
                "Zapier encrypted secret sharing",
                ["1time Zapier app", "Zapier one-time secret integration"],
            )
        ],
        "SECURITY REVIEW REQUIRED",
        "operational:13",
        "INTEGRATION",
        "PARTIAL",
        ["Zapier Platform 19", "1time-compatible service endpoint"],
        "Private Zapier project; its generated scaffolding and synchronized protocol copy are implementation details.",
        categories,
        [],
        extra={"sensitive_data": True},
    )

    for entity in review.existing:
        if entity["id"] != cli["id"]:
            review.drop(entity)

    review.relate("DEPENDS_ON", cli["id"], service["id"], "cli/README.md", 1)
    review.relate("DEPENDS_ON", extension["id"], service["id"], "extension/README.md", 1)
    review.relate("DEPENDS_ON", zapier["id"], service["id"], "zap/README.md", 1)

    result = review.finalize(
        categories,
        [],
        "SECURITY REVIEW REQUIRED",
        "operational:13",
        {
            "SERVICE": "Self-hostable ciphertext and encrypted-file service retained.",
            "CLI": "Published terminal client retained; package declaration folded into it.",
            "PLUGIN": "Chrome extension retained as a browser integration.",
            "INTEGRATION": "Zapier project retained as an automation integration.",
            "PACKAGE": "Private frontend and integration package declarations are represented by their product surfaces.",
            "WORKFLOW": "Container publication CI is repository-specific.",
        },
        deep_review="Sensitive-data and cryptographic-protocol trigger reviewed narrowly. Source documentation and implementations place AES-GCM encryption/decryption in clients, keep decryption keys in URL fragments, store ciphertext plus hashed read tokens server-side and bound reads. Static review does not establish cryptographic correctness, deployment TLS, storage isolation or operational deletion guarantees.",
        details=["private frontend package declaration", "duplicate CLI package declaration", "container publication workflow", "synchronized protocol copies"],
    )
    return complete_scoped(
        review,
        result,
        [("README.md", 1), ("backend/handlers.go", 1), ("extension/README.md", 1), ("cli/README.md", 1)],
        "Inventory is complete. Production use requires independent cryptographic review, TLS, protected Redis/file storage, retention and deletion verification, endpoint permission review and careful handling of links and URL fragments; no secret or service was exercised.",
    )


def review_apaxy() -> dict:
    review = LeanReview(
        "jamesrwatsonx-creator/apaxy-browse",
        "5b76e32d662fa1b0d96ebba2f559b1d3d5ee17d2",
    )
    categories = [
        "category:design-systems",
        "category:templates-boilerplates",
        "category:web-applications",
    ]

    package = one(review, "PACKAGE", path="package.json")
    review.finish(
        package,
        "Customizable Apache mod_autoindex theme with CSS, JavaScript filtering, media-type icons, optional gallery behavior and prepared HTTP configuration.",
        [
            (
                "apache-directory-listing-theme",
                "Apache directory-listing theme",
                ["Apaxy", "mod_autoindex theme"],
            )
        ],
        "USE DIRECTLY",
        "operational:09",
        "CORE",
        "FULL",
        ["Apache HTTP Server 2.4+", "mod_autoindex", "AllowOverride Options Indexes FileInfo"],
        "The Docker image and configuration files package the same theme rather than separate capabilities.",
        categories,
        [],
        extra={"license": "GPL-3.0"},
    )

    configurator = review.make("CLI", "apaxy-configure", "apaxy-configure.sh", 1)
    review.finish(
        configurator,
        "Shell configurator that installs Apaxy into an Apache web root and applies path, gallery, header, footer and logging settings.",
        [
            (
                "apache-directory-theme-installer",
                "Apache directory-theme installer",
                ["apaxy-configure", "Apaxy setup script"],
            )
        ],
        "USE DIRECTLY",
        "operational:09",
        "INTERFACE",
        "PARTIAL",
        ["Bash", "write access to the target Apache directory", "Apaxy theme files"],
        "Installation interface for the retained theme package.",
        categories,
        [],
    )

    review.relate("CONTAINS", package["id"], configurator["id"], "README.md", 1)
    return review.finalize(
        categories,
        [],
        "USE DIRECTLY",
        "operational:09",
        {
            "PACKAGE": "Apache directory-listing theme retained.",
            "CLI": "Theme configuration and installation script retained.",
        },
        details=["Docker packaging", "individual icon and JavaScript implementation fragments"],
    )


def main() -> None:
    results = [
        review_phone_harness(),
        review_superdesign(),
        review_one_time(),
        review_apaxy(),
    ]
    r.build()
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
