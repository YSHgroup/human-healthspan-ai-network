# Handover — MVP update to Architecture v1.2 (API v0.4.0)

## 0. Read this first: verification status
This sandbox had **no network**, so FastAPI, SQLAlchemy, pytest and all npm packages could not be installed.
**Nothing was executed.** What *was* checked: every Python file compiles; every `app.*` import resolves to a real module/name; no undefined names (custom AST checks); all 99 new TS/TSX files parse with the TypeScript compiler (syntax only, no type checking). The 15 new tests in `tests/test_platform_contract.py` were reviewed against the code by hand but have never run. Expect some failures on first run — fix them before relying on anything here.

## 1. Decision on the roadmap
Roadmap needed updating (conflicts on frontend structure, API boundaries, sequencing, admin scope). See `docs/Revised_development_roadmap_v3.md`. Everything reusable from the MVP was kept.

## 2. What changed

### Backend (`apps/api`) — complete for this scope
- **Models** `app/models/platform.py`, 30 additive tables; **migration** `a1c3f0b7d2e4` (creates only those tables; existing tables untouched; it builds them from the models, so use autogenerate for later changes).
- **Domains** `app/domains/*`: organizations (roles, invitations, isolation, attach projects), subscriptions/entitlements, professional records (verification, edit invalidates it), work history (append-only, amendments), badges (2 default per org; extras paid), health (private, scoped/expiring/revocable shares, hashed link tokens, access log, consents), messaging, events (premium-gated, capacity, visibility, discussion post), notifications, research access (apply/approve), tasks/progress/workspace summary.
- **AI** `app/ai/`: General, Private AI Scientist, Organization AI as separate retrievers with separate authorization; one audited orchestrator; answers carry sources, evidence labels, uncertainty, disclaimer; "insufficient evidence" instead of guessing; prompts are not stored in runs/audit. Default provider is offline *extractive* (restates cited sources). Optional Anthropic adapter (`AI_PROVIDER=anthropic`, `AI_API_KEY`, `AI_MODEL`) is General-AI-only unless `AI_ALLOW_EXTERNAL_FOR_PRIVATE=true`; **untested against the live API**.
- **API boundaries**: `/api/v1/user/social|personal|researcher` (+ `/user/ai/general`) and `/api/v1/admin/*` (organizations, events, plans, subscriptions, payments, entitlements, badges, certifications, researcher applications, AI monitoring, configuration, audit, overview). Existing MVP routes still work; aliases reuse the same handlers. `/ai/chat` and `/ai/research` no longer return 503.
- Notifications are created on comments, follows, messages, invitations, event activity, etc.

### Frontend
- **New packages**: `shared-types`, `api-client` (typed, all new endpoints), `auth-client` (session + `useAsync`/`useAction`), `design-tokens`, `validation`, `shared-config` (portal registry/links); `ui` gained `AiChat` and `VerificationBadge`.
- **New apps** (Next.js): `social-web` :3000, `personal-web` :3001, `researcher-web` :3002 — each with own shell, auth routes, BFF proxy, shared-login support via `COOKIE_DOMAIN`, and cross-portal "Switch space" links.
  - Social: home, discover, communities, member profiles (moved from `apps/web`, now on `/user/social`).
  - Personal: profile settings.
  - Researcher: research projects/questions, science search (now on `/user/researcher`).
- `apps/web` kept as legacy (compose profile `legacy`, port 3003). `apps/admin` kept as-is, moved to port 3004.
- Infra: shared `infra/docker/portal.Dockerfile`, compose services, `.env.example` (CORS origins, AI, portal URLs).

## 3. What is NOT done (honest list)
1. **Frontend pages for most new features** — the API and client exist, the screens don't: social (events, messages, notifications, Ask AI); personal (overview, professional/badges/work history, health, sharing, privacy & plan, activity); researcher (workspace, project detail with tasks/progress, organizations, Organization AI, AI Scientist). Nav shows only pages that exist.
2. **Admin migration to React + Vite** not started; admin has no screens for the new admin endpoints.
3. **`package-lock.json` is stale** (new workspaces). Run `npm install` before `npm ci`/Docker builds.
4. Rate limiting, MFA, production email flow changes, CI, Playwright E2E.
5. Payment processor (purchases are reconciled manually by an admin), file upload/object storage, document ingestion, OpenSearch/pgvector, threaded comments, device/wearable integrations, voice/video upload for messages (URL reference only).
6. Real LLM quality: default AI is extractive by design; there is no evaluation set yet.

## 4. How to run
```bash
cp .env.example .env
pip install -r apps/api/requirements.txt
python -m pytest tests -q            # run first; fix failures
npm install                          # refreshes package-lock.json
npm run typecheck:social && npm run typecheck:personal && npm run typecheck:researcher
docker compose up --build            # api + 3 portals (+ admin); add --profile legacy for old web
```
Dev ports: social 3000, personal 3001, researcher 3002, legacy web 3003, admin 3004, API 8000. Locally the portals share one sign-in because cookies ignore ports; in production set `COOKIE_DOMAIN`.

## 5. Try the new flows (after tests pass)
Make an admin (`User.role = "admin"` in DB), then: member applies at `POST /user/researcher/membership/apply` → admin approves at `POST /admin/research-memberships/{user_id}/decision` → admin grants `organization.create` via `POST /admin/entitlements` → member creates an organization → grants/buys `organization.ai` → adds documents → asks the Organization AI. Interactive docs at `http://localhost:8000/docs`.

## 6. Recommended next steps (in order)
Run and fix tests → typecheck portals → build the missing pages (start with Personal health/sharing and Researcher organizations, since the backend rules there are the most sensitive) → Admin on Vite → Phase 1A hardening → Phase 2 documents/search.

## 7. Decisions you may want to revisit
- Researcher approval is required to create organizations and use the AI Scientist (my reading of Blueprint §5).
- Organization-creation and org-AI are one-time countable entitlements; event creation is a non-consumed premium feature (plan or entitlement).
- Health sharing to an organization only exposes data to members in research-capable roles.
