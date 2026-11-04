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
infra/              Local PostgreSQL and Redis development services
tests/              Cross-area test suites
docs/               Architecture, MVP scope, and roadmap
references/         Original product source documents and legacy reference
```

## Getting started

Requirements: Node.js 20+, pnpm 9, Python 3.10+, and Docker Compose (for local infrastructure).

```bash
cp .env.example .env
pnpm install
pnpm dev:social
```

The Social Portal is available at [http://localhost:3000](http://localhost:3000). The Social, Personal, and Researcher portals are configured with shadcn/ui, Tailwind CSS v4, and shared UI primitives. The original logo and emblem live under `public/brand`; app scripts sync them into each app's generated public directory before development and builds.

Other frontends can be started independently:

```bash
pnpm dev:personal     # http://localhost:3001
pnpm dev:researcher   # http://localhost:3002
pnpm dev:admin        # http://localhost:3003
```

Start local dependencies with `docker compose -f infra/docker-compose.yml up -d`. The API can be started separately after installing its Python dependencies:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e "api[dev]"
uvicorn app.main:app --app-dir api --reload --port 8000
```

The API currently exposes only a basic health check. Authentication, persistence, community workflows, AI behavior, and administrative operations are planned work and must not be inferred from the portal scaffolds.

## Project checks

```bash
pnpm build
pnpm lint
pnpm typecheck
pytest -q tests/api
```

## Source of truth

Read [the system architecture](./docs/SYSTEM_DEVELOPMENT_ARCHITECTURE.md), [MVP specification](./docs/MVP_SPECIFICATION.md), and [development roadmap](./docs/DEVELOPMENT_ROADMAP.md) before extending the project. The references directory contains the original blueprint, white paper, and an older project archive. The archive is a source for selected visual assets and context only; it is not the implementation template for this project.