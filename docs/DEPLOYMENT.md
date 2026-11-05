# Deployment

**Status: local development only.** No production deployment exists.

## Local development

```powershell
copy .env.example .env        # PowerShell; use cp on macOS/Linux
npm.cmd install               # or: pnpm.cmd install
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e "api[dev]" -e ai
npm.cmd run dev                # all four frontends (3000-3003)
```

The root `.env` is read by the Next.js apps (via `@next/env`) and by Vite (only `VITE_*`
variables reach the browser). The API and Alembic also load it. No custom domain is needed.
The default database is local SQLite; PostgreSQL and Redis are optional local services (`docker
compose up -d postgres redis`) or can be supplied separately. Redis is not used by the current
API slice.

In PowerShell, prepare the Python environment and run database/API commands in their own terminal:

```powershell
$env:PATH = "$PWD\.venv\Scripts;$env:PATH"
npm.cmd run db:migrate
npm.cmd run dev:api
```

The current development slice includes shared identity/session, text messaging, a configurable
AI provider gateway and consent-aware AI interaction records. It is not production-ready; see
`API.md`, `SECURITY.md` and `PRIVACY_AND_GOVERNANCE.md` for missing controls.

On macOS/Linux use `python3 -m venv .venv` and `.venv/bin/python -m pip install -e "api[dev]" -e ai`,
then activate the venv before running the npm API scripts.

## Principles (from the architecture)

Independent frontend builds and deployments; shared backend; centralized identity; shared
database; secure object storage; separate AI workload execution; centralized monitoring;
automated testing and deployment. Scale frontends, API, AI workloads, workers, search, file
processing and training independently. Introduce microservices only for real operational need.

## Planned (M4 and M10)

CI/CD per application, production configuration under `infra/deployment`, backup and restore
drills, monitoring and alerting, runbooks and incident response.
