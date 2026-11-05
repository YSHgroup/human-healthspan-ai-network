import {
  Bookmark,
  CircleUserRound,
  Heart,
  House,
  LockKeyhole,
  Settings2,
  Sparkles,
} from "lucide-react";

import { Alert, AlertDescription } from "@healthspan/ui/alert";
import { Badge } from "@healthspan/ui/badge";
import { Button } from "@healthspan/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@healthspan/ui/card";
import {
  EmptyState,
  PageShell,
  ProfileAvatar,
  SectionHeading,
  Separator,
  SiteFooter,
  SiteHeader,
} from "@healthspan/ui/composites";
import { Skeleton } from "@healthspan/ui/skeleton";
import { ThemeToggle } from "@healthspan/ui/theme-toggle";

const socialPortalUrl = process.env.PUBLIC_APP_URL ?? "http://localhost:3000";

const sections = [
  { label: "Overview", href: "#overview", icon: House },
  { label: "Your profile", href: "#profile", icon: CircleUserRound },
  { label: "Saved knowledge", href: "#saved", icon: Bookmark },
  { label: "Privacy settings", href: "#privacy", icon: Settings2 },
];

export default function PersonalHome() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <SiteHeader
        title="Your personal space"
        eyebrow="Personal Portal · Foundation"
        homeHref="#overview"
        links={sections}
        themeToggle={<ThemeToggle />}
        actions={
          <div className="flex items-center gap-2">
            <a
              href="/messages"
              className="inline-flex min-h-11 items-center rounded-full border border-border bg-card px-3 text-sm font-medium text-foreground transition-colors hover:bg-accent focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/30"
            >
              Messages
            </a>
            <a
              href={socialPortalUrl}
              className="hidden min-h-11 items-center gap-2 rounded-full border border-border bg-card px-4 text-sm font-medium text-foreground transition-colors hover:bg-accent focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/30 sm:inline-flex"
            >
              Community <Sparkles aria-hidden="true" className="size-4" />
            </a>
          </div>
        }
      />
      <main id="overview">
        <PageShell wide className="grid gap-8 xl:grid-cols-[15rem_minmax(0,1fr)]">
          <aside className="hidden xl:block">
            <nav
              aria-label="Personal portal sections"
              className="sticky top-24 grid gap-1 rounded-xl border border-border/70 bg-card/70 p-2 shadow-xs"
            >
              <p className="px-3 py-2 text-xs font-semibold tracking-[0.14em] text-muted-foreground uppercase">
                Your space
              </p>
              {sections.map(({ label, href, icon: Icon }, index) => (
                <a
                  key={label}
                  href={href}
                  aria-current={index === 0 ? "page" : undefined}
                  className={`flex min-h-11 items-center gap-3 rounded-lg px-3 text-sm transition-colors focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/30 ${
                    index === 0
                      ? "bg-accent text-accent-foreground"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  }`}
                >
                  <Icon aria-hidden="true" className="size-4" />
                  {label}
                </a>
              ))}
              <Separator className="my-2" />
              <p className="px-3 pb-2 text-xs leading-relaxed text-muted-foreground">
                Personal health information stays private by default.
              </p>
            </nav>
          </aside>

          <div className="min-w-0">
            <nav
              aria-label="Personal portal sections"
              className="mb-7 flex gap-2 overflow-x-auto pb-2 xl:hidden"
            >
              {sections.map(({ label, href, icon: Icon }) => (
                <a
                  key={label}
                  href={href}
                  className="inline-flex min-h-11 shrink-0 items-center gap-2 rounded-full border border-border bg-card px-4 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/30"
                >
                  <Icon aria-hidden="true" className="size-4" />
                  {label}
                </a>
              ))}
            </nav>

            <section aria-labelledby="welcome-heading" className="mb-7">
              <Badge variant="outline" className="mb-4 gap-1.5 bg-accent/70">
                <Heart aria-hidden="true" />A calmer space for your health journey
              </Badge>
              <h1
                id="welcome-heading"
                className="max-w-3xl font-display text-4xl leading-tight tracking-tight sm:text-5xl"
              >
                Your health story, on your terms.
              </h1>
              <p className="mt-3 max-w-2xl text-base leading-relaxed text-muted-foreground">
                This private portal is a foundation. Account, health-record, and personalization
                features are not connected yet.
              </p>
            </section>

            <Alert className="mb-7 flex items-start gap-3 border-success/25 bg-success-muted/60">
              <LockKeyhole aria-hidden="true" className="mt-0.5 size-5 shrink-0 text-success" />
              <AlertDescription className="pl-0 text-foreground">
                <strong className="font-semibold">Private by default.</strong> This preview has no
                connected personal health data, and it does not save health information.
              </AlertDescription>
            </Alert>

            <section id="profile" aria-labelledby="profile-heading" className="mb-8 scroll-mt-24">
              <Card className="overflow-hidden border-primary/10 bg-gradient-to-br from-card to-accent/35 shadow-sm">
                <CardContent className="flex flex-col gap-5 py-5 sm:flex-row sm:items-center sm:justify-between sm:py-6">
                  <div className="flex items-center gap-4">
                    <ProfileAvatar initials="HS" className="size-14 text-base" />
                    <div className="min-w-0">
                      <div className="mb-1 flex flex-wrap items-center gap-2">
                        <h2 id="profile-heading" className="font-display text-xl">
                          Your profile
                        </h2>
                        <Badge variant="warning">Setup planned</Badge>
                      </div>
                      <p className="max-w-xl text-sm leading-relaxed text-muted-foreground">
                        Profile details will appear here when account setup is available. Nothing
                        has been entered or saved.
                      </p>
                    </div>
                  </div>
                  <Button variant="outline" disabled className="shrink-0">
                    <Settings2 aria-hidden="true" />
                    Profile setup planned
                  </Button>
                </CardContent>
              </Card>
            </section>

            <section id="saved" aria-labelledby="saved-heading" className="mb-8 scroll-mt-24">
              <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
                <SectionHeading
                  eyebrow="Your library"
                  title="Saved knowledge"
                  description="A place for resources you choose to keep, when saving is available."
                />
                <Badge variant="outline">Planned</Badge>
              </div>
              <EmptyState
                icon={Bookmark}
                title="Your library is ready when you are"
                description="Saved articles and notes are not available in this foundation. No sample health records or saved items are shown."
                className="min-h-56"
              />
            </section>

            <section
              id="privacy"
              aria-labelledby="privacy-heading"
              className="grid gap-4 lg:grid-cols-2"
            >
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between gap-3">
                    <span className="grid size-10 place-items-center rounded-xl bg-accent text-accent-foreground">
                      <LockKeyhole aria-hidden="true" className="size-5" />
                    </span>
                    <Badge variant="outline">Planned controls</Badge>
                  </div>
                  <CardTitle id="privacy-heading" className="pt-2 font-display text-xl">
                    Privacy settings
                  </CardTitle>
                  <CardDescription className="leading-relaxed">
                    Sharing controls and consent settings will be designed before personal records
                    are connected.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <EmptyState
                    icon={LockKeyhole}
                    title="No settings to change yet"
                    description="There are no connected records or sharing preferences in this preview."
                    className="min-h-44 border-0 bg-surface-raised/60"
                  />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between gap-3">
                    <span className="grid size-10 place-items-center rounded-xl bg-secondary text-secondary-foreground">
                      <Sparkles aria-hidden="true" className="size-5" />
                    </span>
                    <Badge variant="outline">Illustration only</Badge>
                  </div>
                  <CardTitle className="pt-2 font-display text-xl">
                    Future dashboard panel
                  </CardTitle>
                  <CardDescription className="leading-relaxed">
                    A loading-state example for a future panel. It contains no health data.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div
                    role="img"
                    aria-label="Example loading placeholder with no connected health data"
                    className="grid gap-3 rounded-xl border border-border/70 bg-surface-raised/60 p-4"
                  >
                    <div className="flex items-center gap-3">
                      <Skeleton className="size-10 rounded-full" />
                      <div className="grid flex-1 gap-2">
                        <Skeleton className="h-3 w-1/3" />
                        <Skeleton className="h-3 w-1/2" />
                      </div>
                    </div>
                    <Skeleton className="h-20 w-full rounded-lg" />
                  </div>
                </CardContent>
              </Card>
            </section>
          </div>
        </PageShell>
      </main>
      <SiteFooter note="Private by default · No health information is connected to this preview." />
    </div>
  );
}
