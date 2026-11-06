# Human Healthspan Scientific AI Network

A people-first, science-led network where open community participation can connect to governed research and responsible AI. This repository currently establishes the workspace and portal foundations, not a feature-complete MVP.

## Product direction

The platform connects three experiences over a shared backend:

- **Social Portal** — discover topics, learn, discuss and connect.
- **Personal Portal** — manage an individual profile, preferences and saved knowledge.
- **Researcher Portal** — participate in approved research communities and collaborate in controlled workspaces.
- **Admin Application** — a separate operations and governance surface.

The long-term AI architecture has three distinct environments: General Platform AI, a permission-controlled Private AI Scientist, and Organization-Specialized AI. They are not interchangeable; private research and personal health information must never cross their boundaries without explicit authorization.

The product progression is **Discover → Learn → Connect → Participate → Collaborate → Research → Validate → Share appropriate knowledge**. Popularity is not scientific evidence, AI hypotheses are not findings, and health information remains private by default.

## Repository layout

```text
apps/
  social-web/       Next.js public entry point and landing page
  personal-web/     Next.js personal portal foundation
  researcher-web/   Next.js researcher portal foundation
  admin/            React + Vite administration foundation
api/                Python + FastAPI modular API foundation
ai/                 Separate Python AI platform foundation
packages/           Shared frontend types, config, tokens, and API client
packages/ui/        Shared shadcn-style primitives for the user portals
public/brand/       Canonical shared logo and emblem assets
docker-compose.yml  Local PostgreSQL and Redis development services
infra/              Infrastructure configuration by concern (postgres, storage, search, queue, ...)
tests/              api, architecture (rule checks), integration, security, end-to-end
docs/               Architecture, MVP scope, and roadmap
references/         Original product source documents and legacy reference
```

## Getting started

Requirements: Node.js 20+, npm 10+ or pnpm 9, Python 3.10+. Docker Compose is optional when using the default local SQLite database.

```bash
cp .env.example .env
npm install            # or: pnpm install
npm run dev:social     # or: pnpm dev:social
```

The root `.env` is read by the Next.js portals, Admin and the API/Alembic. Only `VITE_*` values
reach the Admin browser bundle; secrets remain server-side.

The Social Portal is available at [http://localhost:3000](http://localhost:3000). The Social, Personal, and Researcher portals are configured with shadcn/ui, Tailwind CSS v4, and shared UI primitives. The original logo and emblem live under `public/brand`; app scripts sync them into each app's generated public directory before development and builds.

Other frontends can be started independently:

```bash
npm run dev:personal     # http://localhost:3001
npm run dev:researcher   # http://localhost:3002
npm run dev:admin        # http://localhost:3003
```

All app origins are `localhost`; no custom domain is required. Start the API separately after installing its Python dependencies. On Windows:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e "api[dev]" -e ai
```

In PowerShell, add the venv Python to the current terminal's `PATH` before the npm API scripts:

```powershell
$env:PATH = "$PWD\.venv\Scripts;$env:PATH"
npm.cmd run db:migrate
npm.cmd run dev:api
```

Run the API command in a separate terminal from the frontend commands. For macOS/Linux, substitute
`python3 -m venv .venv`, `.venv/bin/python -m pip ...`, and activate the venv
(`source .venv/bin/activate`) before `npm run db:migrate` and `npm run dev:api`.
The API uses SQLite by default. To use PostgreSQL, start it with `docker compose up -d postgres`
or provide an external server, then set `DATABASE_URL` in the root `.env` before running
`npm run db:migrate`. Redis is not required by the current API slice.

Implemented API scope is shared registration/session, direct and group text messaging, General AI
chat, a restricted prompt-only Scientist prototype and opt-in AI-learning content retention.
Email verification, account recovery, researcher approval workflow, AI retrieval/training,
community workflows and admin operations are not implemented. See [API documentation](./docs/API.md)
and the [implementation inventory](./docs/MIGRATION_PLAN.md) for the current route and model map.

## Project checks

Python-backed checks require the project virtual environment to be active (on Windows PowerShell,
add `"$PWD\.venv\Scripts"` to `PATH`; on macOS/Linux, run `source .venv/bin/activate`).

```bash
npm run build
npm run lint
npm run typecheck
npm test                      # web unit tests, architecture rules, API tests
npm run test:architecture     # AGENT_RULE and architecture checks (standard library only)
```

## Source of truth

Precedence when documents disagree: the idea blueprint, then the architecture, then the roadmap.

Start with [the architecture overview](./docs/ARCHITECTURE.md), then read [the system architecture](./docs/SYSTEM_DEVELOPMENT_ARCHITECTURE.md), [MVP specification](./docs/MVP_SPECIFICATION.md), and [development roadmap](./docs/DEVELOPMENT_ROADMAP.md) before extending the project. The references directory contains the original blueprint and white paper. Consult [the implementation inventory](./docs/MIGRATION_PLAN.md) for the current route and model targets.

> pnpm works the same way (`pnpm install`, `pnpm dev:social`, ...). If Corepack is enabled and blocks npm because of the `packageManager` field, run `corepack disable` or set `COREPACK_ENABLE_STRICT=0`.
