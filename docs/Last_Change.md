# Overall progress implemented

The member web app now uses the existing FastAPI identity service through same-origin Next.js routes. It supports account registration, email verification/resend, sign-in/out, password reset, authenticated password change, and member profile editing. Access and refresh tokens remain in HttpOnly, SameSite=Strict cookies scoped to `/api`; protected member writes are proxied server-side and derive ownership from the authenticated user.

The API profile supports biography, location, time zone, interests, topics, expertise, researcher identifier, organization affiliation, and public/private visibility. Role fields are rejected from member profile updates. A database migration adds the profile fields, and verification/reset emails include links based on `PUBLIC_APP_URL`.

The API continues to provide revocable JWT-backed sessions, one-time email/password recovery tokens, admin/moderation endpoints, audit events, project-scoped research, and an operator path for bootstrapping an administrator. A separate admin app remains in place. AI routes return `503` until an approved provider is configured.

The member feed and research project listing still use mock-backed data. OAuth/OIDC, enforced MFA, login and recovery rate limiting, session-management UI, account deletion, avatar/media upload, and production mail operations are not implemented and remain launch-readiness work.

The JavaScript apps use a root npm workspace and shared UI primitives in `packages/ui`. Docker builds use the repository root context.

----------
# Last Change

Completed the member identity flow end to end: cookie-backed web session proxy, registration/login/verification/recovery pages, password change, profile editing and schema migration, authenticated member write gating, refreshed API/email configuration, and identity documentation.

----------
# What is the next step?

Wire the mock-backed feed and research views to authenticated API data. Before public launch, add rate limiting and abuse monitoring, decide and implement MFA/OIDC requirements, and complete production email, session-management, account deletion, and avatar-storage operations.
