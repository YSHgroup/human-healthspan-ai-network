# API

REST, versioned under `/api/v1/`. The FastAPI application lives in `api/app`.

## Implemented today

| Method | Path | Purpose |
|---|---|---|
| GET | `/healthz` | Liveness only; does not check the database or external services. |
| GET | `/readyz` | Executes `SELECT 1` against the configured database. |
| POST | `/api/v1/user/auth/register` | Register a member and issue an HttpOnly session cookie. Email verification is not implemented. |
| POST | `/api/v1/user/auth/login` | Verify a password and issue a new session cookie. |
| POST | `/api/v1/user/auth/refresh` | Rotate the current session token and extend its idle expiry, up to the absolute lifetime cap. |
| POST | `/api/v1/user/auth/logout` | Revoke the current session and clear the cookie. |
| GET | `/api/v1/user/auth/me` | Return the authenticated member and current AI-learning consent state. |
| PUT | `/api/v1/user/auth/ai-learning-consent` | Record versioned, revocable opt-in/out for retaining AI prompt/response content for review. |
| GET | `/api/v1/user/social/messages/conversations` | List conversations for the authenticated participant. |
| POST | `/api/v1/user/social/messages/conversations` | Create a direct or group conversation by registered participant emails. |
| GET | `/api/v1/user/social/messages/conversations/{conversation_id}/messages` | List text messages for a participant. |
| POST | `/api/v1/user/social/messages/conversations/{conversation_id}/messages` | Send a text-only message; attachments are rejected. |
| WebSocket | `/api/v1/user/social/messages/conversations/{conversation_id}/ws` | Receive new messages for an authenticated conversation participant in real time. |
| POST | `/api/v1/user/social/ai/chat` | General Platform AI chat via the configured provider gateway. |
| POST | `/api/v1/user/researcher/ai/chat` | Restricted Scientist prompt-only prototype; requires verified and approved researcher records and `SCIENTIST_ENABLED=true`. |

Cross-cutting behavior already in place:

- CORS allows only the origins in `API_CORS_ORIGINS`, with credentials (session cookies). The local default is ports 3000–3003 on `localhost`; no custom domain is needed.
- Every response carries `X-Request-ID` and baseline security headers.
- Browser write requests require an `Origin` header matching the trusted-origin list.
- Sessions use a random opaque token in an HttpOnly, SameSite=Lax cookie; only its SHA-256 digest is stored. The cookie has no Domain attribute, so `localhost` apps on ports 3000–3003 share it.
- Sessions expire after 14 days of inactivity and have a 60-day absolute lifetime by default. Refresh rotates the token and extends the idle expiry without extending the absolute lifetime; configure `SESSION_TTL_DAYS` and `SESSION_MAX_LIFETIME_DAYS` as needed.
- The default development database is SQLite at `./healthspan.db`; configure `DATABASE_URL` for PostgreSQL.
- AI provider credentials remain server-side. The default provider is disabled and returns an explicit 503 until configured.

The routers `/api/v1/user/social`, `/api/v1/user/personal`, `/api/v1/user/researcher` and
`/api/v1/admin` are mounted. Beyond the identity, messaging and AI endpoints above, product workflows remain unimplemented.

The owner retired the separate legacy MVP as a migration source. This route list describes the
current API contract; backward compatibility with the removed legacy implementation is not
provided.

## Deliberate limitations

- Account registration does not verify email; password recovery, MFA, refresh rate limiting and administrative identity workflows are not implemented. Do not expose this development slice as a production identity service.
- Researcher approval is never assigned during registration. No researcher approval or admin grant endpoint is implemented.
- The Scientist prototype has no literature retrieval, project context, document access, citations or scientific tools. It explicitly tells the model not to claim these capabilities.
- AI sources are returned as an empty list. The prompt requests non-fabricated citations, but provider output is not independently verified.
- AI interaction metadata is recorded. Prompt/answer content is stored only after affirmative AI-learning consent; revocation clears previously retained content. No training or export job is implemented.
- Direct/group messaging stores text only; attachments, audio and video are not part of this MVP slice.
- Message WebSockets validate the request origin, session cookie and conversation membership. Delivery is in-process; run one API worker for local MVP real-time messaging. Persisted messages remain available through the REST history endpoint after a disconnect.

## Target organization (planned)

```text
/api/v1/user/
  social/       feed, posts, comments, reactions, communities, discussions, events,
                invitations, notifications, connections                      (M2)
  personal/     profile, professional, health, records, sharing, activity,
                devices                                                      (M2, health M5)
  researcher/   research, evidence, literature, projects, tasks, reports,
                organizations, workspace, organization-ai                    (M3)
/api/v1/admin/  users, organizations, communities, events, moderation, reports,
                subscriptions, payments, badges, certifications,
                ai-monitoring, configuration, audit                          (M3)
```

## Rules

- Route handlers stay thin; business rules live in `api/app/domains/<domain>` and are shared by
  all API areas. The same rule is never implemented separately per portal.
- Every sensitive operation verifies the requesting user's rights on the specific resource.
- Preserve request and response behavior of existing MVP endpoints; use compatibility adapters.
- Remove obsolete routes only after migration and tests.
- Errors use the shape `{ code, message, requestId }` (see `@healthspan/shared-types` `ApiProblem`).
- Write endpoints need tests (authorization and privacy) and a row in this document first.
- Migrations are run from the repository root with `npm run db:migrate`; the API dev command applies them before starting the server.
