# Last Change

## Completed

- Started the M4 MVP launch work by tightening the AI gateway routing and OpenAI-compatible provider handling: provider and environment names are normalized before routing, required provider values are stripped and validated, and the request path remains server-only with a redacted authorization header.
- Added an Ubuntu Docker Compose development stack for all four portals, the Python 3.14 API,
  PostgreSQL and Redis. Updated the setup guide and pinned the Node.js engine to major version 24.
- Recorded the owner-approved M1 audience, geographic-availability, and MVP-boundary decisions in
  `docs/DECISIONS.md`.
- Implemented local shared registration/session and Alembic persistence, direct/group text
  messaging with authenticated WebSocket delivery, General AI and a gated prompt-only Scientist
  prototype, and consent-aware AI interaction records.
- Added API and AI tests for identity/session behavior, participant authorization, messaging
  WebSocket access and delivery, consent revocation, provider configuration, and AI access gates.
- Added shared communication UI and connected Social, Personal, and Researcher pages. Separate
  commits were made for design tokens, shared UI, and each modified portal.
- Completed the M2 Personal Portal foundation with editable profile fields, saved-knowledge
  previews, consent toggles, and session-local privacy review controls consistent with the
  private-by-default M2 requirements in `docs/DEVELOPMENT_ROADMAP.md`.
- Mapped the current frontend routes, API endpoints, and persisted models to target domains in
  `docs/MIGRATION_PLAN.md`.
- Recorded owner-approved M2 community access/moderation and contribution-badge principles, and
  M3 organization onboarding/creation-entitlement policy in `docs/DECISIONS.md`.
- Estimated and recorded the owner-approved M2/M3 backlog in `docs/DEVELOPMENT_ROADMAP.md`.
- Began M2 shared-identity hardening: state-changing browser-auth routes now reject missing or
  untrusted Origin headers; regression tests cover registration and consent mutation.
- Started M2 Social Portal core with a public question/discussion feed, authenticated posting, and
  one-pending-report-per-member reporting; added database migration and API authorization tests.
- Connected the feed API to the Social Portal at `/feed`, added homepage/navigation links, and
  exposed the public feed page in the sitemap so the slice can be tested from the browser.
- Added README steps to test feed publishing and reporting with separate browser profiles.
- Implemented M2 community membership, restricted-community applications, community posts,
  comments, reactions, content reports, moderator actions, time-bounded posting suspensions, and
  appeals, with API tests and a reversible migration.
- Connected those workflows to the Social Portal at `/communities`, including community requests,
  membership review, discussions, reports, moderation queues, and appeal flows. Linked the page
  from the landing page and Social Portal navigation.
- Added pending-appeal review to the moderator API/UI, and aligned the model and migration indexes
  so Alembic metadata checks pass.
- Implemented platform-admin community approval/provisioning and a global moderation queue for
  global or escalated reports, including report actions and appeals. Access requires an existing
  verified session account explicitly listed in `PLATFORM_ADMIN_EMAILS`.
- Updated the API inventory, setup instructions, and testing limitations.
- Fixed the local Compose database mismatch that caused `/feed` and community creation requests to
  fail: the persisted PostgreSQL database was still at `0002_social_feed` while the code expected
  `0003_social_communities`. Applied the additive migration without dropping existing data.
- Retired the separate legacy MVP as a source of truth at the owner's direction. Removed its ZIP
  and archive-only characterization test; no legacy parity is promised.
- Removed nested app npm lockfiles to enforce the root-only lockfile rule and added the root pnpm
  lockfile; local package ranges remain `"*"`.
- Implemented the M3 Researcher Portal and backend foundation: verified researcher applications
  and opt-in profiles, verified organization requests, email-bound invitations and roles,
  admin-granted pre-M5 organization entitlements, tenant-scoped projects, collaborators, tasks,
  private/project-shared text documents, research events, and contribution activity.
- Expanded the Admin application/API with account verification records, researcher admission,
  organization verification/provisioning, entitlement grants/revocation, event oversight, and a
  limited audit trail. Added migration `0005_researcher_organizations` and tests for approval,
  tenant boundaries, private document access, invitations, entitlements, events, and admin audit.
- Connected the Researcher Portal UI to the new workflows and documented the implemented routes,
  data boundaries, and deliberate limitations.
- Added private local-volume uploads for PDF, CSV, and UTF-8 text files (10 MiB maximum), bounded
  request bodies, opaque storage keys, digests, authorized attachment downloads, and
  project/document access regression tests. Production object storage, malware scanning, and
  encryption/key management remain outstanding.
- Expanded the Admin UI to inspect entitlement histories and revoke entitlements. Added audit
  records for community decisions, platform moderation actions, and appeal decisions, with tests.
  Added Admin aggregate AI usage and latency monitoring without prompt/answer exposure.
- Added Admin sign-in and sign-out using the shared HttpOnly session endpoints. The UI now checks
  the current session, clearly denies signed-in accounts without platform-admin access, and probes
  Admin authorization before loading operational queues.
- Continued M4 governance hardening: centralized environment permission checks now enforce the
  Scientist feature flag, verified-email state and researcher approval before gateway dispatch.
  AI responses label all provider-supplied source details and notices as unverified.
- Implemented optional, auditable AI cost estimates from provider-reported token counts and
  exact-model USD rates supplied with a pricing-source label. Stored rate snapshots and estimates,
  exposed priced/unpriced usage to Admin, and added focused permission, privacy, pricing and API
  tests. These estimates are not provider invoices.

## Remaining M1 and product gaps

- M1 remains in progress: the owner deferred CI establishment and the corresponding guideline
  update until after M4. The estimated M2/M3 backlog is now approved.
- Automated account verification/recovery, self-service platform-admin identity provisioning,
  general audit-event search, source-backed AI, launch security/privacy review, production audit,
  and production hardening remain unimplemented.
- Automated email verification remains unimplemented; Admin verification is an operator-recorded
  development status.
- M4 remains incomplete: rate limiting/MFA/recovery, malware scanning and production file storage,
  encryption/key management, tested production backup/restore, monitoring/alerting, incident
  runbooks, legal/privacy review, and a production security assessment are not established.
- AI retrieval and verified citations are not connected. Cost estimates remain unavailable when
  token usage, exact-model rates, or the operator-supplied pricing source are missing.
- Production deployment, launch-measure baselines, and operational dashboards beyond current Admin
  AI usage monitoring are not certified.
- Payment/checkout remains deferred until M5; M3 entitlement checks use admin-granted development
  and pilot entitlements.
- The legacy source was retired by owner decision. Its routes, schema, behavior, and production data
  are out of scope; no compatibility or data-migration claim is made.

## Verification

- `git diff --check` passed. Docker Compose could not be run in this environment because the
  Docker daemon is inaccessible.
- `npm test` and `pnpm test`: each passed with 5 frontend tests and 40 Python
  architecture/API/AI tests.
- All Social, Personal, and Researcher app TypeScript checks passed after the shared UI changes.
- WebSocket handshake was verified against Uvicorn in normal and reload modes after installing the
  `websockets` runtime dependency.
- Production deployment, live AI provider operation, and production security/privacy readiness are
  not certified.
- The README's `python -m pip install -e "api[dev]" -e ai` setup succeeded in the configured
  Python 3.14 environment. The architecture, API, and AI suites passed (52 tests). A fresh SQLite
  database upgraded to head, passed `alembic check`, downgraded to `0002_social_feed`, and upgraded
  again. The Compose PostgreSQL database was confirmed at `0003_social_communities`; the live feed
  returned 200 with `Access-Control-Allow-Origin`, community creation returned the expected
  authenticated 401 with CORS headers, and CORS preflight succeeded. Changed Python files passed
  `compileall`, and the frontend editor diagnostics reported no problems in the new page and
  component. Frontend typecheck, lint, build, and browser validation could not be run because
  Node.js/npm are unavailable; Docker CLI access is restricted in this environment.
- After platform approval and moderation work, all 56 Python tests passed. A fresh SQLite database
  upgraded to `0004_platform_community_moderation`, downgraded to `0003_social_communities`, and
  upgraded again; Alembic reported no metadata drift. Admin TypeScript checking and a production
  Vite bundle passed using direct runners. The standard workspace install/build scripts still
  encounter permission errors on pre-existing root-owned `node_modules` and brand-asset paths;
  those paths were not modified.
- M3 validation passed: all 55 API and architecture tests, researcher and Admin TypeScript checks,
  and production builds for the Researcher Portal and Admin. A fresh SQLite database upgraded
  through `0005_researcher_organizations`, passed `alembic check`, downgraded to `0004`, and
  upgraded again. Prettier passed for all three changed frontend source files, and `git diff
  --check` passed. The broad Researcher workspace lint script also scanned generated `.next`
  artifacts and failed on their formatting; focused checks of the changed files passed.
- Follow-up M3 changes: Admin and researcher/API contract tests, including private upload/download,
  request-size limits, entitlement revocation, audit coverage, and aggregate AI usage passed;
  architecture checks passed. Both frontend typechecks and production builds passed, and migration
  `0006_research_document_files` upgraded/downgraded cleanly with no metadata drift. Focused
  Prettier and whitespace checks passed. The complete API and architecture suites passed (57 tests).
- Admin acceptance: the UI maps every current Admin operation in the documented M3 scope. The
  isolated-database browser smoke verified allowlisted sign-in, dashboard access, non-admin denial,
  and server-side sign-out revocation. Admin production build and the API/architecture suite passed
  (57 tests); focused Prettier and `git diff --check` passed.
- M3 exit-gate review: researcher admission, collaboration, document access and cross-organization
  denial pass their API tests. Documented Admin authentication and operational workflows pass
  acceptance; the retired legacy implementation is not a parity baseline. AI usage and latency are
  shown. By owner decision D8, AI provider cost reporting is deferred to M4. Production file
  scanning/storage and general security-event search are subsequent hardening per owner direction.
  All M3 exit-gate criteria pass; M3 is marked complete.
- M4 incremental validation: all 73 architecture, API, AI, and migration tests passed. A fresh
  SQLite database upgraded through `0007_ai_usage_costs`, passed `alembic check`, downgraded to
  `0006_research_document_files`, and upgraded again with no metadata drift. Admin TypeScript
  checking, focused Prettier, the production Vite bundle, and `git diff --check` passed. The Python
  tests report one existing Starlette/httpx deprecation warning.

## Next step

Continue the M4 launch-readiness work without marking the milestone complete until the roadmap
exit gate is met. Resolve production identity and abuse controls, complete security/privacy and
legal assessments, test production backup/restore and operations, and connect only approved,
permission-aware source retrieval before treating AI outputs as source-backed. CI establishment
and its guideline update remain deferred until after M4 per the owner's direction.
