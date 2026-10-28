# Data Model

The Phase 1 relational schema is managed by Alembic under `apps/api/app/db/migrations/versions/`. PostgreSQL is the source of truth; SQLAlchemy UUIDs, foreign keys, unique constraints, timestamps, and indexes enforce the core invariants.

## Implemented

### Identity and access

- `users`, `profiles`
- `auth_sessions` (revocable access/refresh session backing)
- `auth_tokens` (hashed, expiring, single-use email-verification and password-reset tokens)

New users cannot authenticate until their email is verified. Public profile reads do not disclose email addresses. Administrative roles cannot be assigned at registration; use the operator bootstrap command.

### Social and communities

- `communities`, `community_members`
- `posts`, `comments`, `reactions`, `bookmarks`, `follows`
- Content classification labels and soft-delete timestamps on user-generated posts/comments

Post ownership is derived from the authenticated user. Community membership is required to publish into a community. Starter communities are seeded on API startup.

### Research and evidence

- `research_projects`, `research_members`, `research_questions`, `hypotheses`
- `literature`, `evidence`

Projects support `private`, `team`, and `public` visibility. Owners and team members are permission-checked before project resources are read or changed. Team `member` roles can write; `reviewer` roles are read-only. Public search/retrieval is restricted to public projects.

### Governance and administration

- `reports`, `audit_events`

Privileged account changes and moderation actions require reason text and emit audit events. Sensitive administrative actions do not implicitly authorize access to private research resources.

## Key invariants

1. Authenticated identity, not client-supplied author IDs, determines write ownership.
2. Private/team research data is filtered by server-side project authorization.
3. AI retrieval applies project access restrictions before searching literature/evidence.
4. Personal experience, opinion, scientific evidence, hypotheses, AI-generated hypotheses, and speculation remain separately classified.
5. Account recovery and verification credentials are stored as hashes, expire, and are single-use.
6. User-generated posts/comments use soft deletion; research audit events preserve action history.

## Not yet implemented

Organizations/tenant membership, MFA enforcement, OIDC, messages, media/file uploads and scanning, paper-author normalization, claims/citations, datasets/experiments, notifications, AI conversations/runs/evaluations, embedding storage, and a graph projection remain future work. Redis/OpenSearch are provisioned in Compose but are not yet used by application services.
