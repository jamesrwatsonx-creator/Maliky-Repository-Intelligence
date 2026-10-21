"""Lean semantic review of Appwrite at the pinned 2026-10-20 intake commit.

The review keeps deployable product boundaries, explicitly standalone Utopia
libraries, four repository skills, and a small set of composite console
subsystems. Generated/test declarations, repository CI, and thousands of
tightly coupled view fragments are removed from the searchable census.
Inspected source is read only from the verified cache and is never executed.
"""
from __future__ import annotations

import json

from lean_review_lib import LeanReview
import registry as r


FULL_NAME = "jamesrwatsonx-creator/appwrite-supabase-per-agent-"
COMMIT = "61833ff0f9dd5985f580b230244749247b170a6f"


def one(review: LeanReview, kind: str, path: str, name: str | None = None):
    found = review.find(kind, name=name, path=path)
    if len(found) != 1:
        raise ValueError(f"Expected one {kind} {name or ''} at {path}, found {len(found)}")
    return found[0]


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
    evidence = [
        ("README.md", 48),
        ("README.md", 83),
        ("packages/auth/README.md", 1),
        ("src/Appwrite/Platform/Modules/Functions/Module.php", 1),
        ("app/realtime.php", 1),
    ]
    repo["deep_review"] = {
        "completed": True,
        "reviewer": "Automated scoped static review",
        "evidence": [
            {"type": "source_review", "value": review.url(path, line)}
            for path, line in evidence
        ],
        "conclusion": (
            "Inventory is complete. Deployment still requires a dedicated security review of "
            "authentication and authorization policy, secret and encryption-key management, "
            "Docker-socket installer access, tenant isolation, user-code execution, network "
            "exposure, storage permissions, provider credentials and upgrade operations. No "
            "service, installer, function or credential flow was executed."
        ),
        "runtime_tested": False,
    }
    repo.pop("review_reason", None)
    r.write(r.repo_file(repo), repo)
    return {**result, "state": "COMPLETE", "scoped_review": "COMPLETE"}


LIBRARIES = {
    "abuse": "Application usage-limit and time-window abuse-control primitives.",
    "agents": "PHP agent library with multi-provider model adapters, conversations, attachments and streaming output.",
    "audit": "Application user-audit logging with pluggable storage adapters.",
    "auth": "Authentication and authorization primitives for password hashing, proofs, OAuth2, OpenID Connect and signed token verification.",
    "balancer": "Choice-balancing algorithms for random, round-robin and weighted selection.",
    "bus": "Synchronous in-process event bus with typed events and registered listeners.",
    "cache": "Cache storage, loading and invalidation abstractions with multiple adapters.",
    "cdn": "CDN adapter library for URL cache purges and CDN-backed certificate management.",
    "circuit-breaker": "Circuit breaker with shared state and telemetry for containing cascading downstream failures.",
    "cli": "Framework primitives for defining Utopia command-line applications.",
    "client": "PSR-18 HTTP client with cURL and Swoole transports over PSR-7 messages.",
    "compression": "File compression abstraction supporting multiple compression algorithms.",
    "config": "Typed application configuration registration and retrieval.",
    "console": "PHP console helpers for logging, prompts, external commands and long-running daemons.",
    "detector": "Environment, runtime, platform and device identification library.",
    "di": "PSR-11 dependency-injection container with parent-child scopes and managed lifecycles.",
    "dns": "Typed DNS encoder, decoder, resolver and server/client toolkit with UDP, TCP and Swoole transports.",
    "domains": "Public-Suffix-List domain parsing plus registrar adapters for registration operations.",
    "dsn": "Parser and value model for database and service Data Source Names.",
    "emails": "Email address parsing, normalization and validation helpers.",
    "http": "PHP MVC HTTP framework with routing, request lifecycle and dependency-injection integration.",
    "image": "Common image crop, resize, conversion and manipulation operations.",
    "locale": "Translation and localization catalog management.",
    "lock": "Mutex, semaphore, file and distributed locking across coroutines, processes, hosts and clusters.",
    "messaging": "Unified email, SMS, push and chat messaging API with provider adapters.",
    "mqtt": "Framework-independent MQTT 3.1.1 and 5.0 broker toolkit with typed control packets and QoS handling.",
    "nats": "PHP NATS client with JetStream and key-value store support.",
    "openapi": "Parser that normalizes OpenAPI 2.0, 3.0 and 3.1 documents into one immutable typed model.",
    "orchestration": "Container-orchestrator abstraction for image, container and execution lifecycle operations.",
    "platform": "Application framework abstractions for HTTP and CLI services, modules and actions.",
    "pools": "Long-lived connection pools, reusable connections and grouped pool management.",
    "psr7": "PSR-7 HTTP message implementations and PSR-17 factories.",
    "query": "Type-safe dialect-aware query and DDL builder with SQL parsing and serializable query values.",
    "queue": "Queue brokers, connections, consumers and task-processing abstractions.",
    "registry": "Lazy dependency and resource registry for initialized PHP objects.",
    "schedule": "Scheduler that reconciles persistent schedules and reliably dispatches cron, interval, delayed and fixed-time occurrences.",
    "servers": "Base runtime library for building Utopia-style long-running servers.",
    "smtp": "SMTP client implementing mail submission, STARTTLS, authentication, MIME and recipient-level results.",
    "span": "Memory-safe span tracing with automatic Swoole coroutine storage.",
    "storage": "Storage abstraction with local, S3, AWS, Backblaze, DigitalOcean, Linode and Wasabi devices.",
    "system": "Host operating-system and CPU-architecture detection helpers.",
    "telemetry": "Telemetry abstraction and adapters for application metrics and tracing.",
    "usage": "Usage-event and resource-gauge collection with dimensions for request and tenant analysis.",
    "user-agent": "Typed operating-system, browser, device and bot parser with lazy memoized detection.",
    "validators": "Reusable HTTP-oriented validators for text, URLs, IPs, hostnames, lists and input sanitization.",
    "vcs": "Version-control provider abstraction with GitHub and GitLab adapters.",
    "websocket": "WebSocket server abstraction with transport adapters.",
}


LIBRARY_OPERATIONAL = {
    "agents": "operational:03",
    "auth": "operational:13",
    "abuse": "operational:13",
    "audit": "operational:12",
    "cache": "operational:11",
    "cdn": "operational:14",
    "circuit-breaker": "operational:14",
    "compression": "operational:11",
    "dns": "operational:14",
    "lock": "operational:14",
    "messaging": "operational:16",
    "mqtt": "operational:16",
    "nats": "operational:16",
    "orchestration": "operational:14",
    "pools": "operational:14",
    "query": "operational:11",
    "queue": "operational:14",
    "schedule": "operational:14",
    "storage": "operational:11",
    "telemetry": "operational:12",
    "usage": "operational:12",
    "vcs": "operational:14",
    "websocket": "operational:16",
}


def finish_library(review: LeanReview, key: str, description: str, categories: list[str]):
    path = f"packages/{key}/README.md"
    display = "".join(part.capitalize() for part in key.split("-"))
    entity = review.make("LIBRARY", f"Utopia {display}", path, 1)
    sensitive = key in {"auth", "agents", "console", "dns", "http", "mqtt", "orchestration", "queue", "servers", "smtp", "storage", "vcs", "websocket"}
    review.finish(
        entity,
        description,
        [
            (
                f"utopia-{key}-php-library",
                f"Utopia {display} PHP library",
                [f"utopia-php/{key}", f"Utopia {display}"],
            )
        ],
        "SECURITY REVIEW REQUIRED" if sensitive else "USE AS LIBRARY",
        LIBRARY_OPERATIONAL.get(key, "operational:16"),
        "MODULE",
        "FULL",
        ["PHP", f"package-specific extensions and adapters documented in {path}"],
        "Maintained in this monorepo and published as a read-only split package mirror.",
        categories,
        [],
        extra={"composer_package": f"utopia-php/{key}", "split_mirror": True},
    )
    return entity


def review_appwrite() -> dict:
    review = LeanReview(FULL_NAME, COMMIT)
    categories = [
        "category:ai-agents",
        "category:apis",
        "category:application-security",
        "category:backend-services",
        "category:cloud-infrastructure",
        "category:developer-tools",
        "category:full-stack-applications",
        "category:libraries-packages",
        "category:mcp-servers",
        "category:web-applications",
    ]

    platform = review.make("SERVICE", "Appwrite Platform", "README.md", 1)
    review.finish(
        platform,
        "Self-hostable backend platform combining authentication, databases, storage, functions, sites, messaging, realtime APIs and an agent-facing managed-cloud workflow.",
        [("appwrite-backend-platform", "Appwrite backend platform", ["Appwrite", "open-source backend cloud"])],
        "SECURITY REVIEW REQUIRED",
        "operational:16",
        "CORE",
        "PARTIAL",
        ["Docker", "database, cache, queue, storage and executor services", "deployment-specific secrets and network policy"],
        "Top-level deployable product that contains the product services and APIs represented below.",
        categories,
        [],
        extra={"self_hostable": True, "managed_cloud_available": True, "license": "BSD-3-Clause"},
    )

    product_specs = [
        ("SERVICE", "Appwrite Auth", "src/Appwrite/Platform/Modules/Account/Module.php", "User authentication with email, SMS, OAuth, anonymous sessions, magic URLs, MFA and account lifecycle APIs.", "appwrite-auth-service", "operational:13"),
        ("DATABASE", "Appwrite Databases", "src/Appwrite/Platform/Modules/Databases/Module.php", "Managed document, table, relational and vector database APIs with schemas, indexes, transactions, queries and row/document permissions.", "appwrite-database-service", "operational:11"),
        ("SERVICE", "Appwrite Storage", "src/Appwrite/Platform/Modules/Storage/Module.php", "File and bucket service with access control, encryption, compression, previews, transformations and adapter-backed storage.", "appwrite-storage-service", "operational:11"),
        ("SERVICE", "Appwrite Functions", "src/Appwrite/Platform/Modules/Functions/Module.php", "Event-driven serverless function deployment and execution across isolated language runtimes.", "appwrite-serverless-functions", "operational:16"),
        ("SERVICE", "Appwrite Sites", "src/Appwrite/Platform/Modules/Sites/Module.php", "Git-connected static, client-rendered and server-rendered site deployment with preview builds.", "appwrite-sites-hosting", "operational:15"),
        ("SERVICE", "Appwrite Messaging", "src/Appwrite/Platform/Modules/Messaging/Module.php", "Unified email, SMS and push notification service with provider, topic, subscriber and delivery management.", "appwrite-messaging-service", "operational:16"),
        ("SERVICE", "Appwrite Realtime", "app/realtime.php", "Authenticated WebSocket event subscriptions with presence, channel authorization and project resource updates.", "appwrite-realtime-service", "operational:16"),
        ("SERVICE", "Appwrite Firewall", "src/Appwrite/Platform/Modules/Proxy/Module.php", "Project traffic routing and edge-control surface used with abuse limits and network protection policies.", "appwrite-firewall-service", "operational:13"),
    ]
    products = []
    for kind, name, path, description, slug, operational in product_specs:
        entity = review.make(kind, name, path, 1)
        review.finish(
            entity,
            description,
            [(slug, name, [name.lower(), slug.replace("-", " ")])],
            "SECURITY REVIEW REQUIRED",
            operational,
            "SERVICE",
            "PARTIAL",
            ["Appwrite platform runtime", "configured backing services and credentials"],
            "Deployable product boundary inside the Appwrite platform.",
            categories,
            [],
        )
        review.relate("CONTAINS", platform["id"], entity["id"], path, 1)
        products.append(entity)

    rest_api = review.make("API", "Appwrite REST API", "app/controllers/shared/api.php", 1)
    review.finish(
        rest_api,
        "Versioned HTTP API surface shared by Appwrite products, with project, session, key and JWT authentication modes plus scoped authorization.",
        [("appwrite-rest-api", "Appwrite REST API", ["Appwrite HTTP API", "Appwrite v1 API"])],
        "INTEGRATE VIA API",
        "operational:16",
        "INTERFACE",
        "PARTIAL",
        ["Appwrite deployment", "project endpoint", "appropriate session, key, JWT or OAuth identity"],
        "Primary programmatic interface to the product services.",
        categories,
        [],
    )
    graphql = review.make("API", "Appwrite GraphQL API", "app/controllers/api/graphql.php", 1)
    review.finish(
        graphql,
        "GraphQL endpoint exposing enabled Appwrite project operations through the platform authorization context.",
        [("appwrite-graphql-api", "Appwrite GraphQL API", ["Appwrite GraphQL"])],
        "INTEGRATE VIA API",
        "operational:16",
        "INTERFACE",
        "PARTIAL",
        ["Appwrite deployment", "enabled GraphQL project API", "authorized identity"],
        "Alternative API surface over platform products.",
        categories,
        [],
    )
    console = review.make("APP", "Appwrite Console", "apps/console/README.md", 1)
    review.finish(
        console,
        "Bun, TanStack Start and React application serving Appwrite's signed-in console and, in cloud profile, its website, docs, blog and changelog.",
        [("appwrite-administration-console", "Appwrite administration console", ["Appwrite Console", "Appwrite web console"])],
        "USE DIRECTLY",
        "operational:09",
        "CORE",
        "PARTIAL",
        ["Bun 1.4+", "Appwrite API endpoint", "profile-specific runtime configuration"],
        "Standalone application deployed separately from the PHP server.",
        categories,
        [],
    )
    mcp = review.make("MCP_SERVER", "Appwrite MCP Server", "README.md", 180)
    review.finish(
        mcp,
        "OAuth-enabled hosted MCP endpoint for operating live Appwrite projects, with a separately documented local server path for self-hosted deployments.",
        [("appwrite-project-mcp", "Appwrite project MCP", ["mcp.appwrite.io", "Appwrite MCP server"])],
        "INTEGRATE VIA MCP",
        "operational:02",
        "SERVICE",
        "NO",
        ["Hosted Appwrite MCP service or separately installed local MCP server", "Appwrite project authorization"],
        "The pinned repository documents and integrates the MCP service; it does not establish the hosted server implementation as contained source.",
        categories,
        [],
        extra={"hosted_endpoint": "https://mcp.appwrite.io/", "contained_implementation": False},
    )
    worker = review.make("SERVICE", "Appwrite Worker Runtime", "app/worker.php", 1)
    review.finish(
        worker,
        "Queue-driven background runtime that dispatches registered Appwrite jobs across build, execution, messaging, migration, webhook and maintenance workers.",
        [("appwrite-background-worker-runtime", "Appwrite background worker runtime", ["Appwrite workers", "Appwrite job runtime"])],
        "SECURITY REVIEW REQUIRED",
        "operational:14",
        "SERVICE",
        "PARTIAL",
        ["Appwrite service registry", "Redis-backed queue", "worker-specific credentials and backing services"],
        "Shared asynchronous execution surface for multiple product modules.",
        categories,
        [],
    )
    for entity in [rest_api, graphql, console, mcp, worker]:
        review.relate("CONTAINS", platform["id"], entity["id"], entity["source"]["source_path"], 1)

    for key, description in LIBRARIES.items():
        library = finish_library(review, key, description, categories)
        review.relate("CONTAINS", platform["id"], library["id"], f"packages/{key}/README.md", 1)

    skill_specs = {
        "apps/console/.cursor/skills/auditing-seo/SKILL.md": ("Appwrite SEO Audit", "Audit Appwrite content for SEO, answer-engine structure, metadata, links, search intent and source-backed accuracy.", "appwrite-content-seo-audit"),
        "apps/console/.cursor/skills/create-announcement/SKILL.md": ("Appwrite Feature Announcement", "Coordinate documentation, announcement blog and changelog artifacts for an Appwrite feature launch.", "appwrite-feature-announcement-workflow"),
        "apps/console/.cursor/skills/reviewing-blogs/SKILL.md": ("Appwrite Blog Review", "Review Appwrite posts for frontmatter, voice, structure, SEO, formatting and product accuracy.", "appwrite-blog-review-workflow"),
        "apps/console/.cursor/skills/writing-blogs/SKILL.md": ("Appwrite Blog Writing", "Write and format Appwrite blog posts using the repository's Markdoc, voice, frontmatter and SEO conventions.", "appwrite-blog-writing-workflow"),
    }
    for path, (display, description, slug) in skill_specs.items():
        entity = one(review, "SKILL", path)
        review.finish(
            entity,
            description,
            [(slug, display, [entity["name"], display.lower()])],
            "USE DIRECTLY",
            "operational:01",
            "SKILL",
            "PARTIAL",
            ["Appwrite console content tree", "repository-specific documentation and publishing conventions"],
            "Directly usable in this repository and adaptable as a reference for similar developer-content workflows.",
            categories,
            [],
        )

    ui_specs = [
        ("apps/console/src/components/global/api-explorer/ApiExplorer.tsx", "ApiExplorer", "Interactive OpenAPI-backed request explorer with platform selection, authentication, parameter forms and downloadable specifications.", "openapi-console-api-explorer"),
        ("apps/console/src/components/global/cli-shell/ProjectCliShell.tsx", "ProjectCliShell", "Project-scoped browser terminal shell with session layout and command interaction surfaces.", "browser-project-cli-shell"),
        ("apps/console/src/components/global/providers/AgentChat.tsx", "AgentChatProvider", "Console provider and panel integration for an Appwrite-aware agent chat experience.", "appwrite-console-agent-chat"),
        ("apps/console/src/components/global/shared/CodeEditor.tsx", "CodeEditor", "Reusable Monaco-based code editor wrapper for console forms and source editing.", "console-code-editor-component"),
        ("apps/console/src/components/global/shared/CommandCenter.tsx", "CommandCenter", "Keyboard-driven console command center for navigation, support and project actions.", "console-command-center"),
        ("apps/console/src/components/global/shared/EventEditor/EventEditor.tsx", "EventEditor", "Structured event selector and editor for Appwrite function and webhook event configuration.", "appwrite-event-editor"),
    ]
    for path, name, description, slug in ui_specs:
        entity = one(review, "UI_COMPONENT", path, name)
        review.finish(
            entity,
            description,
            [(slug, " ".join(part.capitalize() for part in slug.split("-")), [name])],
            "EXTRACT COMPONENTS",
            "operational:09",
            "COMPONENT",
            "PARTIAL",
            ["Appwrite Console React application", "console state, SDK and design-system dependencies"],
            "Composite console subsystem retained as an extraction or reference boundary; smaller view fragments are omitted.",
            categories,
            [],
        )

    retained = set(review.out)
    for entity in review.existing:
        if entity["id"] not in retained:
            review.drop(entity)

    result = review.finalize(
        categories,
        [],
        "SECURITY REVIEW REQUIRED",
        "operational:16",
        {
            "SERVICE": "Platform, product and worker service boundaries retained.",
            "DATABASE": "Multi-model database product retained.",
            "API": "REST and GraphQL platform interfaces retained; demo snippet routes removed.",
            "APP": "Separately deployable Appwrite Console retained.",
            "MCP_SERVER": "Documented hosted MCP service retained with contained-implementation limitation.",
            "LIBRARY": "Forty-seven explicitly standalone Utopia split packages retained individually.",
            "SKILL": "Four repository content workflows retained.",
            "UI_COMPONENT": "Six composite console subsystems retained; tightly coupled page and view fragments omitted.",
            "PACKAGE": "Root, console, test-fixture and workflow-helper manifests are represented by product entities or omitted as packaging.",
            "WORKFLOW": "Repository CI, release and maintenance automation is not catalogued as standalone product capability.",
        },
        deep_review="Authentication, secrets, privileged infrastructure and arbitrary-execution triggers reviewed narrowly. Appwrite exposes session/key/JWT/OAuth authorization, stores provider and encryption credentials, runs user functions, accepts network traffic, mounts the Docker socket during installation and coordinates many privileged workers. Source includes explicit production-key checks and security scanning rules, but static review does not certify tenant isolation, authorization coverage, cryptographic operation, runtime sandboxing or deployment hardening.",
        details=[
            "2,404 tightly coupled console view fragments",
            "23 repository CI/release workflows",
            "test fixture packages and demo API routes",
            "provider-specific and route-level implementation classes represented by their product or library boundary",
        ],
    )
    return complete_scoped(review, result)


def main() -> None:
    result = review_appwrite()
    r.build()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
