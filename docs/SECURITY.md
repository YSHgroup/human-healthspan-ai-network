# Security Foundation

## Implemented in the MVP backend

- Argon2id password hashing and password-length validation.
- Signed, short-lived JWT access tokens backed by revocable database sessions.
- Single-use, expiring email-verification and password-reset tokens stored as hashes.
- Production guards against the development JWT and database password defaults.
- Server-enforced role checks and project owner/team/public authorization.
- Permission-scoped research retrieval before searching private literature/evidence.
- Least-privilege separation for administrator, moderator, scientific reviewer, and read-only auditor APIs.
- Reasoned, audited moderation and privileged account changes; last-admin/self-lockout safeguards.
- Soft deletion for user posts/comments and restricted public profile fields.
- HTTP(S)-only source URL validation for evidence/literature metadata.

## Required before public launch

- Rate limiting and abuse controls, including login, recovery, registration, and AI routes.
- MFA enforcement for privileged accounts and a complete admin sign-in/access policy.
- OIDC/OAuth integration if required; federation is not implemented.
- Production SMTP configuration, delivery monitoring, and recovery operations.
- Secure file uploads, malware scanning, document ingestion isolation, and retention/deletion workflows.
- Approved AI provider, retrieval/citation evaluation, prompt-injection testing, and AI incident monitoring.
- PostgreSQL backup/restore drills, production observability, secret-manager integration, and dependency/container scanning.
- Threat modeling, SAST/DAST, incident response, and security review.

Health and genomic data require explicit consent and stricter access policies. The current backend is not a clinical system and does not implement a genomic-data platform.
