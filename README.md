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

## Important

This repository is an architectural/product foundation, not a clinical system and not a finished production platform. Health and scientific claims require governance, provenance and review before production use.
