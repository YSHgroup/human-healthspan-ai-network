import type { Metadata } from "next";

import { AIChatPanel } from "@healthspan/ui/communication";
import { PageShell, SiteFooter, SiteHeader } from "@healthspan/ui/composites";
import { ThemeToggle } from "@healthspan/ui/theme-toggle";

export const metadata: Metadata = {
  title: "General Platform AI",
  robots: { index: false, follow: false },
};

export default function GeneralAIPage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <SiteHeader
        title="General Platform AI"
        eyebrow="General knowledge · Source-conscious"
        homeHref="/"
        themeToggle={<ThemeToggle />}
        links={[{ label: "Community", href: "/" }, { label: "Messages", href: "/messages" }]}
      />
      <main>
        <PageShell className="max-w-4xl">
          <div className="mb-6">
            <h1 className="font-display text-4xl tracking-tight">Ask a question.</h1>
            <p className="mt-2 text-muted-foreground">
              AI responses may be incomplete. Do not enter private health or research information.
            </p>
          </div>
          <AIChatPanel
            apiBaseUrl={process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}
            environment="general"
          />
        </PageShell>
      </main>
      <SiteFooter note="AI output is informational and is not medical advice or a validated finding." />
    </div>
  );
}
