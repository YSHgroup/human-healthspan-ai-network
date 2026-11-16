import type { Metadata } from "next";

import { PageShell, SiteFooter, SiteHeader } from "@healthspan/ui/composites";
import { ThemeToggle } from "@healthspan/ui/theme-toggle";

import { SocialFeed } from "./social-feed";

export const metadata: Metadata = {
  title: "Community Feed",
  description: "Browse public questions and discussions from the Healthspan Network community.",
  alternates: { canonical: "/feed" },
};

export default function SocialFeedPage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <SiteHeader
        title="Community Feed"
        eyebrow="Social Portal · Public discussions"
        homeHref="/"
        themeToggle={<ThemeToggle />}
        links={[
          { label: "Communities", href: "/communities" },
          { label: "Home", href: "/" },
          { label: "Messages", href: "/messages" },
          { label: "General AI", href: "/ai" },
        ]}
      />
      <main>
        <PageShell className="max-w-6xl">
          <div className="mb-8 max-w-3xl">
            <h1 className="font-display text-4xl tracking-tight">Questions and ideas, in the open.</h1>
            <p className="mt-2 text-muted-foreground">
              Browse public discussions. Sign in to publish a question or discussion and report
              content that needs review.
            </p>
          </div>
          <SocialFeed apiBaseUrl={process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"} />
        </PageShell>
      </main>
      <SiteFooter note="Community discussions are public. Do not share private health information." />
    </div>
  );
}
