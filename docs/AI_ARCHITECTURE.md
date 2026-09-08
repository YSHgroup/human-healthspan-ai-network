# AI Architecture

Request
→ Authentication
→ Authorization Scope Builder
→ Context/Retrieval Planner
→ PostgreSQL/OpenSearch/pgvector
→ optional graph projection
→ Evidence/Provenance Filter
→ Model Router
→ Tool/Agent execution
→ Citation validator
→ Response policy
→ Audit log

## Rules

- The model provider is replaceable.
- Retrieval is permission-aware.
- Private project context never becomes globally searchable.
- Every scientific answer should be able to expose sources.
- AI-generated hypotheses remain hypotheses.
- Tools receive least-privilege scopes.
- All agent/tool invocations are auditable.

## Future

Add:
- literature agent
- evidence agent
- aging biology agent
- genetics agent
- bioinformatics agent
- data analysis agent
- research planning agent
- scientific review agent
- knowledge graph agent
