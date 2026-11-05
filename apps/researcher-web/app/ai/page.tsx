import type { Metadata } from "next";

import { AIChatPanel } from "@healthspan/ui/communication";
import { PageShell, SiteFooter, SiteHeader } from "@healthspan/ui/composites";
import { ThemeToggle } from "@healthspan/ui/theme-toggle";

export const metadata: Metadata = {
  title: "Private AI Scientist",
  robots: { index: false, follow: false },
};

export default function ScientistPage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <SiteHeader
        title="Private AI Scientist"
        eyebrow="Researcher Portal · Restricted prototype"
        homeHref="/"
        themeToggle={<ThemeToggle />}
        links={[{ label: "Research workspace", href: "/" }]}
      />
      <main>
        <PageShell className="max-w-4xl">
          <div className="mb-6">
            <h1 className="font-display text-4xl tracking-tight">Research assistance prototype.</h1>
            <p className="mt-2 text-muted-foreground">
              Access is granted only by explicit researcher approval. No private research corpus is connected.
            </p>
          </div>
          <AIChatPanel
            apiBaseUrl={process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}
            environment="scientist"
          />
        </PageShell>
      </main>
      <SiteFooter note="Hypotheses are proposals; this prototype does not retrieve or validate literature." />
    </div>
  );
}
