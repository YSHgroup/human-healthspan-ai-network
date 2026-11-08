import type { Metadata } from "next";

import { MessagingPanel } from "@healthspan/ui/communication";
import { PageShell, SiteFooter, SiteHeader } from "@healthspan/ui/composites";
import { ThemeToggle } from "@healthspan/ui/theme-toggle";

export const metadata: Metadata = {
  title: "Messages",
  robots: { index: false, follow: false },
};

export default function MessagesPage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <SiteHeader
        title="Messages"
        eyebrow="Social Portal · Text only"
        homeHref="/"
        themeToggle={<ThemeToggle />}
        links={[
          { label: "Communities", href: "/communities" },
          { label: "Community feed", href: "/feed" },
          { label: "Home", href: "/" },
          { label: "General AI", href: "/ai" },
        ]}
      />
      <main>
        <PageShell className="max-w-5xl">
          <div className="mb-6">
            <h1 className="font-display text-4xl tracking-tight">Stay in the conversation.</h1>
            <p className="mt-2 text-muted-foreground">
              Direct and group text messaging across your localhost portals.
            </p>
          </div>
          <MessagingPanel apiBaseUrl={process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"} />
        </PageShell>
      </main>
      <SiteFooter note="Private messages are not used for AI learning." />
    </div>
  );
}
