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
| `/` | `apps/researcher-web` | M3 Researcher Portal: applications, profiles, and research-community entry |
| `/ai` | `apps/researcher-web` | Restricted Private AI Scientist prototype; research workspace and retrieval are later work |
| Admin operations | `apps/admin` | Verified allowlisted platform admins can approve communities and review global/escalated reports and global-action appeals |

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
| `/api/v1/admin/*` | Router namespace only; no functional admin endpoints | M3 Admin API |

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

## M2 and M3 work not present in the current checkout

The Social community membership, comments/reactions, and community-scoped moderation APIs are
implemented in M2. Platform community approval/provisioning and global/escalated moderation are
implemented; the remaining Personal profile/personalization work is also M2.
Researcher/Admin and organization workflows remain M3.

Approved product decisions are recorded in [DECISIONS.md](./DECISIONS.md). Organization entitlement
timing remains open. See [API.md](./API.md) for the implemented endpoint contract and
[DEVELOPMENT_ROADMAP.md](./DEVELOPMENT_ROADMAP.md) for milestone scope and exit gates.
