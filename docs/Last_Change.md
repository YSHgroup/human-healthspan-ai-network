# Last Change

## Completed

- Recorded the owner-approved M1 audience, geographic-availability, and MVP-boundary decisions in
  `docs/DECISIONS.md`.
- Implemented local shared registration/session and Alembic persistence, direct/group text
  messaging with authenticated WebSocket delivery, General AI and a gated prompt-only Scientist
  prototype, and consent-aware AI interaction records.
- Added API and AI tests for identity/session behavior, participant authorization, messaging
  WebSocket access and delivery, consent revocation, provider configuration, and AI access gates.
- Added shared communication UI and connected Social, Personal, and Researcher pages. Separate
  commits were made for design tokens, shared UI, and each modified portal.
- Mapped the current frontend routes, API endpoints, and persisted models to target domains in
  `docs/MIGRATION_PLAN.md`.
- Recorded owner-approved M2 community access/moderation and contribution-badge principles, and
  M3 organization onboarding/creation-entitlement policy in `docs/DECISIONS.md`.
- Estimated and recorded the owner-approved M2/M3 backlog in `docs/DEVELOPMENT_ROADMAP.md`.
- Began M2 shared-identity hardening: state-changing browser-auth routes now reject missing or
  untrusted Origin headers; regression tests cover registration and consent mutation.
- Added M2 shared-session refresh with opaque-token rotation, a 14-day idle expiry and 60-day
  absolute lifetime cap; documented configuration and added refresh regression tests.
- Retired the separate legacy MVP as a source of truth at the owner's direction. Removed its ZIP
  and archive-only characterization test; no legacy parity is promised.
- Removed nested app npm lockfiles to enforce the root-only lockfile rule and added the root pnpm
  lockfile; local package ranges remain `"*"`.

## Remaining M1 and product gaps

- M1 remains in progress: the owner deferred CI establishment and the corresponding guideline
  update until after M4. The estimated M2/M3 backlog is now approved.
- Account verification/recovery, researcher application and approval workflows, admin
  authentication and operations, community workflows, source-backed AI, launch security/privacy
  review, production audit, and production hardening remain unimplemented.
- Payment/checkout remains deferred until M5; M3 entitlement checks use admin-granted development
  and pilot entitlements.
- The legacy source was retired by owner decision. Its routes, schema, behavior, and production data
  are out of scope; no compatibility or data-migration claim is made.

## Verification

- `npm test` and `pnpm test`: each passed with 5 frontend tests and 40 Python
  architecture/API/AI tests.
- All Social, Personal, and Researcher app TypeScript checks passed after the shared UI changes.
- WebSocket handshake was verified against Uvicorn in normal and reload modes after installing the
  `websockets` runtime dependency.
- Production deployment, live AI provider operation, and production security/privacy readiness are
  not certified.
- The focused identity API tests could not run in this environment: Python has no `pytest`, `pip`,
  or `venv` support, and installing system venv support was denied by environment permissions.
  Python syntax compilation and `git diff --check` passed.

## Next step

Wire refresh into the shared browser-auth lifecycle and implement cross-portal logout propagation
and redirect validation before building the Social and Personal feature workstreams.
