# Human Healthspan, AI & Scientific Network
## MVP v2 — Product & Engineering Specification
**Implementation baseline — September 2026**

> **Status:** Build-ready MVP specification  
> **Architecture:** Modular monolith, progressively extractable into services  
> **Primary goal:** Validate the product loop  
> **People → Questions → Discussion → Evidence → AI → Research Ideas → Collaboration**

---

## 1. Executive Summary

The MVP is a production-oriented first release combining:

1. A consumer health/capability social community.
2. A scientific content and evidence layer.
3. Lightweight research workspaces.
4. An evidence-grounded AI assistant.
5. Unified search and discovery.
6. Moderation, permissions, provenance and auditability.

The MVP intentionally does **not** implement the complete long-term scientific ecosystem. The biomedical knowledge graph, genomic platform, autonomous AI scientists, advanced bioinformatics, institutional infrastructure, funding marketplace, native mobile apps and complex Kubernetes/microservice infrastructure remain future phases.

The MVP must prove one critical hypothesis:

> Social interaction can naturally lead to learning, evidence, structured research questions and collaborative research.

This follows the source specification's intended loop and product boundary. fileciteturn5file0L14-L19 fileciteturn5file0L237-L244

---

# 2. Product Vision and MVP Boundary

## 2.1 Long-term product

A global AI-powered social and scientific network that helps people improve health, physical and cognitive capability and wellbeing while connecting researchers, data, ideas and technology to accelerate responsible innovation in human healthspan.

## 2.2 MVP product

The MVP is intentionally narrower:

```text
USER
  ↓
PROFILE / INTERESTS
  ↓
COMMUNITY
  ↓
POST / QUESTION
  ↓
DISCUSSION
  ↓
EVIDENCE
  ↓
AI EXPLANATION / RESEARCH SUPPORT
  ↓
RESEARCH QUESTION
  ↓
RESEARCH PROJECT
  ↓
COLLABORATION
```

## 2.3 Non-negotiable product distinction

The interface must clearly distinguish:

- Personal experience
- Opinion
- Scientific evidence
- Expert interpretation
- Research hypothesis
- AI-generated hypothesis
- Speculation

A community statement must never automatically become a scientific or medical claim.

---

# 3. MVP Users

| Persona | Primary value |
|---|---|
| General user | Learn, participate, ask questions and improve health/capability |
| Health & fitness enthusiast | Communities, evidence, discussions and discovery |
| Researcher/scientist | Research profile, literature, evidence and projects |
| Biomedical/health professional | Expert participation and scientific discussion |
| Student/educator | Learn and discuss scientific material |
| Scientific moderator | Evidence quality, moderation and governance |
| Administrator | Platform operations, users, reports, AI and audit |

---

# 4. MVP Product Modules

## P0 — Required

### Authentication
- Email/password authentication
- OAuth/OIDC-ready architecture
- Session management
- Password reset
- Email verification
- MFA-ready design

### Profiles
- Basic profile
- Avatar
- Bio
- Location/timezone
- Interests
- Topics
- Expertise
- Researcher identity
- Organization affiliation
- Public/private profile controls

### Social
- Feed
- Posts
- Questions
- Answers
- Comments
- Reactions
- Bookmarks
- Follows
- Content classification labels

### Communities
Initial communities:

1. Healthy Aging
2. Fitness & Strength
3. Nutrition
4. Skin & Appearance
5. Brain & Cognition
6. Biomedical Research

Community capabilities:
- Membership
- Community feed
- Community posts
- Community questions
- Moderation
- Topic metadata

### Science
- Scientific feed
- Papers/documents
- Paper/document detail
- Evidence records
- Citations
- Source metadata
- Evidence classification
- Provenance

### Research
- Research projects
- Research questions
- Objectives
- Hypotheses
- Literature
- Evidence
- Documents
- Team members
- Lightweight tasks/timeline
- Private / Team / Public visibility

### AI
- General health/science educational Q&A
- Evidence-oriented explanations
- Literature/document search
- Summaries
- Evidence comparison
- Research-question support
- Workspace-aware AI
- Citations
- Evidence labels
- Confidence/uncertainty
- Limitations

### Search
Unified search over:
- Users
- Experts
- Posts
- Questions
- Communities
- Research projects
- Papers
- Documents

Search modes:
- Keyword
- Semantic
- Hybrid

Filters:
- Topic
- Evidence type
- Content type
- Community
- Research project

### Moderation
- User reports
- Content reports
- Review queue
- Remove/hide content
- Scientific misinformation flags
- Abuse controls
- Moderator actions
- Audit trail

### Administration
- User management
- Community management
- Content management
- Reports
- AI monitoring
- Audit logs
- Basic analytics

---

# 5. Primary User Journeys

## 5.1 Consumer journey

```text
Landing
  ↓
Sign up
  ↓
Select interests
  ↓
Personalized home
  ↓
Join communities
  ↓
Read / post / ask
  ↓
Community discussion
  ↓
Evidence discovery
  ↓
AI explanation
  ↓
Discover experts / papers
  ↓
Follow topics / researchers
```

## 5.2 Researcher journey

```text
Sign up
  ↓
Researcher profile
  ↓
Add expertise/interests
  ↓
Create research project
  ↓
Define research question
  ↓
Add literature/documents
  ↓
Ask Research AI
  ↓
Review evidence and citations
  ↓
Identify related researchers/projects
  ↓
Invite collaborators
```

---

# 6. Core Screens

1. Landing
2. Sign up
3. Login
4. Home
5. Discover
6. Communities
7. Community detail
8. Create post
9. Question detail
10. User/expert profile
11. Science feed
12. Paper/document detail
13. Research dashboard
14. Research project
15. AI Research Assistant
16. Notifications
17. Settings
18. Moderation queue
19. Admin dashboard

---

# 7. Domain Model

The MVP should treat **Research Question** as a central domain object rather than allowing research to exist as an isolated feature.

```text
PERSON
  ↓
QUESTION
  ├── DISCUSSION
  ├── ANSWERS
  ├── EVIDENCE
  ├── CLAIMS
  ├── AI ANALYSIS
  └── RESEARCH PROJECT
          ↓
      HYPOTHESES
          ↓
       LITERATURE
          ↓
     COLLABORATORS
```

This provides a clean migration path toward the long-term scientific knowledge layer.

---

# 8. Scientific Evidence Model

## 8.1 Evidence types

- Peer-reviewed
- Clinical trial
- Human observational
- Animal
- Cellular
- Computational
- Preprint
- Expert opinion
- Community report
- AI-generated hypothesis
- Speculation

## 8.2 Evidence record

```text
Evidence
├── id
├── evidence_type
├── title
├── source
├── publication
├── authors
├── publication_date
├── population
├── methodology
├── confidence
├── limitations
├── provenance
├── reviewer_id
├── created_at
└── updated_at
```

## 8.3 Claim model

Add a lightweight Claim object in MVP v2:

```text
Claim
├── id
├── statement
├── source_type
├── created_by
├── evidence_links
├── support_status
├── confidence
├── provenance
├── review_status
├── created_at
└── updated_at
```

Possible support states:

- Supported
- Partially supported
- Contradicted
- Insufficient evidence
- Hypothesis
- Speculative

This prepares the product for the future knowledge graph without implementing Neo4j.

---

# 9. Research Workspace

Each research project contains:

```text
Project
├── Overview
├── Research Question
├── Objectives
├── Hypotheses
├── Literature
├── Evidence
├── Claims
├── Documents
├── Team
├── AI Assistant
└── Tasks / Timeline
```

Visibility:

- Private
- Team
- Public

## Authorization rule

AI access must inherit the requesting user's project/resource permissions.

The AI must never retrieve:
- Private projects the user cannot access
- Private documents
- Private team data
- Restricted research information
- Sensitive data outside the permitted purpose

---

# 10. AI Architecture

## 10.1 Principle

Do **not** train a foundation model for the MVP.

Use:

- Frontier model APIs
- Model-provider abstraction
- Embeddings
- RAG
- Tool calling
- Structured outputs
- Citations
- Evaluation

## 10.2 AI request flow

```text
User
 ↓
Authentication
 ↓
Authorization
 ↓
AI Gateway
 ↓
AI Orchestrator
 ↓
Permission-aware Retrieval
 ↓
PostgreSQL / pgvector / OpenSearch
 ↓
Authorized Workspace Documents
 ↓
Prompt Assembly
 ↓
LLM
 ↓
Citation / Evidence Validation
 ↓
Response
```

## 10.3 Critical security rule

Never implement:

```text
User → LLM → Entire Database
```

Implement:

```text
User
 ↓
Authorization
 ↓
Accessible Resources
 ↓
Retrieval
 ↓
LLM
```

## 10.4 AI response contract

Every scientific/research answer should expose, where applicable:

```json
{
  "answer": "...",
  "sources": [],
  "evidence_types": [],
  "confidence": "medium",
  "uncertainty": [],
  "limitations": [],
  "claims": [],
  "generated_hypotheses": []
}
```

AI-generated hypotheses must never be displayed as established scientific evidence.

---

# 11. AI Capability Tiers

## AI-01 — User AI

Purpose:
- General health/science educational questions
- Explain scientific concepts
- Summarize retrieved evidence

## AI-02 — Health Education AI

Purpose:
- Evidence-oriented explanations
- Compare evidence types
- Explain uncertainty and limitations

## AI-03 — Research AI

Purpose:
- Literature search
- Document search
- Summarization
- Evidence comparison
- Research-question refinement

## AI-04 — Workspace AI

Purpose:
- Answer questions using authorized project documents
- Summarize project literature
- Compare project evidence
- Organize hypotheses

Future agents such as bioinformatics, genetics, clinical research and scientific review remain outside the MVP.

---

# 12. Search Architecture

## MVP search pipeline

```text
Content
 ↓
Normalization
 ↓
Metadata extraction
 ↓
Keyword index
 ↓
Embedding generation
 ↓
Vector index
 ↓
Hybrid retrieval
 ↓
Ranking
 ↓
Permission filtering
 ↓
Results
```

Search must support both:

- Lexical/keyword relevance
- Semantic similarity

Scientific relevance and evidence quality should influence ranking; engagement alone must not determine scientific discovery.

---

# 13. Document Ingestion

For papers/documents:

```text
Upload
 ↓
Security scan
 ↓
File validation
 ↓
Text extraction
 ↓
Metadata extraction
 ↓
Chunking
 ↓
Embedding
 ↓
PostgreSQL metadata
 ↓
Object storage original
 ↓
Search index
 ↓
Vector index
 ↓
Evidence/citation candidates
```

Required metadata:
- Owner
- Visibility
- Source
- Title
- Authors
- Publication date
- Evidence type
- Provenance
- Content hash
- Processing status

---

# 14. PostgreSQL Data Model

## Identity

```text
users
profiles
organizations
organization_members
roles
permissions
user_roles
```

## Social

```text
topics
communities
community_members
posts
comments
reactions
bookmarks
follows
```

## Questions

```text
questions
answers
question_topics
question_evidence
```

## Science

```text
papers
documents
citations
evidence
claims
claim_evidence
scientific_reviews
```

## Research

```text
research_projects
research_members
research_questions
hypotheses
research_documents
research_literature
research_tasks
```

## AI

```text
ai_conversations
ai_messages
ai_sources
ai_runs
ai_evaluations
```

## Governance

```text
consents
access_policies
audit_logs
reports
moderation_actions
```

## Common conventions

Every major entity should support:

```text
id UUID
created_at
updated_at
created_by / owner_id where applicable
visibility where applicable
deleted_at where soft deletion is appropriate
provenance metadata where applicable
```

Use foreign keys and appropriate indexes.

---

# 15. Authorization Model

Use two layers:

## RBAC

Examples:

- User
- Researcher
- Moderator
- Scientific Reviewer
- Admin

## Resource-level authorization

Examples:

```text
CanReadProject
CanWriteProject
CanInviteProjectMember
CanReadDocument
CanUploadDocument
CanUseWorkspaceAI
CanModerateContent
CanReviewEvidence
```

Authorization must happen before retrieval, not after AI generation.

---

# 16. API Architecture

Base:

```text
/api/v1
```

## Auth

```text
POST /auth/register
POST /auth/login
POST /auth/logout
POST /auth/refresh
POST /auth/verify-email
POST /auth/password-reset
```

## Users

```text
GET    /users/me
PATCH  /users/me
GET    /users/{id}
GET    /users/{id}/followers
POST   /users/{id}/follow
DELETE /users/{id}/follow
```

## Communities

```text
GET    /communities
POST   /communities/{id}/join
DELETE /communities/{id}/join
GET    /communities/{id}
GET    /communities/{id}/feed
```

## Social

```text
GET    /feed
POST   /posts
GET    /posts/{id}
PATCH  /posts/{id}
DELETE /posts/{id}
POST   /posts/{id}/comments
POST   /posts/{id}/reactions
POST   /posts/{id}/bookmark
```

## Questions

```text
POST   /questions
GET    /questions/{id}
PATCH  /questions/{id}
POST   /questions/{id}/answers
GET    /questions/{id}/evidence
POST   /questions/{id}/research-project
```

## Science

```text
GET    /papers
GET    /papers/{id}
GET    /documents
POST   /documents
GET    /documents/{id}
GET    /evidence/{id}
GET    /claims/{id}
```

## Research

```text
POST   /research/projects
GET    /research/projects
GET    /research/projects/{id}
PATCH  /research/projects/{id}
POST   /research/projects/{id}/members
POST   /research/projects/{id}/questions
POST   /research/projects/{id}/hypotheses
POST   /research/projects/{id}/documents
```

## AI

```text
POST /ai/conversations
POST /ai/conversations/{id}/messages
POST /ai/research/ask
POST /ai/workspaces/{project_id}/ask
GET  /ai/runs/{id}
```

## Search

```text
GET /search
GET /search/suggestions
```

## Moderation

```text
POST /reports
GET  /moderation/queue
POST /moderation/actions
```

## Admin

```text
GET /admin/users
GET /admin/reports
GET /admin/audit-logs
GET /admin/ai-monitoring
```

---

# 17. Repository Structure

```text
healthspan-platform/
│
├── web/
│   ├── app/
│   ├── components/
│   ├── features/
│   ├── hooks/
│   ├── lib/
│   └── tests/
│
├── api/
│   ├── auth/
│   ├── users/
│   ├── social/
│   ├── communities/
│   ├── questions/
│   ├── science/
│   ├── research/
│   ├── ai/
│   ├── search/
│   ├── moderation/
│   └── admin/
│
├── ai/
│   ├── gateway/
│   ├── orchestrator/
│   ├── rag/
│   ├── retrieval/
│   ├── embeddings/
│   ├── citations/
│   ├── tools/
│   └── evaluation/
│
├── database/
│   ├── migrations/
│   └── seeds/
│
├── infrastructure/
│   ├── docker/
│   ├── ci/
│   └── deployment/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   ├── security/
│   └── ai/
│
└── docs/
    ├── architecture/
    ├── api/
    ├── product/
    └── governance/
```

---

# 18. Technology Stack

## Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS

## Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy

## Data

- PostgreSQL
- pgvector
- Redis

## Search

- OpenSearch

## Storage

- S3-compatible object storage

## AI

- Provider abstraction
- LLM APIs
- Embeddings
- RAG
- Structured outputs
- Tool calling

## Identity

- OAuth/OIDC-ready

## Deployment

- Docker
- Managed cloud services
- CI/CD

## Architecture

**Modular monolith first.**

Extract services only when scale, ownership boundaries or workload characteristics justify the split.

---

# 19. Event-Driven Background Jobs

The transactional application remains synchronous where appropriate. Expensive/non-critical work becomes asynchronous.

```text
Application
 ↓
Domain Event
 ↓
Redis Queue
 ↓
Worker
 ↓
Background Processing
```

Example events:

```text
PostCreated
CommentCreated
QuestionCreated
ResearchProjectCreated
DocumentUploaded
DocumentProcessed
EmbeddingCreated
AICompleted
ModerationRequired
EvidenceUpdated
NotificationCreated
```

Workers can handle:
- Notifications
- Search indexing
- Embeddings
- Document processing
- AI evaluation
- Analytics
- Moderation pipelines

---

# 20. Security & Privacy

Required controls:

- OAuth/OIDC-ready identity
- MFA-ready architecture
- RBAC
- Resource-level authorization
- Encryption in transit
- Encryption at rest
- Least privilege
- Audit logging
- Rate limiting
- Abuse prevention
- Secure uploads
- File scanning
- Explicit consent
- Granular sharing controls
- Separation of personal-health and research data
- AI permission boundary

Sensitive health/genomic data must not be treated as ordinary social content without explicit policy controls.

---

# 21. Scientific Governance

Create a lightweight governance layer in MVP rather than postponing scientific trust until later.

## Governance capabilities

- Evidence taxonomy
- Source provenance
- Evidence labeling
- Claim review
- Scientific reviewer role
- Reviewer notes
- Conflict disclosure field
- Correction workflow
- Audit history
- AI scientific evaluation

## Scientific integrity rule

The system must preserve the difference between:

```text
Experience ≠ Evidence
Opinion ≠ Evidence
AI Output ≠ Scientific Truth
Hypothesis ≠ Validated Finding
```

---

# 22. Moderation

## Automated signals

Potential flags:
- Medical misinformation
- Dangerous health claims
- Spam
- Harassment
- Abuse
- Manipulative content
- Misleading scientific claims

## Human review

Moderator can:

```text
Review
 ↓
Classify
 ↓
Approve / Hide / Remove
 ↓
Add reason
 ↓
Audit action
```

Scientific content requiring expertise should be routed to qualified scientific review rather than treated purely as generic community moderation.

---

# 23. Analytics

## Product metrics

- Signups
- Profile completion
- Community joins
- Posts/user
- Questions/user
- Answer rate
- Follow rate
- Repeat participation
- Search usage
- Evidence interaction
- AI questions
- Citation interaction
- Research projects created
- Researcher participation

## North-star conversion

```text
Question
 → Evidence
 → AI interaction
 → Research question
 → Research project
```

Measure this conversion rather than optimizing solely for likes or time spent.

---

# 24. MVP Milestones

## Milestone 1 — Foundation

Deliver:

- Repository
- CI/CD
- Environment configuration
- Database
- Migrations
- Authentication
- Profiles
- Topics
- Communities
- Frontend shell
- API foundation
- RBAC/resource authorization

## Milestone 2 — Social

Deliver:

- Feed
- Posts
- Questions
- Answers
- Comments
- Reactions
- Bookmarks
- Follows
- Community feeds
- Reports
- Basic moderation

## Milestone 3 — Scientific Research

Deliver:

- Researcher profiles
- Papers
- Documents
- Evidence model
- Claims
- Citations
- Scientific search
- Research questions
- Research projects
- Project members
- Project visibility

## Milestone 4 — AI

Deliver:

- AI Gateway
- Provider abstraction
- Embeddings
- RAG
- Document ingestion
- Permission-aware retrieval
- Citations
- User AI
- Research AI
- Workspace AI
- AI evaluation

## Milestone 5 — Beta / Production Hardening

Deliver:

- Security audit
- Authorization testing
- Audit logs
- Abuse controls
- AI evaluation
- Search relevance evaluation
- Performance/load testing
- Observability
- Backup/recovery
- Production deployment
- Analytics

---

# 25. Testing Strategy

## Unit

- Domain logic
- Evidence classification
- Permission rules
- Claim support logic

## API

- Authentication
- Authorization
- Resource isolation
- CRUD contracts

## Frontend

- Component tests
- Critical user journeys
- End-to-end flows

## Security

- Privilege escalation
- Tenant/project isolation
- Prompt injection
- File upload security
- Secret exposure
- Rate-limit abuse

## AI

- Retrieval relevance
- Groundedness
- Citation accuracy
- Hallucination
- Prompt injection
- Permission boundaries
- Regression tests
- Adversarial scientific questions

## Scientific

- Evidence classification
- Provenance preservation
- Claim/evidence support
- Contradiction handling
- Source attribution
- Review workflow

---

# 26. MVP Acceptance Criteria

The MVP is acceptable only when all of the following are demonstrably possible.

## Consumer

A user can:

1. Sign up.
2. Complete a profile.
3. Select interests.
4. Join a community.
5. Publish a post.
6. Ask a question.
7. Receive community responses.
8. Search scientific sources.
9. Ask AI an evidence-grounded question.
10. Inspect citations.
11. Distinguish evidence from opinion/speculation.
12. Convert a question into a research project.

## Researcher

A researcher can:

1. Create a researcher profile.
2. Define expertise.
3. Create a research project.
4. Define a research question.
5. Add documents.
6. Add literature.
7. Review evidence.
8. Ask workspace-aware AI.
9. Inspect cited sources.
10. Invite authorized collaborators.

## Security

The system must demonstrate:

- A user cannot retrieve another user's private project.
- AI cannot retrieve unauthorized documents.
- Project members see only permitted resources.
- Audit events are generated for sensitive actions.
- Uploaded files are scanned before processing.

---

# 27. MVP Non-Goals

Do **not** build these in the first release:

- Biomedical knowledge graph / Neo4j
- Genomic data platform
- Autonomous AI scientists
- Advanced bioinformatics
- Experiment/result management
- Clinical decision support
- Institutional research platform
- Funding marketplace
- Foundation-model training
- Native mobile applications
- Complex microservices
- Kubernetes as an MVP requirement

These boundaries are explicitly consistent with the source MVP specification. fileciteturn5file0L159-L170

---

# 28. Infrastructure Strategy

## Development

```text
Docker Compose
 ├── Next.js
 ├── FastAPI
 ├── PostgreSQL
 ├── Redis
 ├── OpenSearch
 └── S3-compatible local storage
```

## Staging

Use managed equivalents where practical:

```text
CDN
 ↓
Load Balancer
 ↓
Web / API containers
 ↓
PostgreSQL
Redis
OpenSearch
Object Storage
AI providers
```

## Production

Add:

- WAF
- Centralized logs
- Metrics
- Traces
- Alerts
- Automated backups
- Point-in-time recovery
- Disaster recovery
- Health checks
- Rolling/blue-green deployment where justified

Do not introduce Kubernetes simply because the architecture is intended to scale globally.

---

# 29. Deployment Environments

```text
Development
    ↓
CI Tests
    ↓
Security / AI Evaluation
    ↓
Staging
    ↓
Integration / Acceptance
    ↓
Production
```

Each environment must have separate secrets, data policies and access controls.

---

# 30. Performance Targets

Initial engineering targets:

| Area | MVP target |
|---|---|
| Standard API | p95 < 500 ms where practical |
| Search | p95 < 1.5 s |
| Feed | p95 < 1 s after caching |
| AI first response | streaming response initiated quickly; provider-dependent |
| Document processing | asynchronous |
| Background jobs | retryable and observable |
| Critical DB queries | indexed and monitored |

These are engineering targets, not product guarantees. Measure real production performance before optimizing infrastructure.

---

# 31. Scalability Strategy

The MVP should scale through architecture, not premature infrastructure.

## Stage 1

```text
Modular monolith
+
PostgreSQL
+
Redis
+
pgvector
+
OpenSearch
+
Object Storage
```

## Stage 2

When workload requires:

- Read replicas
- Database partitioning
- Dedicated workers
- Search cluster scaling
- AI workload queues
- Separate ingestion workers

## Stage 3

Extract high-value bounded contexts:

```text
Core API
AI Service
Search Service
Document Ingestion
Notification Service
Analytics
```

## Stage 4

Introduce additional scientific infrastructure:

```text
Scientific Knowledge Layer
        ↓
Knowledge Graph
        ↓
Advanced Research Agents
        ↓
Institutional Platform
```

This preserves the long-term architecture without forcing its operational complexity into the MVP.

---

# 32. Future Evolution

```text
PHASE 1
Social
   ↓
PHASE 2
Social + Research Workspaces
   ↓
PHASE 3
Social + Research + RAG AI
   ↓
PHASE 4
Scientific Knowledge Layer
   ↓
PHASE 5
Researcher / Expert / Dataset Matching
   ↓
PHASE 6
Advanced Scientific AI
   ↓
PHASE 7
Institutional Infrastructure
   ↓
PHASE 8
Global Research Ecosystem
```

The long-term architecture specifically recommends implementing later layers only after earlier layers demonstrate value and generate the necessary data. fileciteturn4file1L135-L179

---

# 33. Long-Term Knowledge Graph Readiness

The MVP does not need Neo4j.

However, data should already support relationships such as:

```text
PERSON
 ├── INTERESTED_IN → TOPIC
 ├── MEMBER_OF → COMMUNITY
 ├── ASKED → QUESTION
 ├── AUTHORED → CLAIM
 └── MEMBER_OF → PROJECT

QUESTION
 ├── RELATED_TO → PAPER
 ├── SUPPORTED_BY → EVIDENCE
 ├── CONTAINS → CLAIM
 └── BECOMES → RESEARCH_PROJECT

CLAIM
 ├── SUPPORTED_BY → EVIDENCE
 ├── CONTRADICTED_BY → EVIDENCE
 ├── DERIVED_FROM → PAPER
 └── RELATES_TO → QUESTION
```

The future graph should be derived from governed transactional data rather than replacing PostgreSQL as the system of record.

---

# 34. Observability

Minimum production observability:

- Structured application logs
- Request IDs
- Error tracking
- API latency metrics
- Database performance
- Queue depth
- Worker failures
- Search latency
- AI latency/cost
- AI error rates
- Citation failures
- Authorization failures
- Security events

AI-specific observability:

```text
AI Request
├── model
├── latency
├── tokens
├── retrieval sources
├── permission scope
├── citation results
├── evaluation score
└── outcome
```

Never log sensitive user/project content unnecessarily.

---

# 35. Cost Control

AI cost controls:

- Model routing
- Smaller models for classification/simple tasks
- Caching
- Embedding reuse
- Retrieval limits
- Token budgets
- Per-user quotas
- Per-project quotas
- Async processing for heavy jobs
- Evaluation before model upgrades

Infrastructure cost controls:

- Managed services initially
- Autoscaling where useful
- Storage lifecycle policies
- Search retention policies
- Background-worker scaling

---

# 36. Engineering Work Breakdown

## Epic A — Platform Foundation

- Repository setup
- Docker
- CI/CD
- Environment config
- DB
- migrations
- API framework
- frontend shell
- authentication
- authorization
- logging

## Epic B — Identity & Community

- Profiles
- interests
- topics
- communities
- membership
- feed

## Epic C — Social

- posts
- questions
- answers
- comments
- reactions
- bookmarks
- follows
- notifications

## Epic D — Scientific

- researcher profiles
- papers
- documents
- evidence
- claims
- citations
- provenance

## Epic E — Research

- projects
- research questions
- hypotheses
- project members
- project documents
- literature
- tasks

## Epic F — AI

- provider abstraction
- gateway
- orchestrator
- retrieval
- embeddings
- RAG
- citations
- workspace authorization
- AI evaluation

## Epic G — Search

- indexing
- keyword search
- semantic search
- hybrid ranking
- filters

## Epic H — Governance

- reports
- moderation
- scientific review
- audit
- consent
- access policies

## Epic I — Beta

- performance
- security
- observability
- analytics
- backup/recovery
- production deployment

---

# 37. Definition of Done

A feature is not complete when its UI exists.

A feature is complete when:

- API exists
- Authorization exists
- Validation exists
- Database migrations exist
- Tests exist
- Audit requirements are addressed
- Error handling exists
- Observability exists where appropriate
- Documentation exists
- Frontend is integrated
- Accessibility/basic UX quality is acceptable
- Security implications are reviewed

For AI features additionally:

- Retrieval behavior tested
- Citation behavior tested
- Permission boundary tested
- Hallucination/grounding evaluation exists
- Failure behavior defined

---

# 38. Product Principles

1. Scientific credibility over engagement.
2. Evidence before assertion.
3. Authorization before retrieval.
4. Provenance must survive transformation.
5. AI output is not automatically truth.
6. Community experience is not automatically scientific evidence.
7. Human scientific judgment remains responsible for research decisions.
8. Sensitive health data requires explicit governance.
9. Build a modular monolith before splitting services.
10. Do not let the long-term architecture consume the MVP.

These principles directly reinforce the architecture's non-negotiable rules. fileciteturn4file9L860-L872

---

# 39. Final Build Architecture

```text
                         HUMAN HEALTHSPAN NETWORK
                                   │
                 ┌─────────────────┴─────────────────┐
                 │                                   │
            Social Layer                       Research Layer
                 │                                   │
      Users / Profiles / Feed              Projects / Questions
      Communities / Posts                   Literature / Evidence
      Questions / Discussion                 Claims / Documents
                 │                                   │
                 └─────────────────┬─────────────────┘
                                   │
                         Scientific Knowledge
                         Metadata / Claims /
                         Evidence / Provenance
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
               Search Layer                 AI Gateway
          Keyword + Semantic                  │
                    │                    Authorization
                    │                         │
                    └──────────────┬──────────┘
                                   │
                                RAG
                                   │
                         PostgreSQL / pgvector
                         OpenSearch / Documents
                                   │
                              LLM Provider
                                   │
                         Cited AI Response
```

## Technology baseline

```text
Next.js
  ↓
FastAPI
  ↓
PostgreSQL + pgvector
  +
Redis
  +
S3-compatible Object Storage
  +
OpenSearch
  ↓
AI Gateway
  ↓
RAG + LLM + Citations
```

The final architecture is intentionally aligned with the existing technical baseline: Next.js/React/TypeScript, FastAPI/Python, PostgreSQL, Redis, S3-compatible storage, OpenSearch, pgvector and an AI gateway with RAG/tooling, while keeping the initial system as a modular monolith. fileciteturn4file1L101-L130

---

# 40. Final MVP Outcome

The MVP succeeds if it demonstrates:

```text
People
  ↓
Communities
  ↓
Questions
  ↓
Discussion
  ↓
Evidence
  ↓
AI
  ↓
Research Questions
  ↓
Research Projects
  ↓
Researchers / Collaboration
```

If this loop demonstrates real user value, the next releases can safely expand into:

- Scientific knowledge graph
- Researcher matching
- Dataset discovery
- Advanced scientific agents
- Bioinformatics
- Experiment/result workflows
- Institutional research environments
- Research APIs
- Global scientific ecosystem

The MVP therefore remains **small enough to build, serious enough to validate, and structured enough to scale into the full Human Healthspan AI Scientific Network.**
