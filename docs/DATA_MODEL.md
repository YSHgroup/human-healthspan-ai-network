# Data Model

**Status: incremental development schema.** Alembic revisions through
`0005_researcher_organizations.py` create the shared identity, messaging, AI-consent, social,
researcher, organization, collaboration, event, entitlement, and limited administrative-audit
tables. The owner retired the separate legacy MVP as a migration source; no legacy schema or data
migration is promised.

## Data domains

| Domain | Examples | Principle |
|---|---|---|
| Identity and social | Users, profiles, connections, posts, comments, communities, events | Reliable transactional record in PostgreSQL |
| Implemented identity | `users`, `user_sessions` | Unique normalized email; password hash only; opaque session token digest and expiry |
| Implemented messaging | `conversations`, `conversation_participants`, `messages` | Conversation membership controls reads/writes; message body is text only |
| Implemented AI learning | `ai_learning_consents`, `ai_interactions` | Consent is versioned/revocable; prompt/answer fields are nullable; training eligibility defaults false |
| Implemented researcher access | `researcher_applications` | One application per account; explicit platform decision; profile discovery is opt-in |
| Implemented organizations | `organizations`, `organization_creation_requests`, `organization_memberships`, `organization_invitations`, `entitlements` | Platform review verifies submitted identity/website; invite-based tenant membership; pre-M5 creation entitlement is admin-granted |
| Implemented research workspace | `research_projects`, `research_project_members`, `research_tasks`, `research_documents`, `research_activities` | Organization and project authorization are checked separately; documents are text-only with private/project access |
| Implemented research events | `research_events`, `research_event_registrations` | Published events, organization-scoped visibility, single registration per member |
| Implemented M3 admin audit | `admin_audit_events` | Limited events for M3 verification, admission, organization, entitlement, and event decisions; not a general audit system |
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
- Current models and migrations are extended with reviewed, tested migrations.
- Project summary visibility does not grant access to project tasks, members, or documents. Protected
  project resources require active project membership; private text documents are visible only to
  their uploader and the project owner.
- AI metadata (environment, provider/model, character counts, latency and outcome) is recorded; content retention requires affirmative user consent. Revocation clears retained prompt/answer content. No training process consumes these records.
- `researcher_approved_at` and `email_verified_at` are null on registration; only authorized platform
  administrators can record verification or researcher approval. Automated email verification is
  not implemented.
