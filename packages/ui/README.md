# Shared shadcn/ui primitives

The user portals share these Base UI-backed shadcn primitives:

- `@healthspan/ui/button`
- `@healthspan/ui/badge`
- `@healthspan/ui/card`
- `@healthspan/ui/utils`

Each user app has its own `components.json`, Tailwind CSS v4/PostCSS setup, and `@/lib/utils` alias. Add app-specific shadcn components from that app's directory, for example:

```bash
pnpm --filter @healthspan/social-web exec shadcn add input
```

Prefer the shared package for primitives used across portals; keep portal-specific components in that portal.
