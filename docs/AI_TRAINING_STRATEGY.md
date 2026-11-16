# AI Training Strategy

**Status: policy direction plus consent-aware logging infrastructure.** Nothing is trained and no
dataset, corpus or training pipeline consumes application data.

## Path

1. Use existing base models through the gateway. Never train a large foundation model from scratch.
2. Build curated scientific knowledge, permission-aware retrieval and source citation (M4 to M6).
3. Establish evaluation benchmarks and expert review before broadening tasks (M6).
4. The current slice records operational interaction metadata. It retains prompt/response content
   only when a member affirmatively opts in to versioned, revocable AI-learning consent.
5. Collect authorized feedback and validated outcomes with provenance and rights (M6 to M8).
6. Fine-tune only for specific task behavior, and only when evaluation shows retrieval is not enough.
7. Use retrieval for current, permissioned knowledge and fine-tuning for behavior.

The consented content remains pending review and is not automatically eligible for training.
Revocation clears previously retained prompt and response content. No automated export, evaluation
set construction, or training job exists.

## Go or no-go for training (M8)

Training starts only if all are true: M6 evaluation shows retrieval is insufficient for a defined
task, data rights are cleared, expert-reviewed evaluation sets exist, and the cost is approved.

## Requirements for any training or fine-tuning

Appropriate datasets, explicit data permissions, evaluation datasets, model versioning and
registry, reproducibility, cost controls and model governance.

## Data that may enter a corpus, evaluation set or training pipeline

Only data with recorded source, contributor rights, consent, organization, sensitivity, intended
use and retention, after review and approval. Prefer de-identification, aggregation or
evaluation-only use first. Organization learning stays inside organization boundaries; any
cross-organization contribution needs explicit authorization.

## Never

- Personal health or genomic data used for research or training without separate, explicit
  consent and governance.
- Private conversations, confidential research or organization data transferred automatically.
