This product specification is aligned with the [final architecture](../Human_Healthspan_AI_Scientific_Network_Final_Architecture.md), the [roadmap](../ROADMAP.md), and the detailed [MVP v2 engineering specification](Human_Healthspan_AI_Scientific_Network_MVP_v2_Engineering_Specification.md). The architecture and roadmap define system boundaries and phased scope; this document defines the Phase 1 product.

Phase 1 includes the member platform, foundational research workflows, evidence-grounded AI where it meets quality and privacy requirements, and a separate first-class Admin App. Researcher matching, events, and challenges are later roadmap capabilities, not MVP launch dependencies.

# MVP Specification — Phase 1

Phase 0 validation and architecture work precedes implementation. Phase 1 is the first product release and includes both member-facing and administrative applications.

## 1. MVP objective

The MVP should answer one fundamental question:

> **Will people use a health/science social network where conversations can naturally lead to evidence, AI-assisted knowledge, and research collaboration?**

We should **not** attempt to build the complete knowledge graph, advanced scientific agents, institutional platform, genomic-data infrastructure, funding marketplace, etc. yet.

The MVP should establish the foundation for later phases without making their capabilities launch dependencies.

---

# 2. MVP product

I would define the first version as:

### **Healthspan Network MVP**

A member-facing web application, accompanied by a separate Admin App, where users can:

**Discover → Discuss → Learn → Ask AI → Explore Research → Collaborate**

with two connected experiences:

### Consumer side

* Healthspan
* Fitness & strength
* Nutrition
* Skin & Appearance
* Brain & Cognition
* Healthy Aging

### Research side

* Researchers
* Experts
* Research questions
* Research projects
* Literature
* Evidence
* AI research assistance

This follows the blueprint's principle that the consumer layer provides broad engagement while the scientific layer creates deeper value and defensibility. 

---

# 3. MVP users

The initial personas are:

| User | Primary need |
| --- | --- |
| General user / health and fitness enthusiast | Learn, participate, ask questions, and improve health/capability |
| Researcher / scientific expert | Share expertise, explore evidence, and create or join research projects |
| Scientific reviewer / moderator | Review evidence quality, reports, and community content |
| Administrator / support operator | Safely manage platform operations with least-privilege access and auditability |

Institutional workspaces and organization accounts belong to a later roadmap phase.

---

# 4. MVP modules

The Phase 1 member platform and Admin App provide the following capabilities.

### 1. Identity

* Registration
* Login
* OAuth-ready architecture
* Password reset
* Email verification
* User roles
* Basic profile

### 2. Social graph

* Follow users
* Followers
* Following
* Expert profiles

### 3. Content

* Posts
* Questions
* Comments
* Reactions
* Bookmarks
* Topics
* Basic media support

### 4. Communities

Start with these six:

* Healthy Aging
* Fitness & Strength
* Nutrition
* Skin & Appearance
* Brain & Cognition
* Biomedical Research

The blueprint specifically recommends starting with a small set of these communities. 

### 5. Research

* Researcher profile
* Research interests
* Research project
* Research question
* Project members
* Project permissions

### 6. Literature

* Upload documents
* Store papers/documents
* Extract text
* Index documents
* Semantic search
* Metadata
* Citations

### 7. Evidence

Every scientific item should have an evidence classification.

For MVP:

* Peer-reviewed
* Preprint
* Clinical
* Human observational
* Animal
* Cell-based
* Computational
* Expert opinion
* Community claim
* AI-generated hypothesis

This distinction is central to the blueprint. 

### 8. AI

One AI system initially, rather than many agents.

**Health & Research AI**

It should:

* Answer questions
* Search indexed literature
* Summarize documents
* Compare evidence
* Provide citations
* Identify uncertainty
* Use authorized project documents
* Clearly label AI-generated content

The architecture should nevertheless allow specialized agents later.

### 9. Discovery

Search:

* People
* Communities
* Posts
* Questions
* Research projects
* Papers
* Documents

Semantic search should be available for scientific material.

### 10. Administration

Administration is delivered through a **separately built and deployed Admin App** with its own route, navigation, and production access policy. It shares the backend API and domain services with the member platform and is required for MVP launch, not a later add-on.

* Secure administrator sign-in and session controls; MFA-ready design
* Server-enforced least-privilege roles and resource-level authorization
* Platform/service overview and operational health
* User/account lookup, status changes, and safeguarded role management
* Report and moderation queues with reason codes and appeal/reversal handling
* Community and scientific-content review
* Audited privileged actions and access to sensitive administrative functions
* AI/job monitoring and incident/reporting entry points

Administrative access does not imply access to private user or research content. Exceptional access must be narrowly scoped and audited.

---

# 5. MVP navigation

The member application can have:

```text
Home
Discover
Communities
Science
Research
AI
Notifications
Profile
```

The Admin App has a distinct application boundary and privileged sign-in; it is not part of the member navigation.

Research workspace:

```text
Research Project
├── Overview
├── Questions
├── Hypotheses
├── Literature
├── Evidence
├── Documents
├── Team
└── AI
```

We deliberately leave datasets, experiments, protocols, results, knowledge graph exploration, etc. for subsequent iterations.

---

# 6. Critical MVP user journeys

### Journey A — Consumer

```text
Register
   ↓
Select interests
   ↓
Personalized Home
   ↓
Join community
   ↓
Read discussion
   ↓
Ask question
   ↓
Community + AI answers
   ↓
Evidence/citations
   ↓
Follow topic/expert
```

### Journey B — Researcher

```text
Register as researcher
        ↓
Create researcher profile
        ↓
Add expertise/interests
        ↓
Create research project
        ↓
Create research question
        ↓
Upload/search literature
↓
AI analyzes evidence
↓
Add authorized team members
```

### Journey C — "I have an idea"

The MVP supports creating a research project from an evidence-informed question. Matching people to opportunities is a later-phase capability:

```text
Research Question
       ↓
AI analyzes question
       ↓
Related literature
       ↓
Existing evidence
       ↓
Related projects
       ↓
Create Research Project
```

The MVP does not require an automated collaboration engine or researcher-matching system.

---

# 7. MVP AI architecture

Do **not** build autonomous AI scientists yet.

Start with:

```text
User
 ↓
AI API
 ↓
AI Orchestrator
 ├── Authorization
 ├── Query classification
 ├── Retrieval
 ├── PostgreSQL
 ├── Vector search
 ├── Literature search
 └── Project documents
        ↓
     LLM
        ↓
Citation / Evidence validation
        ↓
Response
```

The master architecture specifically calls for an AI abstraction layer independent of a single model provider, with RAG, tools, embeddings and authorized context. AI features ship in Phase 1 only when they satisfy quality, privacy, citation, and permission requirements; they must never bypass authorization.

---

# 8. MVP database

The initial PostgreSQL database should contain roughly these groups.

### Identity

```text
users
profiles
roles
user_roles
```

### Social

```text
follows
posts
post_media
comments
reactions
bookmarks
topics
post_topics
```

### Communities

```text
communities
community_members
community_topics
```

### Research

```text
researcher_profiles
research_projects
research_project_members
research_questions
hypotheses
```

### Scientific

```text
documents
papers
authors
document_authors
evidence
citations
```

### AI

```text
ai_conversations
ai_messages
ai_sources
ai_runs
```

### Security/governance

```text
permissions
consents
reports
audit_logs
```

This gives us a clean foundation for later expansion.

---

# 9. What we explicitly DON'T build in MVP

This is extremely important.

### Not yet:

* Full biomedical knowledge graph
* Genome database
* Genomic user data
* Advanced bioinformatics
* Experimental laboratory management
* Automated experiments
* AI autonomous scientists
* Advanced research agents
* Institutional workspaces
* Funding marketplace
* Research marketplace
* Automated researcher matching or collaboration recommendations
* Events, challenges, and research-opportunity listings
* Full recommendation ML
* Complex microservice architecture
* Kubernetes
* Custom foundation model
* Medical diagnosis
* Clinical decision support

The blueprint itself warns against scope explosion and recommends introducing these capabilities progressively. 

---

# 10. MVP technical stack

I recommend keeping the first implementation relatively simple:

```text
Frontend
Next.js
React
TypeScript
Tailwind

Backend
Python
FastAPI
SQLAlchemy
Alembic

Database
PostgreSQL
pgvector

Cache / Jobs
Redis

Search
OpenSearch

Storage
S3-compatible object storage

AI
LLM provider abstraction
Embeddings
RAG
Tool calling

Auth
OAuth/OIDC-ready
JWT/session architecture

Infrastructure
Docker
Docker Compose initially

Testing
Pytest
Vitest
Playwright

CI/CD
GitHub Actions

Observability
Structured logs
Metrics
Tracing
Error monitoring
```

This stays consistent with the architecture in the blueprint while avoiding premature infrastructure complexity. 

---

# 11. MVP repository

The project should be structured so that Round 2 can extend it without rewriting the foundation:

```text
healthspan-network/
│
├── apps/
│   ├── web/
│   ├── admin/
│   └── api/
│
├── packages/
│   ├── ui/
│   ├── types/
│   └── config/
│
├── services/
│   ├── ai/
│   ├── search/
│   └── ingestion/
│
├── database/
│   ├── migrations/
│   └── seeds/
│
├── infrastructure/
│   ├── docker/
│   ├── nginx/
│   └── monitoring/
│
├── tests/
│   ├── integration/
│   ├── e2e/
│   └── fixtures/
│
├── docs/
│
├── docker-compose.yml
├── .env.example
├── Makefile
└── README.md
```

This is also where I would correct the weakness from the earlier MVP you mentioned: **the MVP should be a real extensible software repository, not merely a document describing an MVP.**

---

# 12. Phase 1 delivery sequence

The roadmap phases define product scope; these workstreams are an implementation sequence within Phase 1, not additional roadmap phases:

1. **Foundation:** repository, local/deployment workflow, data model, migrations, CI, identity, authorization, and audit events.
2. **Member platform:** profiles, starter communities, posts, questions, discussion, reporting, and discovery.
3. **Research foundation:** projects, research questions, team membership and permissions, literature/evidence records, citations, and provenance.
4. **Essential Admin App:** separate application boundary, privileged authentication and roles, user/community management, moderation and scientific-review queues, operational visibility, and audited actions. It must be ready before public MVP launch.
5. **Evidence-grounded AI and launch readiness:** permission-aware retrieval and citations where quality gates pass; security/privacy acceptance checks, observability, backup/recovery, and operational readiness.

Workstreams can overlap where dependencies allow. The Admin App and member platform launch together.

---

# 13. MVP acceptance criteria

The MVP is successful when a test user can:

**Consumer**

> Register → select interests → join a community → follow someone → publish a post → ask a question → discuss it → ask AI → receive cited evidence.

**Researcher**

> Register → create researcher profile → create project → create research question → add/search literature → review evidence → use project AI where enabled → inspect sources → add authorized team members.

**Admin**

> Sign in to the separate Admin App → review platform health and queues → manage accounts and communities within assigned role → review reports and scientific content → inspect permitted AI/job operational status → inspect audit records.

And critically:

> **The AI cannot retrieve information that the requesting user is not authorized to access.**

That permission boundary should be a non-negotiable MVP requirement.

The Admin App must enforce server-side authorization, least privilege, reason codes for sensitive actions, and audit events. It must not expose private health or research data by default. Access-boundary tests must cover user, team, project, and administrative roles.

---

# 14. The MVP boundary

So the first real product is **not**:

> "A complete AI scientific research platform."

It is:

> **A healthspan-focused social and research network with evidence-grounded AI and the architectural foundation for a much larger scientific platform.**

That is small enough to build, but large enough to test the core network loop described in the blueprint:

**Question → Discussion → Evidence → Knowledge → Collaboration → Research.** 

Implementation details, API contracts, data model, security requirements, and test strategy are specified in the linked MVP v2 engineering specification. Keep both specifications aligned with Phase 1 of the roadmap; move deferred capabilities into their corresponding later phases rather than treating them as launch requirements.
