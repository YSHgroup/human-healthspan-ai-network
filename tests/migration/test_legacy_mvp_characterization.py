"""Freeze the inspectable v0.4 legacy MVP contract stored in references/."""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "references" / "human-healthspan-ai-network-mvp-v0.4.zip"
ARCHIVE_ROOT = "human-healthspan-ai-network-main/"
API_ROOT = ARCHIVE_ROOT + "apps/api/app/"
ARCHIVE_SHA256 = "8539aab1f73a87754ac7bbef584df6e032c9866640b11fb7a5bce38cc72c66c7"

LEGACY_TABLES = {
    "ai_conversations",
    "ai_feedback",
    "ai_messages",
    "ai_runs",
    "audit_events",
    "auth_sessions",
    "auth_tokens",
    "badges",
    "bookmarks",
    "comments",
    "communities",
    "community_members",
    "consent_records",
    "conversation_participants",
    "conversations",
    "entitlements",
    "event_invitations",
    "event_registrations",
    "events",
    "evidence",
    "follows",
    "health_records",
    "health_shares",
    "hypotheses",
    "literature",
    "messages",
    "notifications",
    "org_ai_instances",
    "org_knowledge_documents",
    "organization_invitations",
    "organization_members",
    "organizations",
    "posts",
    "professional_records",
    "profiles",
    "project_organizations",
    "purchases",
    "reactions",
    "reports",
    "research_members",
    "research_memberships",
    "research_projects",
    "research_questions",
    "research_tasks",
    "subscription_plans",
    "subscriptions",
    "user_badges",
    "users",
    "work_history_entries",
}

LEGACY_MIGRATIONS = {
    "17101feebea7": None,
    "bf0deb599c56": "17101feebea7",
    "521e5042e44d": "bf0deb599c56",
    "cf5b66bc658f": "521e5042e44d",
    "9ac2a7348f16": "cf5b66bc658f",
    "a1c3f0b7d2e4": "9ac2a7348f16",
}


def _read_archive_file(name: str) -> str:
    with ZipFile(ARCHIVE) as archive:
        return archive.read(name).decode("utf-8")


def test_legacy_archive_matches_the_inventoried_baseline() -> None:
    assert ARCHIVE.is_file()
    assert hashlib.sha256(ARCHIVE.read_bytes()).hexdigest() == ARCHIVE_SHA256


def _routes(name: str) -> set[tuple[str, str, str]]:
    tree = ast.parse(_read_archive_file(API_ROOT + name))
    result: set[tuple[str, str, str]] = set()
    methods = {"get", "post", "put", "patch", "delete"}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
                continue
            if decorator.func.attr not in methods:
                continue
            router = ast.unparse(decorator.func.value)
            path = ast.literal_eval(decorator.args[0]) if decorator.args else ""
            result.add((router, decorator.func.attr.upper(), path))
    return result


def _model_tables(name: str) -> set[str]:
    tree = ast.parse(_read_archive_file(API_ROOT + name))
    tables: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(target, ast.Name) and target.id == "__tablename__" for target in targets):
                tables.add(ast.literal_eval(node.value))
    return tables


def _migration_revision(name: str) -> tuple[str | None, str | None]:
    tree = ast.parse(_read_archive_file(name))
    values: dict[str, str | None] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        else:
            continue
        for target in targets:
            if isinstance(target, ast.Name) and target.id in {"revision", "down_revision"}:
                values[target.id] = ast.literal_eval(node.value)
    return values.get("revision"), values.get("down_revision")


def test_archived_auth_social_research_and_messaging_routes_are_characterized() -> None:
    assert ARCHIVE.is_file()
    auth = _routes("api/auth.py")
    assert {
        ("router", "POST", "/register"),
        ("router", "POST", "/verify-email"),
        ("router", "POST", "/password-reset"),
        ("router", "POST", "/password-reset/confirm"),
        ("router", "POST", "/refresh"),
        ("router", "POST", "/logout"),
    } <= auth

    product = _routes("api/v1_routes.py")
    assert {
        ("router", "GET", "/feed"),
        ("router", "POST", "/posts"),
        ("router", "POST", "/posts/{post_id}/comments"),
        ("router", "POST", "/posts/{post_id}/reactions"),
        ("router", "GET", "/communities"),
        ("router", "POST", "/communities/{community_id}/join"),
        ("router", "GET", "/research/projects"),
        ("router", "POST", "/research/projects"),
        ("router", "POST", "/research/questions"),
        ("router", "POST", "/research/projects/{project_id}/hypotheses"),
        ("router", "POST", "/research/projects/{project_id}/literature"),
        ("router", "POST", "/research/projects/{project_id}/evidence"),
    } <= product

    messaging = _routes("domains/messaging/router.py")
    assert {
        ("router", "POST", ""),
        ("router", "GET", "/conversations"),
        ("router", "GET", "/conversations/{conversation_id}/messages"),
        ("router", "DELETE", "/{message_id}"),
    } <= messaging


def test_archived_ai_environments_and_data_boundaries_are_characterized() -> None:
    routes = _routes("ai/router.py")
    assert {
        ("general_router", "POST", "/chat"),
        ("general_router", "GET", "/conversations"),
        ("general_router", "POST", "/runs/{run_id}/feedback"),
        ("scientist_router", "POST", "/chat"),
        ("organization_ai_router", "POST", "/{organization_id}/chat"),
        ("organization_ai_router", "POST", "/{organization_id}/documents"),
    } <= routes

    test_sources = [
        _read_archive_file(ARCHIVE_ROOT + "tests/test_api_contract.py"),
        _read_archive_file(ARCHIVE_ROOT + "tests/test_platform_contract.py"),
    ]
    characterized = {
        node.name
        for source in test_sources
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    }
    assert len(characterized) == 37
    assert {
        "test_registration_login_profile_and_logout",
        "test_direct_messaging_privacy_and_notifications",
        "test_general_ai_cites_public_sources_and_never_reads_private_data",
        "test_ai_scientist_requires_approval_and_respects_project_permissions",
        "test_organization_ai_is_paid_and_strictly_org_scoped",
        "test_ai_runs_are_monitored_without_prompt_storage",
        "test_health_data_is_not_reachable_from_any_ai_retriever",
    } <= characterized


def test_archived_data_model_and_migration_chain_are_characterized() -> None:
    tables = _model_tables("models/domain.py") | _model_tables("models/platform.py")
    assert tables == LEGACY_TABLES

    migration_directory = API_ROOT + "db/migrations/versions/"
    with ZipFile(ARCHIVE) as archive:
        migration_files = [
            name
            for name in archive.namelist()
            if name.startswith(migration_directory)
            and name.endswith(".py")
            and not name.endswith("__init__.py")
        ]
    migrations = dict(_migration_revision(name) for name in migration_files)
    assert migrations == LEGACY_MIGRATIONS
