# Migration Plan

The existing MVP remains the source of working functionality until each replacement is
implemented, tested and verified. The legacy MVP source is **not included in this repository**
(it is kept separately). This inventory is complete for the files available in this checkout;
the separately stored legacy application still needs to be supplied before its routes, data and
behavior can be inventoried or migrated safely.

## M1 inventory — this repository

| Area | Observed implementation | Target / migration note |
|---|---|---|
| Social frontend | `apps/social-web/app/`: public landing page, General AI and text-message pages | Social API; landing-page behavior predates this slice, new chat pages use shared API |
| Personal frontend | `apps/personal-web/app/`: foundation page and text-message page | Personal API; health records remain unimplemented |
| Researcher frontend | `apps/researcher-web/app/`: foundation page and restricted Scientist prototype page | Researcher API; approval gate is enforced by backend |
| Admin frontend | `apps/admin/`: React + Vite foundation | Admin features and administration API remain unimplemented |
| API endpoints | `/healthz`, `/readyz`; shared registration/login/logout/me and AI-learning consent; direct/group text messaging; General AI and gated Scientist chat | Current route list and request contracts are in `API.md`; no legacy API endpoints are present in this checkout |
| API domains | Domain packages exist; identity, messaging and AI request services are implemented for the current slice | Other domain packages are placeholders; legacy model/service mapping awaits source access |
| Database | SQLAlchemy models for accounts, sessions, conversations, participants, messages, AI consent and AI interaction metadata/content | Alembic file `0001_identity_messaging_ai_learning.py` (revision `0001_core`) is the first migration in this repository; no prior migrations or legacy schema were present to preserve |
| Identity/security | Opaque random session cookie, hashed server-side token, scrypt password hash, trusted-origin check for browser writes | Email verification, recovery, MFA, rate limiting, full RBAC/ABAC and production audit controls remain incomplete |
| AI | OpenAI-compatible provider gateway; general and Scientist prompt workflows; opt-in learning-content retention | No retrieval, curated corpus, training, evaluation pipeline or Organization AI; provider disabled unless configured |
| Tests | `tests/api` covers liveness, CORS, security headers, migration, identity/session, messaging isolation, consent and AI gates; `tests/ai` covers gateway behavior; `tests/architecture` enforces repository rules | No legacy characterization tests can be written without the separate legacy implementation and its runnable dependencies |
| Infrastructure | Root `docker-compose.yml` configures PostgreSQL and Redis; this machine has no Docker command | Local default is SQLite; PostgreSQL remains supported through `DATABASE_URL` |

## Target mapping

| Existing location | Target | Strategy |
|---|---|---|
| Legacy web app (not in checkout) | `apps/social-web`, `apps/personal-web`, `apps/researcher-web` | Inventory first; extract only after legacy behavior is characterized |
| Legacy admin (not in checkout) | `apps/admin` (React + Vite) | Inventory and preserve workflow parity before retiring legacy Admin |
| Legacy API (not in checkout) | `api/` | Compare routes, models, migrations and compatibility before any move |
| Current `packages/ui` | `packages/ui` | Preserve and extend shared primitives and communication surfaces |
| Current database migrations | `api/alembic/` | Preserve and extend; first local schema is file `0001_identity_messaging_ai_learning.py` (revision `0001_core`) |
| Current domain services | `api/app/domains`, `api/app/services` | Keep business rules in backend domains; map legacy services once available |
| Current AI gateway | `ai/healthspan_ai/gateway` | Provider-independent adapter; legacy provider behavior is not available for comparison |
| Legacy retrieval service (not in checkout) | `ai/healthspan_ai/knowledge` | Preserve behavior only after its source and tests are supplied |
| Current tests | `tests/api`, `tests/ai`, `tests/architecture` | Preserve and expand; legacy tests are unavailable |

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

- [x] Routes in the current repository mapped to target portals
- [x] Current API endpoints and implemented domains mapped
- [x] Current SQLAlchemy models and first Alembic migration documented
- [x] Current identity/session controls and missing launch requirements reviewed
- [x] Current AI gateway reviewed; no pre-existing local retrieval implementation found
- [x] Current API, AI, architecture tests and Docker configuration inventoried
- [ ] Legacy frontend/API/domain/migration/AI behavior characterized — blocked until the separately stored legacy source is provided

The new characterization tests describe observed behavior in this checkout. They do not claim
parity with an absent legacy application or invent legacy users, records, migrations or routes.
