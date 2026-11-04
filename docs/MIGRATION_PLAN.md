# Migration Plan

The existing MVP remains the source of working functionality until each replacement is
implemented, tested and verified. The legacy MVP source is **not included in this repository**
(it is kept separately), so the inventory below is an open M1 task, not a finished list.

## Target mapping

| Existing location | Target | Strategy |
|---|---|---|
| `apps/web` | `apps/social-web`, `apps/personal-web`, `apps/researcher-web` | Extract incrementally |
| `apps/admin` (Next.js) | `apps/admin` (React + Vite) | Migrate incrementally; keep Admin API compatible |
| `apps/api` | `api/` | Move only after imports, Docker, env, migrations, tests and deployment are updated |
| `packages/ui` | `packages/ui` | Preserve and extend |
| `infra/postgres` | `infra/postgres` | Preserve |
| Services | `api/app/domains`, `api/app/services` | Refactor gradually |
| AI gateway | `ai/healthspan_ai/gateway` or an adapter | Preserve behavior, separate responsibilities |
| Retrieval service | `ai/healthspan_ai/knowledge` | Evolve incrementally |
| Tests | `tests/*`, `api/` tests | Preserve and expand |

## Method (per feature)

1. Inventory routes, endpoints, models, services and tests.
2. Assign each to a portal and an API domain.
3. Add characterization tests that capture current behavior.
4. Build the replacement; keep compatibility adapters for old endpoints.
5. Verify against the characterization tests, then switch clients gradually.
6. Retire the old code only after verified parity.

## Order (from the architecture)

Social Portal, Personal Portal, Researcher Portal, Admin, then backend reorganization as a
continuous track. Never delete `apps/web` before all three portals are verified.

## M1 inventory checklist

- [ ] Frontend routes mapped to a target portal
- [ ] API endpoints mapped to a target domain
- [ ] Domain models and Alembic migrations mapped
- [ ] Authentication and authorization foundations reviewed
- [ ] AI gateway and retrieval services reviewed
- [ ] Existing tests and Docker configuration preserved
