# Last Change

## Completed

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

## Remaining M1 and product gaps

- M1 remains in progress: the owner deferred CI establishment and the corresponding guideline
  update until after M4. The estimated M2/M3 backlog is now approved.
- Account verification/recovery, researcher application and approval workflows, self-service
  platform-admin identity provisioning, general audit-event search, source-backed AI, launch
  security/privacy review, production audit, and production hardening remain unimplemented.
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

## Next step

Continue the M4 backlog. CI establishment and the corresponding guideline update remain deferred
until after M4 per the owner's direction.
