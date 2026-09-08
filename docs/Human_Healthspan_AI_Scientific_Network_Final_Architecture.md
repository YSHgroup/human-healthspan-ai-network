---
date: September 2026
subtitle: Architecture Specification v1.0
title: Human Healthspan AI Scientific Network --- Final Implementation
  Architecture
---

# 1. Executive Summary

This document defines the **final implementation architecture** for the
Human Healthspan AI Scientific Network, synthesized from:

-   `Human_Healthspan_AI_Scientific_Network_Blueprint(1).docx`
-   `Final Architecture.md`
-   the architectural recommendations made from comparing those
    documents.

The platform is not designed as merely a longevity app, health tracker,
social network, or AI chatbot. It is a **global AI-powered social and
scientific network** connecting people, researchers, knowledge,
evidence, data, ideas and technology to improve human healthspan and
accelerate responsible scientific innovation.

The architecture therefore has two levels:

1.  **Product architecture:** the Question → Evidence → Knowledge →
    Hypothesis → Collaboration → Research → Validation loop.
2.  **Software architecture:** a modular, secure, evidence-aware
    platform that can start as a modular monolith and progressively
    evolve into distributed services.

The central implementation principle is:

> **Global architecture from day one; narrow product scope at launch;
> simple infrastructure initially; extensible domain/data models;
> evidence-first AI; governance and privacy built into the foundation.**

------------------------------------------------------------------------

# 2. Product Mission and Architectural Principles

## 2.1 Mission

Improve human healthspan, human capability and wellbeing while
accelerating responsible innovation in medicine, biotechnology, genome
engineering, bioengineering and AI.

The platform must not be positioned as:

-   an autonomous doctor;
-   a replacement for medical professionals;
-   an unsupported immortality service;
-   an AI system that makes scientific judgments without human
    responsibility.

The system must clearly distinguish:

-   personal experience;
-   medical information;
-   scientific evidence;
-   hypothesis;
-   speculation;
-   AI-generated hypotheses.

## 2.2 Core Product Loop

The product is organized around:

``` text
QUESTION
   ↓
DISCUSSION
   ↓
EVIDENCE
   ↓
KNOWLEDGE
   ↓
HYPOTHESIS
   ↓
COLLABORATION
   ↓
RESEARCH
   ↓
EXPERIMENT
   ↓
RESULT
   ↓
VALIDATION
   ↓
NEW KNOWLEDGE
   ↓
AI IMPROVEMENT
   ↓
BETTER QUESTIONS
   └──────────────────────→
```

This loop is more important than any individual technology choice.

## 2.3 Architectural Principles

1.  **Domain-first architecture**
2.  **Modular monolith before microservices**
3.  **PostgreSQL as the transactional source of truth**
4.  **Scientific knowledge separated from raw documents**
5.  **Research Question as a first-class domain object**
6.  **Claim/Evidence as a first-class scientific model**
7.  **Permission-aware AI**
8.  **Evidence-grounded responses with provenance**
9.  **Granular consent and data isolation**
10. **Human scientific judgment remains authoritative**
11. **Scientific quality affects discovery and ranking**
12. **Event-driven background processing**
13. **Managed infrastructure before operational complexity**
14. **Every major subsystem designed for later horizontal scaling**
15. **Build the complete foundation, but activate capabilities
    progressively**

------------------------------------------------------------------------

# 3. Target Product Domains

The backend is organized into bounded domains even while initially
deployed as one application.

``` text
Identity
Users
Profiles
Social
Content
Questions
Communities
Messaging
Events
Research
Research Questions
Hypotheses
Literature
Evidence
Claims
Datasets
Experiments
Results
Knowledge
Search
AI
Collaboration
Recommendations
Moderation
Governance
Consent
Notifications
Analytics
Administration
```

The most important conceptual relationship is:

``` text
PERSON
  │
  ├── participates in SOCIAL
  │
  └── creates/joins RESEARCH
                │
                ▼
        RESEARCH QUESTION
                │
        ┌───────┼────────┐
        ▼       ▼        ▼
    Discussion Evidence Literature
        │       │        │
        └───────┼────────┘
                ▼
           KNOWLEDGE
                │
                ▼
            HYPOTHESIS
                │
                ▼
          COLLABORATION
                │
                ▼
             PROJECT
                │
                ▼
           EXPERIMENT
                │
                ▼
             RESULT
                │
                ▼
           VALIDATION
                │
                ▼
         NEW KNOWLEDGE
```

------------------------------------------------------------------------

# 4. High-Level System Architecture

``` text
                         ┌──────────────────────────────┐
                         │          USERS                │
                         │ Consumers / Researchers /     │
                         │ Experts / Organizations       │
                         └──────────────┬───────────────┘
                                        │
                                        ▼
                         ┌──────────────────────────────┐
                         │ Web / Mobile / Future APIs   │
                         │ Next.js + React + TypeScript │
                         └──────────────┬───────────────┘
                                        │
                                        ▼
                         ┌──────────────────────────────┐
                         │ Edge Security                │
                         │ CDN / WAF / Rate Limiting    │
                         └──────────────┬───────────────┘
                                        │
                                        ▼
                ┌─────────────────────────────────────────────┐
                │              FASTAPI APPLICATION             │
                │             MODULAR MONOLITH                 │
                │                                             │
                │ Identity | Social | Questions | Research   │
                │ Evidence | Knowledge | Search | AI         │
                │ Collaboration | Governance | Admin         │
                └───────┬────────────┬────────────┬───────────┘
                        │            │            │
          ┌─────────────┘            │            └──────────────┐
          ▼                          ▼                           ▼
 ┌────────────────┐         ┌────────────────┐          ┌────────────────┐
 │ PostgreSQL     │         │ Redis          │          │ Object Storage │
 │ Source of truth│         │ Cache / Queue  │          │ Files / Data   │
 │ + pgvector     │         │ Events / Jobs  │          │ / Originals    │
 └───────┬────────┘         └───────┬────────┘          └───────┬────────┘
         │                          │                           │
         │                          ▼                           ▼
         │                  ┌────────────────┐         ┌────────────────┐
         │                  │ Worker Layer   │         │ Ingestion      │
         │                  │ Async Jobs     │         │ Pipeline       │
         │                  └───────┬────────┘         └───────┬────────┘
         │                          │                           │
         └──────────────┬───────────┴──────────────┬────────────┘
                        ▼                          ▼
               ┌────────────────┐        ┌────────────────────┐
               │ OpenSearch     │        │ Scientific         │
               │ Hybrid Search  │        │ Knowledge Layer    │
               └────────────────┘        └─────────┬──────────┘
                                                    │
                                           ┌────────┴─────────┐
                                           ▼                  ▼
                                      Knowledge Graph     Claim/Evidence
                                      (Neo4j later)        Model
                                           │                  │
                                           └────────┬─────────┘
                                                    ▼
                                          ┌───────────────────┐
                                          │ AI Gateway        │
                                          │ RAG + Tools       │
                                          │ Agent Registry    │
                                          └─────────┬─────────┘
                                                    │
                                                    ▼
                                          External AI Models
```

------------------------------------------------------------------------

# 5. Technology Stack

  -----------------------------------------------------------------------
  Layer                   Initial Technology      Long-Term Direction
  ----------------------- ----------------------- -----------------------
  Web                     Next.js + React +       Same
                          TypeScript              

  API                     FastAPI + Python        Modular services where
                                                  justified

  Database                PostgreSQL              PostgreSQL cluster/read
                                                  replicas/partitioning

  Vector                  pgvector                Dedicated vector
                                                  infrastructure only if
                                                  needed

  Cache                   Redis                   Redis cluster if
                                                  required

  Queue                   Redis-backed workers    Dedicated messaging
                          initially               platform if scale
                                                  requires

  Search                  OpenSearch              Distributed OpenSearch

  Object storage          S3-compatible storage   Cloud object storage

  Graph                   Derived graph; Neo4j    Neo4j or equivalent
                          later                   graph platform

  AI                      AI Gateway + external   Multi-model routing /
                          LLM APIs                private models where
                                                  justified

  Containers              Docker                  Managed
                                                  containers/Kubernetes
                                                  when necessary

  CI/CD                   GitHub Actions or       Same + progressive
                          equivalent              deployment

  Observability           Centralized             Full production
                          logs/metrics/traces     observability

  IaC                     Terraform               Same
  -----------------------------------------------------------------------

### Important constraint

Do not introduce Kubernetes, a large microservice fleet, a separate
vector database, or a graph database as mandatory MVP infrastructure
unless actual scale or product requirements justify it.

------------------------------------------------------------------------

# 6. Modular Monolith Architecture

The first production-capable system should be one deployable backend
with strict internal module boundaries.

``` text
apps/api/
├── identity/
├── users/
├── profiles/
├── social/
├── content/
├── questions/
├── communities/
├── messaging/
├── events/
├── research/
├── research_questions/
├── hypotheses/
├── literature/
├── evidence/
├── claims/
├── datasets/
├── experiments/
├── results/
├── knowledge/
├── search/
├── ai/
├── collaboration/
├── recommendations/
├── moderation/
├── governance/
├── consent/
├── notifications/
├── analytics/
└── administration/
```

Each domain should own:

-   domain entities;
-   business rules;
-   repository interfaces;
-   application services;
-   authorization policies;
-   API handlers;
-   domain events;
-   tests.

Cross-domain communication should use explicit interfaces and domain
events rather than uncontrolled direct database coupling.

------------------------------------------------------------------------

# 7. Repository Architecture

``` text
healthspan-platform/
│
├── apps/
│   ├── web/
│   ├── api/
│   ├── worker/
│   └── admin/
│
├── packages/
│   ├── ui/
│   ├── types/
│   ├── api-client/
│   ├── auth/
│   ├── config/
│   └── validation/
│
├── services/
│   ├── ai/
│   ├── search/
│   ├── knowledge/
│   ├── recommendations/
│   └── ingestion/
│
├── infrastructure/
│   ├── docker/
│   ├── terraform/
│   ├── environments/
│   └── monitoring/
│
├── database/
│   ├── migrations/
│   ├── seeds/
│   └── schemas/
│
├── docs/
│   ├── architecture/
│   ├── api/
│   ├── security/
│   ├── ai/
│   ├── scientific-governance/
│   └── product/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   ├── security/
│   └── ai-evaluation/
│
└── README.md
```

The repository is structured for future service extraction without
forcing service deployment prematurely.

------------------------------------------------------------------------

# 8. Core Domain Model

The initial relational model should be designed around the product's
long-term scientific workflow.

## 8.1 Identity and Social

``` text
users
profiles
organizations
organization_members
follows
posts
comments
questions
question_answers
communities
community_members
messages
conversations
events
notifications
```

## 8.2 Research

``` text
research_questions
research_projects
project_members
hypotheses
experiments
experiment_protocols
results
research_artifacts
```

## 8.3 Scientific Knowledge

``` text
scientific_entities
entity_relationships
claims
claim_evidence
evidence
publications
publication_authors
datasets
biomarkers
genes
proteins
pathways
diseases
interventions
methods
```

## 8.4 Governance

``` text
consents
access_policies
audit_logs
provenance_records
content_reviews
scientific_reviews
ip_records
data_processing_records
```

------------------------------------------------------------------------

# 9. Research Question as a First-Class Entity

This is a key improvement over the original architecture.

A `ResearchQuestion` should connect the social layer and scientific
layer.

``` text
ResearchQuestion
├── id
├── title
├── description
├── author
├── status
├── domain
├── tags
├── visibility
├── scientific_scope
├── created_at
├── updated_at
└── provenance
```

Relationships:

``` text
ResearchQuestion
 ├── discussions
 ├── claims
 ├── evidence
 ├── publications
 ├── hypotheses
 ├── researchers
 ├── datasets
 ├── projects
 ├── experiments
 └── knowledge entities
```

This creates the platform's central bridge:

``` text
Social Question
      ↓
Research Question
      ↓
Evidence
      ↓
Knowledge
      ↓
Research Opportunity
      ↓
Collaboration
```

------------------------------------------------------------------------

# 10. Scientific Knowledge Layer

The system must not treat raw documents as the knowledge system.

The target architecture is:

``` text
Raw Sources
   ↓
Ingestion
   ↓
Extraction
   ↓
Evidence
   ↓
Claims
   ↓
Scientific Knowledge Layer
   ├── Entities
   ├── Relationships
   ├── Claims
   ├── Evidence
   ├── Provenance
   ├── Confidence
   └── Contradictions
   ↓
Search / Vector / Graph
   ↓
AI
```

The AI consumes governed knowledge and evidence rather than becoming the
authoritative source of knowledge.

------------------------------------------------------------------------

# 11. Claim and Evidence Architecture

A `Claim` is a first-class scientific object.

``` text
CLAIM
├── id
├── statement
├── claim_type
├── created_by
├── generated_by
├── confidence
├── status
├── provenance
└── created_at
```

Relationships:

``` text
CLAIM
 ├── supported_by → EVIDENCE
 ├── contradicted_by → EVIDENCE
 ├── derived_from → PUBLICATION
 ├── relates_to → RESEARCH_QUESTION
 ├── relates_to → KNOWLEDGE_ENTITY
 ├── generated_by → HUMAN / AI
 └── reviewed_by → SCIENTIFIC_REVIEWER
```

This model enables the AI to reason over:

-   supporting evidence;
-   contradictory evidence;
-   source quality;
-   publication context;
-   confidence;
-   provenance;
-   scientific review status.

------------------------------------------------------------------------

# 12. Evidence Classification

Every scientific object or claim should carry explicit evidence
classification.

Recommended levels:

``` text
PEER_REVIEWED
CLINICAL
OBSERVATIONAL
ANIMAL
CELLULAR
COMPUTATIONAL
PREPRINT
EXPERT_OPINION
COMMUNITY_REPORT
AI_HYPOTHESIS
SPECULATION
```

Evidence metadata:

``` text
Evidence
├── evidence_type
├── source
├── publication
├── authors
├── publication_date
├── population
├── methodology
├── confidence
├── limitations
├── provenance
└── reviewed_by
```

This is a core trust mechanism.

A community report should never automatically be presented as equivalent
to clinical evidence.

------------------------------------------------------------------------

# 13. Knowledge Graph Architecture

The knowledge graph should be a **derived scientific representation**,
not the primary transactional database.

Initial source of truth:

``` text
PostgreSQL
```

Derived graph:

``` text
PostgreSQL
   ↓
Knowledge extraction
   ↓
Validated relationships
   ↓
Graph projection
   ↓
Neo4j later
```

Potential graph entities:

``` text
Person
Organization
Publication
ResearchQuestion
Claim
Evidence
Gene
Protein
Pathway
Disease
Biomarker
Intervention
Dataset
Experiment
Hypothesis
ResearchProject
```

Potential relationships:

``` text
AUTHORED
WORKS_AT
STUDIES
MENTIONS
SUPPORTS
CONTRADICTS
RELATES_TO
TARGETS
ASSOCIATED_WITH
MEASURES
USES_DATASET
PART_OF
COLLABORATES_WITH
```

The graph should only contain validated/qualified relationships where
practical.

------------------------------------------------------------------------

# 14. Scientific Data Ingestion Pipeline

``` text
Upload / External Source
        ↓
Security Scan
        ↓
File Validation
        ↓
Metadata Extraction
        ↓
Text / Table Extraction
        ↓
Scientific Entity Extraction
        ↓
Chunking
        ↓
Embedding
        ↓
Evidence / Claim Extraction
        ↓
PostgreSQL Metadata
        ↓
Object Storage Original
        ↓
OpenSearch Index
        ↓
pgvector Index
        ↓
Knowledge Graph Candidate Relationships
        ↓
Validation
```

External scientific sources may include:

-   publications;
-   preprints;
-   structured scientific datasets;
-   approved public biomedical resources;
-   user-provided research documents.

Source licensing and provenance must be recorded.

------------------------------------------------------------------------

# 15. Search Architecture

Use hybrid retrieval:

``` text
User Query
   │
   ├── Keyword Search → OpenSearch
   │
   ├── Semantic Search → pgvector
   │
   ├── Knowledge Lookup → Knowledge Layer
   │
   └── Graph Traversal → Graph DB later
             │
             ▼
        Candidate Results
             ↓
        Re-ranking
             ↓
        Permission Filtering
             ↓
        Evidence/Quality Ranking
             ↓
        Final Context
```

Ranking should consider:

-   relevance;
-   evidence quality;
-   source authority;
-   recency where appropriate;
-   scientific relationship;
-   user context;
-   expertise;
-   permissions;
-   provenance.

Engagement alone must not determine scientific ranking.

------------------------------------------------------------------------

# 16. AI Architecture

The AI platform is composed of:

``` text
AI Gateway
   │
   ├── Model Router
   ├── Prompt / Policy Layer
   ├── Retrieval Orchestrator
   ├── Tool Registry
   ├── Agent Registry
   ├── Safety Layer
   ├── Citation Engine
   ├── Provenance Engine
   ├── Cost Controls
   └── Evaluation
```

AI should initially use frontier/external models with RAG and tools
rather than training a foundation model.

------------------------------------------------------------------------

# 17. Permission-Aware AI

This is non-negotiable.

Correct flow:

``` text
User
 ↓
Authentication
 ↓
Authorization
 ↓
Determine accessible resources
 ↓
Retrieve only authorized data
 ↓
RAG
 ↓
LLM
 ↓
Citation / Provenance
 ↓
Response
```

Never:

``` text
User → LLM → Entire Database
```

The AI must never have broader access than the requesting user/team.

------------------------------------------------------------------------

# 18. AI Agent Registry

Agents should be registered rather than hard-coded.

Initial future-capable registry:

``` text
Literature Agent
Evidence Agent
Aging Biology Agent
Genetics Agent
Clinical Research Agent
Bioinformatics Agent
Data Analysis Agent
Research Planning Agent
Scientific Review Agent
Knowledge Graph Agent
```

Each agent should define:

``` text
Agent
├── system instructions
├── allowed models
├── allowed tools
├── allowed data sources
├── permission requirements
├── safety policy
├── output schema
└── evaluation suite
```

Only the agents needed for the current phase should be activated.

------------------------------------------------------------------------

# 19. AI Research Workflow

The research assistant should evolve toward:

``` text
Research Question
       ↓
AI Interpretation
       ↓
Literature Search
       ↓
Evidence Retrieval
       ↓
Claim Comparison
       ↓
Contradiction Detection
       ↓
Knowledge Gap Detection
       ↓
Related Researchers
       ↓
Expertise Matching
       ↓
Datasets
       ↓
Existing Projects
       ↓
Organizations
       ↓
Potential Collaborators
       ↓
Research Workspace
```

AI output should always preserve uncertainty and source provenance.

------------------------------------------------------------------------

# 20. Collaboration Engine

The long-term differentiation is the conversion of ideas into research
networks.

``` text
Idea
 ↓
Question
 ↓
Evidence
 ↓
Knowledge Gaps
 ↓
Relevant Experts
 ↓
Researchers
 ↓
Datasets
 ↓
Projects
 ↓
Organizations
 ↓
Collaborators
 ↓
Research Workspace
```

Matching signals:

``` text
Expertise
+
Research history
+
Scientific topic relationships
+
Projects
+
Datasets
+
Community participation
+
Research question relevance
+
Evidence quality
```

------------------------------------------------------------------------

# 21. Recommendation Architecture

Do not build a simple:

``` text
People who liked X also liked Y
```

Instead:

``` text
User interests
+
Behavior
+
Topic relationships
+
Scientific relevance
+
Expertise
+
Research relationships
+
Community participation
+
Evidence quality
```

Outputs:

``` text
People
Experts
Communities
Posts
Papers
Research Projects
Datasets
Events
Research Opportunities
```

Scientific quality should be a ranking signal, not merely engagement.

------------------------------------------------------------------------

# 22. Privacy and Data Architecture

Health and genomic information must be separated from ordinary social
information.

``` text
                     USER
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
     Social Data            Sensitive Data
                                  │
                       ┌──────────┼──────────┐
                       ▼          ▼          ▼
                     Health     Genomic    Research
                       │          │          │
                       └──────────┼──────────┘
                                  ▼
                           Consent Engine
                                  │
                                  ▼
                            Access Policies
```

Visibility and processing permissions should support:

``` text
Private
Team
Selected People
Community
Public
AI Accessible
Research Accessible
Model-Improvement Eligible
```

Model-improvement eligibility must be explicit and opt-in where
applicable.

------------------------------------------------------------------------

# 23. Authorization Model

Use layered authorization:

``` text
Authentication
    ↓
Identity
    ↓
Role
    ↓
Resource
    ↓
Relationship
    ↓
Purpose
    ↓
Consent
    ↓
Policy Decision
```

Use:

-   OAuth/OIDC;
-   MFA;
-   RBAC;
-   ABAC for sensitive research;
-   resource-level permissions;
-   team/project permissions;
-   audit logs;
-   explicit consent;
-   least privilege.

------------------------------------------------------------------------

# 24. Security Architecture

``` text
Internet
   ↓
CDN / WAF
   ↓
API Gateway / Edge
   ↓
Authentication
   ↓
Authorization
   ↓
Application
   ↓
Database Authorization
   ↓
Encrypted Storage
```

Security capabilities:

-   TLS;
-   encryption at rest;
-   secure secret management;
-   rate limiting;
-   session controls;
-   MFA;
-   audit logging;
-   anomaly detection;
-   secure file scanning;
-   data isolation;
-   backup/recovery;
-   least privilege;
-   dependency and container scanning.

Security must be tested continuously rather than added at the end.

------------------------------------------------------------------------

# 25. Scientific Governance

Scientific governance is a first-class subsystem.

It should cover:

-   evidence standards;
-   claim review;
-   source provenance;
-   conflict disclosure;
-   scientific reviewer workflows;
-   research integrity;
-   dataset provenance;
-   publication provenance;
-   AI scientific evaluation;
-   research ethics;
-   content classification;
-   correction and retraction workflows;
-   audit trails.

Human experts remain responsible for scientific judgment.

AI may:

-   summarize;
-   compare;
-   organize;
-   discover relationships;
-   identify potential gaps;
-   generate hypotheses.

AI should not silently convert hypotheses into established facts.

------------------------------------------------------------------------

# 26. Moderation Architecture

Moderation should operate at several levels:

``` text
Content Moderation
Scientific Moderation
Medical-Risk Moderation
Privacy Moderation
IP / Copyright Moderation
Research-Integrity Moderation
AI Output Safety
```

Signals may include:

-   automated classifiers;
-   evidence quality;
-   user reports;
-   expert review;
-   source provenance;
-   suspicious behavior;
-   repeated misinformation;
-   scientific contradiction.

High-risk decisions should support human review.

------------------------------------------------------------------------

# 27. Event-Driven Architecture

Operations that do not need to block user requests should be
asynchronous.

``` text
Application
    ↓
Domain Event
    ↓
Redis Queue
    ↓
Worker
    ├── Notifications
    ├── Search Indexing
    ├── Embeddings
    ├── Recommendations
    ├── Analytics
    ├── Moderation
    ├── Knowledge Graph Updates
    └── AI Jobs
```

Example events:

``` text
UserCreated
PostCreated
CommentCreated
QuestionCreated
ResearchQuestionCreated
ResearchProjectCreated
PaperImported
DatasetUploaded
ExperimentCompleted
ResultSubmitted
AICompleted
EvidenceUpdated
KnowledgeEntityUpdated
ModerationRequired
NotificationCreated
```

------------------------------------------------------------------------

# 28. MVP Architecture

The MVP must not contain the entire future platform.

Recommended launch architecture:

``` text
Next.js
   ↓
FastAPI
   ├── PostgreSQL
   ├── Redis
   ├── Object Storage
   ├── OpenSearch
   └── pgvector
          ↓
      AI Gateway
          ↓
       RAG + LLM
```

## MVP Product Scope

### Social

-   accounts;
-   profiles;
-   follow;
-   posts;
-   comments;
-   questions;
-   communities;
-   basic messaging.

### Scientific

-   researcher profiles;
-   research questions;
-   research projects;
-   literature/document storage;
-   evidence classification;
-   basic claims and provenance.

### AI

-   evidence-grounded Q&A;
-   document Q&A;
-   literature search;
-   citations;
-   project AI assistant.

### Discovery

-   people;
-   communities;
-   researchers;
-   projects;
-   papers.

### MVP central journey

``` text
User asks an important health/science question
             ↓
Community discussion
             ↓
Evidence and literature
             ↓
AI evidence-grounded synthesis
             ↓
Relevant researchers
             ↓
Research opportunity
             ↓
Create research workspace
```

This is the narrowest product that still demonstrates the full strategic
thesis.

------------------------------------------------------------------------

# 29. What Must NOT Be Built in the MVP

Do not make these launch dependencies:

-   full Neo4j deployment;
-   large autonomous agent ecosystem;
-   advanced bioinformatics platform;
-   institutional private clouds;
-   funding marketplace;
-   research marketplace;
-   complex blockchain/token infrastructure;
-   Kubernetes without operational need;
-   dozens of independent microservices;
-   custom foundation model training;
-   highly sophisticated recommendation ML;
-   full clinical decision-support functionality.

The architecture should support them later without requiring them now.

------------------------------------------------------------------------

# 30. Evolution Roadmap

## Phase 1 --- Social Foundation

``` text
Social Network
```

Profiles, content, questions, communities, follow, basic messaging and
discovery.

## Phase 2 --- Research

``` text
Social
 +
Research Workspaces
```

Research questions, projects, literature, evidence, hypotheses, datasets
and experiments.

## Phase 3 --- AI

``` text
Social
 +
Research
 +
Evidence-Grounded RAG AI
```

AI Q&A, document analysis, literature synthesis, citations and project
assistance.

## Phase 4 --- Knowledge

``` text
Social
 +
Research
 +
AI
 +
Scientific Knowledge Graph
```

Entities, relationships, claims, evidence, knowledge discovery and graph
reasoning.

## Phase 5 --- Collaboration

``` text
Everything
 +
Research Matching
 +
Experts
 +
Datasets
 +
Challenges
```

Researcher matching, collaboration discovery and research opportunity
workflows.

## Phase 6 --- Scientific AI

``` text
Everything
 +
Agents
 +
Data Analysis
 +
Bioinformatics
 +
Research Discovery
```

Advanced research automation with strict permissions, evaluation and
governance.

## Phase 7 --- Institutions

``` text
Everything
 +
Private Institutional Environments
 +
Enterprise Governance
 +
Institutional AI
 +
Research APIs
```

Universities, laboratories, biotech companies and other organizations.

## Phase 8 --- Global Ecosystem

``` text
People
Researchers
Universities
Labs
Biotech
Healthcare
AI
Data
Funding
Research Marketplace
```

The platform becomes a global human-health innovation ecosystem.

------------------------------------------------------------------------

# 31. Infrastructure Strategy

## Development

``` text
Docker Compose
PostgreSQL
Redis
OpenSearch
Local Object Storage
FastAPI
Next.js
AI Gateway
```

## Staging

``` text
Managed PostgreSQL
Managed Redis
Managed OpenSearch
Cloud Object Storage
Container Deployment
CI/CD
Observability
```

## Production

``` text
CDN
WAF
Load Balancer
API Containers
Worker Containers
PostgreSQL
Redis
OpenSearch
Object Storage
pgvector
Graph DB when justified
Observability
Backup
Disaster Recovery
```

Kubernetes should be introduced only when operational scale actually
requires it.

------------------------------------------------------------------------

# 32. Scaling Strategy

Scale in this order:

``` text
1. Optimize application code
2. Add caching
3. Add asynchronous workers
4. Add database indexes
5. Add PostgreSQL read replicas
6. Partition high-volume tables
7. Scale OpenSearch
8. Separate heavy AI/data workloads
9. Extract high-load domains into services
10. Introduce Kubernetes only if justified
```

The architecture should scale by extraction rather than by premature
distribution.

------------------------------------------------------------------------

# 33. Service Extraction Criteria

A module should become an independent service only when one or more are
true:

-   independent scaling requirement;
-   independent deployment cadence;
-   different runtime/resource profile;
-   clear domain boundary;
-   operational isolation requirement;
-   security isolation requirement;
-   team ownership requires separation.

Potential future services:

``` text
AI Service
Search Service
Ingestion Service
Knowledge Service
Recommendation Service
Notification Service
Analytics Service
```

------------------------------------------------------------------------

# 34. API Architecture

The API should be domain-oriented.

Example:

``` text
/api/v1/auth
/api/v1/users
/api/v1/profiles
/api/v1/posts
/api/v1/questions
/api/v1/communities
/api/v1/messages
/api/v1/research/questions
/api/v1/research/projects
/api/v1/research/hypotheses
/api/v1/literature
/api/v1/evidence
/api/v1/claims
/api/v1/datasets
/api/v1/experiments
/api/v1/results
/api/v1/knowledge
/api/v1/search
/api/v1/ai
/api/v1/collaboration
/api/v1/recommendations
/api/v1/events
/api/v1/governance
/api/v1/admin
```

API requirements:

-   versioning;
-   authentication;
-   authorization;
-   schema validation;
-   rate limiting;
-   idempotency where required;
-   auditability for sensitive operations;
-   consistent error model;
-   OpenAPI documentation.

------------------------------------------------------------------------

# 35. Frontend Architecture

Recommended:

``` text
Next.js
React
TypeScript
```

Application areas:

``` text
Public
 ├── Home
 ├── Explore
 ├── Questions
 ├── Communities
 ├── Research
 └── Events

Authenticated
 ├── Feed
 ├── Profile
 ├── Messages
 ├── Questions
 ├── Research Workspace
 ├── AI Assistant
 ├── Literature
 ├── Evidence
 └── Discovery

Admin
 ├── Moderation
 ├── Scientific Review
 ├── Governance
 ├── Users
 ├── Content
 └── System Health
```

UX should make evidence status and confidence understandable without
overwhelming ordinary users.

------------------------------------------------------------------------

# 36. Analytics

Analytics should measure both network health and scientific value.

## Product

-   activation;
-   retention;
-   questions created;
-   discussions;
-   follows;
-   community participation;
-   research workspace creation;
-   AI usage.

## Scientific

-   evidence retrieval quality;
-   citation quality;
-   research-question conversion;
-   collaboration formation;
-   knowledge-gap discoveries;
-   research project creation;
-   validation activity.

## AI

-   groundedness;
-   citation correctness;
-   retrieval precision;
-   hallucination rate;
-   user feedback;
-   cost per request;
-   model performance.

Avoid optimizing solely for engagement.

------------------------------------------------------------------------

# 37. Testing Architecture

Testing must go beyond conventional software tests.

## Software

-   unit tests;
-   integration tests;
-   API tests;
-   end-to-end tests;
-   load tests;
-   migration tests.

## Security

-   authorization tests;
-   privilege escalation tests;
-   tenant/project isolation tests;
-   injection testing;
-   file upload security;
-   secret exposure tests.

## AI

-   retrieval evaluation;
-   citation evaluation;
-   groundedness evaluation;
-   hallucination tests;
-   prompt-injection tests;
-   permission-boundary tests;
-   regression suites;
-   adversarial scientific queries.

## Scientific

-   evidence classification tests;
-   provenance tests;
-   claim-support tests;
-   contradiction handling;
-   source attribution;
-   reviewer workflow tests.

------------------------------------------------------------------------

# 38. Deployment Architecture

Use environment separation:

``` text
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

Production should support:

-   automated backups;
-   point-in-time recovery;
-   disaster recovery;
-   health checks;
-   rolling/blue-green deployments where justified;
-   centralized logs;
-   metrics;
-   traces;
-   alerting;
-   incident response.

------------------------------------------------------------------------

# 39. Engineering Team

A serious initial team can be:

``` text
1 × Principal / Staff Architect
2 × Backend Engineers
2 × Frontend Engineers
1 × AI/ML Engineer
1 × Data/Search Engineer
1 × DevOps/SRE
1 × Product/UX Designer
```

Advisory/part-time:

``` text
Biomedical Scientist
Scientific Governance Expert
Security Specialist
Privacy / Legal Specialist
```

As research capabilities become central, scientific expertise should
become part of the product architecture, not merely an external review
function.

------------------------------------------------------------------------

# 40. Key Risks and Mitigations

  -----------------------------------------------------------------------
  Risk                                Architectural Response
  ----------------------------------- -----------------------------------
  Scientific misinformation           Evidence classification +
                                      moderation + review

  AI hallucination                    RAG + citations + provenance +
                                      evaluation

  Unauthorized AI access              Authorization before retrieval

  Sensitive data breach               Encryption + isolation + least
                                      privilege

  IP disputes                         Provenance + ownership metadata +
                                      access controls

  Poor graph quality                  Validation + derived graph
                                      architecture

  Search quality                      Hybrid keyword + semantic search

  High AI cost                        Model routing + caching + quotas

  Database scaling                    Indexing + replicas + partitioning
                                      later

  Search scaling                      OpenSearch scaling later

  Cold start                          Narrow communities and focused MVP

  Regulatory exposure                 Educational positioning initially +
                                      governance

  Recommendation quality              Scientific relevance + quality
                                      signals

  Scope explosion                     Phased roadmap

  Premature infrastructure            Managed services + modular monolith
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 41. Core Non-Negotiable Rules

1.  **Never allow AI to bypass authorization.**
2.  **Never treat AI output as scientific truth by default.**
3.  **Never equate community experience with scientific evidence.**
4.  **Never make Neo4j the transactional source of truth.**
5.  **Never start with a large microservice architecture.**
6.  **Never make Kubernetes an MVP requirement.**
7.  **Never optimize scientific discovery only for engagement.**
8.  **Never mix sensitive health/genomic data with ordinary social data
    without explicit policy controls.**
9.  **Never lose provenance when transforming scientific information.**
10. **Never allow the MVP scope to consume the long-term architecture.**

------------------------------------------------------------------------

# 42. Final Target Architecture

The final implementation model is:

``` text
                    HUMAN HEALTHSPAN NETWORK
                              │
             ┌────────────────┴────────────────┐
             │                                 │
       SOCIAL NETWORK                    SCIENTIFIC NETWORK
             │                                 │
 Profiles / Posts / Questions        Researchers / Projects
 Communities / Messaging             Literature / Evidence
 Events / Discovery                  Claims / Datasets
             │                                 │
             └────────────────┬────────────────┘
                              ▼
                    RESEARCH QUESTION LAYER
                              │
                              ▼
                     SCIENTIFIC KNOWLEDGE
                              │
                ┌─────────────┼──────────────┐
                ▼             ▼              ▼
             Claims        Evidence       Entities
                │             │              │
                └─────────────┼──────────────┘
                              ▼
                     SEARCH / VECTOR / GRAPH
                              │
                              ▼
                         AI PLATFORM
                ┌─────────────┼──────────────┐
                ▼             ▼              ▼
               RAG          Tools          Agents
                │             │              │
                └─────────────┼──────────────┘
                              ▼
                     COLLABORATION ENGINE
                              │
                              ▼
                       RESEARCH WORKSPACE
                              │
                              ▼
                    EXPERIMENTS / RESULTS
                              │
                              ▼
                         VALIDATION
                              │
                              ▼
                       NEW KNOWLEDGE
                              │
                              ▼
                       BETTER QUESTIONS
                              └──────────────→
```

Software foundation:

``` text
Next.js + React + TypeScript
            ↓
FastAPI + Python
            ↓
PostgreSQL
 ├── transactional data
 ├── domain data
 └── pgvector
            +
Redis
            +
S3-compatible Object Storage
            +
OpenSearch
            ↓
AI Gateway
 ├── RAG
 ├── model routing
 ├── tools
 ├── agent registry
 ├── citations
 ├── provenance
 └── evaluation
            ↓
Knowledge Graph later
            ↓
External Scientific Sources
```

------------------------------------------------------------------------

# 43. Implementation Priority

The recommended implementation order is:

``` text
STEP 1
Identity + Profiles + Permissions

STEP 2
Social + Questions + Communities

STEP 3
Research Questions + Research Projects

STEP 4
Literature + Evidence + Claims + Provenance

STEP 5
AI Gateway + RAG + Citations

STEP 6
Research Workspace

STEP 7
Discovery + Researcher Matching

STEP 8
Scientific Knowledge Layer

STEP 9
Knowledge Graph

STEP 10
Advanced Agents + Data Analysis

STEP 11
Institutional Infrastructure

STEP 12
Global Research Ecosystem
```

Do not implement later steps merely because they exist in the
architecture. Implement them when the previous layer has demonstrated
product value and generated the data required by the next layer.

------------------------------------------------------------------------

# 44. Final Architectural Decision

This architecture is the recommended **implementation baseline** for the
Human Healthspan AI Scientific Network.

It preserves the original blueprint's vision while resolving the main
implementation risks:

-   the platform remains a social + scientific network;
-   the research question becomes the connective backbone;
-   scientific knowledge is modeled explicitly;
-   claims and evidence become first-class objects;
-   AI is evidence-grounded and permission-aware;
-   the knowledge graph is derived rather than transactional;
-   privacy, consent, provenance and governance are foundational;
-   the MVP remains narrow enough to build;
-   the long-term architecture remains capable of supporting
    institutions and a global ecosystem;
-   infrastructure complexity is introduced only when justified by
    scale.

The strategic rule is therefore:

> **Build a narrow product on a complete architectural foundation.**

The MVP should prove the core loop:

``` text
QUESTION
→ EVIDENCE
→ KNOWLEDGE
→ AI UNDERSTANDING
→ RESEARCHER DISCOVERY
→ COLLABORATION
→ RESEARCH
```

while the underlying architecture remains capable of evolving into the
full global human-health innovation network.

------------------------------------------------------------------------

# Appendix A --- Architecture-to-Blueprint Alignment

  -----------------------------------------------------------------------
  Blueprint Requirement               Final Architecture
  ----------------------------------- -----------------------------------
  Social/professional network         Social + profile + community +
                                      messaging domains

  Consumer health/capability          Topic/content/question/community
                                      model

  Scientific network                  Researchers + organizations +
                                      research domains

  Research workspaces                 Research projects/workspaces

  Knowledge graph                     Scientific knowledge layer +
                                      derived graph

  AI Q&A                              AI Gateway + RAG

  Literature review                   Literature/search/retrieval
                                      pipeline

  Evidence comparison                 Claim/Evidence model

  Research gaps                       Knowledge-gap workflow

  Collaboration matching              Collaboration engine

  Privacy                             Data separation + consent + policy
                                      engine

  Provenance                          Provenance records across
                                      scientific objects

  Scientific integrity                Governance + review + audit

  Evidence classification             Explicit evidence taxonomy

  Network effects                     Social + scientific discovery +
                                      recommendations

  Phased development                  8-phase evolution architecture

  Long-term global ecosystem          Institution + marketplace + global
                                      ecosystem phases
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# Appendix B --- Architectural Quality Target

The architecture should be evaluated continuously against:

``` text
Product alignment        ██████████
Scientific integrity     ██████████
AI grounding             ██████████
Privacy/security         ██████████
Scalability              █████████░
MVP practicality         █████████░
Extensibility            ██████████
Operational simplicity   █████████░
```

The target is not maximum technical complexity.

The target is **maximum long-term capability with minimum unnecessary
early complexity**.
