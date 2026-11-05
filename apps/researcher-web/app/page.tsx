import {
  ArrowUpRight,
  BookOpenCheck,
  CircleHelp,
  FlaskConical,
  FolderKanban,
  LockKeyhole,
  Microscope,
  ShieldCheck,
} from "lucide-react";

import { Alert, AlertDescription } from "@healthspan/ui/alert";
import { Badge } from "@healthspan/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@healthspan/ui/card";
import {
  EmptyState,
  EvidenceBadge,
  PageShell,
  SectionHeading,
  SiteFooter,
  SiteHeader,
  Separator,
  VerificationBadge,
} from "@healthspan/ui/composites";
import { Skeleton } from "@healthspan/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@healthspan/ui/tabs";
import { ThemeToggle } from "@healthspan/ui/theme-toggle";
import { ResearcherCommandPalette } from "../components/command-palette";

const socialPortalUrl = process.env.PUBLIC_APP_URL ?? "http://localhost:3000";

const workspaceLinks = [
  { label: "Overview", href: "#overview", icon: Microscope },
  { label: "Projects", href: "#projects", icon: FolderKanban },
  { label: "Evidence", href: "#evidence", icon: BookOpenCheck },
];

const evidenceExamples = [
  {
    evidenceClass: "peer_reviewed" as const,
    title: "Peer-reviewed source",
    detail: "Example classification only. No paper or result is attached.",
    icon: BookOpenCheck,
  },
  {
    evidenceClass: "preprint" as const,
    title: "Preprint",
    detail: "Example classification only. Preprints have not completed peer review.",
    icon: FlaskConical,
  },
  {
    evidenceClass: "ai_generated_hypothesis" as const,
    title: "AI-generated hypothesis",
    detail: "A proposal, not a validated finding. No AI output is connected.",
    icon: CircleHelp,
  },
];

export default function ResearcherHome() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <a
        href="#workspace-main"
        className="sr-only z-50 rounded-md bg-card px-4 py-3 text-foreground focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus-visible:ring-[3px] focus-visible:ring-ring/40"
      >
        Skip to workspace
      </a>
      <SiteHeader
        title="Research workspace"
        eyebrow="Researcher Portal · Foundation"
        homeHref="#overview"
        links={workspaceLinks}
        themeToggle={<ThemeToggle />}
        actions={
          <div className="flex items-center gap-2">
            <a
              href="/ai"
              className="inline-flex min-h-11 items-center rounded-full border border-border bg-card px-3 text-sm font-medium text-foreground transition-colors hover:bg-accent focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/30"
            >
              Scientist prototype
            </a>
            <ResearcherCommandPalette />
          </div>
        }
      />
      <main id="workspace-main">
        <PageShell wide className="grid gap-8 xl:grid-cols-[15rem_minmax(0,1fr)]">
          <aside className="hidden xl:block">
            <nav
              aria-label="Research workspace sections"
              className="sticky top-24 grid gap-1 rounded-xl border border-border/70 bg-card/70 p-2 shadow-xs"
            >
              <p className="px-3 py-2 text-xs font-semibold tracking-[0.14em] text-muted-foreground uppercase">
                Workspace
              </p>
              {workspaceLinks.map(({ label, href, icon: Icon }, index) => (
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
              <div className="px-3 pb-2">
                <VerificationBadge state="unverified" />
                <p className="mt-2 text-xs leading-relaxed text-muted-foreground">
                  Example status only. No researcher profile is connected.
                </p>
              </div>
            </nav>
          </aside>

          <div className="min-w-0">
            <nav
              aria-label="Research workspace sections"
              className="mb-7 flex gap-2 overflow-x-auto pb-2 xl:hidden"
            >
              {workspaceLinks.map(({ label, href, icon: Icon }) => (
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

            <section id="overview" aria-labelledby="workspace-title" className="scroll-mt-24">
              <div className="mb-6 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
                <div>
                  <Badge variant="outline" className="mb-4 gap-1.5 bg-accent/70">
                    <Microscope aria-hidden="true" />
                    Protected research environment
                  </Badge>
                  <h1
                    id="workspace-title"
                    className="font-display text-4xl leading-tight tracking-tight sm:text-5xl"
                  >
                    Research, with the right foundations.
                  </h1>
                  <p className="mt-3 max-w-2xl text-base leading-relaxed text-muted-foreground">
                    A focused space for careful collaboration. This foundation is not connected to
                    accounts, projects, files, or research data.
                  </p>
                </div>
                <a
                  href={socialPortalUrl}
                  className="inline-flex min-h-11 shrink-0 items-center justify-center gap-2 rounded-full border border-border bg-card px-4 text-sm font-medium text-foreground transition-colors hover:bg-accent focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/30"
                >
                  Network principles <ArrowUpRight aria-hidden="true" className="size-4" />
                </a>
              </div>

              <Alert className="mb-7 flex items-start gap-3 border-warning/25 bg-warning-muted/60">
                <LockKeyhole
                  aria-hidden="true"
                  className="mt-0.5 size-5 shrink-0 text-warning-foreground"
                />
                <AlertDescription className="pl-0 text-foreground">
                  <strong className="font-semibold">Portal access is not research access.</strong>{" "}
                  Membership, organization, and project permissions must be explicitly verified by
                  the backend before restricted resources are available.
                </AlertDescription>
              </Alert>
            </section>

            <section id="projects" aria-labelledby="projects-heading" className="mb-8 scroll-mt-24">
              <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
                <SectionHeading
                  eyebrow="Your work"
                  title="Projects"
                  description="Project membership and access controls are not available in this foundation."
                />
                <Badge variant="outline">Planned</Badge>
              </div>
              <EmptyState
                icon={FolderKanban}
                title="No projects are connected"
                description="Projects will appear here after researcher identity, organization access, and backend permissions are implemented."
                className="min-h-52"
              />
            </section>

            <section id="evidence" aria-labelledby="evidence-heading" className="mb-8 scroll-mt-24">
              <div className="mb-5">
                <SectionHeading
                  eyebrow="Evidence and provenance"
                  title="Keep the source in view."
                  description="Evidence labels distinguish source classes. They do not imply quality, certainty, or endorsement."
                />
              </div>
              <Tabs defaultValue="overview">
                <TabsList aria-label="Research workspace views">
                  <TabsTrigger value="overview">Overview</TabsTrigger>
                  <TabsTrigger value="evidence">Evidence classes</TabsTrigger>
                </TabsList>
                <TabsContent value="overview">
                  <div className="grid gap-4 md:grid-cols-3">
                    {evidenceExamples.map(({ evidenceClass, title, detail, icon: Icon }) => (
                      <Card
                        key={title}
                        className="h-full bg-gradient-to-br from-card to-surface-raised/70"
                      >
                        <CardHeader>
                          <div className="flex items-center justify-between gap-2">
                            <span className="grid size-10 place-items-center rounded-xl bg-accent text-accent-foreground">
                              <Icon aria-hidden="true" className="size-5" />
                            </span>
                            <EvidenceBadge evidenceClass={evidenceClass} />
                          </div>
                          <CardTitle className="pt-2 font-display text-lg">{title}</CardTitle>
                          <CardDescription className="leading-relaxed">{detail}</CardDescription>
                        </CardHeader>
                      </Card>
                    ))}
                  </div>
                  <p className="mt-3 text-xs leading-relaxed text-muted-foreground">
                    Illustrative labels only — this page contains no publications, study results, or
                    project findings.
                  </p>
                </TabsContent>
                <TabsContent value="evidence">
                  <Card>
                    <CardHeader>
                      <CardTitle className="font-display text-lg">
                        Evidence review is planned
                      </CardTitle>
                      <CardDescription>
                        Source linking, provenance, appraisal, and uncertainty communication are not
                        connected yet.
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <EmptyState
                        icon={BookOpenCheck}
                        title="No research sources"
                        description="Evidence records will only be shown when they are connected to verifiable sources."
                        className="min-h-44 border-0 bg-surface-raised/50"
                      />
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>
            </section>

            <section aria-labelledby="loading-heading" className="grid gap-4 lg:grid-cols-2">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between gap-3">
                    <CardTitle id="loading-heading" className="font-display text-lg">
                      Loading-state example
                    </CardTitle>
                    <Badge variant="outline">Illustration only</Badge>
                  </div>
                  <CardDescription>No project data is being loaded or displayed.</CardDescription>
                </CardHeader>
                <CardContent>
                  <div
                    role="img"
                    aria-label="Example loading placeholder with no research data"
                    className="grid gap-3 rounded-xl border border-border/70 bg-surface-raised/60 p-4"
                  >
                    <Skeleton className="h-3 w-1/3" />
                    <Skeleton className="h-3 w-2/3" />
                    <Skeleton className="h-20 w-full rounded-lg" />
                  </div>
                </CardContent>
              </Card>
              <Card className="border-primary/10 bg-gradient-to-br from-card to-accent/35">
                <CardHeader>
                  <div className="flex items-center justify-between gap-3">
                    <span className="grid size-10 place-items-center rounded-xl bg-accent text-accent-foreground">
                      <ShieldCheck aria-hidden="true" className="size-5" />
                    </span>
                    <Badge variant="outline">Verification planned</Badge>
                  </div>
                  <CardTitle className="pt-2 font-display text-lg">
                    Professional verification
                  </CardTitle>
                  <CardDescription>
                    Credentials and verification status must be established before they can be
                    represented as verified.
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex items-center gap-3">
                  <VerificationBadge state="unverified" />
                  <span className="text-xs text-muted-foreground">
                    Example badge only · no profile exists
                  </span>
                </CardContent>
              </Card>
            </section>
          </div>
        </PageShell>
      </main>
      <SiteFooter note="Research workspace foundation · No research data is connected." />
    </div>
  );
}
