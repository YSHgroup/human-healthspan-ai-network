# Shared shadcn/ui components

`@healthspan/ui` contains Base UI-backed shadcn primitives and reusable composites shared by the
Social, Personal, Researcher, and Admin apps. Prefer these components over app-local duplicates.

## Primitives

The package exports Button, Badge, Card, Alert, Input, Label, Textarea, Select, Tabs, Dialog,
DropdownMenu, Tooltip, Avatar, Skeleton, Separator, Sheet, Sonner, and Command components from its
root entry point. Individual components are also available through package subpaths, for example
`@healthspan/ui/button` and `@healthspan/ui/dialog`.

The package also provides theme controls, reduced-motion-aware `Reveal` and `StatCard` components,
and shared layout/content composites: `PageShell`, `SiteHeader`, `SiteFooter`, `SectionHeading`,
`FeatureCard`, `EmptyState`, `PortalSwitcher`, `EvidenceBadge`, and `VerificationBadge`.

`EvidenceBadge` covers every `EvidenceClass` in `@healthspan/shared-types`. Evidence and
verification status always use a text label and icon alongside color; color is never the only
signal. The Personal and Researcher portals are foundations only: sample badges are clearly
identified and no source, identity, or research records are implied.

## App setup

Each Next.js portal has a `components.json`, Tailwind CSS v4 setup, and `@/lib/utils` alias. Admin
uses React + Vite with its own shadcn config and Tailwind Vite plugin. Keep local package ranges as
`"*"` so both npm and pnpm workspace installs remain supported.

Prefer the shared package for primitives used across portals; keep truly app-specific composition
in that app. For new registry components, run the shadcn CLI from the target app directory, then
move reusable primitives into this package when appropriate:

```bash
pnpm --filter @healthspan/social-web exec shadcn add input
```
