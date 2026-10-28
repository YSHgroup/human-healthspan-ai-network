# Overall progress implemented

The member-facing web MVP shell is in place. A separate lightweight, noindex Admin App is initialized at `apps/admin/`, with an operator login, dashboard, moderation queue, user management, and audit-log views. It proxies the backend server-side and keeps auth tokens in HttpOnly cookies.

The backend now has a persistent FastAPI/SQLAlchemy API foundation, Alembic migrations, PostgreSQL runtime configuration, and SQLite-backed integration tests.

Implemented backend capabilities include email/password registration and login, email verification, password reset, revocable JWT-backed sessions, profile management, public feed and post creation, comments, follows, reactions, bookmarks, six seeded communities, team-scoped research projects/questions/hypotheses/literature/evidence, scoped search/retrieval, reports/moderation, admin account controls, audit events, readiness checks, and an operator command for bootstrapping an administrator.

SMTP delivery is configurable. Development/test environments return one-time verification/reset tokens in API responses. AI routes explicitly return `503` until an approved provider is configured; no fake AI outputs are returned.

The frontend still uses mock-backed feed/projects and its composer still sends a temporary author ID. The backend ignores client-supplied authors and requires authentication for writes, so completing the frontend auth/API integration remains necessary.

----------
# Last Change

Initialized the separate Admin App, integrated it in Docker Compose at port 3001, and implemented session-protected dashboard, moderation, user management, and audit views. Verified sign-in, user search, moderation queue, audit log, and mobile layout in a browser. Tightened backend access boundaries so admins do not implicitly access private research projects and support operators cannot suspend administrator accounts.

----------
# What is the next step?

Integrate the member web app with registration, email verification, login, and `/me`; pass bearer tokens on writes and replace mock feed/project data with the API. Then wire an approved AI provider, file/document ingestion with scanning, rate limiting, and production observability before public launch.
