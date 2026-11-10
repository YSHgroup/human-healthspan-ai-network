# Security

**Status: development foundations.** Shared identity/session, API-origin checks and messaging
authorization are implemented for local development. The requirements below remain necessary
before public production launch.

## In place

- Backend CORS restricted to trusted application origins (`API_CORS_ORIGINS`).
- `X-Request-ID` and baseline security headers on API responses.
- Security headers on the three Next.js portals; private portals and Admin are not indexable.
- API client sends credentials for cookie sessions; tests forbid browser-stored tokens.
- Registration hashes passwords with scrypt; session cookies are HttpOnly, SameSite=Lax, host-only, and Secure in production; only a session-token digest is stored.
- Platform administration requires an authenticated, email-verified account in the explicit `PLATFORM_ADMIN_EMAILS` allowlist; state-changing admin requests also enforce trusted origins.
- Sensitive conversation and message routes check authenticated conversation membership on every read/write; non-members receive not-found responses.
- Researcher AI requires explicit verified-email and researcher-approval records; neither is granted by public registration.
- Researcher applications are reviewed by platform admins; researcher profile discovery is opt-in. Project and organization access is checked on the API. Organization membership does not grant project membership, and public project visibility does not grant access to tasks, membership rosters, or project-shared documents.
- Organization invitations are accepted only by the invited case-insensitive email address. Organization provisioning requires an admin-reviewed request and an active admin-granted pre-M5 entitlement.
- Text and uploaded-file documents default to private access; shared documents require project membership. Uploads are limited to PDF, CSV, and UTF-8 text up to 10 MiB, use generated storage keys in a private local volume outside static assets, and download as attachments through an API authorization check. Project activities and M3 admin access, organization, entitlement, event, and platform moderation decisions are recorded in a limited audit trail.
- Architecture tests enforce: no direct database access from frontends, no cross-application imports.
- `.env.example` holds placeholders only; secrets never enter the repository.

## Required before the MVP launch (M4)

- Email verification, password recovery, MFA support, rate limiting and operational abuse controls.
- RBAC and ABAC with least privilege at organization, project, resource and administrative level.
- Shared identity across portals: token lifecycle and refresh, logout propagation,
  CSRF protection, cookie security, redirect validation. No long-lived tokens in browser storage.
- Authorization on every API, object, file, dataset, AI retrieval and administrative action.
- Audit logs for sensitive access, sharing, exports, AI retrieval, model actions and admin changes.
- Rate limiting, secure file ingestion with malware scanning, backup and restore, monitoring.
- Encryption in transit and at rest; managed secrets and keys.

## Security tests (grow with each milestone)

Cross-user access, cross-organization access, unauthorized health-data access, share-link scope
and expiry, AI retrieval isolation, administrative authorization, entitlement enforcement.
Add tests before removing any existing functionality.

The M3 tests cover researcher approval, organization invite matching and entitlement gating,
organization/project isolation, private document visibility, file upload/download permissions,
and event/admin workflows. Email verification in Admin is an operator-recorded development state,
not an email challenge. Malware scanning, production object storage and encryption/key management,
comprehensive audit/security search, and production security review remain incomplete.
