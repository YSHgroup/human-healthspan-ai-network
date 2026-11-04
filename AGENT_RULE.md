# Engineering rules

These rules apply to contributors and coding agents working in this repository.

## Architecture

- Follow the architecture, roadmap and product scope in `docs/`; this repository is being built incrementally.
- Keep Social, Personal, Researcher, and Admin applications independently buildable.
- Use Next.js + TypeScript for the three user portals and React + Vite + TypeScript for Admin.
- Keep backend API code in `api/` and AI system code in `ai/`; do not move business logic into a frontend.
- Keep shared contracts and shadcn/ui primitives in `packages/`. Do not couple one application to another application's internal implementation.
- Treat `public/brand/` as the canonical brand-asset source; use the sync script to populate app public directories.
- Preserve the modular-monolith backend direction and shared API boundaries.

## Security, privacy, and scientific integrity

- The backend is the authorization authority. Frontend routing and hidden controls are not access control.
- Keep sitemaps and crawlable metadata limited to public pages; verify private routes are not indexable when they are introduced.
- Keep personal health information private by default. Never use personal health data for AI training without separate explicit consent and governance.
- Enforce organization and project isolation for every protected resource and AI retrieval operation.
- Keep General Platform AI, Private AI Scientist, and Organization-Specialized AI logically separate.
- Preserve source provenance and communicate uncertainty. AI hypotheses are not validated findings.
- Do not add secrets to the repository; use environment variables and update `.env.example` with safe placeholders.

## Change quality

- Preserve existing behavior and migrations; verify a migration before removing an old capability.
- Add or update tests for behavior, authorization, privacy, and data-boundary changes.
- Keep documentation aligned with the implementation and label planned work as planned.
- Run the smallest relevant lint, type-check available.
- Update `docs/Last_Change.md` with completed work and the next step.
- When you are coding, if you make the something distinct in normal and it's important to be inexed, You MUST make the git commit with the changes.
