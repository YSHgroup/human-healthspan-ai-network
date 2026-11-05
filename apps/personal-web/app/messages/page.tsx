import type { Metadata } from "next";

import { MessagingPanel } from "@healthspan/ui/communication";
import { PageShell, SiteFooter, SiteHeader } from "@healthspan/ui/composites";
import { ThemeToggle } from "@healthspan/ui/theme-toggle";

export const metadata: Metadata = {
  title: "Messages",
  robots: { index: false, follow: false },
};

export default function PersonalMessagesPage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <SiteHeader
        title="Messages"
        eyebrow="Personal Portal · Text only"
        homeHref="/"
        themeToggle={<ThemeToggle />}
        links={[
          { label: "Personal space", href: "/" },
          { label: "Social Portal", href: "http://localhost:3000" },
        ]}
      />
      <main>
        <PageShell className="max-w-5xl">
          <div className="mb-6">
            <h1 className="font-display text-4xl tracking-tight">Your conversations.</h1>
            <p className="mt-2 text-muted-foreground">
              Shared identity keeps your messages available across the portals.
            </p>
          </div>
          <MessagingPanel apiBaseUrl={process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"} />
        </PageShell>
      </main>
      <SiteFooter note="Private messages are not used for AI learning." />
    </div>
  );
}
