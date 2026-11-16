import type { Metadata } from "next";

import { PageShell, SiteFooter, SiteHeader } from "@healthspan/ui/composites";
import { ThemeToggle } from "@healthspan/ui/theme-toggle";

import { CommunityHub } from "./community-hub";

export const metadata: Metadata = {
  title: "Communities",
  description: "Join communities and take part in moderated Healthspan Network discussions.",
  robots: { index: false, follow: false },
};

export default function CommunitiesPage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <SiteHeader
        title="Communities"
        eyebrow="Social Portal · Shared interests"
        homeHref="/"
        themeToggle={<ThemeToggle />}
        links={[
          { label: "Community feed", href: "/feed" },
          { label: "Messages", href: "/messages" },
          { label: "General AI", href: "/ai" },
        ]}
      />
      <main>
        <PageShell className="max-w-6xl">
          <div className="mb-8 max-w-3xl">
            <h1 className="font-display text-4xl tracking-tight">Find your community.</h1>
            <p className="mt-2 text-muted-foreground">
              Join open communities or apply to restricted research communities. Every community
              has its own membership and moderation.
            </p>
          </div>
          <CommunityHub apiBaseUrl={process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"} />
        </PageShell>
      </main>
      <SiteFooter
        note="Community membership does not grant access to separate research projects or resources."
      />
    </div>
  );
}
