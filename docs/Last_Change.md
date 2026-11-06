# Last Change

## Completed

- Recorded the approved M1 audience, geographic-availability and MVP-boundary decisions in
  `docs/DECISIONS.md`; public eligibility is open across topics and regions, while research spaces
  remain permission-gated. Legal review remains necessary and is not replaced by an acknowledgment.
- Implemented local shared registration/session and Alembic persistence, direct/group text
  messaging, General AI and a gated prompt-only Scientist prototype, and consent-aware AI
  interaction records. The API defaults to SQLite and supports PostgreSQL by `DATABASE_URL`.
- Added API and AI tests for identity/session behavior, participant authorization, consent
  revocation, provider configuration, AI access gates and existing API foundation behavior.
- Added shared communication UI and connected Social, Personal and Researcher pages. Separate
  commits were made for design tokens, shared UI and each modified portal.
- Completed the repository-local M1 inventory in `docs/MIGRATION_PLAN.md`, documented route and
  data-model status, and clarified missing functionality across architecture, API, security,
  privacy, deployment and AI documentation.
- Removed nested app npm lockfiles to enforce the root-only lockfile rule and added the root pnpm
  lockfile; local package ranges remain `"*"`.
- Completed the M1 source inventory for the supplied v0.4 archive and added archive-bound tests
  for its API route declarations, all 49 ORM tables, six-revision Alembic chain and 37 archived
  behavioral test cases.

## Known gaps and conflicts

- The v0.4 archive is inventoried and its API behavior suite passes, but the live production
  database and its applied migration revision are not in the archive and remain unverified. The
  current `0001_core` migration is not compatible with the legacy six-revision history; do not
  use it to upgrade a legacy database.
- Legacy identity includes verified-email, password-reset and rotating-token workflows absent from
  the current API. Legacy AI has permission-scoped retrieval and tests for metadata-only run
  monitoring; current opt-in content retention and prompt-only responses differ and need review
  before any production migration.
- Initial identity, messaging and AI slices are implemented ahead of their roadmap gates. This
  does not mean M2/M4/M6 or production launch criteria are complete.
- Email verification/recovery, researcher approval workflow, rate limiting, production audit and
  hardening, AI retrieval/source validation, training and administration are not implemented.
- Docker/PostgreSQL and external AI provider operation have not been verified in this environment.
  The local browser configuration remains `localhost:3000`–`3003`; the API uses port `8000`.

## Verification

- Python: architecture/API/AI/migration suites passed, 42 tests total; Pylance found no syntax
  errors in the Alembic dotenv update.
- Legacy baseline: 37 archived API/platform behavior tests passed from a safe temporary extraction;
  new archive-contract tests pin its routes, 49 tables and six-migration history.
- `npm test` and `pnpm test` each passed: 5 frontend unit tests and 42 Python tests.
- Frontend: 10 workspace typechecks and all 5 frontend unit tests passed; the architecture script
  passed 20 tests.
- Production build: all 4 application builds passed.
- Package managers: `npm ci` passed; `pnpm install --frozen-lockfile` passed with an isolated
  store. The default pnpm store encountered Windows `EBUSY` rename errors. npm reported 11 audit
  findings (2 low, 6 moderate, 1 high, 2 critical); no automated dependency changes were applied.
- Not verified: production deployment, live PostgreSQL/Docker, real AI provider, actual configured
  `.env` migration target and deployed legacy-system parity.

## Next step

Inspect the deployed database's actual Alembic revision and data, then design and rehearse a
compatibility/data migration before connecting the current API to it. Complete the
email-verification/researcher-approval workflow, security/privacy review, source-backed AI work
and required launch gates before any public release.
