# Round 2 — Expanded MVP

## Goal

Move the original MVP from a demo-oriented concept into a maintainable implementation foundation.

## Scope

### Social
- Account/profile foundation
- Follow graph
- Posts
- Comments
- Communities
- Topic taxonomy
- Feed/discovery API boundaries
- Reporting/moderation hooks

### Research
- Researcher profiles
- Research projects
- Project membership and roles
- Research questions
- Hypotheses
- Literature records
- Evidence records
- Project visibility
- Audit/versioning foundations

### AI
- Provider-neutral AI gateway
- Retrieval service boundary
- Citation/source model
- Authorization-aware context construction
- AI run audit boundary
- No unrestricted agent access

### Search
- PostgreSQL canonical records
- OpenSearch indexing boundary
- pgvector-ready embeddings
- Permission-filtered retrieval contract

### Infrastructure
- Dockerfiles for API and web
- Docker Compose for local development
- PostgreSQL + pgvector
- Redis
- OpenSearch
- Separate service boundaries ready for staging/production

## Deliberate exclusions

- No autonomous biomedical experimentation
- No diagnostic/clinical decision engine
- No foundation-model training
- No full knowledge graph deployment yet
- No microservice explosion
- No real-time messaging backend yet
- No institutional multi-tenancy implementation yet

## Acceptance criteria

1. `docker compose up --build` starts all local services.
2. API health endpoint responds.
3. Web app loads.
4. API v1 exposes social and research resource boundaries.
5. PostgreSQL is designated system of record.
6. AI retrieval has an explicit authorization boundary.
7. Evidence records can preserve provenance and classification.
8. Repository supports migration from MVP to later graph/agent/collaboration phases.
