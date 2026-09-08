# Technical Architecture

## Logical layers

1. Web experience — Next.js/React/TypeScript
2. API/application — FastAPI/Python
3. Domain services — social, research, evidence, search, AI, governance
4. System of record — PostgreSQL + pgvector
5. Supporting infrastructure — Redis, OpenSearch, object storage
6. Scientific projection — graph database later
7. External providers — identity, model APIs, literature/data sources
8. Observability — logs, metrics, traces, audit

## Scaling strategy

Start as a modular monolith with clear domain boundaries. Split only high-load or high-isolation domains later. The design avoids premature microservices while preserving service contracts.

## Future graph

Relational scientific entities become canonical source records. A graph projection can later materialize relationships such as:

Researcher → ResearchQuestion → Hypothesis → Evidence → Paper → Gene → Protein → Pathway → Disease → Experiment → Result
