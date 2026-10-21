"""Resolve Bitcart source-parser limitations and run its lean semantic census.

The pinned source requires Python 3.12 and uses PEP 695 type aliases and generic
syntax. Python versions older than 3.12 cannot parse those declarations, although
the files were downloaded, hash verified and readable. This review records that
resolution, groups route-level candidates into stable API surfaces, and retains
the reusable daemon, plugin and notification boundaries. No source is executed.
"""
from __future__ import annotations

import json
from pathlib import Path

from lean_review_lib import LeanReview
import registry as r


FULL_NAME = "jamesrwatsonx-creator/bitcart-recieve-crypto-as-payment-"
COMMIT = "6388adcf017907d975eed4ed4a1b975d5e120059"
REPOSITORY_ID = "repository:1418688735"
GITHUB_ID = 1418688735

PEP695_PATHS = {
    "api/db.py",
    "api/ext/moneyformat/__init__.py",
    "api/logging.py",
    "api/plugins.py",
    "api/services/crud/__init__.py",
    "api/services/crud/repository.py",
    "api/services/settings.py",
    "api/types.py",
    "api/utils/authorization.py",
    "api/utils/common.py",
    "api/utils/database.py",
    "api/utils/files.py",
    "api/utils/routing.py",
    "tests/functional/test_functional.py",
    "tests/test_views/test_views_metadata.py",
}


def resolve_parser_evidence() -> int:
    resolution = (
        "Reviewed against pinned source and pyproject.toml. This is valid Python "
        ">=3.12 PEP 695 type-alias or generic-parameter syntax that the intake "
        "runtime's older ast parser does not support; it is a detector limitation, "
        "not unread or damaged source."
    )

    def resolve(payload: dict) -> int:
        paths = {error["path"] for error in payload.get("errors", [])}
        if paths != PEP695_PATHS:
            raise ValueError(
                f"Bitcart parser-error set changed: expected {sorted(PEP695_PATHS)}, got {sorted(paths)}"
            )
        for error in payload.get("errors", []):
            error["review_resolution"] = resolution
            error["reviewed_at"] = r.now()
        return len(paths)

    public_path = f"system/evidence/{GITHUB_ID}.json"
    public = r.read(public_path)
    count = resolve(public)
    r.write(public_path, public)

    local_path = r.ROOT / ".local" / "evidence-manifests" / f"{GITHUB_ID}.json"
    if local_path.exists():
        local = json.loads(local_path.read_text(encoding="utf-8"))
        resolve(local)
        local_path.write_text(json.dumps(local, indent=2) + "\n", encoding="utf-8")
    return count


def complete_scoped(review: LeanReview, result: dict, resolved_errors: int) -> dict:
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
            {"type": "source_review", "value": review.url("pyproject.toml", 1)},
            {"type": "source_review", "value": review.url("api/utils/authorization.py", 1)},
            {"type": "source_review", "value": review.url("api/services/plugin_manager.py", 1)},
            {"type": "source_review", "value": review.url("daemons/base.py", 1)},
        ],
        "conclusion": (
            "Inventory is complete. Production use requires dedicated review of wallet "
            "and private-key custody, payment and payout authorization, invoice/refund "
            "state transitions, authentication scopes, token and 2FA flows, daemon RPC "
            "authentication, blockchain reorganization handling, plugin archive trust, "
            "server-management operations, third-party RPC and rate providers, backups, "
            "notifications and secrets. No API, daemon, wallet, payment, plugin or "
            "management operation was executed."
        ),
        "runtime_tested": False,
    }
    repo.pop("review_reason", None)
    r.write(r.repo_file(repo), repo)
    return {
        **result,
        "state": "COMPLETE",
        "scoped_review": "COMPLETE",
        "parser_errors_resolved": resolved_errors,
    }


def finish(
    review: LeanReview,
    entity: dict,
    description: str,
    slug: str,
    name: str,
    operational: str,
    role: str,
    dependencies: list[str],
    categories: list[str],
    overlap: str,
    *,
    recommendation: str = "SECURITY REVIEW REQUIRED",
    extra: dict | None = None,
):
    return review.finish(
        entity,
        description,
        [(slug, name, [entity["name"], name.lower()])],
        recommendation,
        operational,
        role,
        "PARTIAL",
        dependencies,
        overlap,
        categories,
        [],
        extra={"license": "MIT", **(extra or {})},
    )


def review_bitcart() -> dict:
    resolved_errors = resolve_parser_evidence()
    review = LeanReview(FULL_NAME, COMMIT)
    categories = [
        "category:apis",
        "category:application-security",
        "category:backend-services",
        "category:blockchain-web3-security",
        "category:commerce-e-commerce",
        "category:distributed-systems",
        "category:finance-accounting",
        "category:message-event-systems",
        "category:plugins-extensions",
    ]

    platform = review.make("SERVICE", "Bitcart Core", "README.md", 1)
    finish(
        review,
        platform,
        "Self-hostable cryptocurrency payment-processing core combining a merchant API with wallet daemons for invoices, stores, products, payouts, refunds and operational management.",
        "bitcart-cryptocurrency-payment-core",
        "Bitcart cryptocurrency payment core",
        "operational:22",
        "CORE",
        ["Python 3.12+", "PostgreSQL", "Redis", "configured coin daemons", "deployment secrets"],
        categories,
        "Central backend repository in the wider Bitcart admin, store, deployment and SDK ecosystem.",
        extra={"self_hostable": True, "financial_execution": True},
    )

    merchants_api = review.make("API", "Bitcart Merchants API", "api/views/__init__.py", 1)
    finish(
        review,
        merchants_api,
        "FastAPI merchant and administration interface covering users, stores, products, invoices, wallets, payouts, notifications, plugins, tokens and server operations.",
        "bitcart-merchants-api",
        "Bitcart Merchants API",
        "operational:16",
        "INTERFACE",
        ["Bitcart Core", "database and cache", "coin daemons", "scoped authentication"],
        categories,
        "Primary HTTP interface to the payment core.",
        extra={"framework": "FastAPI", "authentication_scopes": True},
    )
    review.relate("PROVIDES", platform["id"], merchants_api["id"], "api/views/__init__.py", 1)

    api_specs = [
        ("Configurator API", "api/views/configurator.py", "Initial deployment configuration and setup operations.", "configurator"),
        ("Cryptocurrency Metadata API", "api/views/cryptos.py", "Supported cryptocurrency, token, exchange-rate, explorer and RPC metadata operations.", "cryptocurrency-metadata"),
        ("Discount API", "api/views/discounts.py", "Merchant discount CRUD operations.", "discount"),
        ("File API", "api/views/files.py", "Authenticated file upload, retrieval and deletion operations.", "file"),
        ("Health API", "api/views/health.py", "Service health and readiness checks.", "health"),
        ("Invoice and Refund API", "api/views/invoices.py", "Invoice creation, export, customer/payment-detail updates, refund creation and refund submission operations.", "invoice-refund"),
        ("Server Management API", "api/views/manage.py", "Policies, backup, logs, updates, cleanup, host-agent jobs, daemon status and exchange-rate source administration.", "server-management"),
        ("Metrics API", "api/views/metrics.py", "Prometheus-compatible operational metrics surface.", "metrics"),
        ("Notification API", "api/views/notifications.py", "Notification provider discovery, schemas and notification configuration CRUD.", "notification"),
        ("Payout API", "api/views/payouts.py", "Authenticated payout creation and lifecycle operations.", "payout"),
        ("Plugin API", "api/views/plugins.py", "Plugin installation, removal, settings and license administration.", "plugin"),
        ("Product API", "api/views/products.py", "Store product catalog, image, category, price and CRUD operations.", "product"),
        ("Store API", "api/views/stores.py", "Store configuration, email, theme, plugin, rate and checkout operations.", "store"),
        ("Template API", "api/views/templates.py", "Merchant-facing template retrieval operations.", "template"),
        ("Authentication Token API", "api/views/token.py", "Login, token refresh, password reset, email verification and WebAuthn or two-factor authentication operations.", "authentication-token"),
        ("Tor API", "api/views/tor.py", "Tor deployment and address information surface.", "tor"),
        ("Update API", "api/views/update.py", "Bitcart update availability and version information.", "update"),
        ("User API", "api/views/users.py", "User, account, policy, password, token and identity management operations.", "user"),
        ("Wallet API", "api/views/wallets.py", "Wallet CRUD, validation, balances, history, channel and Lightning payment operations.", "wallet"),
        ("WebSocket API", "api/views/websocket.py", "Authenticated realtime event subscription surface.", "websocket"),
    ]
    for name, path, description, slug in api_specs:
        entity = review.make("API", f"Bitcart {name}", path, 1)
        finish(
            review,
            entity,
            description,
            f"bitcart-{slug}-api",
            f"Bitcart {name}",
            "operational:16",
            "INTERFACE",
            ["Bitcart Merchants API", "operation-specific authorization scope"],
            categories,
            "Stable router-level API boundary; individual route functions are folded into this surface.",
        )
        review.relate("CONTAINS", merchants_api["id"], entity["id"], path, 1)

    daemon_framework = review.make("SERVICE", "Bitcart Coin Daemon Framework", "daemons/base.py", 1)
    finish(
        review,
        daemon_framework,
        "Authenticated aiohttp daemon framework with extended JSON-RPC 2.0 execution, WebSocket notifications, specifications and coin-specific configuration.",
        "bitcart-coin-daemon-framework",
        "Bitcart coin daemon framework",
        "operational:22",
        "FRAMEWORK",
        ["aiohttp", "coin-specific wallet or RPC implementation", "daemon authentication secret"],
        categories,
        "Base implementation shared by the ready coin daemons.",
        extra={"protocol": "extended JSON-RPC 2.0", "websocket_notifications": True},
    )
    review.relate("CONTAINS", platform["id"], daemon_framework["id"], "daemons/README.md", 1)
    review.relate("DEPENDS_ON", merchants_api["id"], daemon_framework["id"], "README.md", 1)

    daemon_specs = [
        ("Bitcoin", "BTC", "daemons/btc.py", "Electrum-backed Bitcoin wallet daemon with optional Lightning Network operations."),
        ("Bitcoin Cash", "BCH", "daemons/bch.py", "Electron Cash-backed Bitcoin Cash wallet daemon."),
        ("BNB Smart Chain", "BNB", "daemons/bnb.py", "Ethereum-compatible BNB Smart Chain payment daemon."),
        ("Ethereum", "ETH", "daemons/eth.py", "Web3-based Ethereum account, token, transaction and payment daemon."),
        ("Groestlcoin", "GRS", "daemons/grs.py", "Electrum-derived Groestlcoin wallet daemon."),
        ("Litecoin", "LTC", "daemons/ltc.py", "Electrum-derived Litecoin wallet daemon."),
        ("Polygon", "MATIC", "daemons/matic.py", "Ethereum-compatible Polygon payment daemon."),
        ("Tron", "TRX", "daemons/trx.py", "Tron account, token, transaction and payment daemon."),
        ("Monero", "XMR", "daemons/xmr.py", "Monero wallet and payment daemon."),
        ("Ergon", "XRG", "daemons/xrg.py", "Bitcoin-family Ergon wallet daemon."),
    ]
    for name, symbol, path, description in daemon_specs:
        entity = review.make("SERVICE", f"Bitcart {name} Daemon", path, 1)
        finish(
            review,
            entity,
            description,
            f"bitcart-{symbol.lower()}-payment-daemon",
            f"Bitcart {name} payment daemon",
            "operational:22",
            "SERVICE",
            ["Bitcart daemon framework", "coin network provider or wallet library", "wallet material and RPC credentials"],
            categories,
            "Ready coin-specific implementation of the shared daemon protocol.",
            extra={"currency_symbol": symbol, "wallet_or_private_key_access": True},
        )
        review.relate("PROVIDES", daemon_framework["id"], entity["id"], path, 1)

    plugin = review.make("PLUGIN", "Bitcart Plugin System", "api/services/plugin_manager.py", 1)
    finish(
        review,
        plugin,
        "Installable archive-based plugin system spanning backend, admin, store and deployment assets with hooks, filters, settings and license handling.",
        "bitcart-plugin-system",
        "Bitcart plugin system",
        "operational:02",
        "FRAMEWORK",
        ["Bitcart deployment", "trusted .bitcart plugin archive", "writable plugin and deployment directories"],
        categories,
        "Extends the payment platform and can install executable backend or deployment content.",
        extra={"arbitrary_code_installation": True, "archive_format": ".bitcart"},
    )
    review.relate("CONTAINS", platform["id"], plugin["id"], "api/services/plugin_manager.py", 1)

    notifications = review.make("SERVICE", "Bitcart Notification Manager", "api/services/notification_manager.py", 1)
    finish(
        review,
        notifications,
        "Apprise-backed notification service that discovers provider schemas and sends store events through configured notification channels.",
        "bitcart-apprise-notification-service",
        "Bitcart notification service",
        "operational:16",
        "SERVICE",
        ["Bitcart store configuration", "Apprise", "provider-specific credentials"],
        categories,
        "Reusable delivery service behind the notification API and payment events.",
    )
    review.relate("CONTAINS", platform["id"], notifications["id"], "api/services/notification_manager.py", 1)

    retained = set(review.out)
    for entity in review.existing:
        if entity["id"] not in retained:
            review.drop(entity)

    result = review.finalize(
        categories,
        [],
        "SECURITY REVIEW REQUIRED",
        "operational:22",
        {
            "SERVICE": "Payment core, daemon framework, ten coin daemons and notification service retained.",
            "API": "Merchants API plus twenty router-level surfaces retained; 121 route declarations folded into those stable boundaries.",
            "PLUGIN": "Archive-based cross-product plugin system retained.",
            "PACKAGE": "Python project declaration represented by the payment-core service.",
            "WORKFLOW": "Repository lint, test, image and release workflows are operational automation rather than product capabilities.",
        },
        deep_review=(
            "Wallet/private-key, payment, payout, secrets, authentication and arbitrary-code triggers were reviewed narrowly. "
            "The system operates coin wallets and Lightning channels, creates payouts and refunds, exposes scoped management APIs, "
            "loads provider credentials, installs executable plugin archives and can restart or update its host deployment."
        ),
        details=[
            "121 route-level declarations represented by twenty router APIs",
            "four repository CI and release workflows",
            "CRUD repositories, schemas and models represented by product/API boundaries",
        ],
    )
    return complete_scoped(review, result, resolved_errors)


def main() -> None:
    result = review_bitcart()
    r.build()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
