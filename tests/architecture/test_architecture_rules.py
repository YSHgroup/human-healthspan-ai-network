"""Architecture fitness tests.

They encode the mandatory rules of AGENT_RULE.md and docs/SYSTEM_DEVELOPMENT_ARCHITECTURE.md
so structural drift fails fast. Standard library only; run with `pnpm test:architecture`.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKIP_DIRS = {"node_modules", ".next", ".turbo", "dist", ".venv", "__pycache__"}

PORTALS = ["social-web", "personal-web", "researcher-web"]
APPS = PORTALS + ["admin"]
PACKAGES = [
    "ui", "design-tokens", "api-client", "auth-client",
    "shared-types", "validation", "shared-config", "testing",
]
API_DOMAINS = [
    "identity", "users", "profiles", "social", "messaging", "events", "communities", "health",
    "organizations", "professional_history", "research", "evidence", "projects", "workspace",
    "subscriptions", "payments", "badges", "notifications", "files", "governance", "audit",
]
AI_MODULES = [
    "gateway", "orchestration", "general", "scientist", "organization", "knowledge",
    "training", "evaluation", "governance", "monitoring", "shared",
]
AI_ENVIRONMENTS = ["general", "scientist", "organization"]


def _files(base: Path, suffixes: tuple[str, ...]):
    for path in base.rglob("*"):
        if path.is_file() and path.suffix in suffixes and not (set(path.parts) & SKIP_DIRS):
            yield path


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            found.append(node.module)
    return found


# --------------------------------------------------------------------------- structure
def test_top_level_areas_exist() -> None:
    for name in ["apps", "api", "ai", "packages", "infra", "docs", "tests"]:
        assert (ROOT / name).is_dir(), f"missing top-level area: {name}"
    for name in ["AGENT_RULE.md", "package.json", "pnpm-workspace.yaml", "turbo.json",
                 "docker-compose.yml", ".env.example", "README.md"]:
        assert (ROOT / name).is_file(), f"missing root file: {name}"


def test_api_and_ai_are_not_nested_in_apps() -> None:
    assert not (ROOT / "apps" / "api").exists()
    assert not (ROOT / "apps" / "ai").exists()


def test_applications_exist() -> None:
    for app in APPS:
        assert (ROOT / "apps" / app / "package.json").is_file(), app


def test_shared_packages_exist() -> None:
    for pkg in PACKAGES:
        assert (ROOT / "packages" / pkg / "package.json").is_file(), pkg


def test_api_domains_and_versioned_areas_exist() -> None:
    for domain in API_DOMAINS:
        assert (ROOT / "api/app/domains" / domain / "__init__.py").is_file(), domain
    for area in ["user/social", "user/personal", "user/researcher", "admin"]:
        assert (ROOT / "api/app/api/v1" / area / "__init__.py").is_file(), area


def test_ai_modules_exist() -> None:
    for module in AI_MODULES:
        assert (ROOT / "ai/healthspan_ai" / module / "__init__.py").is_file(), module


def test_required_documentation_exists() -> None:
    docs = [
        "SYSTEM_DEVELOPMENT_ARCHITECTURE.md", "MVP_SPECIFICATION.md", "DEVELOPMENT_ROADMAP.md",
        "ARCHITECTURE.md", "API.md", "DATA_MODEL.md", "AI_ARCHITECTURE.md",
        "AI_TRAINING_STRATEGY.md", "SECURITY.md", "PRIVACY_AND_GOVERNANCE.md",
        "MIGRATION_PLAN.md", "DEPLOYMENT.md", "Last_Change.md",
    ]
    for name in docs:
        assert (ROOT / "docs" / name).is_file(), f"missing docs/{name}"


# --------------------------------------------------------------------------- frontends
def test_applications_do_not_depend_on_each_other() -> None:
    names = {"social-web", "personal-web", "researcher-web", "admin"}
    pattern = re.compile(r"""['"](?:[./]*/)?apps/([a-z-]+)|@healthspan/(social-web|personal-web|researcher-web|admin)\b""")
    for base in [ROOT / "apps", ROOT / "packages"]:
        for path in _files(base, (".ts", ".tsx", ".mjs", ".json")):
            if path.name in {"package-lock.json", "tsconfig.tsbuildinfo"}:
                continue
            own = path.relative_to(ROOT).parts
            own_app = own[1] if own[0] == "apps" else None
            for match in pattern.finditer(path.read_text(encoding="utf-8")):
                target = match.group(1) or match.group(2)
                if target in names and target != own_app and path.name != "sync-brand-assets.mjs":
                    raise AssertionError(f"{path.relative_to(ROOT)} references application {target}")


def test_frontends_do_not_access_databases_directly() -> None:
    forbidden = {"pg", "postgres", "prisma", "@prisma/client", "drizzle-orm", "typeorm", "knex",
                 "mongoose", "sequelize", "mysql2", "redis", "ioredis"}
    for pkg_json in list((ROOT / "apps").glob("*/package.json")) + list((ROOT / "packages").glob("*/package.json")):
        data = json.loads(pkg_json.read_text(encoding="utf-8"))
        deps = set(data.get("dependencies", {})) | set(data.get("devDependencies", {}))
        assert not (deps & forbidden), f"{pkg_json.relative_to(ROOT)} depends on {deps & forbidden}"


def test_no_tokens_in_browser_storage() -> None:
    pattern = re.compile(r"(localStorage|sessionStorage)")
    for base in [ROOT / "apps", ROOT / "packages"]:
        for path in _files(base, (".ts", ".tsx")):
            assert not pattern.search(path.read_text(encoding="utf-8")), (
                f"{path.relative_to(ROOT)} uses browser storage; sessions use secure cookies"
            )


def test_private_portals_are_not_indexable() -> None:
    for portal in ["personal-web", "researcher-web"]:
        layout = (ROOT / "apps" / portal / "app/layout.tsx").read_text(encoding="utf-8")
        assert "index: false" in layout, f"{portal} layout must set robots index:false"
        robots = (ROOT / "apps" / portal / "app/robots.ts").read_text(encoding="utf-8")
        assert 'disallow: "/"' in robots, f"{portal} robots.ts must disallow everything"
    admin = (ROOT / "apps/admin/index.html").read_text(encoding="utf-8")
    assert "noindex" in admin


def test_public_sitemap_lists_only_the_social_portal() -> None:
    for portal in ["personal-web", "researcher-web"]:
        assert not (ROOT / "apps" / portal / "app/sitemap.ts").exists()


def test_framework_decisions() -> None:
    for portal in PORTALS:
        deps = json.loads((ROOT / "apps" / portal / "package.json").read_text())["dependencies"]
        assert "next" in deps and "vite" not in deps, portal
    admin = json.loads((ROOT / "apps/admin/package.json").read_text())
    assert "vite" in admin["devDependencies"] and "next" not in admin.get("dependencies", {})


def test_workspace_works_with_npm_and_pnpm() -> None:
    """npm cannot read the pnpm `workspace:` protocol, so local packages use a plain range."""
    root_pkg = json.loads((ROOT / "package.json").read_text())
    assert root_pkg["workspaces"] == ["apps/*", "packages/*"]
    assert (ROOT / "pnpm-workspace.yaml").is_file()
    for pkg_json in list((ROOT / "apps").glob("*/package.json")) + list((ROOT / "packages").glob("*/package.json")):
        text = pkg_json.read_text(encoding="utf-8")
        assert "workspace:" not in text, f"{pkg_json.relative_to(ROOT)} uses the pnpm-only workspace: protocol"


def test_lockfiles_exist_only_at_the_repository_root() -> None:
    stray = [p for pattern in ("*/*/package-lock.json", "*/*/pnpm-lock.yaml", "*/*/yarn.lock")
             for p in ROOT.glob(pattern) if "node_modules" not in p.parts]
    assert not stray, f"nested lockfiles found: {stray}"
    assert not (ROOT / "yarn.lock").exists()


# --------------------------------------------------------------------------- AI separation
def test_ai_platform_does_not_import_the_api() -> None:
    for path in _files(ROOT / "ai", (".py",)):
        for module in _imports(path):
            assert module.split(".")[0] != "app", f"{path.relative_to(ROOT)} imports the API ({module})"


def test_api_reaches_ai_only_through_stable_interfaces() -> None:
    allowed = {"healthspan_ai.gateway", "healthspan_ai.shared"}
    for path in _files(ROOT / "api", (".py",)):
        for module in _imports(path):
            if module.split(".")[0] == "healthspan_ai":
                assert any(module == a or module.startswith(a + ".") for a in allowed), (
                    f"{path.relative_to(ROOT)} imports {module}; use gateway or shared interfaces"
                )


def test_ai_environments_are_logically_separated() -> None:
    """General, Private Scientist and Organization AI must not import one another."""
    for env in AI_ENVIRONMENTS:
        others = [e for e in AI_ENVIRONMENTS if e != env]
        for path in _files(ROOT / "ai/healthspan_ai" / env, (".py",)):
            for module in _imports(path):
                for other in others:
                    assert not module.startswith(f"healthspan_ai.{other}"), (
                        f"{path.relative_to(ROOT)} crosses AI boundary: {module}"
                    )


# --------------------------------------------------------------------------- API
def test_api_does_not_expose_unplanned_product_routes() -> None:
    """Every implemented write route has explicit documentation."""
    route_prefixes = {
        "auth.py": "/api/v1/user/auth",
        "messaging.py": "/api/v1/user/social/messages",
        "feed.py": "/api/v1/user/social",
        "communities.py": "/api/v1/user/social",
        "ai_chat.py": "/api/v1/user",
    }
    path_prefixes = {
        ROOT / "api/app/api/v1/admin/research.py": "/api/v1/admin",
        ROOT / "api/app/api/v1/user/researcher/__init__.py": "/api/v1/user/researcher",
    }
    route_pattern = re.compile(r'@router\.(post|put|patch|delete)\(\s*"([^"]+)"')
    routes: set[tuple[str, str]] = set()
    for path in _files(ROOT / "api/app/api", (".py",)):
        source = path.read_text(encoding="utf-8")
        matches = list(route_pattern.finditer(source))
        if not matches:
            continue
        prefix = path_prefixes.get(
            path,
            "/api/v1/admin"
            if path == ROOT / "api/app/api/v1/admin/__init__.py"
            else route_prefixes.get(path.name),
        )
        assert prefix is not None, f"unreviewed write routes in {path.relative_to(ROOT)}"
        routes.update(
            (match.group(1).upper(), f"{prefix}{match.group(2)}") for match in matches
        )

    api_doc = (ROOT / "docs" / "API.md").read_text(encoding="utf-8")
    for method, route in routes:
        assert f"| {method} | `{route}` |" in api_doc, f"undocumented API route: {method} {route}"
    assert routes, "expected the authenticated MVP write routes to be documented"


def test_env_example_has_no_real_secrets() -> None:
    text = (ROOT / ".env.example").read_text(encoding="utf-8")
    assert "replace-with" in text
    assert not re.search(r"sk-[A-Za-z0-9]{20,}", text)
