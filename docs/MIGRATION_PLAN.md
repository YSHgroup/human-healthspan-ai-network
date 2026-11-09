# Implementation Inventory and Target Map

The owner retired the supplied legacy MVP as a product and migration source on 2026-11-06.
Its archive and archive-only characterization test were removed. The project does not promise
legacy feature, API, database, or data parity. This document maps the current checkout to the
planned M2/M3 architecture; it does not ask the owner to assign individual routes or models.

## Current frontend routes

| Current route | Application | Target area |
|---|---|---|
| `/` | `apps/social-web` | M2 Social Portal: public discovery and community entry |
| `/feed` | `apps/social-web` | M2 Social Portal: public questions/discussions, authenticated posting and report submission |
| `/communities` | `apps/social-web` | M2 Social Portal: community requests, membership, discussions, comments, reactions, and moderator review |
| `/messages` | `apps/social-web` | Shared text-messaging UI in `packages/ui`; backed by the messaging domain |
| `/ai` | `apps/social-web` | General Platform AI; later M4/M5 scope deepens sources and production safeguards |
| `/` | `apps/personal-web` | M2 Personal Portal: member profile, preferences, and saved/personal activity |
| `/messages` | `apps/personal-web` | Shared text-messaging UI and messaging domain |
| `/` | `apps/researcher-web` | M3 researcher access/profile, organization, project, task, text-document, and event workflows |
| `/ai` | `apps/researcher-web` | Restricted Private AI Scientist prototype; research workspace and retrieval are later work |
| Admin operations | `apps/admin` | Verified allowlisted platform admins can review researcher applications and organizations, grant development entitlements, manage community moderation, oversee events, and inspect the M3 audit subset |

## Current API routes

| Route | Current purpose | Target domain / milestone |
|---|---|---|
| `GET /healthz`, `GET /readyz` | Liveness and database readiness | Platform operations |
| `POST /api/v1/user/auth/register` | Register a member and create a session | Shared identity |
| `POST /api/v1/user/auth/login` | Authenticate and create a session | Shared identity |
| `POST /api/v1/user/auth/logout` | Revoke the current session | Shared identity |
| `GET /api/v1/user/auth/me` | Read current member and consent state | Shared identity |
| `PUT /api/v1/user/auth/ai-learning-consent` | Record or revoke AI-learning content consent | AI governance |
| `GET /api/v1/user/social/feed` | List recent public questions and discussions | M2 Social Portal |
| `POST /api/v1/user/social/posts` | Publish an authenticated public question or discussion | M2 Social Portal |
| `/api/v1/user/social/communities*` | List communities, request creation, join/apply, and review restricted membership | M2 Social Portal |
| `/api/v1/user/social/communities/{community_id}/posts` | List/publish community posts with membership checks | M2 Social Portal |
| `/api/v1/user/social/posts/{post_id}/comments` | List/publish comments on accessible posts | M2 Social Portal |
| `/api/v1/user/social/posts/{post_id}/reactions` | Read, set, or remove a member's reaction | M2 Social Portal |
| `/api/v1/user/social/posts/{post_id}/reports`, `/api/v1/user/social/comments/{comment_id}/reports` | Submit moderation reports | M2 safety |
| `/api/v1/user/social/communities/{community_id}/moderation/*` | Moderator report review, actions, and appeals | M2 safety |
| `/api/v1/user/social/me/moderation/*` | List a member's actions and submit appeals | M2 safety |
| `/api/v1/admin/communities/requests*` | Approve/provision or reject community requests | M3 platform operations |
| `/api/v1/admin/moderation/*` | Review global/escalated reports and global-action appeals | M3 platform moderation |
| `GET /api/v1/user/social/messages/conversations` | List a member's conversations | Messaging; shared by Social and Personal |
| `POST /api/v1/user/social/messages/conversations` | Create direct/group text conversation | Messaging; shared by Social and Personal |
| `GET /api/v1/user/social/messages/conversations/{conversation_id}/messages` | Read authorized text history | Messaging |
| `POST /api/v1/user/social/messages/conversations/{conversation_id}/messages` | Persist and deliver a text message | Messaging |
| `WebSocket /api/v1/user/social/messages/conversations/{conversation_id}/ws` | Deliver new messages to connected participants | Messaging real-time delivery |
| `POST /api/v1/user/social/ai/chat` | General AI chat through the provider gateway | General Platform AI |
| `POST /api/v1/user/researcher/ai/chat` | Access-gated Scientist prompt prototype | Researcher AI; retrieval/workspaces remain M3/M6 work |
| `/api/v1/user/researcher/applications*`, `/profile*`, `/profiles` | Researcher application, private profile editing, and opt-in public discovery | M3 researcher |
| `/api/v1/user/researcher/organizations*` | Free organization requests, memberships, email-bound invitations, and membership review | M3 organizations |
| `/api/v1/user/researcher/projects*` | Tenant/project-scoped projects, collaborators, tasks, text documents, and activity | M3 research workspace |
| `/api/v1/user/researcher/events*` | Create, discover, and register for research events | M3 events |
| `/api/v1/admin/*` | Community/moderation, researcher, organization, entitlement, event, and limited audit workflows | M3 Admin API |

## Current persisted models

| Model / table | Target domain | Current boundary |
|---|---|---|
| `User` / `users` | Shared identity | Account and approval-state fields; platform admins use a verified-email allowlist rather than a user role column |
| `UserSession` / `user_sessions` | Shared identity | Opaque hashed session token, expiry, revocation |
| `Conversation` / `conversations` | Messaging | Conversation ownership and persisted text-message thread |
| `ConversationParticipant` / `conversation_participants` | Messaging | Membership is required for history and WebSocket access |
| `Message` / `messages` | Messaging | Text only; no attachment/audio/video support |
| `Community` / `communities` | Social | Open/restricted access, rules, and creator |
| `CommunityMembership` / `community_memberships` | Social | Per-community role and pending/active/rejected membership |
| `CommunityCreationRequest` / `community_creation_requests` | Social/admin | Free request; platform decision records reviewer/time and approval provisions its owner community |
| `SocialPost` / `social_posts` | Social | Public or community-scoped questions/discussions with moderation state |
| `SocialPostComment` / `social_post_comments` | Social | Text comments with moderation state |
| `SocialPostReaction` / `social_post_reactions` | Social | One reaction per member per post |
| `SocialPostReport` / `social_post_reports` | Social/moderation | One report per member and post/comment; community-local queue plus global/escalated platform queue |
| `ModerationAction` / `moderation_actions` | Social/moderation | Recorded hide/remove/warn/suspend/escalate/dismiss action; community scope is nullable for global actions |
| `CommunityPostingSuspension` / `community_posting_suspensions` | Social/moderation | Time-bounded community posting restriction |
| `ModerationAppeal` / `moderation_appeals` | Social/moderation | One appeal per action, with moderator decision |
| `AIConsent` / `ai_learning_consents` | AI governance | Versioned and revocable opt-in |
| `AIInteraction` / `ai_interactions` | AI governance/operations | Usage metadata; content retention is consent-gated |
| `ResearcherApplication` / `researcher_applications` | Researcher | One application per account; public profile discovery is opt-in |
| `Organization*` / `organizations`, `organization_creation_requests`, `organization_memberships`, `organization_invitations` | Organization | Admin-verified tenant; invitations bind to and require acceptance by the target email |
| `Entitlement` / `entitlements` | Subscriptions | Admin-granted `organization_create` development entitlement; no payment workflow |
| `ResearchProject*`, `ResearchTask`, `ResearchDocument`, `ResearchActivity` | Research | Project and tenant membership checks; text documents only; project activities are append-only |
| `ResearchEvent*` / `research_events`, `research_event_registrations` | Events | Published events, organization-scoped visibility, one registration per user |
| `AdminAuditEvent` / `admin_audit_events` | Admin/audit | Limited audit trail for M3 administrative decisions |

## M2 and M3 implementation status

The Social community membership, comments/reactions, and community-scoped moderation APIs are
implemented in M2. Platform community approval/provisioning and global/escalated moderation are
implemented. M3 now includes a gated researcher application/profile path, organization requests
and invite-based membership, tenant-scoped project/task/text-document APIs, research events, a
pre-M5 entitlement foundation, and matching Admin workflows. Binary document storage, automated
email verification, full audit/security search, advanced organization administration, and AI
retrieval remain later or out-of-scope work. The separate retired legacy admin implementation is
not a parity source.

Approved product decisions are recorded in [DECISIONS.md](./DECISIONS.md), including the
organization entitlement timing. See [API.md](./API.md) for the implemented endpoint contract and
[DEVELOPMENT_ROADMAP.md](./DEVELOPMENT_ROADMAP.md) for milestone scope and exit gates.
