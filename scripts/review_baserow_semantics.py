"""Lean semantic census of Baserow at its pinned intake revision.

The census retains documented product boundaries, MCP tools, repository skills,
connectors and separately useful deployment/development assets. Package manifests,
CI workflows, tests and tightly coupled implementation fragments are folded into
their owning capability or excluded. Inspected source is read only and never run.
"""
from __future__ import annotations

import json

from lean_review_lib import LeanReview
import registry as r


FULL_NAME = "jamesrwatsonx-creator/baserow-like-airtable-"
COMMIT = "0b1e7ee8255039e11257fd1d5a2dd56f25722105"


def one(review: LeanReview, kind: str, path: str):
    found = review.find(kind, path=path)
    if len(found) != 1:
        raise ValueError(f"Expected one {kind} at {path}, found {len(found)}")
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
    repo["deep_review"] = {
        "completed": True,
        "reviewer": "Automated scoped static review",
        "evidence": [
            {"type": "source_review", "value": review.url("LICENSE", 1)},
            {
                "type": "source_review",
                "value": review.url("enterprise/LICENSE", 1),
            },
            {
                "type": "source_review",
                "value": review.url("backend/src/baserow/core/mcp/__init__.py", 1),
            },
            {
                "type": "source_review",
                "value": review.url(
                    "enterprise/backend/src/baserow_enterprise/code_runner/code_runner_types.py",
                    1,
                ),
            },
        ],
        "conclusion": (
            "Inventory is complete. Deployment requires a separate security review of "
            "authentication, role and field authorization, API and MCP endpoint keys, "
            "tenant isolation, secrets, third-party integration credentials, imported "
            "data, webhooks, file handling, network egress and user-supplied code. "
            "Premium and enterprise source has subscription-bound licenses and must be "
            "used under its applicable terms. No server, workflow, connector or code "
            "runner was executed."
        ),
        "runtime_tested": False,
    }
    repo.pop("review_reason", None)
    r.write(r.repo_file(repo), repo)
    return {**result, "state": "COMPLETE", "scoped_review": "COMPLETE"}


def finish(
    review: LeanReview,
    entity: dict,
    description: str,
    slug: str,
    cap_name: str,
    recommendation: str,
    operational: str,
    role: str,
    standalone: str,
    dependencies: list[str],
    categories: list[str],
    overlap: str,
    *,
    aliases: list[str] | None = None,
    extra: dict | None = None,
):
    return review.finish(
        entity,
        description,
        [(slug, cap_name, aliases or [entity["name"], cap_name.lower()])],
        recommendation,
        operational,
        role,
        standalone,
        dependencies,
        overlap,
        categories,
        [],
        extra=extra,
    )


def review_baserow() -> dict:
    review = LeanReview(FULL_NAME, COMMIT)
    categories = [
        "category:ai-agents",
        "category:ai-applications",
        "category:automation-scripting",
        "category:business-applications",
        "category:cloud-infrastructure",
        "category:data-engineering",
        "category:data-visualization",
        "category:databases",
        "category:full-stack-applications",
        "category:iam",
        "category:kubernetes-orchestration",
        "category:mcp-servers",
        "category:plugins-extensions",
        "category:skills",
    ]

    platform = review.make("APP", "Baserow Platform", "README.md", 1)
    finish(
        review,
        platform,
        "Self-hostable no-code platform for databases, applications, automations, dashboards and AI-assisted agents, exposed through web, API and integration surfaces.",
        "baserow-platform",
        "Baserow no-code platform",
        "SECURITY REVIEW REQUIRED",
        "operational:21",
        "CORE",
        "FULL",
        ["Python 3.14", "Django", "Vue and Nuxt", "PostgreSQL", "Redis", "object storage"],
        categories,
        "Top-level deployable product containing the product modules represented below.",
        extra={"version": "2.4.1", "license_model": "open core"},
    )

    product_specs = [
        (
            "DATABASE",
            "Baserow Database",
            "backend/src/baserow/contrib/database/application_types.py",
            "No-code relational and spreadsheet-style database with typed fields, tables, views, formulas, import/export, search, permissions and workflow actions.",
            "baserow-no-code-database",
            "Baserow no-code database",
            "operational:11",
        ),
        (
            "APP",
            "Baserow Application Builder",
            "backend/src/baserow/contrib/builder/application_types.py",
            "Responsive no-code application and portal builder with pages, elements, themes, data sources, user sources, integrations and workflow actions.",
            "baserow-application-builder",
            "Baserow application builder",
            "operational:09",
        ),
        (
            "AUTOMATION",
            "Baserow Automation Builder",
            "backend/src/baserow/contrib/automation/application_types.py",
            "Visual workflow builder that composes triggers, actions, formulas, integrations and data providers into executable automations.",
            "baserow-automation-builder",
            "Baserow automation builder",
            "operational:18",
        ),
        (
            "APP",
            "Baserow Dashboard Builder",
            "backend/src/baserow/contrib/dashboard/application_types.py",
            "Dashboard application surface for composing summary, chart and pie-chart widgets over Baserow data sources.",
            "baserow-dashboard-builder",
            "Baserow dashboard builder",
            "operational:12",
        ),
        (
            "AGENT_FRAMEWORK",
            "Baserow Workspace Agents",
            "backend/src/baserow/core/agents/service.py",
            "Permission-aware framework for creating, assigning roles to, extending, updating and deleting workspace agents.",
            "baserow-workspace-agent-framework",
            "Baserow workspace agent framework",
            "operational:03",
        ),
        (
            "AGENT",
            "Kuma AI Assistant",
            "enterprise/backend/src/baserow_enterprise/assistant/assistant.py",
            "Streaming tool-using assistant that routes across database, application builder, automation, navigation and documentation tools with conversation history and action outcome tracking.",
            "baserow-kuma-ai-assistant",
            "Kuma AI assistant",
            "operational:03",
        ),
    ]
    products = []
    for kind, name, path, description, slug, cap_name, operational in product_specs:
        entity = review.make(kind, name, path, 1)
        restricted = path.startswith("enterprise/")
        finish(
            review,
            entity,
            description,
            slug,
            cap_name,
            "SECURITY REVIEW REQUIRED" if restricted else "USE DIRECTLY",
            operational,
            "CORE",
            "PARTIAL",
            ["Baserow platform runtime", "configured backing services and product permissions"],
            categories,
            "Product boundary within the Baserow deployment.",
            extra={"license": "Baserow Enterprise Edition License" if restricted else "MIT"},
        )
        review.relate("CONTAINS", platform["id"], entity["id"], path, 1)
        products.append(entity)

    api_specs = [
        (
            "Baserow REST API",
            "docs/apis/rest-api.md",
            "Token-authenticated HTTP API and generated OpenAPI surface for Baserow workspace and database operations.",
            "baserow-rest-api",
        ),
        (
            "Baserow WebSocket API",
            "docs/apis/web-socket-api.md",
            "Authenticated WebSocket subscription API for workspace, table, row, view, field and collaboration events.",
            "baserow-websocket-api",
        ),
    ]
    for name, path, description, slug in api_specs:
        entity = review.make("API", name, path, 1)
        finish(
            review,
            entity,
            description,
            slug,
            name,
            "INTEGRATE VIA API",
            "operational:16",
            "INTERFACE",
            "PARTIAL",
            ["Running Baserow deployment", "authorized user or database token"],
            categories,
            "Programmatic interface to platform capabilities.",
        )
        review.relate("PROVIDES", platform["id"], entity["id"], path, 1)

    mcp = one(review, "MCP_SERVER", "backend/src/baserow/core/mcp/__init__.py")
    finish(
        review,
        mcp,
        "Workspace-scoped MCP server over SSE that validates endpoint keys and exposes registered Baserow database tools under current user permissions.",
        "baserow-database-mcp-server",
        "Baserow database MCP server",
        "SECURITY REVIEW REQUIRED",
        "operational:02",
        "SERVICE",
        "PARTIAL",
        ["Baserow backend", "valid MCP endpoint key", "workspace membership and permissions"],
        categories,
        "MCP interface to the database capabilities and tools represented below.",
        extra={"transport": "SSE", "resources": False, "prompts": False},
    )
    review.relate("PROVIDES", platform["id"], mcp["id"], "backend/src/baserow/core/mcp/__init__.py", 1)

    mcp_tools = [
        ("list_databases", "List Baserow Databases", "backend/src/baserow/contrib/database/mcp/table/tools.py", "List databases visible in the authenticated workspace.", True),
        ("create_database", "Create Baserow Database", "backend/src/baserow/contrib/database/mcp/table/tools.py", "Create a database in the authenticated workspace.", False),
        ("list_tables", "List Baserow Tables", "backend/src/baserow/contrib/database/mcp/table/tools.py", "List visible tables, optionally within one database.", True),
        ("create_table", "Create Baserow Table", "backend/src/baserow/contrib/database/mcp/table/tools.py", "Create a table and dependency-ordered initial fields.", False),
        ("update_table", "Update Baserow Table", "backend/src/baserow/contrib/database/mcp/table/tools.py", "Rename an accessible table.", False),
        ("delete_table", "Delete Baserow Table", "backend/src/baserow/contrib/database/mcp/table/tools.py", "Move an accessible table and its rows to trash.", False),
        ("get_table_schema", "Get Baserow Table Schema", "backend/src/baserow/contrib/database/mcp/table/tools.py", "Return field schemas for accessible tables.", True),
        ("create_fields", "Create Baserow Fields", "backend/src/baserow/contrib/database/mcp/fields/tools.py", "Create dependency-ordered fields in an accessible table.", False),
        ("update_fields", "Update Baserow Fields", "backend/src/baserow/contrib/database/mcp/fields/tools.py", "Rename or change field types and properties.", False),
        ("delete_fields", "Delete Baserow Fields", "backend/src/baserow/contrib/database/mcp/fields/tools.py", "Move non-primary fields to trash.", False),
        ("list_table_rows", "List Baserow Rows", "backend/src/baserow/contrib/database/mcp/rows/tools.py", "List accessible rows with search and pagination.", True),
        ("create_rows", "Create Baserow Rows", "backend/src/baserow/contrib/database/mcp/rows/tools.py", "Create one or more rows using user-facing field names.", True),
        ("update_rows", "Update Baserow Rows", "backend/src/baserow/contrib/database/mcp/rows/tools.py", "Update one or more rows using row IDs and user-facing field names.", True),
        ("delete_rows", "Delete Baserow Rows", "backend/src/baserow/contrib/database/mcp/rows/tools.py", "Delete one or more accessible rows by ID.", True),
    ]
    for tool_name, display, path, description, enabled in mcp_tools:
        entity = review.make("TOOL", tool_name, path, 1)
        finish(
            review,
            entity,
            description,
            f"baserow-mcp-{tool_name.replace('_', '-')}",
            display,
            "INTEGRATE VIA MCP" if enabled else "REFERENCE ONLY",
            "operational:02",
            "TOOL",
            "NO",
            ["Baserow MCP server", "valid endpoint key", "required workspace permissions"],
            categories,
            "Individual MCP operation provided by the Baserow MCP server.",
            aliases=[tool_name, display.lower()],
            extra={"enabled_by_default": enabled},
        )
        review.relate("PROVIDES", mcp["id"], entity["id"], path, 1)

    plugin = review.make("PLUGIN", "Baserow Plugin Framework", "docs/plugins/introduction.md", 1)
    finish(
        review,
        plugin,
        "Experimental self-hosted extension framework for adding field, view, filter, sort, formula, page, component and third-party integration behavior to Baserow.",
        "baserow-plugin-framework",
        "Baserow plugin framework",
        "SECURITY REVIEW REQUIRED",
        "operational:02",
        "FRAMEWORK",
        "PARTIAL",
        ["Self-hosted Baserow", "trusted Python and Node plugin code", "custom container image"],
        categories,
        "Full-internal-access plugin mechanism; the source explicitly marks it experimental.",
        extra={"experimental": True, "trusted_code_required": True},
    )
    review.relate("CONTAINS", platform["id"], plugin["id"], "docs/plugins/introduction.md", 1)

    helm = review.make("INFRASTRUCTURE_MODULE", "Baserow Helm Chart", "deploy/helm/baserow/Chart.yaml", 1)
    finish(
        review,
        helm,
        "Production-oriented Helm chart for Baserow services with optional Redis, PostgreSQL, MinIO, Caddy ingress and embeddings dependencies.",
        "baserow-helm-chart",
        "Baserow Helm chart",
        "SECURITY REVIEW REQUIRED",
        "operational:15",
        "DEPLOYMENT",
        "PARTIAL",
        ["Kubernetes", "Helm 3", "DNS and TLS configuration", "deployment secrets"],
        categories,
        "Deployment packaging for the Baserow platform.",
    )
    review.relate("DEPENDS_ON", platform["id"], helm["id"], "deploy/helm/baserow/Chart.yaml", 1)

    email_compiler = review.make("TOOL", "Baserow Email Compiler", "backend/email_compiler/package.json", 1)
    finish(
        review,
        email_compiler,
        "Node.js build tool that compiles MJML and Eta email sources into Django templates, with one-shot and watch modes.",
        "mjml-eta-django-email-compiler",
        "MJML and Eta Django email compiler",
        "EXTRACT",
        "operational:02",
        "TOOL",
        "PARTIAL",
        ["Node.js", "MJML", "Eta", "Baserow backend template layout"],
        categories,
        "Small private build package with a reusable compilation pattern.",
        extra={"license": "MIT", "private_package": True},
    )

    connector_specs = [
        ("Baserow AI Provider Integration", "backend/src/baserow/contrib/integrations/ai/integration_types.py", "Configurable AI-provider integration used by AI fields, agent actions, formula suggestions and the assistant.", "baserow-ai-provider-integration", "operational:17", "MIT"),
        ("Baserow SMTP Integration", "backend/src/baserow/contrib/integrations/core/integration_types.py", "SMTP credential and service integration for sending email from product workflows.", "baserow-smtp-integration", "operational:16", "MIT"),
        ("Baserow Local Data Integration", "backend/src/baserow/contrib/integrations/local_baserow/integration_types.py", "Integration that exposes local Baserow tables and services to builder, dashboard and automation surfaces.", "baserow-local-data-integration", "operational:11", "MIT"),
        ("Baserow Slack Bot Integration", "backend/src/baserow/contrib/integrations/slack/integration_types.py", "Slack bot credential and service integration for workflow actions.", "baserow-slack-bot-integration", "operational:16", "MIT"),
        ("Baserow Zapier Integration", "integrations/zapier/package.json", "Private Zapier application package connecting Zapier workflows to Baserow operations.", "baserow-zapier-integration", "operational:18", "MIT"),
    ]
    connectors = []
    for name, path, description, slug, operational, license_name in connector_specs:
        entity = review.make("CONNECTOR", name, path, 1)
        finish(
            review,
            entity,
            description,
            slug,
            name,
            "SECURITY REVIEW REQUIRED",
            operational,
            "INTEGRATION",
            "PARTIAL",
            ["Baserow deployment", "provider-specific credentials and network access"],
            categories,
            "Reusable integration boundary consumed by Baserow products.",
            extra={"license": license_name},
        )
        review.relate("COMPLEMENTS", platform["id"], entity["id"], path, 1)
        connectors.append(entity)

    sync_specs = [
        ("PostgreSQL", "enterprise/backend/src/baserow_enterprise/data_sync/data_sync_types.py", "Synchronize an external PostgreSQL relation into a Baserow table.", "postgresql"),
        ("Baserow Table", "enterprise/backend/src/baserow_enterprise/data_sync/baserow_table_data_sync.py", "Synchronize a table or view from another Baserow source into a local table.", "baserow-table"),
        ("GitHub Issues", "enterprise/backend/src/baserow_enterprise/data_sync/github_issues_data_sync.py", "Synchronize GitHub issue metadata and content into typed Baserow fields.", "github-issues"),
        ("GitLab Issues", "enterprise/backend/src/baserow_enterprise/data_sync/gitlab_issues_data_sync.py", "Synchronize GitLab issue metadata and content into typed Baserow fields.", "gitlab-issues"),
        ("HubSpot Contacts", "enterprise/backend/src/baserow_enterprise/data_sync/hubspot_contacts_data_sync.py", "Synchronize HubSpot contact properties into typed Baserow fields.", "hubspot-contacts"),
        ("Jira Issues", "enterprise/backend/src/baserow_enterprise/data_sync/jira_issues_data_sync.py", "Synchronize selected Jira issue fields into typed Baserow fields.", "jira-issues"),
    ]
    for label, path, description, slug in sync_specs:
        entity = review.make("CONNECTOR", f"Baserow {label} Data Sync", path, 1)
        finish(
            review,
            entity,
            description,
            f"baserow-{slug}-data-sync",
            f"Baserow {label} data sync",
            "SECURITY REVIEW REQUIRED",
            "operational:11",
            "INTEGRATION",
            "PARTIAL",
            ["Baserow Enterprise subscription", "source credentials", "network access", "target workspace permissions"],
            categories,
            "Enterprise data-sync connector implemented in this monorepo.",
            extra={"license": "Baserow Enterprise Edition License"},
        )
        review.relate("COMPLEMENTS", products[0]["id"], entity["id"], path, 1)

    enterprise_specs = [
        ("SERVICE", "Baserow Enterprise RBAC", "enterprise/backend/src/baserow_enterprise/role/models.py", "Scoped roles and role assignments that grant operation sets to users or other subjects across workspaces and resources.", "baserow-enterprise-rbac", "operational:13"),
        ("SERVICE", "Baserow Enterprise SSO", "enterprise/backend/src/baserow_enterprise/sso/saml/auth_provider_types.py", "Enterprise authentication providers for SAML and OAuth2/OpenID Connect single sign-on.", "baserow-enterprise-sso", "operational:13"),
        ("SERVICE", "Baserow Audit Log", "enterprise/backend/src/baserow_enterprise/audit_log/models.py", "Durable enterprise action log retaining actor, workspace, command, context, time and source-address details.", "baserow-enterprise-audit-log", "operational:13"),
        ("SERVICE", "Baserow Data Scanner", "enterprise/backend/src/baserow_enterprise/data_scanner/handler.py", "Staff-only scanner for locating configured patterns or value lists across selected Baserow workspaces and tables.", "baserow-enterprise-data-scanner", "operational:13"),
        ("TOOL", "Baserow QuickJS Code Runner", "enterprise/backend/src/baserow_enterprise/code_runner/code_runner_types.py", "Wasmtime-hosted QuickJS runner with time, memory, fuel and output limits for user-supplied JavaScript in workflow contexts.", "baserow-wasmtime-quickjs-code-runner", "operational:13"),
    ]
    for kind, name, path, description, slug, operational in enterprise_specs:
        entity = review.make(kind, name, path, 1)
        finish(
            review,
            entity,
            description,
            slug,
            name,
            "SECURITY REVIEW REQUIRED",
            operational,
            "SERVICE" if kind == "SERVICE" else "TOOL",
            "PARTIAL",
            ["Baserow Enterprise subscription", "Baserow backend", "feature-specific configuration"],
            categories,
            "Enterprise-licensed platform capability.",
            extra={"license": "Baserow Enterprise Edition License"},
        )
        review.relate("CONTAINS", platform["id"], entity["id"], path, 1)

    skill_specs = {
        ".agents/skills/add-config-env-var/SKILL.md": ("Baserow Configuration Variable", "Add or review a Baserow environment-backed setting across backend, frontend, deployment, documentation, consumers and tests.", "baserow-config-variable-skill"),
        ".agents/skills/add-update-builder-element-type/SKILL.md": ("Baserow Builder Element", "Add or update an Application Builder element across backend types, frontend registry and components, migrations and tests.", "baserow-builder-element-skill"),
        ".agents/skills/baserow-registry/SKILL.md": ("Baserow Registry", "Explain or modify Baserow's backend and frontend typed registry patterns and registration points.", "baserow-registry-skill"),
        ".agents/skills/core-graph/SKILL.md": ("Baserow Core Graph", "Work with reusable graph relationships used by Application Builder elements and Automation nodes.", "baserow-core-graph-skill"),
        ".agents/skills/create-changelog/SKILL.md": ("Baserow Changelog", "Generate a public changelog entry from a branch diff using Baserow's domain and type conventions.", "baserow-changelog-skill"),
        ".agents/skills/create-in-app-notification/SKILL.md": ("Baserow In-App Notification", "Create or update backend notification types and corresponding frontend rendering, routing and deduplication.", "baserow-notification-skill"),
        ".agents/skills/create-update-runtime-formula/SKILL.md": ("Create Baserow Runtime Formula", "Create or update cross-product runtime formula types in backend and frontend implementations.", "baserow-create-runtime-formula-skill"),
        ".agents/skills/create-update-service/SKILL.md": ("Baserow Service Integration", "Create or update integrations and reusable service types shared by builder, dashboard and automation products.", "baserow-service-integration-skill"),
        ".agents/skills/manage-backend-layers/SKILL.md": ("Baserow Backend Layers", "Manage domain behavior across models, handlers, services, actions, APIs, permissions, migrations and tests.", "baserow-backend-layers-skill"),
        ".agents/skills/manage-permissions/SKILL.md": ("Baserow Permissions", "Create, edit or debug backend and frontend operation and permission manager behavior.", "baserow-permissions-skill"),
        ".agents/skills/review-pr/SKILL.md": ("Baserow Pull Request Review", "Review Baserow changes against their actual base using project invariants and evidence-backed findings.", "baserow-pr-review-skill"),
        ".agents/skills/runtime-formulas/SKILL.md": ("Baserow Runtime Formulas", "Explain, debug or extend runtime formula storage, validation, data providers, context dispatch and import/export.", "baserow-runtime-formulas-skill"),
        ".agents/skills/silk-profiler/SKILL.md": ("Baserow Silk Profiling", "Investigate backend endpoint performance, query patterns and bottlenecks using captured Django Silk data.", "baserow-silk-profiling-skill"),
        ".agents/skills/write-backend-unit-test/SKILL.md": ("Baserow Backend Testing", "Write backend tests using the repository's pytest, Django, DRF and fixture conventions.", "baserow-backend-test-skill"),
        ".agents/skills/write-e2e-test/SKILL.md": ("Baserow End-to-End Testing", "Write and debug Playwright end-to-end tests using Baserow fixtures, page objects and Docker stack.", "baserow-e2e-test-skill"),
        ".agents/skills/write-frontend-unit-test/SKILL.md": ("Baserow Frontend Testing", "Write frontend tests using Baserow's Vitest, Nuxt, Vue Test Utils and shared application patterns.", "baserow-frontend-test-skill"),
    }
    for path, (name, description, slug) in skill_specs.items():
        entity = one(review, "SKILL", path)
        finish(
            review,
            entity,
            description,
            slug,
            name,
            "USE DIRECTLY",
            "operational:01",
            "SKILL",
            "PARTIAL",
            ["Baserow source tree", "repository-specific architecture and commands"],
            categories,
            "Directly usable in Baserow and adaptable as a reference for similar monorepos.",
            aliases=[entity["name"], name.lower()],
        )

    retained = set(review.out)
    for entity in review.existing:
        if entity["id"] not in retained:
            review.drop(entity)

    result = review.finalize(
        categories,
        [],
        "SECURITY REVIEW REQUIRED",
        "operational:11",
        {
            "APP": "Platform, application builder and dashboard product boundaries retained.",
            "DATABASE": "No-code database product retained.",
            "AUTOMATION": "Visual automation product retained.",
            "AGENT_FRAMEWORK": "Workspace-agent management framework retained.",
            "AGENT": "Kuma tool-using assistant retained.",
            "API": "REST and WebSocket interfaces retained.",
            "MCP_SERVER": "Workspace-scoped MCP server retained.",
            "TOOL": "Fourteen MCP operations, email compiler and sandboxed code runner retained.",
            "PLUGIN": "Experimental self-hosted plugin framework retained.",
            "INFRASTRUCTURE_MODULE": "Helm deployment chart retained.",
            "CONNECTOR": "Product integrations and six enterprise data-sync connectors retained.",
            "SKILL": "Sixteen repository development skills retained.",
            "PACKAGE": "Backend, frontend, premium, enterprise and test package declarations are represented by product boundaries or omitted as packaging.",
            "CLI": "The Django management entry point is part of the backend platform rather than a separate reusable CLI product.",
            "WORKFLOW": "Repository CI, test, release and project-board workflows are operational automation rather than product capabilities.",
            "UI_COMPONENT": "A notification-type declaration is an implementation fragment of the automation product.",
        },
        deep_review=(
            "Authentication, authorization, secrets, sensitive-data, arbitrary-execution and license triggers were reviewed narrowly. "
            "The platform exposes token, WebSocket and MCP endpoints; stores external-provider credentials; imports and synchronizes external data; "
            "supports trusted full-access plugins; and includes a bounded Wasmtime/QuickJS runner. Premium and enterprise directories have subscription-bound licenses."
        ),
        details=[
            "repository CI, release and project automation",
            "test-only package declarations",
            "frontend notification and view fragments",
            "route, serializer, model and provider implementation classes represented by their product boundary",
        ],
    )
    return complete_scoped(review, result)


def main() -> None:
    result = review_baserow()
    r.build()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
