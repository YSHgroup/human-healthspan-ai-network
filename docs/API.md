# API v1

Base path: `/api/v1`. Interactive OpenAPI documentation is available at `/docs`.

## Authentication

Registration creates an unverified account and issues a single-use verification token. In development/test mode the token is returned in the response; configure SMTP (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, and `EMAIL_FROM`) to deliver verification and password-reset tokens by email. Production registration is unavailable if delivery is not configured.

The member web app exchanges credentials through same-origin Next.js routes and stores both tokens in HttpOnly, SameSite=Strict cookies scoped to `/api` (Secure in production). Tokens are not exposed to browser JavaScript or local storage. Protected writes are proxied server-side with the access token.

The web session routes are `/api/auth/login`, `/api/auth/register`, `/api/auth/session`, `/api/auth/logout`, `/api/auth/verify-email`, `/api/auth/resend-verification`, `/api/auth/password-reset`, `/api/auth/password-reset-confirm`, and `/api/auth/password-change`.

Set `PUBLIC_APP_URL` to the canonical web origin so verification and reset emails contain working one-time links. Production requires HTTPS. Password changes require the current password and revoke every active session; users must sign in again afterward.

After verifying email, log in to receive short-lived access and refresh tokens. Send the access token as `Authorization: Bearer <token>`. Refresh tokens rotate on use and cannot be replayed. Logout revokes the associated session; password reset revokes all active sessions for that account.

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `POST /auth/verify-email`
- `POST /auth/resend-verification`
- `POST /auth/password-reset`
- `POST /auth/password-reset/confirm`
- `POST /auth/password-change`
- `GET|PATCH /auth/me`
- `GET|PATCH /me` and `/users/me` (compatibility aliases)

New passwords must be at least 12 characters. Passwords are hashed with Argon2id through `pwdlib`. Access and refresh tokens are signed JWTs backed by revocable database sessions.

Member profiles include a display name, biography, location, time zone, interests, topics, expertise, researcher identifier, and organization affiliation. Users control whether their profile is public. Unexpected profile fields (including role) are rejected; roles remain operator-managed.

## Profiles and social

- `GET /users/{id}` — public profiles only; private profiles return 404
- `GET /feed?limit=25&offset=0&community_id=...`
- Feed records include public-safe author labels, content classification, comment/reaction counts, and the current member's reaction/bookmark state when authenticated.
- `POST /posts` — authenticated; author identity comes from the token, never the request body
- `GET|DELETE /posts/{id}`
- `GET|POST /posts/{id}/comments`
- `POST|DELETE /posts/{id}/reactions`
- `POST|DELETE /posts/{id}/bookmark`
- `POST|DELETE /users/{id}/follow`
- `GET /communities`
- Community records include current member counts and, when authenticated, whether the current member has joined.
- `GET /communities/{id}`
- `GET /communities/{id}/feed`
- `GET /communities/{id}/feed`
- `POST|DELETE /communities/{id}/join`

Post classifications distinguish personal experience, opinion, scientific evidence, expert interpretation, research hypotheses, AI-generated hypotheses, and speculation. Deletions are soft deletes. Users must join a community before posting to it.

## Research and evidence

- `GET|POST /research/projects`
- `GET|PATCH /research/projects/{id}`
- `POST /research/projects/{id}/members`
- `GET /research/projects/{id}/members`
- `GET /research/projects/{id}/questions`
- `GET|POST /research/projects/{id}/hypotheses`
- `POST /research/questions`
- `POST /research/questions/{id}/hypotheses`
- `GET|POST /research/projects/{id}/literature`
- `GET|POST /research/projects/{id}/evidence`

Project visibility is `private`, `team`, or `public`. Project membership and owner permissions are enforced server-side for project metadata, questions, literature, and evidence. Team members can write; reviewers are read-only. Adding a member requires team visibility.

## Search

- `GET /search?q=...&limit=20` — posts, public profiles, public projects, and communities
- `GET /science/search?q=...&limit=20` — literature metadata attached to public projects

Search currently uses PostgreSQL text matching. Redis and OpenSearch are not yet wired into application behavior.

## Moderation and administration

- `POST /reports`
- `GET /moderation/queue` — administrator, moderator, or scientific reviewer
- `POST /moderation/reports/{id}/decision`
- `GET /admin/users` — administrator only
- `PATCH /admin/users/{id}` — administrator only; requires a reason
- `GET /admin/communities` — administrator only
- `PATCH /admin/communities/{id}` — administrator only; activation changes require a reason and are audited
- `GET /admin/reports`
- `GET /admin/audit-logs` — administrator or read-only auditor
- `GET /admin/ai-monitoring` — currently reports provider status

The separate Admin App runs at `http://localhost:3001` in Docker Compose. Its same-origin server proxy stores backend tokens in HttpOnly cookies and only forwards admin/moderation API routes.

Administrative account changes and moderation actions are audited. Admin creation is an operator action:

```text
docker compose exec api python -m app.cli create-admin admin@example.org
```

## AI

- `POST /ai/chat`
- `POST /ai/research`

Both require authentication and return `503 Service Unavailable` until an approved AI provider is configured. No generated answers or fake AI-run records are returned.

## Runtime and migrations

- `GET /health` — API process liveness
- `GET /ready` — database readiness
- Database schema changes are managed with Alembic and applied when the API container starts.
- Tests: `python -m pytest tests\test_api_contract.py -q`

Rate limiting and abuse monitoring, MFA enforcement, OIDC/SSO, session-management UI, account deletion, avatar/media upload, background document ingestion/file scanning, AI-provider integration, and production mail-delivery operations remain follow-up work. The current implementation is not a substitute for these production controls.
