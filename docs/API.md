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
| GET | `/api/v1/admin/communities/requests` | List pending community requests for a verified, allowlisted platform administrator. |
| POST | `/api/v1/admin/communities/requests/{request_id}/decision` | Approve and provision a community with its requester as active owner, or reject the request. |
| GET | `/api/v1/admin/moderation/reports` | List pending reports on global content and escalated community reports. |
| POST | `/api/v1/admin/moderation/reports/{report_id}/actions` | Hide/remove content, warn its author, or dismiss an eligible global/escalated report. |
| GET | `/api/v1/admin/moderation/appeals` | List appeals against global moderation actions. |
| POST | `/api/v1/admin/moderation/appeals/{appeal_id}/decision` | Uphold or overturn a global moderation action. |

## M3 researcher and administration endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/user/researcher/me` | Read email-verification, researcher-approval, and application status. |
| POST | `/api/v1/user/researcher/applications` | Submit or resubmit a researcher-access application after account verification. |
| GET | `/api/v1/user/researcher/profile` | Read the current approved researcher profile. |
| PUT | `/api/v1/user/researcher/profile` | Edit an approved profile and opt into or out of public researcher discovery. |
| GET | `/api/v1/user/researcher/profiles` | Browse only approved profiles explicitly marked public. |
| GET | `/api/v1/user/researcher/organizations` | List the authenticated member's active organization memberships. |
| POST | `/api/v1/user/researcher/organizations/requests` | Submit a free organization-creation request with identity and website details. |
| GET | `/api/v1/user/researcher/organizations/requests/me` | List the authenticated member's organization requests. |
| GET | `/api/v1/user/researcher/organizations/invitations` | List unexpired invitations addressed to the authenticated email. |
| POST | `/api/v1/user/researcher/organizations/invitations/{invitation_id}/accept` | Accept an invitation addressed to the current account. |
| POST | `/api/v1/user/researcher/organizations/invitations/{invitation_id}/decline` | Decline an invitation addressed to the current account. |
| POST | `/api/v1/user/researcher/organizations/{organization_id}/invitations` | Invite an email to an organization as a member or admin. |
| GET | `/api/v1/user/researcher/organizations/{organization_id}/members` | List members only when the caller belongs to that organization. |
| GET | `/api/v1/user/researcher/projects` | List projects visible through project membership or declared public/community visibility. |
| POST | `/api/v1/user/researcher/projects` | Create a project as an approved researcher; organization projects require organization membership. |
| GET | `/api/v1/user/researcher/projects/{project_id}` | Read a project only when its visibility and tenant boundary permit. |
| GET | `/api/v1/user/researcher/projects/{project_id}/members` | List active project collaborators only to project members. |
| POST | `/api/v1/user/researcher/projects/{project_id}/members` | Add an approved researcher as a collaborator; organization projects require both users to belong to that organization. |
| GET | `/api/v1/user/researcher/projects/{project_id}/tasks` | List tasks only to active project members. |
| POST | `/api/v1/user/researcher/projects/{project_id}/tasks` | Create a task and optionally assign it to an active project member. |
| PATCH | `/api/v1/user/researcher/projects/{project_id}/tasks/{task_id}` | Update an authorized project's task status. |
| GET | `/api/v1/user/researcher/projects/{project_id}/documents` | List only project-shared documents and private documents owned by the caller or project owner. |
| POST | `/api/v1/user/researcher/projects/{project_id}/documents` | Attach a text document (up to 100 KB) with private or project-member access. |
| GET | `/api/v1/user/researcher/projects/{project_id}/activity` | Read the auditable project contribution history. |
| GET | `/api/v1/user/researcher/events` | Discover published research events visible to the caller. |
| POST | `/api/v1/user/researcher/events` | Publish a future research event as an approved researcher. |
| POST | `/api/v1/user/researcher/events/{event_id}/registration` | Register for an eligible event once. |
| GET | `/api/v1/admin/users` | List accounts and current verification, researcher-approval, and organization-creation-entitlement state. |
| PUT | `/api/v1/admin/users/{user_id}/verification` | Record or revoke an account's administrator-verified email state. |
| GET | `/api/v1/admin/researcher/applications` | List pending researcher applications. |
| POST | `/api/v1/admin/researcher/applications/{application_id}/decision` | Approve a verified account for researcher access or reject its application. |
| GET | `/api/v1/admin/organizations/requests` | List pending organization requests for identity and website review. |
| POST | `/api/v1/admin/organizations/requests/{request_id}/decision` | Reject or verify and provision an organization when the requester has an active entitlement. |
| GET | `/api/v1/admin/organizations` | List provisioned organizations and their verification records. |
| GET | `/api/v1/admin/users/{user_id}/entitlements` | List an account's entitlement history. |
| POST | `/api/v1/admin/users/{user_id}/entitlements` | Grant the development/pilot `organization_create` entitlement; no checkout or payment. |
| POST | `/api/v1/admin/entitlements/{entitlement_id}/revoke` | Revoke an active entitlement. |
| GET | `/api/v1/admin/events` | List research events and registration counts. |
| POST | `/api/v1/admin/events/{event_id}/decision` | Cancel a research event. |
| GET | `/api/v1/admin/audit/events` | List recent researcher/organization/entitlement/event administration actions. |

Cross-cutting behavior already in place:

- CORS allows only the origins in `API_CORS_ORIGINS`, with credentials (session cookies). The local default is ports 3000–3003 on `localhost`; no custom domain is needed.
- Every response carries `X-Request-ID` and baseline security headers.
- Browser write requests with an `Origin` header are checked against the trusted-origin list.
- Social feed content is public. Posting and reporting require an authenticated session and a trusted `Origin`; reports are queued for later moderation review.
- Community membership is scoped to each community. Open communities admit registered members directly; restricted communities require moderator approval. Restricted-community posts/comments/reactions are available only to active members.
- Community moderation is enforced by active owner/moderator membership. Actions are recorded; posting suspensions are time-limited, and appeals can overturn actions and restore hidden content or posting access.
- Platform routes require an authenticated session, a verified account, and a case-insensitive email match in `PLATFORM_ADMIN_EMAILS`; browser writes also require a trusted `Origin`. The allowlist is empty by default. Automated account verification is not implemented, so the first platform administrator account must be provisioned and verified through a trusted operational process before it can use these routes.
- Researcher routes require a verified account and explicit platform approval for profiles, projects, tasks, documents, and events. Public researcher discovery is opt-in. Organization requests are open to registered members, but organization provisioning additionally requires platform review and an active admin-granted `organization_create` entitlement. No payment path exists before M5.
- Organization invitations are case-insensitive email-bound, expire after 30 days, and grant membership only after the invitee accepts. Organization projects require organization membership and independent project membership for protected resources. Public/community project visibility does not grant access to task lists, member rosters, or project-shared documents. Private text documents are visible only to their uploader and the project owner; project-shared documents require active project membership.
- Project activities and M3 administrative decisions are recorded. The M3 audit endpoint covers only researcher access, account verification, organization provisioning, entitlement, and event decisions; it is not a complete audit/security event system.
- Community approval records the reviewer and timestamp and atomically creates the community plus an active owner membership for the requester. The platform moderation queue contains pending reports against global content and reports explicitly escalated by community moderators; ordinary pending community reports remain in their community queues. Global actions and their appeals are recorded and reviewable.
- Sessions use a random opaque token in an HttpOnly, SameSite=Lax cookie; only its SHA-256 digest is stored. The cookie has no Domain attribute, so `localhost` apps on ports 3000–3003 share it.
- The default development database is SQLite at `./healthspan.db`; configure `DATABASE_URL` for PostgreSQL.
- AI provider credentials remain server-side. The default provider is disabled and returns an explicit 503 until configured.

The routers `/api/v1/user/social`, `/api/v1/user/personal`, `/api/v1/user/researcher` and
`/api/v1/admin` are mounted. Admin endpoints cover community approval/provisioning, global and
escalated report review, researcher admission, organization verification/provisioning, development
entitlements, event oversight, and the M3 administrative audit subset. Broad account restrictions,
advanced organization administration, topics, comment reactions, and warnings/appeals notifications
are not implemented.

The owner retired the separate legacy MVP as a migration source. This route list describes the
current API contract; backward compatibility with the removed legacy implementation is not
provided.

## Deliberate limitations

- Account registration does not verify email; password recovery, MFA, refresh/rotation, rate limiting and a self-service administrative identity workflow are not implemented. Email verification in the M3 Admin is an operator-recorded state, not proof of an email challenge. A trusted operator must provision and verify platform admin accounts. Do not expose this development slice as a production identity service.
- Organization website/identity verification is an administrator attestation to the submitted details; there is no automated domain ownership check or external verification provider.
- Project attachments in this milestone are text records only. Binary upload, object storage, malware scanning, document versioning, and production document retention are not implemented.
- Research events support publication, discovery, registration, and admin cancellation only; event discussion, capacity, notifications, and attendance workflows are not implemented.
- The M3 audit trail is limited to the explicit admin workflows listed above and does not replace general audit-event search or a production security review.
- The Scientist prototype has no literature retrieval, project context, document access, citations or scientific tools. It explicitly tells the model not to claim these capabilities.
- AI sources are returned as an empty list. The prompt requests non-fabricated citations, but provider output is not independently verified.
- AI interaction metadata is recorded. Prompt/answer content is stored only after affirmative AI-learning consent; revocation clears previously retained content. No training or export job is implemented.
- Direct/group messaging stores text only; attachments, audio and video are not part of this MVP slice.
- Message WebSockets validate the request origin, session cookie and conversation membership. Delivery is in-process; run one API worker for local MVP real-time messaging. Persisted messages remain available through the REST history endpoint after a disconnect.
- Admin actions are authenticated and authorization-gated but do not yet have a general-purpose audit-event search or production security review. Do not treat these APIs as production moderation coverage.

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
