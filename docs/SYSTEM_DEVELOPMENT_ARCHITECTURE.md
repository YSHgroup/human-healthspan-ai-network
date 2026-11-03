# Human Healthspan Scientific AI Network
# System Development Architecture

**Document:** System Development Architecture  
**Version:** 1.0  
**Status:** Target Architecture and Development Specification  
**Project:** Human Healthspan Scientific AI Network  
**Architecture Strategy:** Multi-application platform, modular backend, independent AI systems  
**Migration Strategy:** Incremental evolution and preservation of the existing MVP

---

# 1. Executive Summary

The Human Healthspan Scientific AI Network is designed as a comprehensive digital ecosystem for human healthspan, scientific research, professional collaboration, personal health management and AI-assisted scientific discovery.

The platform will consist of:

1. Three independent user-facing frontend applications.
2. One independent administration application.
3. A shared backend API platform.
4. A dedicated AI system architecture.
5. Shared databases and infrastructure.
6. Common development packages and tools.

The three user-facing applications are:

- Social Portal.
- Personal Portal.
- Researcher Portal.

The administration application is separate from the user platform.

The AI system is a major architectural component and will eventually support three distinct AI environments:

- General Platform AI.
- Private AI Scientist.
- Organization-Specialized AI.

## 1.1 Final Technology Decisions

| System | Technology |
|---|---|
| Social Portal | Next.js + TypeScript |
| Personal Portal | Next.js + TypeScript |
| Researcher Portal | Next.js + TypeScript |
| Admin Application | React + Vite + TypeScript |
| Backend API | Python + FastAPI |
| Primary database | PostgreSQL |
| AI services | Python-based AI services |
| AI model integration | Model gateway and provider adapters |
| Search | Dedicated search infrastructure |
| Vector retrieval | Vector database or PostgreSQL vector extension |
| File storage | S3-compatible object storage |
| Background processing | Queue and worker architecture |
| Shared frontend packages | TypeScript packages |
| Infrastructure | Docker-based development and deployment |

Astro may be introduced later for a separate public scientific publication, knowledge or documentation website. It is not required for the initial application architecture.

## 1.2 Existing MVP Preservation

The existing MVP is the foundation of this project.

The new architecture must preserve working components wherever possible.

Existing components include:

- Next.js member-facing application.
- Next.js administration application.
- FastAPI backend.
- PostgreSQL database.
- Existing domain models.
- Authentication and authorization foundations.
- Existing social features.
- Existing research features.
- AI gateway and retrieval foundations.
- Audit and security services.
- Existing tests.
- Docker-based development infrastructure.

The architecture defines the target organization of the project. It does not require a complete rewrite.

Existing functionality must be mapped to the new architecture before it is moved, replaced or removed.

---

# 2. Overall System Architecture

The system has four major architectural areas:

1. Frontend applications.
2. Backend API platform.
3. AI platform.
4. Shared infrastructure.

```text
HUMAN HEALTHSPAN SCIENTIFIC AI NETWORK
│
├── FRONTEND APPLICATIONS
│   │
│   ├── USER PLATFORM
│   │   ├── Social Portal
│   │   ├── Personal Portal
│   │   └── Researcher Portal
│   │
│   └── ADMIN APPLICATION
│
├── BACKEND PLATFORM
│   │
│   ├── User API
│   │   ├── Social API
│   │   ├── Personal API
│   │   └── Researcher API
│   │
│   ├── Admin API
│   │
│   ├── Shared Domain Services
│   │
│   └── Backend Infrastructure Services
│
├── AI PLATFORM
│   │
│   ├── AI Gateway
│   ├── AI Orchestration
│   ├── General Platform AI
│   ├── Private AI Scientist
│   ├── Organization AI
│   ├── Knowledge and Retrieval
│   ├── Model Training
│   └── Evaluation and Governance
│
└── SHARED INFRASTRUCTURE
    │
    ├── PostgreSQL
    ├── Object Storage
    ├── Search
    ├── Vector Retrieval
    ├── Cache
    ├── Message Queue
    ├── Monitoring
    └── Deployment
```

## 2.1 Architectural Principles

The architecture follows these principles:

1. Independent frontend applications.
2. Shared identity and authentication.
3. Shared backend business services.
4. Clearly defined API boundaries.
5. Modular backend architecture.
6. Independent AI system boundaries.
7. Organization-level data isolation.
8. Personal health-data protection.
9. Shared reusable frontend packages.
10. Independent application deployment.
11. Incremental migration from the MVP.
12. Backend-enforced security and authorization.
13. AI model and data governance.
14. Long-term support for proprietary AI development.

## 2.2 Application Independence

Each frontend application must be independently buildable and deployable.

Each application owns its:

- Routing.
- Page layouts.
- Frontend state.
- Feature modules.
- Application-specific components.
- Environment configuration.
- Build configuration.
- Deployment pipeline.

Shared packages may be used for common components and utilities.

However, the applications must not depend on the internal implementation of another application.

---

# 3. Frontend Architecture

## 3.1 Frontend Application Structure

The platform will have four independent frontend applications.

| Application | Framework | Audience |
|---|---|---|
| Social Portal | Next.js | General community members |
| Personal Portal | Next.js | All registered members |
| Researcher Portal | Next.js | Researchers and organizations |
| Admin Application | React + Vite | Authorized administrators |

All frontend applications will use TypeScript.

## 3.2 Social Portal

**Directory:** `apps/social-web/`  
**Framework:** Next.js + TypeScript

The Social Portal is the default entry point for ordinary users.

Its main purpose is community participation, communication, idea exchange and event participation.

### 3.2.1 Community Feed

Features:

- Public posts.
- Community posts.
- Idea sharing.
- Discussions.
- Comments.
- Reactions.
- Content discovery.
- Announcements.
- Community activity.
- Recommended content.

### 3.2.2 Discussion and Forums

Features:

- Open discussion forums.
- Topic-based discussions.
- Health and longevity discussions.
- Scientific discussions.
- Idea development.
- Threaded conversations.
- Discussion categories.
- Moderation.
- Content reporting.

### 3.2.3 Events

Features:

- Event creation.
- Event discovery.
- Event invitations.
- Event participation.
- Event registration.
- Event notifications.
- Calendar scheduling.
- Founding meetings.
- Conferences.
- Scientific meetings.
- Festivals.
- Community activities.

Event creation is subject to the applicable premium entitlement.

### 3.2.4 Messaging

Features:

- Text messages.
- Audio messages.
- Video messages.
- Emoticons.
- Reactions.
- Media sharing.
- Resource sharing.
- Conversation management.

Messaging is a shared backend capability available from the relevant portals.

### 3.2.5 Communities and Connections

Features:

- Member discovery.
- Follow members.
- Connect with members.
- Join communities.
- Community activity.
- Invitations.
- Membership notifications.

### 3.2.6 Notifications

Notification categories:

- Messages.
- Invitations.
- Events.
- Community activity.
- Discussions.
- Comments.
- Reactions.
- Organization updates.
- Research collaboration.

### 3.2.7 SEO Requirements

The Social Portal should support:

- Server-side rendering.
- Static generation where appropriate.
- Dynamic metadata.
- Canonical URLs.
- Open Graph metadata.
- Sitemap generation.
- Robots configuration.
- Structured data where appropriate.
- Publicly accessible content pages.
- Shareable discussion and event URLs.

Private content must not become publicly indexable merely because the application uses server-side rendering.

## 3.3 Personal Portal

**Directory:** `apps/personal-web/`  
**Framework:** Next.js + TypeScript

The Personal Portal provides comprehensive personal and professional identity management.

It combines personal information, professional history, health records and personal data management.

### 3.3.1 Personal Profile

Profile information:

- Name.
- Avatar.
- Personal description.
- Current status.
- Availability.
- Registration date.
- Membership date.
- Social links.
- Portfolio.
- Company information.
- Profile visibility.

### 3.3.2 Professional Profile

Information:

- Education.
- Certifications.
- Employment history.
- Professional experience.
- Research experience.
- Projects.
- Contributions.
- Professional references.

Verification states:

| Indicator | Meaning |
|---|---|
| Green | Verified |
| Yellow | Unverified |

Verification must be supported by authorized organization or platform processes.

### 3.3.3 Community Recognition and Badges

Potential badges include:

- Ideaman.
- Researcher.
- Professor.
- Founder.
- Community Member.
- Organization Contributor.
- Organization Membership.
- Community Certifications.

Badges must be managed by a centralized backend service.

Organization contributor badges must be associated with the relevant organization.

### 3.3.4 Health Records

The Personal Portal should support categorized personal health information.

Potential categories:

- Medical records.
- Health measurements.
- Laboratory results.
- Health observations.
- Nutrition.
- Fitness.
- Physical performance.
- Sleep and activity.
- Other relevant health information.

Data input methods:

1. Manual entry.
2. Device integrations.
3. Wearable integrations.
4. Document uploads.
5. Future external platform integrations.

Health records should support:

- Categorization.
- Historical tracking.
- Graphs.
- Trend analysis.
- Personal analysis.
- Private storage.
- Controlled sharing.
- Authorized researcher access.

Health information must remain private by default.

It must not automatically become research material or AI training data.

### 3.3.5 Health Data Sharing

Users should control access to individual health records.

Possible access settings:

- Private.
- Public, where appropriate.
- Connections only.
- Specific individuals.
- Specific researchers.
- Authorized organizations.
- Time-limited sharing links.

Sharing links should support:

- Scoped permissions.
- Expiration.
- Revocation.
- Access auditing.

### 3.3.6 Activity History

The Personal Portal should display:

- Posts.
- Events.
- Discussions.
- Forum participation.
- Shared resources.
- Research contributions.
- Professional activities.
- Relevant health trends.

Activity records should link to their original resources.

### 3.3.7 Profile Layout

The profile interface may include a left-side information panel:

- Avatar.
- Name.
- Status.
- Availability.
- Join date.
- Social links.
- Portfolio.
- Company information.
- Badges.
- Certifications.

The main profile area may contain:

- Personal information.
- Professional history.
- Health records.
- Activity timeline.
- Graphs.
- Publications.
- Connections.
- Shared content.

### 3.3.8 Messaging

The Personal Portal may provide access to:

- Text messages.
- Audio messages.
- Video messages.
- Emoticons.
- Media sharing.
- Resource sharing.

Messaging remains a shared backend capability.

## 3.4 Researcher Portal

**Directory:** `apps/researcher-web/`  
**Framework:** Next.js + TypeScript

The Researcher Portal provides a professional scientific research environment.

It supports individual researchers, collaborative projects and organization-based research.

### 3.4.1 Research Dashboard

The dashboard should display:

- Active projects.
- Research activity.
- Assigned tasks.
- Recent evidence.
- Research progress.
- Reports.
- AI recommendations.
- Organization updates.

### 3.4.2 Research Tools

The system should support:

- Scientific literature discovery.
- Evidence collection.
- Evidence classification.
- Research notes.
- Hypothesis development.
- Research documentation.
- Scientific resource management.
- AI-assisted research.
- Research reporting.

AI-recommended tools should be available according to permissions and entitlements.

### 3.4.3 Research Publications

Researchers should be able to publish professional, SEO-friendly research content.

Publication types:

- Scientific blogs.
- Research articles.
- Evidence-based posts.
- Research summaries.
- Research reports.
- Citations and references.

Publication workflows should support:

- Evidence references where required.
- Optional confirmation or verification.
- Original contributions.
- Valuable content.
- Redundancy reduction.
- Search-engine-friendly metadata.

### 3.4.4 Organizations

Researchers should be able to:

- Create organizations.
- Join existing organizations.
- Manage organization membership.
- Assign roles.
- Manage projects.
- Create organization workspaces.
- Configure organization access policies.
- Manage organization AI.

Organization creation is a premium feature.

### 3.4.5 Research Workspace

The research workspace should provide collaboration capabilities inspired by professional project-management and software-development platforms.

Features:

- Project creation.
- Project participation.
- Task assignment.
- Progress tracking.
- Project documentation.
- File attachments.
- Research reports.
- Milestones.
- Team collaboration.
- Daily progress.
- Weekly progress.
- Monthly progress.

### 3.4.6 Professional Work History

The system should record actual research and organizational contributions.

Records may include:

- Assigned tasks.
- Completed tasks.
- Research contributions.
- Project participation.
- Reports.
- Deliverables.
- Organization verification.
- Employer or leader references.

Work history should be auditable.

Unauthorized alteration should be prevented.

Corrections should use amendments or other auditable processes. Legal deletion, privacy and retention requirements must still be respected.

### 3.4.7 Organization AI

Organizations may create specialized AI environments.

Organization AI should support:

- Organization-specific knowledge.
- Research document retrieval.
- Organization-specific configuration.
- Authorized research assistance.
- Knowledge-base management.
- AI evaluation.
- Usage monitoring.
- Cost tracking.
- Controlled model customization.
- Fine-tuning or training where supported.

Each organization AI environment must maintain its own access boundaries.

---

# 4. Admin Application

**Directory:** `apps/admin/`  
**Framework:** React + Vite + TypeScript

The Admin Application is independent from the three user portals.

The existing administration functionality should be preserved and migrated from Next.js to React + Vite incrementally.

## 4.1 Administrative Modules

### User Management

- User accounts.
- Account status.
- Verification.
- Account restrictions.
- User reports.

### Organization Management

- Organization records.
- Organization verification.
- Membership administration.
- Organization permissions.
- Organization AI administration.

### Community Management

- Community records.
- Community moderation.
- Community reports.
- Community configuration.

### Event Management

- Event oversight.
- Event moderation.
- Event reports.
- Event administration.

### Content Moderation

- Posts.
- Discussions.
- Reports.
- User complaints.
- Moderation actions.

### Subscription Management

- Subscription plans.
- Payments.
- Premium entitlements.
- Purchase records.
- Organization billing.

### Badge and Certification Management

- Platform badges.
- Community certifications.
- Organization contributor badges.
- Verification processes.

### AI Monitoring

- AI usage.
- AI costs.
- AI requests.
- AI safety events.
- Model evaluation monitoring.
- Organization AI monitoring.

### Audit and Security

- Administrative audit logs.
- Permission changes.
- Security events.
- Access monitoring.
- Platform configuration.

All administrative permissions must be enforced by the backend.

---

# 5. Backend API Architecture

## 5.1 Backend Strategy

The backend will initially remain a modular monolith based on the existing FastAPI implementation.

The backend is separated from frontend applications at the repository level.

The modular monolith allows:

- A unified backend deployment.
- Shared database infrastructure.
- Clear internal domain boundaries.
- Centralized authentication.
- Consistent authorization.
- Lower initial operational complexity.
- Future extraction of independent services when justified.

## 5.2 Backend Technology

| Component | Technology |
|---|---|
| Framework | FastAPI |
| Language | Python |
| Database | PostgreSQL |
| API style | REST initially |
| API versioning | `/api/v1/` |
| Authentication | Existing authentication foundation, extended as required |
| File storage | Object storage |
| Search | Search infrastructure |
| Background jobs | Queue and workers |
| AI integration | AI gateway and orchestration |

## 5.3 API Separation

The backend should expose two primary API areas:

1. User API.
2. Admin API.

The User API serves all three user portals.

The Admin API serves the administration application.

### User API

```text
/api/v1/user/
│
├── social/
│   ├── feed/
│   ├── posts/
│   ├── comments/
│   ├── reactions/
│   ├── communities/
│   ├── discussions/
│   ├── events/
│   ├── invitations/
│   ├── notifications/
│   └── connections/
│
├── personal/
│   ├── profile/
│   ├── professional/
│   ├── health/
│   ├── records/
│   ├── sharing/
│   ├── activity/
│   ├── messages/
│   └── devices/
│
└── researcher/
    ├── research/
    ├── evidence/
    ├── literature/
    ├── projects/
    ├── tasks/
    ├── reports/
    ├── organizations/
    ├── workspace/
    └── organization-ai/
```

### Admin API

```text
/api/v1/admin/
│
├── users/
├── organizations/
├── communities/
├── events/
├── moderation/
├── reports/
├── subscriptions/
├── payments/
├── badges/
├── certifications/
├── ai-monitoring/
├── configuration/
└── audit/
```

These paths define the target logical API organization.

They do not require immediate replacement of existing endpoints.

## 5.4 Shared API Services

Common services should be shared by all API areas.

Examples:

- Identity.
- Authentication.
- Authorization.
- User management.
- Organization membership.
- Notifications.
- Messaging.
- File management.
- Subscription entitlements.
- Audit logging.
- AI gateway access.

The same business rules must not be implemented separately in Social, Personal and Researcher APIs.

## 5.5 Domain Modules

The backend should contain the following domains:

```text
domains/
│
├── identity/
├── users/
├── profiles/
├── social/
├── messaging/
├── events/
├── communities/
├── health/
├── organizations/
├── professional_history/
├── research/
├── evidence/
├── projects/
├── workspace/
├── subscriptions/
├── payments/
├── badges/
├── notifications/
├── files/
├── governance/
└── audit/
```

Each domain should own its:

- Models.
- Schemas.
- Business logic.
- Service interfaces.
- Data access.
- Authorization rules.
- Tests.

## 5.6 API Compatibility

Existing API functionality must be preserved wherever possible.

Migration process:

1. Inventory existing endpoints.
2. Identify the portal responsible for each feature.
3. Map endpoints to target API domains.
4. Preserve request and response behavior.
5. Add new endpoints incrementally.
6. Introduce compatibility adapters where necessary.
7. Update frontend API clients gradually.
8. Remove obsolete routes only after migration and testing.

---

# 6. AI Platform Architecture

## 6.1 AI Platform Separation

The AI system should be a separate top-level project area.

It should not be treated as a collection of frontend components inside the Researcher Portal.

The AI platform will provide shared AI infrastructure and independently managed AI environments.

Its responsibilities include:

- Model access.
- AI orchestration.
- Prompt management.
- Retrieval.
- Knowledge management.
- Model evaluation.
- Training pipelines.
- AI governance.
- Organization-specific AI.
- Usage and cost monitoring.

## 6.2 AI System Components

The AI platform consists of:

1. AI Gateway.
2. AI Orchestration.
3. General Platform AI.
4. Private AI Scientist.
5. Organization-Specialized AI.
6. Knowledge and Retrieval.
7. Training and Evaluation.
8. AI Governance and Monitoring.

## 6.3 General Platform AI

General Platform AI provides common AI capabilities across the platform.

Responsibilities:

- General user assistance.
- Community assistance.
- Content discovery.
- Research discovery.
- Platform navigation.
- Knowledge retrieval.
- Recommendations.
- Shared AI functionality.

General AI must respect user permissions and organization boundaries.

## 6.4 Private AI Scientist

Private AI Scientist is a major long-term strategic technology asset.

Its purpose is to provide advanced scientific research assistance and support proprietary scientific AI development.

Potential capabilities:

- Scientific literature analysis.
- Evidence evaluation.
- Research synthesis.
- Hypothesis assistance.
- Research planning.
- Scientific knowledge retrieval.
- Personal research assistance.
- Scientific knowledge organization.
- Model improvement and evaluation.

### Development Strategy

The development path should support:

1. External model integration.
2. Permission-aware retrieval.
3. Curated scientific knowledge bases.
4. Scientific evaluation datasets.
5. Dataset quality management.
6. Fine-tuning capabilities.
7. Proprietary model development.
8. Advanced scientific AI training.

Priorities:

- Scientific reliability.
- Evidence provenance.
- Data quality.
- Reproducibility.
- Evaluation.
- Intellectual property protection.

## 6.5 Organization-Specialized AI

Each organization may have its own specialized AI environment.

Capabilities:

- Organization-specific knowledge.
- Research document retrieval.
- Organization-specific configuration.
- Authorized research assistance.
- Knowledge-base management.
- AI evaluation.
- Usage monitoring.
- Cost tracking.
- Model customization.
- Fine-tuning or training where supported.

Each organization AI environment must maintain its own:

- Organization identity.
- Knowledge sources.
- Retrieval permissions.
- Access policies.
- Training-data permissions.
- Evaluation datasets.
- Usage records.
- Cost records.
- Ownership and administration rules.

One organization must not access another organization's private AI information without explicit authorization.

## 6.6 AI Model and Training Architecture

The architecture must distinguish between:

- Prompt customization.
- Retrieval-augmented generation.
- Fine-tuning.
- Actual model training.

An organization-specific knowledge base does not automatically mean the organization owns or has trained a separate model.

Actual training and fine-tuning require:

- Appropriate datasets.
- Explicit data permissions.
- Data processing.
- Evaluation datasets.
- Training infrastructure.
- Model versioning.
- Reproducibility.
- Cost controls.
- Model governance.

## 6.7 AI Interfaces

AI interfaces should be integrated into the relevant portals.

Examples:

| AI capability | User interface |
|---|---|
| General Platform AI | Social and Personal Portals |
| Personal AI assistance | Personal Portal |
| Scientific AI Scientist | Researcher Portal |
| Organization AI | Researcher Portal organization workspace |
| AI administration and monitoring | Admin Application |

The AI systems themselves remain backend services.

The user-facing AI interfaces do not need to be separate applications initially.

A dedicated internal AI management console may be added later if operational needs justify it.

---

# 7. AI Platform Internal Structure

Recommended AI repository structure:

```text
ai/
│
├── gateway/
│   ├── providers/
│   ├── adapters/
│   ├── routing/
│   └── usage/
│
├── orchestration/
│   ├── workflows/
│   ├── agents/
│   ├── tools/
│   └── policies/
│
├── general/
│   ├── assistants/
│   ├── prompts/
│   ├── services/
│   └── workflows/
│
├── scientist/
│   ├── assistants/
│   ├── scientific_reasoning/
│   ├── literature/
│   ├── evidence/
│   ├── hypothesis/
│   ├── research/
│   └── evaluation/
│
├── organization/
│   ├── environments/
│   ├── knowledge/
│   ├── retrieval/
│   ├── configuration/
│   ├── evaluation/
│   └── training/
│
├── knowledge/
│   ├── ingestion/
│   ├── parsing/
│   ├── indexing/
│   ├── embeddings/
│   ├── retrieval/
│   └── provenance/
│
├── training/
│   ├── datasets/
│   ├── preparation/
│   ├── fine_tuning/
│   ├── training_jobs/
│   ├── checkpoints/
│   └── model_registry/
│
├── evaluation/
│   ├── datasets/
│   ├── benchmarks/
│   ├── experiments/
│   └── reports/
│
├── governance/
│   ├── permissions/
│   ├── privacy/
│   ├── safety/
│   ├── audit/
│   └── policies/
│
├── monitoring/
│   ├── usage/
│   ├── costs/
│   ├── performance/
│   └── quality/
│
├── shared/
│   ├── schemas/
│   ├── contracts/
│   ├── utilities/
│   └── configuration/
│
└── tests/
```

## 7.1 AI Deployment Boundaries

The AI platform may initially run within the same deployment environment as the backend.

However, its internal modules must have clear interfaces.

The architecture should allow the following components to become independently deployable:

- AI gateway.
- AI orchestration workers.
- Scientific AI workloads.
- Organization AI workloads.
- Training workers.
- Evaluation workers.

AI model training should not block ordinary API requests.

Long-running AI operations should run through background jobs.

---

# 8. Shared Data Architecture

## 8.1 PostgreSQL

PostgreSQL remains the primary relational database.

It should store:

- User identities.
- Profiles.
- Organizations.
- Memberships.
- Posts.
- Discussions.
- Comments.
- Events.
- Research projects.
- Tasks.
- Evidence metadata.
- Health-record metadata.
- Subscriptions.
- Entitlements.
- Permissions.
- Audit records.
- AI configuration metadata.

Existing models and migrations should be preserved and extended.

## 8.2 Object Storage

Object storage should support:

- Images.
- Videos.
- Audio.
- Health documents.
- Research papers.
- Research documents.
- Project files.
- Reports.
- Attachments.
- Training dataset artifacts where authorized.

Files must be accessed through controlled backend authorization.

## 8.3 Search Infrastructure

Search should support:

- User discovery.
- Community content.
- Discussions.
- Research publications.
- Literature.
- Evidence.
- Organization knowledge.

## 8.4 Vector Retrieval

Vector retrieval should support:

- Scientific knowledge retrieval.
- Research document search.
- AI-assisted evidence discovery.
- Organization knowledge bases.
- Permission-aware AI retrieval.

Vector search must respect the same permissions as the underlying source documents.

## 8.5 Background Processing

Background workers should support:

- Notifications.
- Email delivery.
- File processing.
- Media processing.
- Search indexing.
- AI processing.
- Research document ingestion.
- Scheduled reports.
- Subscription events.
- Training jobs.
- Evaluation jobs.

---

# 9. Shared Frontend Packages

The frontend applications should share common libraries through packages.

```text
packages/
│
├── ui/
├── design-tokens/
├── api-client/
├── auth-client/
├── shared-types/
├── validation/
├── shared-config/
└── testing/
```

## 9.1 UI Package

Shared components may include:

- Buttons.
- Inputs.
- Modals.
- Dialogs.
- Cards.
- Navigation elements.
- Form components.
- Common visual elements.

Portal-specific design and components should remain within their respective applications.

## 9.2 API Client

The shared API client should provide:

- API communication.
- Authentication headers.
- Request handling.
- Response parsing.
- Error handling.
- Common API types.

## 9.3 Authentication Client

The authentication package should provide reusable functionality for:

- Login.
- Logout.
- Session handling.
- Token handling.
- Authentication state.
- Permission-aware navigation support.

Backend authorization remains authoritative.

## 9.4 Shared Types

Shared types should describe common entities such as:

- User.
- Organization.
- Membership.
- Event.
- Post.
- Project.
- Task.
- Subscription.
- Badge.
- Notification.

---

# 10. Complete Target Repository Structure

The recommended target repository is:

```text
human-healthspan-ai-network/
│
├── apps/
│   │
│   ├── social-web/
│   │   ├── app/
│   │   │   ├── (public)/
│   │   │   ├── (auth)/
│   │   │   ├── (community)/
│   │   │   ├── posts/
│   │   │   ├── discussions/
│   │   │   ├── events/
│   │   │   ├── communities/
│   │   │   └── members/
│   │   │
│   │   ├── components/
│   │   ├── features/
│   │   │   ├── feed/
│   │   │   ├── discussions/
│   │   │   ├── messaging/
│   │   │   ├── events/
│   │   │   ├── communities/
│   │   │   ├── connections/
│   │   │   └── notifications/
│   │   ├── lib/
│   │   ├── services/
│   │   ├── public/
│   │   └── tests/
│   │
│   ├── personal-web/
│   │   ├── app/
│   │   │   ├── (public)/
│   │   │   ├── (auth)/
│   │   │   ├── profile/
│   │   │   ├── professional/
│   │   │   ├── health/
│   │   │   ├── records/
│   │   │   ├── sharing/
│   │   │   └── activity/
│   │   │
│   │   ├── components/
│   │   ├── features/
│   │   │   ├── profiles/
│   │   │   ├── professional/
│   │   │   ├── health-records/
│   │   │   ├── sharing/
│   │   │   ├── activity/
│   │   │   └── messaging/
│   │   ├── lib/
│   │   ├── services/
│   │   ├── public/
│   │   └── tests/
│   │
│   ├── researcher-web/
│   │   ├── app/
│   │   │   ├── (public)/
│   │   │   ├── (auth)/
│   │   │   ├── research/
│   │   │   ├── evidence/
│   │   │   ├── literature/
│   │   │   ├── projects/
│   │   │   ├── organizations/
│   │   │   └── workspace/
│   │   │
│   │   ├── components/
│   │   ├── features/
│   │   │   ├── research/
│   │   │   ├── evidence/
│   │   │   ├── literature/
│   │   │   ├── projects/
│   │   │   ├── tasks/
│   │   │   ├── organizations/
│   │   │   ├── workspace/
│   │   │   └── organization-ai/
│   │   ├── lib/
│   │   ├── services/
│   │   ├── public/
│   │   └── tests/
│   │
│   ├── admin/
│   │   ├── src/
│   │   │   ├── app/
│   │   │   ├── components/
│   │   │   ├── features/
│   │   │   │   ├── users/
│   │   │   │   ├── organizations/
│   │   │   │   ├── communities/
│   │   │   │   ├── events/
│   │   │   │   ├── moderation/
│   │   │   │   ├── subscriptions/
│   │   │   │   ├── badges/
│   │   │   │   ├── ai-monitoring/
│   │   │   │   └── audit/
│   │   │   ├── services/
│   │   │   ├── lib/
│   │   │   └── tests/
│   │   ├── index.html
│   │   └── vite.config.ts
│   │
│   └── ai-console/
│       ├── src/
│       ├── components/
│       ├── features/
│       └── services/
│
├── api/
│   │
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── user/
│   │   │   │   │   ├── social/
│   │   │   │   │   ├── personal/
│   │   │   │   │   └── researcher/
│   │   │   │   │
│   │   │   │   └── admin/
│   │   │   │
│   │   │   ├── dependencies/
│   │   │   └── middleware/
│   │   │
│   │   ├── domains/
│   │   │   ├── identity/
│   │   │   ├── users/
│   │   │   ├── profiles/
│   │   │   ├── social/
│   │   │   ├── messaging/
│   │   │   ├── events/
│   │   │   ├── communities/
│   │   │   ├── health/
│   │   │   ├── organizations/
│   │   │   ├── professional_history/
│   │   │   ├── research/
│   │   │   ├── evidence/
│   │   │   ├── projects/
│   │   │   ├── workspace/
│   │   │   ├── subscriptions/
│   │   │   ├── payments/
│   │   │   ├── badges/
│   │   │   ├── notifications/
│   │   │   ├── files/
│   │   │   ├── governance/
│   │   │   └── audit/
│   │   │
│   │   ├── services/
│   │   ├── infrastructure/
│   │   │   ├── database/
│   │   │   ├── storage/
│   │   │   ├── cache/
│   │   │   ├── queue/
│   │   │   ├── search/
│   │   │   └── observability/
│   │   │
│   │   ├── models/
│   │   ├── schemas/
│   │   └── config/
│   │
│   ├── migrations/
│   ├── scripts/
│   └── tests/
│
├── ai/
│   │
│   ├── gateway/
│   ├── orchestration/
│   │
│   ├── general/
│   │   ├── assistants/
│   │   ├── prompts/
│   │   ├── services/
│   │   └── workflows/
│   │
│   ├── scientist/
│   │   ├── assistants/
│   │   ├── scientific_reasoning/
│   │   ├── literature/
│   │   ├── evidence/
│   │   ├── hypothesis/
│   │   ├── research/
│   │   └── evaluation/
│   │
│   ├── organization/
│   │   ├── environments/
│   │   ├── knowledge/
│   │   ├── retrieval/
│   │   ├── configuration/
│   │   ├── evaluation/
│   │   └── training/
│   │
│   ├── knowledge/
│   │   ├── ingestion/
│   │   ├── parsing/
│   │   ├── indexing/
│   │   ├── embeddings/
│   │   ├── retrieval/
│   │   └── provenance/
│   │
│   ├── training/
│   │   ├── datasets/
│   │   ├── preparation/
│   │   ├── fine_tuning/
│   │   ├── training_jobs/
│   │   ├── checkpoints/
│   │   └── model_registry/
│   │
│   ├── evaluation/
│   │   ├── datasets/
│   │   ├── benchmarks/
│   │   ├── experiments/
│   │   └── reports/
│   │
│   ├── governance/
│   ├── monitoring/
│   ├── shared/
│   └── tests/
│
├── packages/
│   │
│   ├── ui/
│   ├── design-tokens/
│   ├── api-client/
│   ├── auth-client/
│   ├── shared-types/
│   ├── validation/
│   ├── shared-config/
│   └── testing/
│
├── infra/
│   │
│   ├── postgres/
│   ├── storage/
│   ├── search/
│   ├── vector/
│   ├── cache/
│   ├── queue/
│   ├── monitoring/
│   ├── deployment/
│   ├── docker/
│   └── environments/
│
├── docs/
│   │
│   ├── SYSTEM_DEVELOPMENT_ARCHITECTURE.md
│   ├── MVP_SPECIFICATION.md
│   ├── LAST_CHANGE.md
│   ├── API.md
│   ├── DATA_MODEL.md
│   ├── AI_ARCHITECTURE.md
│   ├── AI_TRAINING_STRATEGY.md
│   ├── SECURITY.md
│   ├── PRIVACY_AND_GOVERNANCE.md
│   ├── DEVELOPMENT_ROADMAP.md
│   ├── MIGRATION_PLAN.md
│   └── DEPLOYMENT.md
│
├── tests/
│   ├── api/
│   ├── integration/
│   ├── security/
│   ├── end-to-end/
│   └── architecture/
│
├── AGENT_RULE.md
├── package.json
├── pnpm-workspace.yaml
├── turbo.json
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## 10.1 Important Repository Decisions

### Frontend applications

The four applications are independent.

They share packages but do not share application routing or application-specific state.

### API

The API is a top-level project area.

It is not a frontend application and should not be nested inside `apps/`.

### AI

The AI system is also a top-level project area.

It has its own internal modules, workflows, training infrastructure and tests.

### AI Console

`apps/ai-console/` is an optional future internal interface.

It is not required for the first implementation.

AI administration can initially be handled through the Admin Application.

### Infrastructure

Infrastructure configuration is separate from application business logic.

### Documentation

Architecture, API, AI, security, migration and development documentation must be maintained separately.

---

# 11. Authentication and Authorization Architecture

All user applications must use a shared identity system.

A user should be able to access Social, Personal and Researcher Portals using the same account.

## 11.1 Authentication

The system should support:

- Registration.
- Email verification.
- Login.
- Logout.
- Password recovery.
- Session management.
- Secure authentication.
- Future MFA support.

## 11.2 Authorization

The system should support:

- User roles.
- Organization roles.
- Membership permissions.
- Project-level permissions.
- Resource-level permissions.
- Administrative permissions.
- Health-data permissions.
- AI retrieval permissions.

## 11.3 Permission Enforcement

Permissions must be checked by the backend.

Frontend restrictions are presentation controls only.

Every sensitive API operation must verify that the requesting user is authorized to access or modify the relevant resource.

## 11.4 Cross-Application Authentication

The applications should share an identity provider or centralized authentication service.

The implementation should define:

- Trusted application origins.
- Secure session handling.
- Token lifecycle.
- Refresh behavior.
- Logout propagation.
- CSRF protections where applicable.
- Cookie security.
- Redirect validation.

Authentication should not depend on insecure storage of long-lived tokens in browser local storage.

---

# 12. Organization Architecture

Organizations are central to the Researcher Portal and scientific collaboration ecosystem.

An organization should support:

- Organization profile.
- Members.
- Roles.
- Membership invitations.
- Projects.
- Tasks.
- Reports.
- Documents.
- Work history.
- Contributor badges.
- Organization AI.
- Subscription and payment information.

## 12.1 Organization Roles

The architecture should support roles such as:

- Founder.
- Owner.
- Administrator.
- Research Leader.
- Researcher.
- Contributor.
- Member.

The actual permission structure should be configurable and enforced by the backend.

## 12.2 Organization Data Isolation

Organization information must be protected.

Members should access organization resources according to:

- Organization membership.
- Assigned role.
- Resource permissions.
- Organization policies.
- Explicit sharing arrangements.

## 12.3 Organization Work History

Organization contributions should be recorded with appropriate provenance.

Records may contain:

- User.
- Organization.
- Project.
- Task.
- Contribution.
- Completion status.
- Verification status.
- Responsible leader.
- Relevant timestamps.

---

# 13. Subscription and Premium Architecture

Premium functionality should be controlled through a centralized backend entitlement system.

## 13.1 Initial Premium Features

| Feature | Payment model |
|---|---|
| Create organization | Paid per organization creation |
| Create event | Paid according to the applicable user plan |
| Organization contributor badges | Two default badges with organization creation; additional badges purchasable |
| Organization AI | Paid per organization AI instance |

## 13.2 Entitlement System

The system should support:

- Subscription plans.
- One-time purchases.
- Recurring payments where applicable.
- Feature entitlements.
- Purchase records.
- Payment status.
- Organization billing.
- Usage tracking.
- Refund and cancellation workflows.

The backend is authoritative for premium access.

## 13.3 Future Premium Features

Future AI-suggested one-time and permanent features should be reserved in the architecture but not implemented in the current MVP scope.

---

# 14. Security, Privacy and Governance

Security and privacy must be built into all system layers.

## 14.1 General Security

Requirements:

- Secure authentication.
- Backend authorization.
- Secure session management.
- Input validation.
- API protection.
- File access control.
- Audit logging.
- Rate limiting.
- Monitoring.
- Backup and recovery.

## 14.2 Health Data Privacy

Health data must have additional protection.

Requirements:

- Private by default.
- Explicit sharing permissions.
- Controlled access.
- Access auditing.
- Appropriate retention policies.
- Secure file storage.
- Consent management.

Health data must not automatically be used for research or AI training.

## 14.3 Research Data Governance

Research data should support:

- Ownership and attribution.
- Source references.
- Evidence provenance.
- Access permissions.
- Organization boundaries.
- Version history.
- Auditability.

## 14.4 AI Governance

AI systems should enforce:

- Permission-aware retrieval.
- Data provenance.
- Organization isolation.
- Consent and purpose limitations.
- Training-data permissions.
- Evaluation.
- Monitoring.
- Intellectual property protection.

---

# 15. Deployment Architecture

Frontend applications should be independently deployable.

The backend and AI platform should have separate deployment configurations, even if some components initially run in the same infrastructure environment.

```text
                        USERS
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
   SOCIAL PORTAL     PERSONAL PORTAL   RESEARCHER PORTAL
     Next.js            Next.js           Next.js
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                    ADMIN APPLICATION
                     React + Vite
                          │
                          ▼
                     API GATEWAY
                          │
                          ▼
                    FASTAPI BACKEND
                          │
       ┌──────────────────┼──────────────────┐
       │                  │                  │
       ▼                  ▼                  ▼
    USER API           ADMIN API        AI INTEGRATION
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                   SHARED DOMAIN SERVICES
                          │
           ┌──────────────┼──────────────┐
           │              │              │
           ▼              ▼              ▼
       PostgreSQL    Object Storage   Search/Vector
                          │
                          ▼
                    Background Queue
                          │
                          ▼
                     AI PLATFORM
                          │
           ┌──────────────┼──────────────┐
           │              │              │
           ▼              ▼              ▼
       General AI    AI Scientist   Organization AI
```

## 15.1 Deployment Principles

- Independent frontend builds.
- Independent frontend deployments.
- Shared backend.
- Centralized identity.
- Shared database.
- Secure object storage.
- Separate AI workload execution.
- Centralized monitoring.
- Automated testing and deployment.

## 15.2 Future Scaling

The architecture should allow independent scaling of:

- Frontend applications.
- API workloads.
- AI workloads.
- Background workers.
- Search infrastructure.
- File processing.
- Training infrastructure.

Microservices should only be introduced when justified by actual operational requirements.

---

# 16. Testing Architecture

Testing must cover individual applications and cross-platform behavior.

## 16.1 Frontend Tests

Each application should have:

- Component tests.
- Feature tests.
- Routing tests.
- Authentication tests.
- Permission-related UI tests.
- Accessibility tests.

## 16.2 Backend Tests

The backend should have:

- API contract tests.
- Domain service tests.
- Authentication tests.
- Authorization tests.
- Database tests.
- Integration tests.
- AI permission tests.

## 16.3 AI Tests

The AI platform should have:

- Prompt and workflow tests.
- Retrieval tests.
- Permission-boundary tests.
- Organization-isolation tests.
- Model evaluation tests.
- Dataset validation tests.
- Training reproducibility tests.
- Safety and quality tests.

## 16.4 End-to-End Tests

Cross-application workflows should be tested.

Examples:

1. Register once and access all three portals.
2. Publish a public post in the Social Portal.
3. Share a personal profile.
4. Create a research project.
5. Invite a member to an organization.
6. Assign a project task.
7. Verify a professional contribution.
8. Access health data using explicit permission.
9. Create an organization AI instance.
10. Purchase a premium entitlement.

## 16.5 Security Tests

Security testing should include:

- Cross-user access attempts.
- Cross-organization access attempts.
- Unauthorized health-data access.
- Share-link permission checks.
- AI retrieval isolation.
- Administrative authorization.
- Subscription entitlement enforcement.

---

# 17. Migration Strategy from Existing MVP

The existing MVP must remain the source of working functionality until each replacement has been verified.

## 17.1 Current Baseline

The existing project currently contains:

- `apps/web`: existing Next.js user-facing application.
- `apps/admin`: existing Next.js admin application.
- `apps/api`: existing FastAPI backend.
- `packages/ui`: shared UI package.
- `infra/postgres`: existing database infrastructure.
- Existing documentation and tests.

The target architecture changes the organization but does not require discarding these implementations.

## 17.2 Migration Mapping

| Existing location | Target location | Migration strategy |
|---|---|---|
| `apps/web` | `apps/social-web`, `apps/personal-web`, `apps/researcher-web` | Extract functionality incrementally |
| `apps/admin` | `apps/admin` | Migrate Next.js to React + Vite |
| `apps/api` | `api/` | Move or reorganize incrementally |
| `packages/ui` | `packages/ui` | Preserve and extend |
| `infra/postgres` | `infra/postgres` | Preserve |
| Existing services | `api/app/domains` and `api/app/services` | Refactor gradually |
| Existing AI gateway | `ai/gateway` or API integration adapter | Preserve behavior and separate responsibilities |
| Existing retrieval service | `ai/knowledge` and retrieval integration | Evolve incrementally |
| Existing tests | Relevant target test directories | Preserve and expand |
| Existing docs | `docs/` | Update and consolidate |

## 17.3 Frontend Migration

The current `apps/web` should not be deleted immediately.

First, map existing routes and features to the three new portals.

Then:

1. Create `apps/social-web`.
2. Establish its Next.js configuration.
3. Migrate social routes and features.
4. Test existing functionality.
5. Create `apps/personal-web`.
6. Migrate profile functionality.
7. Introduce personal health foundations.
8. Create `apps/researcher-web`.
9. Migrate research functionality.
10. Verify all applications.
11. Retire or repurpose the original `apps/web` only after successful migration.

## 17.4 Admin Migration

The existing admin application should be migrated to React + Vite.

The migration should preserve:

- Administrative workflows.
- API integrations.
- Authentication.
- Permissions.
- Audit functionality.
- Existing administrative features.

The backend Admin API should remain compatible during the frontend migration.

## 17.5 Backend Migration

The current `apps/api` implementation should be moved to the top-level `api/` structure only after:

- Import paths have been mapped.
- Docker configurations have been updated.
- Environment variables have been reviewed.
- Database migration paths have been preserved.
- API tests have been updated.
- Deployment scripts have been updated.

The backend should not be rewritten merely to change its directory.

## 17.6 AI Migration

Existing AI gateway and retrieval services should be inventoried.

Their working implementations should be reused.

AI responsibilities should gradually move into the dedicated `ai/` architecture.

API endpoints should communicate with AI services through stable internal interfaces.

---

# 18. Development Roadmap

## Phase 1 — Repository Foundation

Objectives:

- Preserve the existing project.
- Inventory existing functionality.
- Establish the target repository structure.
- Identify existing frontend routes.
- Identify existing API routes.
- Map existing domain models.
- Define shared packages.
- Define application boundaries.
- Establish workspace tooling.

Deliverables:

- Repository migration plan.
- Existing feature inventory.
- API compatibility plan.
- Updated architecture documentation.

## Phase 2 — Social Portal

Objectives:

- Create `apps/social-web`.
- Use Next.js and TypeScript.
- Integrate existing authentication.
- Migrate feed functionality.
- Migrate communities.
- Migrate discussions.
- Implement event foundations.
- Implement notifications.

Deliverables:

- Independent Social Portal.
- Shared API integration.
- SEO-friendly public pages.

## Phase 3 — Personal Portal

Objectives:

- Create `apps/personal-web`.
- Use Next.js and TypeScript.
- Migrate personal profiles.
- Migrate professional profiles.
- Implement profile visibility.
- Implement sharing.
- Introduce health-record foundations.
- Introduce activity history.

Deliverables:

- Independent Personal Portal.
- Personal data management foundations.
- Professional profile system.

## Phase 4 — Researcher Portal

Objectives:

- Create `apps/researcher-web`.
- Use Next.js and TypeScript.
- Migrate existing research features.
- Improve evidence management.
- Introduce project workspaces.
- Introduce task management.
- Introduce organization management.
- Establish organization AI foundations.

Deliverables:

- Independent Researcher Portal.
- Research workspace.
- Organization management foundations.

## Phase 5 — Admin Migration

Objectives:

- Migrate administration to React + Vite.
- Preserve existing admin features.
- Preserve administrative API compatibility.
- Implement user and organization management.
- Implement moderation interfaces.
- Implement subscription management.
- Implement AI monitoring.

Deliverables:

- Independent React administration application.
- Preserved administrative capabilities.

## Phase 6 — Backend Reorganization

Objectives:

- Organize existing routes into clearer API boundaries.
- Preserve existing service implementations.
- Extend shared domain services.
- Implement missing backend capabilities.
- Improve authorization.
- Add audit and governance functionality.

Deliverables:

- Modular backend architecture.
- Social, Personal, Researcher and Admin API boundaries.
- Expanded domain services.

## Phase 7 — AI Platform Development

Objectives:

- Improve General Platform AI.
- Develop Private AI Scientist.
- Establish scientific data pipelines.
- Build evaluation infrastructure.
- Implement organization AI.
- Establish organization data isolation.
- Develop proprietary model capabilities over time.

Deliverables:

- Three logically separated AI environments.
- AI governance foundations.
- Scientific AI development infrastructure.

## Phase 8 — Production Readiness

Objectives:

- Security assessment.
- Privacy assessment.
- Performance testing.
- Backup and recovery.
- Monitoring and alerting.
- Deployment automation.
- Operational documentation.

Deliverables:

- Production-ready system.
- Operational procedures.
- Deployment and recovery documentation.

---

# 19. Repository and Development Tooling

The monorepo should support independent application development while sharing packages.

Recommended tooling:

| Purpose | Recommendation |
|---|---|
| JavaScript package manager | pnpm |
| Monorepo orchestration | Turborepo |
| Frontend language | TypeScript |
| Frontend linting | ESLint |
| Formatting | Prettier |
| Frontend testing | Vitest |
| End-to-end testing | Playwright |
| Backend testing | Pytest |
| API documentation | OpenAPI |
| Containerization | Docker |
| Local environment | Docker Compose |
| Version control | Git |

The tooling should be introduced in a way that does not disrupt the existing MVP.

The root workspace should manage the frontend applications and shared TypeScript packages.

Python backend and AI dependencies may use their own Python environment and dependency management configuration.

The JavaScript and Python toolchains should remain independently maintainable.

---

# 20. Documentation Architecture

The following documentation files should be maintained:

| File | Responsibility |
|---|---|
| `SYSTEM_DEVELOPMENT_ARCHITECTURE.md` | Complete system architecture |
| `ARCHITECTURE.md` | Concise architecture overview and key decisions |
| `LAST_CHANGE.md` | Most recent development changes |
| `API.md` | API contracts and endpoint documentation |
| `DATA_MODEL.md` | Database and domain model |
| `AI_ARCHITECTURE.md` | AI platform architecture |
| `AI_TRAINING_STRATEGY.md` | Scientific and organization model training strategy |
| `SECURITY.md` | Security architecture |
| `PRIVACY_AND_GOVERNANCE.md` | Privacy, consent and data governance |
| `DEVELOPMENT_ROADMAP.md` | Development phases |
| `MIGRATION_PLAN.md` | Existing MVP migration |
| `DEPLOYMENT.md` | Deployment and infrastructure |

Documentation must reflect actual implementation.

A planned feature must not be documented as already implemented.

---

# 21. AGENT_RULE.md

The project should contain a root-level `AGENT_RULE.md` defining mandatory development instructions for AI coding agents and human developers.

It should cover:

1. Existing MVP preservation.
2. Repository structure.
3. Frontend framework decisions.
4. Backend architecture.
5. AI architecture.
6. Shared packages.
7. API contracts.
8. Database migration rules.
9. Security and privacy requirements.
10. Testing requirements.
11. Documentation updates.
12. Deployment rules.

The following rules are mandatory:

- Do not replace working MVP functionality without a verified migration.
- Use Next.js for Social, Personal and Researcher portals.
- Use React + Vite for Admin.
- Keep API code separate from frontend applications.
- Keep AI system code separate from the API implementation.
- Do not duplicate shared business logic.
- Do not access the database directly from frontend applications.
- Enforce permissions in the backend.
- Keep health data private by default.
- Do not automatically use personal health data for AI training.
- Preserve organization-level data isolation.
- Keep the three AI environments logically separated.
- Preserve existing database migrations.
- Preserve API compatibility during migrations.
- Add tests before removing existing functionality.
- Update documentation after architectural changes.
- Do not claim planned functionality is implemented.

---

# 22. Final Architecture Decisions

| Area | Final decision |
|---|---|
| Social Portal | Next.js + TypeScript |
| Personal Portal | Next.js + TypeScript |
| Researcher Portal | Next.js + TypeScript |
| Admin Application | React + Vite + TypeScript |
| Optional publication site | Astro, only if justified later |
| Backend | Existing FastAPI modular monolith |
| API directory | Top-level `api/` |
| AI directory | Top-level `ai/` |
| AI Console | Optional future application |
| Database | Existing PostgreSQL |
| Authentication | Shared identity system |
| API architecture | User API and Admin API boundaries |
| Frontend deployment | Independent applications |
| Shared packages | UI, design tokens, API client, authentication, types |
| File storage | Object storage |
| Search | Dedicated search infrastructure |
| Vector retrieval | Dedicated vector retrieval |
| Background processing | Queue and workers |
| General AI | Shared platform AI |
| Private AI Scientist | Dedicated scientific AI environment |
| Organization AI | Organization-specialized AI environments |
| Premium features | Centralized backend entitlements |
| Migration strategy | Incremental preservation of existing MVP |

# 23. Final Development Direction

The Human Healthspan Scientific AI Network will be developed as a multi-application platform with independent user portals, shared backend infrastructure and three distinct AI environments.

The three user-facing portals will use Next.js:

- Social Portal.
- Personal Portal.
- Researcher Portal.

The Admin Application will use React + Vite.

The backend API and AI platform will be maintained as separate top-level project areas.

The existing FastAPI backend, PostgreSQL infrastructure, services, models, tests and working functionality will be preserved and extended.

The architecture supports independent frontend development, shared backend services, secure personal health-data management, organization-based research collaboration and long-term proprietary scientific AI development.

**Implementation directive:** This document defines the target architecture. The existing MVP remains the source of working functionality until each migration has been implemented, tested and verified. New structure should be introduced incrementally rather than through an unnecessary wholesale rewrite.