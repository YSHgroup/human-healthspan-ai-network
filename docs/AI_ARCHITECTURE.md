# AI Architecture

**Status: thin development slice.** `ai/healthspan_ai` now has an OpenAI-compatible chat-completions
gateway and separate General and Scientist prompt workflows. Provider access is disabled until
explicitly configured; retrieval, evaluation and production governance are not implemented.

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

## Implemented slice and boundaries

- The API calls AI only through `healthspan_ai.gateway` and `healthspan_ai.shared`.
- `AI_PROVIDER=openai-compatible` sends chat-completions requests to `AI_BASE_URL` using server-only `AI_API_KEY` and `AI_MODEL`. `AI_PROVIDER=disabled` is the default and returns an explicit error.
- General Platform AI receives a public/general-knowledge system instruction and the current chat history only. No private platform data is retrieved.
- The Scientist route requires `SCIENTIST_ENABLED=true`, an authenticated user, a verified email and an explicit researcher-approval timestamp. Registration grants neither state. No corpus, project file, retrieval tool or AI admin grant workflow is connected.
- Chat history is held in the browser for the current page and sent with each request; it is not persisted as a conversation by default.
- Operational AI interaction metadata is stored. Prompt and response content are retained only with a current affirmative AI-learning consent. Revocation deletes retained content, while metadata remains. `training_eligible` stays false.
- Provider-supplied source metadata can pass through the chat response, but the API always marks it
  `sources_verified: false` and states that it is unverified. No retrieval index or verified source
  pipeline is connected.
- Provider token counts are retained as operational metadata. Optional estimated USD cost requires
  exact-model input/output rates and a traceable `AI_PRICING_SOURCE`; unknown rates or missing
  provider usage remain unpriced. The applied rates and source label are snapshotted per
  interaction. Estimates are not invoices and do not certify provider billing.

## Rules

- Any future retrieval and tool execution must inherit the requesting user's real rights at call time.
- Outputs preserve citations, provenance, uncertainty and model version. Hypotheses are proposals.
- The API reaches AI only through `healthspan_ai.gateway` and `healthspan_ai.shared`.
- AI code never imports the API. Long-running AI work runs as background jobs.
- Distinguish prompt customization, retrieval, fine-tuning and training. A knowledge base does not
  mean an organization owns a trained model.

## Where each part lands

The current implementation is a prompt-only prototype. Retrieval and research workflows remain
planned for M4/M6; Organization AI remains planned for M9 (see the roadmap).
