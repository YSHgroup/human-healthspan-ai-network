# Overall progress implemented

## APPS

- Independent Next.js foundations for Social, Personal and Researcher portals; React + Vite foundation for Admin.
- Social Portal landing page; shadcn/ui, Tailwind CSS v4 and shared Button, Badge and Card primitives (`@healthspan/ui`).
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

Aligned the repository with the architecture and blueprint: fixed workspace install configuration, completed the target structure, added the missing documentation set and automated architecture checks.

## What is the next step?

1. Run `npm install` (or `pnpm install`), then `npm run typecheck`, `npm test`, `npm run build` and fix anything they report (nothing has been installed or built in this environment).
2. Complete the M1 inventory of the existing MVP in `MIGRATION_PLAN.md` and add characterization tests.
3. Resolve the MVP-blocking open decisions (audience, MVP boundary, regulatory scope) and write the PRD.
4. Add ESLint and Playwright to the tooling, then start shared identity (M2). Do not expose health records or private research until consent, authorization and audit controls exist.
