# Data Model

## Identity
- users
- profiles
- organizations
- organization_members
- roles
- permissions
- sessions

## Social
- follows
- connections
- topics
- posts
- post_topics
- comments
- reactions
- bookmarks
- communities
- community_members
- media
- reports
- notifications

## Research
- research_projects
- research_members
- research_questions
- hypotheses
- papers
- paper_authors
- citations
- evidence
- datasets
- experiments
- protocols
- research_results
- project_files

## Scientific entities (Round 2-ready)
- genes
- proteins
- pathways
- diseases
- biomarkers
- therapeutics
- scientific_entities
- scientific_relationships

These are introduced as normalized relational entities first. A later graph projection can be derived from them.

## AI
- ai_conversations
- ai_messages
- ai_runs
- ai_sources
- embeddings
- tool_invocations

## Governance
- consents
- access_grants
- audit_logs
- moderation_actions
- content_classifications
- provenance_records

## Key invariants

1. Every private research resource has an owner/project access policy.
2. AI retrieval must be evaluated against the same access policy.
3. Scientific claims must preserve provenance.
4. Personal experience is not automatically classified as scientific evidence.
5. AI-generated hypotheses are explicitly labeled.
6. Soft deletion is preferred for user-generated content where legal/operationally appropriate.
7. Important scientific records require immutable audit history.
