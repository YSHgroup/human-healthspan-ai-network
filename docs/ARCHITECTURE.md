# Architecture Overview

Concise overview and key decisions. The complete specification is
[SYSTEM_DEVELOPMENT_ARCHITECTURE.md](./SYSTEM_DEVELOPMENT_ARCHITECTURE.md).

> Status rule: a planned capability is never documented as implemented. This repository is a
> foundation; see [Last_Change.md](./Last_Change.md) for what exists today.

## Source documents and precedence

When documents disagree, apply this order:

1. **Idea Blueprint** (`references/`) - the product idea, principles and scope.
2. **System Development Architecture** - how the system is organized.
3. **Development Roadmap** - sequencing; it may be adapted to fit 1 and 2.

The White Paper (`references/`) explains the same idea for external readers.

**Naming.** The blueprint calls the default portal the *General portal*. The architecture and
this repository call it the **Social Portal** (`apps/social-web`). They are the same portal.

## System map

| Area | Location | Technology | Status |
|---|---|---|---|
| Social Portal | `apps/social-web` | Next.js + TypeScript | Landing page only |
| Personal Portal | `apps/personal-web` | Next.js + TypeScript | Foundation page only |
| Researcher Portal | `apps/researcher-web` | Next.js + TypeScript | Foundation page only |
| Admin Application | `apps/admin` | React + Vite + TypeScript | Foundation page only |
| Backend API | `api/` | Python + FastAPI modular monolith | `/healthz` and empty versioned routers |
| AI platform | `ai/` | Python | Package boundaries only |
| Shared packages | `packages/` | TypeScript | Skeletons; shared types and UI primitives |
| Infrastructure | `docker-compose.yml`, `infra/` | Docker | PostgreSQL and Redis for local development |

## Key decisions

- **Independent portals over one platform.** Each portal builds and deploys on its own, but all
  share one identity, one backend and one database. A portal never imports another portal.
- **Modular monolith.** One FastAPI deployment with domain modules under `api/app/domains`.
  Extract services only when operations justify it.
- **Two API areas.** `/api/v1/user/{social,personal,researcher}` and `/api/v1/admin`.
- **Backend authorization is authoritative.** Navigation, hidden controls and portal access never
  grant resource access. Every sensitive operation, file, retrieval and AI tool call is checked.
- **Three separated AI environments.** General Platform AI, Private AI Scientist and
  Organization-Specialized AI have separate data boundaries and never import one another.
- **Health data is private by default** and never becomes research or training data silently.
- **Incremental migration.** The existing MVP stays the source of working behavior until each
  replacement is verified ([MIGRATION_PLAN.md](./MIGRATION_PLAN.md)).

## Enforcement

`tests/architecture` turns the mandatory rules into automated checks: structure, application
independence, no direct database access from frontends, no browser-stored tokens, private portals
not indexable, API-to-AI interface limits and AI environment separation. Run `npm run test:architecture`.
