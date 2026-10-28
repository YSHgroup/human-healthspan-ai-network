# Human Healthspan, Scientific Research & AI Network — Round 2

A scalable foundation for the Human Healthspan / Scientific Research / AI Network.

## Round 2 focus

- Social network foundation: profiles, follows, posts, comments, communities
- Research foundation: projects, research questions, hypotheses, evidence, literature metadata
- Permission-aware AI/RAG boundary
- Unified search boundary
- Audit and governance foundations
- Dockerized local development
- PostgreSQL as system of record
- Redis for cache/queues
- OpenSearch for search
- pgvector-ready PostgreSQL for embeddings
- Next.js + TypeScript web application
- FastAPI + Python backend
- Clean module boundaries so later rounds can add knowledge graph, collaboration engine, agents and institutional controls

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

Web: http://localhost:3000
API: http://localhost:8000/docs
OpenSearch: http://localhost:9200

The API applies Alembic migrations when its container starts and seeds the six MVP communities. In development, account registration returns a one-time email-verification token in the response because no mail provider is configured. Set SMTP values in `.env` to deliver verification and password-reset tokens.

Create the first administrator from an operator shell:

```bash
docker compose exec api python -m app.cli create-admin admin@example.org
```

The API tests use SQLite and do not require Docker:

```bash
python -m pip install -r apps/api/requirements.txt
python -m pytest tests/test_api_contract.py -q
```

## Important

This repository is an MVP foundation, not a clinical system or finished production platform. External AI, OpenSearch/Redis integration, file upload/scan pipelines, rate limiting, MFA enforcement, and production observability still require implementation. Health and scientific claims require governance, provenance, and review before production use.

## Important for Agent!!!
If you are an AI agent, you need to update the `./docs/Last_Change.md` with the terms `Overall progress implemented`, `Last Change`, `What is the next step?` after updating this project.
