# Overall progress implemented

## APPS

- Independent Next.js foundations for Social, Personal and Researcher portals; React + Vite foundation for Admin.
- Redesigned all four portal visual layers with a shared shadcn/ui and Tailwind CSS v4 system, responsive shells, light/dark themes, accessible status badges, and reduced-motion-aware animation.
- Expanded `@healthspan/ui` with Base UI-backed shadcn primitives and reusable composites; added `motion`, `cmdk`, `sonner`, and `next-themes` for motion, command search, toasts, and Next.js theme handling.
- Added semantic palette, typography, radius, shadow, and spacing tokens, plus Social, Personal, Researcher, and Admin accent variations.
- Social Portal now has a public landing page; Personal and Researcher are clearly labeled foundations, and Admin remains a planned operations foundation.
- Personal and Researcher portals and Admin are never indexable (`robots` metadata, `robots.ts`, `noindex`); only the Social Portal is public.
- All portals send baseline security headers; Admin reads only `VITE_*` values from the root `.env`.
- Feature directories follow the architecture (`features/`, `services/`, `components/`, `tests/`) and are empty placeholders.

## API

- FastAPI application with `/healthz`, versioned empty routers (`/api/v1/user/{social,personal,researcher}`, `/api/v1/admin`), environment-driven CORS and request-id and security-header middleware.
- Domain packages for all 21 architecture domains (planned, no behavior).

## AI SYSTEM

- Separate Python package with all architecture modules, including `organization`, `orchestration`, `training`, `governance`, `monitoring` and `shared`. No AI workflow or provider integration is implemented.

## Shared platform

- pnpm workspaces, Turborepo (`build`, `dev`, `lint`, `typecheck`, `test`), `.npmrc`, npm and pnpm both supported (local packages use `*` ranges, npm `workspaces` added), root `.env` loaded by the portals.
- `@healthspan/shared-types` now carries the blueprint's evidence classes, visibility levels, portal states, AI environments, organization roles and premium features.
- `@healthspan/api-client` sends credentials for cookie sessions; unit tests added for it and `@healthspan/validation` (Vitest).
- `docker-compose.yml` moved to the repository root; `infra/` has one folder per concern.
- `tests/architecture` enforces AGENT_RULE and architecture rules (structure, application independence, no direct DB access from frontends, no browser-stored tokens, private portals not indexable, API-to-AI interface limits, AI environment separation).
- Added `ARCHITECTURE.md`, `API.md`, `DATA_MODEL.md`, `AI_ARCHITECTURE.md`, `AI_TRAINING_STRATEGY.md`, `SECURITY.md`, `PRIVACY_AND_GOVERNANCE.md`, `MIGRATION_PLAN.md`, `DEPLOYMENT.md`; expanded `AGENT_RULE.md` with the architecture's mandatory rules; roadmap M1 marked in progress.

## Last Change

Recorded the owner-approved M1 audience, geographic-availability and MVP-boundary decisions in `docs/DECISIONS.md`, and aligned the roadmap and MVP specification. The public launch is open across topics and regions, while research access remains permission-gated. Applicable legal and regulatory review remains a launch prerequisite; an onboarding acknowledgment does not replace it.

Previous implementation verification: `npm install`, workspace typecheck, serial workspace build, JavaScript unit tests, and API tests passed. The root lint and architecture checks still report existing repository issues: formatting in `packages/shared-types/src/index.ts`, and nested app lockfiles that conflict with the current architecture test. These were left unchanged to preserve the requested lockfile strategy. The architecture suite otherwise passed 19 tests; the API suite passed 6 tests. The current documentation-only update was checked for whitespace errors and against the source documents.

## What is the next step?

1. Complete the M1 inventory of the existing MVP in `MIGRATION_PLAN.md` and add characterization tests.
2. Complete the applicable legal and regulatory review, then write the PRD and prioritized MVP backlog from the approved M1 decisions.
3. Resolve the existing lint and architecture-check failures without changing the npm/pnpm lockfile strategy.
4. Add ESLint and Playwright to the tooling, then start shared identity (M2). Do not expose health records or private research until consent, authorization, and audit controls exist.
