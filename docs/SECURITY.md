# Security Foundation

- OIDC/OAuth2-ready identity boundary
- MFA-ready authentication
- RBAC for baseline permissions
- ABAC for project/data sensitivity
- Least privilege
- Audit logging
- Rate limiting
- Secure file scanning before processing
- Secrets supplied by environment/secret manager, never source control
- AI authorization must be enforced before retrieval
- Health/genomic data requires explicit consent and stricter access policies

Production deployment additionally requires threat modeling, dependency scanning, SAST/DAST, backup/restore testing, incident response and security review.
