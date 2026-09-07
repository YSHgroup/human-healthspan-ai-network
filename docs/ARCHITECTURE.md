# MVP Architecture

Web -> FastAPI modular monolith -> PostgreSQL/pgvector, Redis, OpenSearch, object storage.
AI is isolated behind an AI Gateway and must inherit user/resource authorization.

## Core product loop
QUESTION -> DISCUSSION -> EVIDENCE -> KNOWLEDGE -> HYPOTHESIS -> COLLABORATION -> RESEARCH

## MVP modules
- Identity/auth
- Profiles
- Social posts/comments
- Communities
- Questions/discussions
- Scientific content/evidence
- Researcher profiles
- Research workspaces
- Literature/document search
- Evidence-grounded AI
- Basic discovery/matching
- Admin/moderation

## Deliberately deferred
Knowledge graph, autonomous AI scientists, advanced bioinformatics, clinical decision support, institutional platform, funding marketplace, foundation-model training, Kubernetes/microservices.
