# API

REST, versioned under `/api/v1/`. The FastAPI application lives in `api/app`.

## Implemented today

| Method | Path | Purpose |
|---|---|---|
| GET | `/healthz` | Liveness only. Does not check the database or external services. |

Cross-cutting behavior already in place:

- CORS allows only the origins in `API_CORS_ORIGINS`, with credentials (session cookies).
- Every response carries `X-Request-ID` and baseline security headers.

The routers `/api/v1/user/social`, `/api/v1/user/personal`, `/api/v1/user/researcher` and
`/api/v1/admin` are mounted but **contain no endpoints yet**.

## Target organization (planned)

```text
/api/v1/user/
  social/       feed, posts, comments, reactions, communities, discussions, events,
                invitations, notifications, connections                      (M2)
  personal/     profile, professional, health, records, sharing, activity,
                messages, devices                                            (M2, health M5)
  researcher/   research, evidence, literature, projects, tasks, reports,
                organizations, workspace, organization-ai                    (M3)
/api/v1/admin/  users, organizations, communities, events, moderation, reports,
                subscriptions, payments, badges, certifications,
                ai-monitoring, configuration, audit                          (M3)
```

## Rules

- Route handlers stay thin; business rules live in `api/app/domains/<domain>` and are shared by
  all API areas. The same rule is never implemented separately per portal.
- Every sensitive operation verifies the requesting user's rights on the specific resource.
- Preserve request and response behavior of existing MVP endpoints; use compatibility adapters.
- Remove obsolete routes only after migration and tests.
- Errors use the shape `{ code, message, requestId }` (see `@healthspan/shared-types` `ApiProblem`).
- Write endpoints need tests (authorization and privacy) and a row in this document first.
