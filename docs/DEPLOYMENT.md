# Deployment

**Status: local development only.** No production deployment exists.

## Local development

```bash
cp .env.example .env
npm install                   # or: pnpm install
docker compose up -d          # PostgreSQL and Redis
npm run dev                  # all four frontends (3000-3003)
npm run dev:api                  # API on http://localhost:8000
```

The root `.env` is read by the Next.js apps (via `@next/env`) and by Vite (only `VITE_*`
variables reach the browser).

## Principles (from the architecture)

Independent frontend builds and deployments; shared backend; centralized identity; shared
database; secure object storage; separate AI workload execution; centralized monitoring;
automated testing and deployment. Scale frontends, API, AI workloads, workers, search, file
processing and training independently. Introduce microservices only for real operational need.

## Planned (M4 and M10)

CI/CD per application, production configuration under `infra/deployment`, backup and restore
drills, monitoring and alerting, runbooks and incident response.
