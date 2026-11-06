# Migration Plan

The existing MVP remains the source of working functionality until each replacement is
implemented, tested and verified. The v0.4 source archive is
[`references/human-healthspan-ai-network-mvp-v0.4.zip`](../references/human-healthspan-ai-network-mvp-v0.4.zip).
The inventory below describes that archived source, the current checkout, and the known gaps
between them. It does not claim production-database or deployment parity.

## M1 legacy inventory — v0.4 archive

### Baseline and verification

- Archive SHA-256: `8539aab1f73a87754ac7bbef584df6e032c9866640b11fb7a5bce38cc72c66c7`.
- The archive contains three separate Next.js member portals (`apps/social-web`,
  `apps/personal-web`, `apps/researcher-web`), a legacy `apps/web`, an Admin app, a FastAPI API,
  SQLAlchemy models, Alembic migrations, and two API behavior-test modules.
- The archived tests were run from a validated, temporary extraction using the test database
  setup in the archive. Result: **37 passed**. No production database, credentials, or user data
  were used. The archive handover's “Nothing was executed” note describes its original handover,
  not this later test run.
- The archive has **49 SQLAlchemy tables** and **six chained Alembic revisions**. The production
  database contents and its exact applied revision are not in the ZIP and remain unverified.

### Portals and API behavior

| Legacy area | Observed in v0.4 | Current checkout / migration note |
|---|---|---|
| Social Portal | `apps/social-web`: landing, registration/login/verification/reset, home, discover, communities and member pages; posts/feed, comments, reactions, follows and bookmarks are backed by API routes. | Current Social has a landing page, text-message and General AI pages. Legacy community/feed/profile behavior is not migrated. |
| Personal Portal | `apps/personal-web`: home/profile, identity forms, activity, shared auth and backend proxy. | Current Personal has foundation and shared messaging pages; profiles, activity, health records and sharing are not migrated. |
| Researcher Portal | `apps/researcher-web`: home, research projects, science search, registration/login/verification/reset and backend proxy. | Current Researcher has foundation and a Scientist prototype; research workspaces/search and researcher application/review workflow are not migrated. |
| Legacy web app | `apps/web` is also retained in the archive, with home, feed, discover, communities, profile, research, science and AI pages. | Its behavior is not represented by the current public landing page alone; keep the archive as a source until parity is explicitly verified. |
| Admin | Archived `apps/admin` provides login/session/backend proxy and an operations page. Backend Admin routes cover organizations, event moderation, plans, subscriptions, payments, entitlements, badges, professional verification, researcher approvals, AI monitoring, configuration and audit. | Current Admin is a React/Vite foundation; no corresponding admin workflows are implemented. |
| Identity and profiles | `/api/v1/auth/*` includes register, login, email verification/resend, password reset/confirm, authenticated password change, refresh, logout and current-user profile operations. Short-lived access and rotating refresh tokens are used; email must be verified before login. Profile privacy and field/role validation are covered by tests. | Current API uses opaque cookie sessions, has no email verification, password recovery, token refresh or profile workflow. Existing API compatibility is not established. |
| Social/community | `/api/v1/feed`, posts, comments, reactions, bookmarks, follows, communities/join, public profiles, search, reports and moderation. Author identity comes from the authenticated user; privacy-safe feed summaries, soft deletion, idempotent community joins and audited moderation are tested. | These v0.4 routes and data models are not implemented in the current API. |
| Research/science | Research projects and membership, questions, hypotheses, literature, evidence, project-scoped permissions and science search. Tests cover private/team/public access and reviewer permissions. | Current API has no project/question/literature/evidence persistence or legacy route adapters. |
| Messaging | A shared messaging domain is mounted under Social and Personal. It supports direct conversations, participant-authorized reads, unread/read state, notifications, sender-owned deletion, and message `kind`/`media_url` references. | Current API supports direct/group text only. The owner-approved M1 boundary excludes audio, video and attachments; that narrowing is intentional, but other legacy messaging semantics still need parity decisions/tests. |
| Personal health | Health records, scoped/time-limited sharing and consent records exist in the archived schema/API; tests check private-by-default access, sharing, expiry and audit. AI retrievers are explicitly tested not to read health records. | Current API does not expose health-record operations. Do not copy health records into AI or test fixtures. |
| Organizations/events/entitlements | Organization membership/invitations, project links, research tasks, append-only work history, professional records, events/registration/invitations, notifications, plans, purchases and entitlements. Tests exercise organization isolation and entitlement gates. | Current API does not implement these workflows. |
| AI | Separate General, approved-researcher Scientist and organization-scoped AI routers; extractive and Anthropic provider adapters; shared orchestration, public/project/organization retrieval, sources/evidence labels/uncertainty, feedback and AI-run monitoring. Tests cover source-backed General answers, Scientist permissions, paid/org isolation and health-data exclusion. | Current implementation has a configurable OpenAI-compatible gateway and prompt-only General/Scientist endpoints. Retrieval, citations/source validation, org AI, feedback and persisted AI conversations are absent. |

The v0.4 API entry point mounts versioned routes under `/api/v1`, including portal aliases under
`/user/social`, `/user/personal`, `/user/researcher`, `/user/ai/general`, plus `/admin`. The legacy
API also has route families at `/auth`, `/feed`, `/posts`, `/communities`, `/research`,
`/moderation`, and `/ai`. The current route inventory is documented separately in [API.md](./API.md);
the two route sets are **not interchangeable**.

### Persistence, migrations and infrastructure

Legacy SQLAlchemy models define these 49 tables:

- Identity/social/research: `users`, `profiles`, `auth_sessions`, `auth_tokens`, `communities`,
  `community_members`, `follows`, `research_projects`, `research_members`, `posts`, `comments`,
  `reactions`, `bookmarks`, `research_questions`, `hypotheses`, `literature`, `evidence`,
  `reports`, `audit_events`.
- Platform domains: `organizations`, `organization_members`, `organization_invitations`,
  `project_organizations`, `research_memberships`, `research_tasks`, `work_history_entries`,
  `professional_records`, `badges`, `user_badges`, `health_records`, `health_shares`,
  `consent_records`, `conversations`, `conversation_participants`, `messages`, `events`,
  `event_registrations`, `event_invitations`, `notifications`, `subscription_plans`,
  `subscriptions`, `purchases`, `entitlements`, `ai_conversations`, `ai_messages`, `ai_runs`,
  `ai_feedback`, `org_ai_instances`, `org_knowledge_documents`.

The archived migration history is linear:

| Revision | File | Parent | Scope |
|---|---|---|---|
| `17101feebea7` | `17101feebea7_phase_1_initial_schema.py` | — | Initial schema |
| `bf0deb599c56` | `bf0deb599c56_add_email_verification_tokens.py` | `17101feebea7` | Email action tokens |
| `521e5042e44d` | `521e5042e44d_add_mvp_social_interactions.py` | `bf0deb599c56` | MVP social interactions |
| `cf5b66bc658f` | `cf5b66bc658f_add_research_hypotheses.py` | `521e5042e44d` | Research hypotheses |
| `9ac2a7348f16` | `9ac2a7348f16_extend_member_profiles.py` | `cf5b66bc658f` | Member-profile fields |
| `a1c3f0b7d2e4` | `a1c3f0b7d2e4_platform_domains.py` | `9ac2a7348f16` | Additive platform-domain tables |

The archive configures PostgreSQL as the system of record, Redis for cache/queue foundations, and
Docker-based local services. Search in the archived tests/docs uses PostgreSQL text matching;
Redis and OpenSearch are not wired into that behavior. The current checkout's
`api/alembic/versions/0001_identity_messaging_ai_learning.py` is an unrelated fresh-schema
revision (`0001_core`), not a continuation or data migration from the six v0.4 revisions. **Do not
run the current migration chain against an existing v0.4 database or claim preservation/parity.**
Before a cutover, inspect the real database's Alembic revision, preserve the legacy history, and
design and rehearse an explicit schema/data migration.

### Archived characterization suite

The archive includes `tests/test_api_contract.py` (22 tests) and `tests/test_platform_contract.py`
(15 tests). They characterize authentication/profile, social interactions, community membership,
project permissions, moderation/audit, messaging privacy/notifications, health-record sharing,
AI source and data boundaries, researcher approvals, organization isolation and entitlements.
The new `tests/migration/test_legacy_mvp_characterization.py` freezes the archived routes, schema,
migration chain and key behavior-test inventory without importing legacy code or creating users.
The archived behavior tests were independently executed as described above.

## Mapping and compatibility status

| Legacy source | Current target | Status / next migration action |
|---|---|---|
| `apps/social-web` and legacy `apps/web` | `apps/social-web` | Surface inventory complete; feed/community/member parity is missing. Migrate incrementally with route and behavior tests. |
| `apps/personal-web` | `apps/personal-web` | Shared messaging page exists; profile, activity, health/sharing and consent parity is missing. |
| `apps/researcher-web` | `apps/researcher-web` | Scientist prototype exists; membership/review and project/research parity is missing. |
| Archived `apps/admin` | `apps/admin` | Current framework/surface differs; preserve backend Admin behaviors while implementing and testing parity. |
| `apps/api/app/api`, `domains`, `models` | `api/app/api`, `domains`, `models` | Current modular-monolith directories exist, but most v0.4 endpoints/domains/models are not ported. No compatibility claim. |
| v0.4 Alembic chain and PostgreSQL data | `api/alembic/` | Not migrated. Preserve the six archived revisions and establish a verified continuation/data migration before connecting the new API to legacy data. |
| v0.4 AI providers/retrievers/orchestrator | `ai/healthspan_ai/` | Only gateway/prompt-only slices exist; retrieval, separate source permissions, feedback, run monitoring and organization AI require migration. |
| Archived 37-test suite | `tests/migration` plus current API/AI tests | Legacy tests run from the reference archive; new archive-contract tests prevent losing its route/schema/migration inventory. Expand current executable tests as each feature is ported. |

## M1 inventory checklist

- [x] Inventory archived frontend routes and portal/API boundaries.
- [x] Inventory v0.4 identity, social, research, messaging, health, organization, event, admin and AI behavior.
- [x] Inventory all 49 ORM tables and the six-revision Alembic lineage.
- [x] Add archive-based characterization tests for representative routes, schema, migration chain and existing behavior tests.
- [x] Run the archived behavior suite: 37 passed.
- [x] Inventory current checkout and document differences from the v0.4 baseline.
- [ ] Inspect the actual deployed/production database revision and data, then rehearse a migration. The archive contains migration source, not a database dump.

M1 source inventory is complete for the supplied v0.4 archive. Production database state,
compatibility, and migration execution remain separate verification gates; no users or records
were fabricated.
