# Roadmap

This is the concise project roadmap. See [Human_Healthspan_AI_Scientific_Network_Roadmap.md](Human_Healthspan_AI_Scientific_Network_Roadmap.md) for scope, requirements, and exit criteria.

## Principles

- Build a useful, safe MVP on a modular monolith before adding advanced infrastructure.
- Keep web/admin clients and shared frontend packages in a workspace monorepo; deploy client apps independently when useful.
- Centralize domain behavior and authorization in the versioned API rather than adding portal-specific backends.
- Add shared packages and worker processes to solve real reuse or workload needs; avoid empty scaffolding.
- Deliver the member-facing platform and a separate, first-class Admin App together for the MVP.
- Make privacy, consent, least privilege, resource-level authorization, provenance, and auditability foundational.
- Gate later capabilities on validated product value, governance, and operational readiness.

## Phase 0 — Validation and Architecture

Validate MVP journeys, personas, success metrics, architecture, data boundaries, permissions, governance, and operational requirements. Establish the data model, tests, CI, and local/deployment workflows. Set up the npm workspace for the web/admin apps and extract only the UI primitives they actually share.

## Phase 1 — MVP: Social Platform, Research Foundation, and Essential Admin App

Deliver accounts and profiles, starter communities, social participation and discovery, scientific evidence with provenance, foundational research projects with scoped permissions, and evidence-grounded AI support where it meets quality requirements.

Launch a separate Admin App alongside the member platform, sharing its backend API and domain services. Include secure administrator access, server-enforced least-privilege roles, platform and service overview, account and community management, moderation and scientific-review queues, audited privileged actions, operational visibility, and incident/reporting entry points. Verify access boundaries, privacy, and audit behavior before launch.

Complete end-to-end member and admin journeys against the same API. Keep application code independently buildable; require production deployment and load tests before claiming traffic scalability.

## Phase 2 — Research and Governance Maturity

Strengthen project permissions and access reviews, evidence review and correction handling, conflicts-of-interest declarations, privacy requests, sensitive-data controls, and governance reporting.

**Gate:** Demonstrate reliable research permissions, provenance, and review processes before expanding powerful AI or institutional data features.

## Phase 3 — AI Operations and Evidence-Grounded Assistance

Expand AI Q&A, document analysis, literature synthesis, citation support, and project assistance. Add model routing, quality and cost evaluation, operational oversight, and audited Admin App configuration. Introduce a worker process using existing API domain modules for ingestion, indexing, and other long-running tasks. Preserve user, team, and resource permissions throughout retrieval and tool use.

**Gate:** Require appropriate evaluations, privacy controls, human review, logging, and incident response for each higher-impact capability.

## Phase 4 — Knowledge Infrastructure

Add structured scientific entities, relationships, claims, evidence, and provenance; improve discovery, ingestion, deduplication, taxonomy, and quality review. Keep PostgreSQL and existing search/retrieval as the system of record unless product and scale needs justify more infrastructure.

## Phase 5 — Collaboration and Research Opportunities

Add researcher matching, collaboration and project discovery, research opportunities, events, challenges, and supporting administration and abuse prevention.

## Phase 6 — Scientific AI and Research Automation

Introduce specialized agents, data analysis, bioinformatics workflows, and research-discovery tools only where justified, with scoped permissions, human oversight, provenance, evaluations, and controlled tool access.

**Gate:** Each advanced capability needs a risk assessment, reproducible evaluations, human oversight, and a rollback or disable mechanism.

## Phase 7 — Institutional Environments

Support organization workspaces with strong tenant isolation, delegated administration, institutional policies and audit reporting, validated SSO needs, data ownership and retention controls, and scoped research APIs. Add an institution-facing portal as a separately deployed client only after API-enforced tenant isolation and delegated roles pass security tests.

## Phase 8 — Global Ecosystem

Grow cross-community and cross-institution collaboration under explicit governance. Consider broader research marketplace and funding capabilities when validated; continue improving localization, accessibility, resilience, abuse prevention, and operational scalability.

## Continuous engineering commitments

Across every phase, maintain automated testing and CI, dependency and image maintenance, backups and recovery, observability, privacy and consent controls, secure authentication and authorization, encryption and secrets management, rate limiting, audit logging, evidence and citation integrity, correction mechanisms, accessible responsive UX, privacy-respecting analytics, and disciplined migrations and API evolution.

As multiple clients need the same contracts, add a typed API client generated from or verified against the API schema. Add shared types or tooling configuration only when there are real consumers; maintain one authoritative API schema and keep app-specific configuration local where that improves isolation.

## Explicitly deferred until justified

The MVP does not depend on a full biomedical knowledge graph, dedicated genomic-analysis platform, autonomous AI scientists, advanced bioinformatics infrastructure, funding marketplace, native mobile apps, Kubernetes, or microservices. Revisit these only when user demand, technical evidence, scale, and governance readiness support them.
