# Implementation Inventory and Target Map

The owner retired the supplied legacy MVP as a product and migration source on 2026-11-06.
Its archive and archive-only characterization test were removed. The project does not promise
legacy feature, API, database, or data parity. This document maps the current checkout to the
planned M2/M3 architecture; it does not ask the owner to assign individual routes or models.

## Current frontend routes

| Current route | Application | Target area |
|---|---|---|
| `/` | `apps/social-web` | M2 Social Portal: public discovery and community entry |
| `/messages` | `apps/social-web` | Shared text-messaging UI in `packages/ui`; backed by the messaging domain |
| `/ai` | `apps/social-web` | General Platform AI; later M4/M5 scope deepens sources and production safeguards |
| `/` | `apps/personal-web` | M2 Personal Portal: member profile, preferences, and saved/personal activity |
| `/messages` | `apps/personal-web` | Shared text-messaging UI and messaging domain |
| `/` | `apps/researcher-web` | M3 Researcher Portal: applications, profiles, and research-community entry |
| `/ai` | `apps/researcher-web` | Restricted Private AI Scientist prototype; research workspace and retrieval are later work |
| Admin foundation | `apps/admin` | M3 Admin Application; authentication, authorization, workflows, and backend endpoints remain unimplemented |

## Current API routes

| Route | Current purpose | Target domain / milestone |
|---|---|---|
| `GET /healthz`, `GET /readyz` | Liveness and database readiness | Platform operations |
| `POST /api/v1/user/auth/register` | Register a member and create a session | Shared identity |
| `POST /api/v1/user/auth/login` | Authenticate and create a session | Shared identity |
| `POST /api/v1/user/auth/logout` | Revoke the current session | Shared identity |
| `GET /api/v1/user/auth/me` | Read current member and consent state | Shared identity |
| `PUT /api/v1/user/auth/ai-learning-consent` | Record or revoke AI-learning content consent | AI governance |
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
| `User` / `users` | Shared identity | Account and approval-state fields; no admin role model |
| `UserSession` / `user_sessions` | Shared identity | Opaque hashed session token, expiry, revocation |
| `Conversation` / `conversations` | Messaging | Conversation ownership and persisted text-message thread |
| `ConversationParticipant` / `conversation_participants` | Messaging | Membership is required for history and WebSocket access |
| `Message` / `messages` | Messaging | Text only; no attachment/audio/video support |
| `AIConsent` / `ai_learning_consents` | AI governance | Versioned and revocable opt-in |
| `AIInteraction` / `ai_interactions` | AI governance/operations | Usage metadata; content retention is consent-gated |

## M2 and M3 work not present in the current checkout

The roadmap assigns Social/Personal community and profile workflows to M2, and Researcher/Admin,
organizations, membership, moderation, entitlements, and audit workflows to M3. Implementation
must add route-to-domain and model-to-domain entries here as those features are approved and built.

Approved product decisions are recorded in [DECISIONS.md](./DECISIONS.md). Organization entitlement
timing remains open. See [API.md](./API.md) for the implemented endpoint contract and
[DEVELOPMENT_ROADMAP.md](./DEVELOPMENT_ROADMAP.md) for milestone scope and exit gates.
