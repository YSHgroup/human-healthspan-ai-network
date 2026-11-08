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

Use Node.js 24 and Python 3.14. On Windows, install and run them on the host. On Ubuntu, install
Docker Engine and the Compose plugin, and run all project tooling in Docker rather than installing
Node.js or Python on the host.

```bash
cp .env.example .env
```

The root `.env` is read by the Next.js portals, Admin and the API/Alembic. Only `VITE_*` values
reach the Admin browser bundle; secrets remain server-side.

### Windows

Install dependencies and start the Social Portal from the repository root:

```powershell
npm install
npm run dev:social
```

The Social Portal is available at [http://localhost:3000](http://localhost:3000). The Social, Personal, and Researcher portals are configured with shadcn/ui, Tailwind CSS v4, and shared UI primitives. The original logo and emblem live under `public/brand`; app scripts sync them into each app's generated public directory before development and builds.

Other frontends can be started independently:

```bash
npm run dev:personal     # http://localhost:3001
npm run dev:researcher   # http://localhost:3002
npm run dev:admin        # http://localhost:3003
```

All app origins are `localhost`; no custom domain is required. To start the API, use a second
PowerShell terminal:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e "api[dev]" -e ai
$env:PATH = "$PWD\.venv\Scripts;$env:PATH"
npm.cmd run db:migrate
npm.cmd run dev:api
```

### Ubuntu (Docker only)

Docker Compose runs every project component in containers: all four portals use Node.js 24; the API
uses Python 3.14; and PostgreSQL and Redis run as supporting services. From the repository root,
build and start the full stack:

```bash
docker compose up --build
```

Compose installs JavaScript dependencies in a Node.js container before starting the portals. The
API image installs its Python dependencies and runs database migrations before starting the API.
Open the services at:

- Social Portal: [http://localhost:3000](http://localhost:3000)
- Personal Portal: [http://localhost:3001](http://localhost:3001)
- Researcher Portal: [http://localhost:3002](http://localhost:3002)
- Admin: [http://localhost:3003](http://localhost:3003)
- API: [http://localhost:8000](http://localhost:8000)

Run the stack in the background with `docker compose up --build -d`. Follow its logs with
`docker compose logs -f`; stop the containers with `docker compose down`. PostgreSQL data is kept
in a named volume when containers stop. To delete the database and Redis data as well, use
`docker compose down --volumes`.

Run project commands inside the appropriate service containers, for example:

```bash
docker compose exec social-web npm run build
docker compose exec api python -m pytest tests/api -q
docker compose exec api python -m alembic -c api/alembic.ini upgrade head
```

Implemented API scope is shared registration/session, direct and group text messaging, General AI
chat, a restricted prompt-only Scientist prototype and opt-in AI-learning content retention.
Email verification, account recovery, researcher approval workflow, AI retrieval/training,
community workflows and admin operations are not implemented. See [API documentation](./docs/API.md)
and the [implementation inventory](./docs/MIGRATION_PLAN.md) for the current route and model map.

## Project checks

On Windows, run checks with the project dependencies installed on the host:

```powershell
npm run build
npm run lint
npm run typecheck
npm test                      # web unit tests, architecture rules, API tests
npm run test:architecture     # AGENT_RULE and architecture checks (standard library only)
```

On Ubuntu, start the stack with `docker compose up --build -d`, then run checks in the matching
containers. `npm test` combines both toolchains, so run the suites separately:

```bash
docker compose exec social-web npm run build
docker compose exec social-web npm run lint
docker compose exec social-web npm run typecheck
docker compose exec social-web npm run test:web
docker compose exec api python -m pytest tests/architecture tests/api tests/ai tests/migration -q
```

## Source of truth

Precedence when documents disagree: the idea blueprint, then the architecture, then the roadmap.

Start with [the architecture overview](./docs/ARCHITECTURE.md), then read [the system architecture](./docs/SYSTEM_DEVELOPMENT_ARCHITECTURE.md), [MVP specification](./docs/MVP_SPECIFICATION.md), and [development roadmap](./docs/DEVELOPMENT_ROADMAP.md) before extending the project. The references directory contains the original blueprint and white paper. Consult [the implementation inventory](./docs/MIGRATION_PLAN.md) for the current route and model targets.

> pnpm works the same way (`pnpm install`, `pnpm dev:social`, ...). If Corepack is enabled and blocks npm because of the `packageManager` field, run `corepack disable` or set `COREPACK_ENABLE_STRICT=0`.
