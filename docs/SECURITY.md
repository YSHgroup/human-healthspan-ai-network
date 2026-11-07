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
- Session refresh rotates the opaque token, enforces a 14-day idle timeout and 60-day absolute lifetime by default, and invalidates the previous token.
- Sensitive conversation and message routes check authenticated conversation membership on every read/write; non-members receive not-found responses.
- Researcher AI requires explicit verified-email and researcher-approval records; neither is granted by public registration.
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
