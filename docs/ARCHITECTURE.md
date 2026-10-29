# Technical Architecture

## Architecture decisions

- Keep the repository as a monorepo so coordinated portal, API-contract, and shared-UI changes are easy to review.
- Treat each user-facing portal as an independently buildable and deployable client.
- Keep one versioned API as the only application boundary to domain data.
- Start the backend as a modular monolith. Split a domain only when measured scale, resilience, or isolation needs justify the operational cost.
- Run long-running and scheduled work in a separate worker process when required; initially it can reuse the API's domain code and database boundaries.
- Do not add a service, package, or infrastructure technology before there is a consumer and a concrete requirement.

## Current repository structure

```text
apps/
  web/                 # Member-facing Next.js application
  admin/               # Platform operations and moderation portal
  api/                 # FastAPI modular monolith
packages/
  ui/                  # Shared React/shadcn primitives and brand tokens
infra/
  postgres/            # Local database initialization
tests/
  test_api_contract.py # API integration and authorization tests
docs/
docker-compose.yml
package.json           # npm workspace root for frontend apps and packages
```

The API owns authentication, authorization, domain workflows, and persistence. The portals must never connect directly to PostgreSQL, Redis, or search infrastructure.

## Target structure as the system grows

```text
apps/
  web/                 # Member platform
  admin/               # Platform-wide administration
  api/                 # Shared, versioned domain API
  worker/              # Ingestion and other asynchronous jobs, when needed
  institution/         # Organization-scoped portal, after tenant controls exist
packages/
  ui/                  # Shared shadcn components and design tokens
  api-client/          # Typed client generated from or verified against API schemas
  types/               # Shared public contracts only where multiple clients need them
  config/              # Shared frontend tooling configuration
```

`worker`, `institution`, `api-client`, `types`, and `config` are planned extension points, not currently implemented applications/packages. Add each only when a real workflow needs it. Keep domain models authoritative in the API; shared frontend types must not become a second source of truth.

## Client and package boundaries

- `web` serves members and researchers. `admin` serves platform operators and moderators. They may share UI primitives and API contracts, but have separate route trees, builds, and access policies.
- An institution portal is distinct from the platform admin portal. Institution roles must be scoped to their tenant; platform administrator status must not silently grant access to private research content.
- Every protected operation is authorized server-side. UI route guards and hidden controls are usability features, not security controls.
- Shared packages should contain stable, reusable code with explicit exports. Do not share server secrets, database models, or application-specific page components.
- The npm workspace is for JavaScript/TypeScript applications and packages. Python API dependencies and domain modules remain managed by the Python project.

## Logical layers

1. Client applications — Next.js/React/TypeScript portals.
2. API/application — FastAPI endpoints, identity, authorization, and domain use cases.
3. Domain modules — social, communities, research, evidence, search, AI, moderation, governance, and administration.
4. System of record — PostgreSQL + pgvector.
5. Supporting infrastructure — Redis for queues/cache, search, and object storage as workflows require them.
6. External providers — identity, email, model APIs, literature/data sources.
7. Operations — logs, metrics, traces, audit, backups, and recovery.
8. Optional scientific projection — graph database only when relational/search approaches no longer meet validated needs.

## Scaling and extraction strategy

Scale the API and worker processes independently before splitting domain services. Keep modules behind explicit interfaces and test their contracts. Consider extracting a domain only after observing a clear trigger, such as sustained workload contention, independent availability requirements, strict data isolation, or an independently managed release cadence. Extraction requires defined APIs/events, ownership of data and migrations, observability, and failure handling.

Portals can deploy independently while sharing the API. Production scalability still requires deployment automation, capacity/load testing, resource limits, monitoring, rate limiting, backup/restore drills, and resilience testing; a monorepo or Docker Compose alone does not provide those guarantees.

## Future graph

Relational scientific entities remain canonical source records. A graph projection can later materialize relationships such as:

Researcher → ResearchQuestion → Hypothesis → Evidence → Paper → Gene → Protein → Pathway → Disease → Experiment → Result
