# AI Architecture

**Status: boundaries only.** `ai/healthspan_ai` defines module boundaries. No model provider,
retrieval workflow or AI endpoint is implemented.

## Three separated environments

| Environment | Module | Audience | Knowledge boundary |
|---|---|---|---|
| General Platform AI | `general` | All members | Public knowledge and approved common platform data |
| Private AI Scientist | `scientist` | Approved researchers | Authorized scientific corpus, projects and datasets; confidential by default |
| Organization-Specialized AI | `organization` | Members of one organization | That organization's approved knowledge only |

They are not one unrestricted model. No system infers authorization from interface visibility
or conversation context. Any exchange between environments uses explicit, narrow, audited
interfaces, and external providers receive only data approved for that provider and use case.
`tests/architecture` fails if these modules import one another.

## Supporting modules

`gateway` (provider-independent model access, routing, usage) - `orchestration` (workflows,
agents, tools, policies) - `knowledge` (ingestion, parsing, indexing, embeddings, retrieval,
provenance) - `training` - `evaluation` - `governance` - `monitoring` - `shared` (contracts).

## Rules

- Retrieval and tool execution inherit the requesting user's real rights at call time.
- Outputs preserve citations, provenance, uncertainty and model version. Hypotheses are proposals.
- The API reaches AI only through `healthspan_ai.gateway` and `healthspan_ai.shared`.
- AI code never imports the API. Long-running AI work runs as background jobs.
- Distinguish prompt customization, retrieval, fine-tuning and training. A knowledge base does not
  mean an organization owns a trained model.

## Where each part lands

General AI and the restricted Private AI Scientist prototype arrive as thin slices in M4; the
Scientist is deepened in M6 to M8; Organization AI arrives in M9 (see the roadmap).
