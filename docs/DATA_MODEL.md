# Data Model

**Status: initial development schema.** The Alembic migration file
`0001_identity_messaging_ai_learning.py` (revision ID `0001_core`) creates identity, session,
text-messaging, AI-learning-consent and AI-interaction tables. This is not a migration of the
separately stored legacy MVP; no legacy schema or migration files were available in this checkout.

## Data domains

| Domain | Examples | Principle |
|---|---|---|
| Identity and social | Users, profiles, connections, posts, comments, communities, events | Reliable transactional record in PostgreSQL |
| Implemented identity | `users`, `user_sessions` | Unique normalized email; password hash only; opaque session token digest and expiry |
| Implemented messaging | `conversations`, `conversation_participants`, `messages` | Conversation membership controls reads/writes; message body is text only |
| Implemented AI learning | `ai_learning_consents`, `ai_interactions` | Consent is versioned/revocable; prompt/answer fields are nullable; training eligibility defaults false |
| Research management | Projects, questions, hypotheses, tasks, experiments, results | Ownership, permissions, versioning, provenance |
| Scientific knowledge | Papers, authors, citations, genes, proteins, pathways, biomarkers | Source traceability and entity resolution |
| Files and datasets | Documents, images, structured datasets | Object storage with metadata and access controls |
| Search and retrieval | Keyword indexes, embeddings | Permission-aware indexing and retrieval |
| AI operations | Conversations, runs, sources, evaluations, model versions | Auditable behavior and provider boundaries |
| Governance | Roles, consents, audit logs, retention records | Security, privacy, accountability |

## Candidate entities

User, Profile, Organization, Role, Permission, Membership, Invitation, Connection, Follow, Post,
Blog, Comment, Reaction, Message, Bookmark, Notification, Community, Group, Event,
ResearchProject, Hypothesis, Task, Protocol, Experiment, Result, Paper, Author, Citation,
Evidence, Gene, Protein, Pathway, Disease, Biomarker, Dataset, File, DataLicense, Consent,
ProvenanceRecord, AIConversation, AIRun, ModelVersion, Evaluation, AuditLog, Policy, AccessGrant.

## Shared enumerations (implemented in `@healthspan/shared-types`)

- **Visibility:** private, team, invited, community, public.
- **Evidence class:** peer reviewed, clinical trial, human observational, animal, cellular or
  in-vitro, computational, preprint, expert opinion, community experience, AI-generated
  hypothesis, speculation.
- **Organization role:** founder, owner, administrator, research leader, researcher, contributor, member.
- **Verification state:** verified, unverified.

## Constraints every model must respect

- Every research artifact has an owner, version history, provenance, access policy and status.
- Organization data is isolated per tenant; resource permissions are checked on every access.
- Health records are private by default and separate from research data.
- Work history is auditable; corrections use amendments, subject to legal deletion and retention rules.
- Existing MVP models and migrations are preserved and extended, never replaced without a verified migration.
- AI metadata (environment, provider/model, character counts, latency and outcome) is recorded; content retention requires affirmative user consent. Revocation clears retained prompt/answer content. No training process consumes these records.
- `researcher_approved_at` and `email_verified_at` are null on registration; no self-selected or synthetic researcher accounts are created.
