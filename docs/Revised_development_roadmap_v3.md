# Revised development roadmap v3 — aligned to Blueprint V2.2 and Architecture v1.2

Priority order used: **1. Blueprint → 2. Architecture → 3. Roadmap.** Where the v2 roadmap conflicted with the Architecture, the Architecture won.

## 1. Does the roadmap need updating? Yes — in five places

| # | v2 roadmap said | Architecture / Blueprint says | Change in v3 |
|---|---|---|---|
| 1 | Keep one member app (`apps/web`) and a Next.js admin; "do not rebuild" | Three independent Next.js portals (Social, Personal, Researcher) + a separate React/Vite admin; shared packages | Phase 1 now includes the **portal split**. `apps/web` stays as a legacy app during migration, not extended. |
| 2 | One flat API (`/api/v1/...`) | User API `/api/v1/user/{social,personal,researcher}` and Admin API `/api/v1/admin` | Portal API boundaries added as aliases over proven routes; old paths kept for compatibility. |
| 3 | Organizations, health data, messaging, events, badges, entitlements appear late or not at all | These are first-class domains (Architecture §3, §12) with backend-enforced entitlements | Pulled forward into a new **Phase 1B – Platform domains**. |
| 4 | AI activates in Phase 3 (general) and Phase 4 (private) | Three separate AI systems with their own authorization, plus an audited orchestrator | A governed **AI baseline** (retrieval + citations + audit, no proprietary model) is delivered in 1B; Phases 3/4/7 now mean *upgrading* it (document ingestion, vector search, stronger models). |
| 5 | Admin = moderation/users only | Admin also owns organizations, events, subscriptions, payments, badges, AI monitoring, configuration | Admin scope expanded; admin migrates to Vite + a small BFF. |

**Kept from v2 unchanged:** the phase ordering after Phase 1 (documents → general AI → private AI → collaboration → advanced AI → organization AI → shared learning → global), all exit criteria for security/testing/deployment, the "do not let AI invent evidence" rules, and the list of items deliberately kept outside the MVP.

## 2. Status of each phase (after this update)

| Phase | v3 scope | Status |
|---|---|---|
| 1A. MVP completion | auth hardening, rate limiting, MFA strategy, email, CI/CD, E2E tests | **Not done** (unchanged from v2) |
| 1B. Platform domains + portal split | organizations, researcher access, tasks/work history, professional records, badges, health data + sharing + consent, messaging, events, notifications, entitlements/payments (manual), User/Admin API boundaries | **Backend done (unverified at runtime)**; frontend **partly done** (see handover) |
| 2. Scientific documents & search | file upload, object storage, parsing, OpenSearch/pgvector | Not started (text-only org documents exist as a stopgap) |
| 3. General Platform AI | real provider, evaluation set | **Baseline done**: public-knowledge retrieval, citations, evidence labels, uncertainty, audit; optional external-provider adapter (untested) |
| 4. Private AI Scientist | researcher-only AI over authorized projects | **Baseline done**: same retriever pattern + approval gate. No proprietary models. |
| 5. Research collaboration | structured claims, reviews, version history | Partly: tasks, progress, org projects. Reviews/claims not started |
| 6. Advanced Scientist | proprietary specialization | Not started |
| 7. Organization AI | paid per-org AI instance, isolated knowledge | **Baseline done**: entitlement-gated instance, org-scoped documents and retrieval |
| 8. Shared learning | governed feedback → improvement | **Foundation only**: feedback with explicit permitted-use + consent records |
| 9. Global | i18n, regional compliance | Not started |

## 3. Revised sequence from today

**Sprint 1 — make it run (blocking)**
1. Install deps, run `pytest tests -q`; fix whatever fails (this code was never executed — see handover).
2. `npm install` to regenerate `package-lock.json`; `npm run typecheck:*` for each portal; fix type errors.
3. Run `alembic upgrade head` on a fresh Postgres.

**Sprint 2 — finish Phase 1B frontend**
Social: events, messages, notifications, Ask-AI. Personal: overview, professional, health, sharing, privacy & plan, activity. Researcher: workspace, project detail (tasks/progress), organizations, Organization AI, AI Scientist. The typed API client and shared `AiChat` / `VerificationBadge` components already exist.

**Sprint 3 — Admin migration**
Port `apps/admin` to React + Vite with a small BFF that keeps HttpOnly cookies; add screens for organizations, events, subscriptions/payments, badges, researcher applications, AI monitoring, configuration.

**Sprint 4 — Phase 1A hardening** (rate limiting on Redis, MFA, production email, CI with API + Playwright tests, secrets, backups, monitoring).

**Then Phase 2** (documents/ingestion/search), which unlocks real value for all three AI systems.

## 4. Release gates added in v3
- No portal ships a premium feature gated only in the UI; every entitlement is enforced by the API (done and tested in `tests/test_platform_contract.py`).
- Health data must stay unreachable from AI/search code (static guard test included).
- Org AI must never return another organization's content (tested).
- Payment provider integration is required before any paid feature is offered publicly (currently manual reconciliation by an admin).
