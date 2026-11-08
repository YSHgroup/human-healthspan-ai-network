# API

REST, versioned under `/api/v1/`. The FastAPI application lives in `api/app`.

## Implemented today

| Method | Path | Purpose |
|---|---|---|
| GET | `/healthz` | Liveness only; does not check the database or external services. |
| GET | `/readyz` | Executes `SELECT 1` against the configured database. |
| POST | `/api/v1/user/auth/register` | Register a member and issue an HttpOnly session cookie. Email verification is not implemented. |
| POST | `/api/v1/user/auth/login` | Verify a password and issue a new session cookie. |
| POST | `/api/v1/user/auth/logout` | Revoke the current session and clear the cookie. |
| GET | `/api/v1/user/auth/me` | Return the authenticated member and current AI-learning consent state. |
| PUT | `/api/v1/user/auth/ai-learning-consent` | Record versioned, revocable opt-in/out for retaining AI prompt/response content for review. |
| GET | `/api/v1/user/social/feed` | List recent public discussions and questions. |
| POST | `/api/v1/user/social/posts` | Publish an authenticated public discussion or question. |
| GET | `/api/v1/user/social/communities` | List communities and the current member's access status. |
| POST | `/api/v1/user/social/communities/requests` | Submit a free community creation request for platform review. |
| POST | `/api/v1/user/social/communities/{community_id}/join` | Join an open community or apply to a restricted one. |
| GET | `/api/v1/user/social/communities/{community_id}/memberships/pending` | List applications for a community moderator. |
| POST | `/api/v1/user/social/communities/{community_id}/memberships/{membership_id}/decision` | Approve or reject a restricted-community application. |
| GET | `/api/v1/user/social/communities/{community_id}/posts` | List published discussions in an accessible community. |
| POST | `/api/v1/user/social/communities/{community_id}/posts` | Publish to a community as an active member. |
| GET | `/api/v1/user/social/posts/{post_id}/comments` | List published comments when the member can access the post. |
| POST | `/api/v1/user/social/posts/{post_id}/comments` | Comment on an accessible post. |
| GET | `/api/v1/user/social/posts/{post_id}/reactions` | Read reaction count and the current member's reaction. |
| PUT | `/api/v1/user/social/posts/{post_id}/reactions` | Set or change the current member's reaction. |
| DELETE | `/api/v1/user/social/posts/{post_id}/reactions` | Remove the current member's reaction. |
| POST | `/api/v1/user/social/posts/{post_id}/reports` | Submit one pending moderation report per member/post. |
| POST | `/api/v1/user/social/comments/{comment_id}/reports` | Submit one pending moderation report per member/comment. |
| GET | `/api/v1/user/social/communities/{community_id}/moderation/reports` | List pending reports for an authorized community moderator. |
| POST | `/api/v1/user/social/communities/{community_id}/moderation/reports/{report_id}/actions` | Hide/remove content, warn, suspend posting temporarily, escalate, or dismiss a report. |
| GET | `/api/v1/user/social/me/moderation/actions` | List moderation actions against the current member. |
| POST | `/api/v1/user/social/me/moderation/actions/{action_id}/appeals` | Appeal an eligible warning, hide, removal, or suspension. |
| GET | `/api/v1/user/social/communities/{community_id}/moderation/appeals` | List pending appeals for an authorized community moderator. |
| POST | `/api/v1/user/social/communities/{community_id}/moderation/appeals/{appeal_id}/decision` | Uphold or overturn a member's appeal. |
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
- Browser write requests with an `Origin` header are checked against the trusted-origin list.
- Social feed content is public. Posting and reporting require an authenticated session and a trusted `Origin`; reports are queued for later moderation review.
- Community membership is scoped to each community. Open communities admit registered members directly; restricted communities require moderator approval. Restricted-community posts/comments/reactions are available only to active members.
- Community moderation is enforced by active owner/moderator membership. Actions are recorded; posting suspensions are time-limited, and appeals can overturn actions and restore hidden content or posting access.
- Sessions use a random opaque token in an HttpOnly, SameSite=Lax cookie; only its SHA-256 digest is stored. The cookie has no Domain attribute, so `localhost` apps on ports 3000–3003 share it.
- The default development database is SQLite at `./healthspan.db`; configure `DATABASE_URL` for PostgreSQL.
- AI provider credentials remain server-side. The default provider is disabled and returns an explicit 503 until configured.

The routers `/api/v1/user/social`, `/api/v1/user/personal`, `/api/v1/user/researcher` and
`/api/v1/admin` are mounted. The admin router is still only a namespace: platform staff cannot
approve community-creation requests or review escalations in this slice. Communities and their
initial owner/moderator membership must currently be provisioned by trusted operations. Topics,
comment reactions, warnings/appeals notifications, and a platform-wide moderation queue are also
not implemented.

The owner retired the separate legacy MVP as a migration source. This route list describes the
current API contract; backward compatibility with the removed legacy implementation is not
provided.

## Deliberate limitations

- Account registration does not verify email; password recovery, MFA, refresh/rotation, rate limiting and administrative identity workflows are not implemented. Do not expose this development slice as a production identity service.
- Researcher approval is never assigned during registration. No researcher approval or admin grant endpoint is implemented.
- The Scientist prototype has no literature retrieval, project context, document access, citations or scientific tools. It explicitly tells the model not to claim these capabilities.
- AI sources are returned as an empty list. The prompt requests non-fabricated citations, but provider output is not independently verified.
- AI interaction metadata is recorded. Prompt/answer content is stored only after affirmative AI-learning consent; revocation clears previously retained content. No training or export job is implemented.
- Direct/group messaging stores text only; attachments, audio and video are not part of this MVP slice.
- Message WebSockets validate the request origin, session cookie and conversation membership. Delivery is in-process; run one API worker for local MVP real-time messaging. Persisted messages remain available through the REST history endpoint after a disconnect.
- Escalated reports are recorded as escalated but are not yet visible in an Admin queue. Reports against global posts/comments without a community likewise have no moderator queue until Admin moderation is implemented. Do not treat these APIs as production moderation coverage.

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
