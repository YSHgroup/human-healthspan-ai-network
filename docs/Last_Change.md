# Overall progress implemented

The member-facing web MVP shell is in place. A separate lightweight, noindex Admin App is initialized at `apps/admin/`, with an operator login, dashboard, moderation queue, user management, and audit-log views. It proxies the backend server-side and keeps auth tokens in HttpOnly cookies.

The backend now has a persistent FastAPI/SQLAlchemy API foundation, Alembic migrations, PostgreSQL runtime configuration, and SQLite-backed integration tests.

Implemented backend capabilities include email/password registration and login, email verification, password reset, revocable JWT-backed sessions, profile management, public feed and post creation, comments, follows, reactions, bookmarks, six seeded communities, team-scoped research projects/questions/hypotheses/literature/evidence, scoped search/retrieval, reports/moderation, admin account controls, audit events, readiness checks, and an operator command for bootstrapping an administrator.

SMTP delivery is configurable. Development/test environments return one-time verification/reset tokens in API responses. AI routes explicitly return `503` until an approved provider is configured; no fake AI outputs are returned.

The frontend still uses mock-backed feed/projects and its composer still sends a temporary author ID. The backend ignores client-supplied authors and requires authentication for writes, so completing the frontend auth/API integration remains necessary.

The JavaScript apps now use a root npm workspace. Shared Button, Badge, Input, Select, and brand tokens are consumed from `packages/ui`; web and admin retain their own routes, layouts, and remaining app-specific UI. Docker builds use the repository root as context so workspace packages are available.

----------
# Last Change

Introduced the root npm workspace for the web/admin apps, extracted shared UI primitives into `packages/ui`, updated Docker builds for monorepo context, and revised architecture/roadmap docs to define the current structure, future worker/portal extension points, and scaling gates.

----------
# What is the next step?

Integrate member authentication and real API data, implement AI/document-ingestion workflows behind permission and quality gates, and add production observability, rate limiting, and recovery testing before public launch.
