import { StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  ArrowUpRight,
  ClipboardList,
  CircleDot,
  FileClock,
  Info,
  LayoutDashboard,
  Moon,
  ShieldCheck,
  Sun,
  UsersRound,
} from "lucide-react";

import { Alert, AlertDescription } from "@healthspan/ui/alert";
import { Badge } from "@healthspan/ui/badge";
import { Button } from "@healthspan/ui/button";
import {
  EmptyState,
  PageShell,
  SectionHeading,
  SiteFooter,
  SiteHeader,
} from "@healthspan/ui/composites";
import { Card, CardContent, CardHeader, CardTitle } from "@healthspan/ui/card";
import "./styles.css";

const socialPortalUrl = import.meta.env.VITE_SOCIAL_APP_URL ?? "http://localhost:3000";

const navigation = [
  { label: "Overview", href: "#overview", icon: LayoutDashboard },
  { label: "Users & organizations", href: "#users", icon: UsersRound },
  { label: "Moderation", href: "#moderation", icon: ClipboardList },
  { label: "Audit & security", href: "#audit", icon: FileClock },
];

function AdminThemeToggle() {
  const [dark, setDark] = useState(false);

  useEffect(() => {
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const syncTheme = () => {
      const isDark = document.documentElement.classList.contains("dark") || media.matches;
      document.documentElement.classList.toggle("dark", isDark);
      setDark(isDark);
    };
    syncTheme();
    media.addEventListener("change", syncTheme);
    return () => media.removeEventListener("change", syncTheme);
  }, []);

  function toggleTheme() {
    const nextDark = !dark;
    document.documentElement.classList.toggle("dark", nextDark);
    setDark(nextDark);
  }

  return (
    <Button
      type="button"
      variant="outline"
      size="icon"
      onClick={toggleTheme}
      aria-label={`Switch to ${dark ? "light" : "dark"} theme`}
      title={`Switch to ${dark ? "light" : "dark"} theme`}
    >
      {dark ? <Sun aria-hidden="true" /> : <Moon aria-hidden="true" />}
    </Button>
  );
}

function AdminApp() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <a
        href="#admin-main"
        className="sr-only z-50 rounded-md bg-card px-4 py-3 text-foreground focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus-visible:ring-[3px] focus-visible:ring-ring/40"
      >
        Skip to administration
      </a>
      <SiteHeader
        title="Healthspan Operations"
        eyebrow="Administration"
        homeHref="#overview"
        links={navigation.map(({ label, href }) => ({ label, href }))}
        themeToggle={<AdminThemeToggle />}
        actions={
          <a
            href={socialPortalUrl}
            className="hidden min-h-11 items-center gap-2 rounded-full border border-border bg-card px-4 text-sm font-medium text-foreground transition-colors hover:bg-accent focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/30 sm:inline-flex"
          >
            Public network <ArrowUpRight aria-hidden="true" className="size-4" />
          </a>
        }
      />
      <main id="admin-main">
        <PageShell wide className="grid gap-6 py-6 lg:grid-cols-[14rem_minmax(0,1fr)] lg:gap-8">
          <aside className="hidden lg:block">
            <nav
              aria-label="Administration sections"
              className="sticky top-24 grid gap-1 rounded-xl border border-border/70 bg-card/70 p-2 shadow-xs"
            >
              <p className="px-3 py-2 text-xs font-semibold tracking-[0.14em] text-muted-foreground uppercase">
                Platform
              </p>
              {navigation.map(({ label, href, icon: Icon }, index) => (
                <a
                  key={label}
                  href={href}
                  aria-current={index === 0 ? "page" : undefined}
                  className={`flex min-h-11 items-center gap-2.5 rounded-lg px-3 text-sm transition-colors focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/30 ${
                    index === 0
                      ? "bg-accent text-accent-foreground"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  }`}
                >
                  <Icon aria-hidden="true" className="size-4" />
                  {label}
                </a>
              ))}
              <div className="mt-2 border-t border-border px-3 pt-3 pb-2">
                <Badge variant="outline" className="gap-1.5">
                  <CircleDot aria-hidden="true" />
                  Foundation
                </Badge>
              </div>
            </nav>
          </aside>

          <div className="min-w-0">
            <nav
              aria-label="Administration sections"
              className="mb-5 flex gap-2 overflow-x-auto pb-2 lg:hidden"
            >
              {navigation.map(({ label, href, icon: Icon }) => (
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

            <section id="overview" aria-labelledby="admin-heading" className="scroll-mt-24">
              <div className="mb-5 flex flex-wrap items-end justify-between gap-4">
                <SectionHeading
                  as="h1"
                  id="admin-heading"
                  eyebrow="Operations & governance"
                  title="A clear view of platform foundations."
                  description="The administration app is a visual foundation for future oversight. No administrative actions or live platform data are connected."
                />
                <Badge variant="outline" className="gap-1.5">
                  <Activity aria-hidden="true" />
                  Local foundation
                </Badge>
              </div>
              <Alert className="mb-6 flex items-start gap-3 border-warning/25 bg-warning-muted/60">
                <Info
                  aria-hidden="true"
                  className="mt-0.5 size-5 shrink-0 text-warning-foreground"
                />
                <AlertDescription className="pl-0 text-foreground">
                  Authentication, role checks, audit logging, and API integration must be
                  implemented before this interface can manage platform data.
                </AlertDescription>
              </Alert>
            </section>

            <section id="users" aria-labelledby="users-heading" className="mb-6 scroll-mt-24">
              <Card className="overflow-hidden">
                <CardHeader className="flex flex-col gap-3 border-b border-border/70 bg-surface-raised/50 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex items-center justify-between gap-3">
                    <CardTitle id="users-heading" className="font-display text-xl">
                      Users and organizations
                    </CardTitle>
                    <Badge variant="outline">Planned</Badge>
                  </div>
                  <Button variant="outline" disabled className="sm:w-auto">
                    <UsersRound aria-hidden="true" />
                    User management planned
                  </Button>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="overflow-x-auto">
                    <table className="w-full min-w-[38rem] text-left text-sm">
                      <caption className="sr-only">
                        Placeholder for future user and organization records; no records are
                        connected.
                      </caption>
                      <thead className="border-b border-border/70 bg-surface-raised/30 text-xs text-muted-foreground">
                        <tr>
                          <th scope="col" className="px-5 py-3 font-medium">
                            Name
                          </th>
                          <th scope="col" className="px-5 py-3 font-medium">
                            Organization
                          </th>
                          <th scope="col" className="px-5 py-3 font-medium">
                            Status
                          </th>
                          <th scope="col" className="px-5 py-3 font-medium">
                            Access
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td colSpan={4} className="p-4">
                            <EmptyState
                              icon={UsersRound}
                              title="No user records"
                              description="User and organization records are not connected in this foundation."
                              className="min-h-40 border-0 bg-transparent"
                            />
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </section>

            <div className="grid gap-4 md:grid-cols-2">
              <section
                id="moderation"
                aria-labelledby="moderation-heading"
                className="scroll-mt-24"
              >
                <Card className="h-full">
                  <CardHeader>
                    <div className="flex items-center justify-between gap-3">
                      <span className="grid size-10 place-items-center rounded-xl bg-accent text-accent-foreground">
                        <ClipboardList aria-hidden="true" className="size-5" />
                      </span>
                      <Badge variant="outline">Planned</Badge>
                    </div>
                    <CardTitle id="moderation-heading" className="pt-2 font-display text-lg">
                      Community moderation
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <EmptyState
                      icon={ClipboardList}
                      title="No moderation queue"
                      description="Moderation tools and reports are not connected."
                      className="min-h-40 border-0 bg-surface-raised/50"
                    />
                  </CardContent>
                </Card>
              </section>

              <section id="audit" aria-labelledby="audit-heading" className="scroll-mt-24">
                <Card className="h-full">
                  <CardHeader>
                    <div className="flex items-center justify-between gap-3">
                      <span className="grid size-10 place-items-center rounded-xl bg-secondary text-secondary-foreground">
                        <FileClock aria-hidden="true" className="size-5" />
                      </span>
                      <Badge variant="outline">Planned</Badge>
                    </div>
                    <CardTitle id="audit-heading" className="pt-2 font-display text-lg">
                      Audit and security
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <EmptyState
                      icon={ShieldCheck}
                      title="Audit events are not connected"
                      description="Auditable operations and security review must be implemented before administration is enabled."
                      className="min-h-40 border-0 bg-surface-raised/50"
                    />
                  </CardContent>
                </Card>
              </section>
            </div>
          </div>
        </PageShell>
      </main>
      <SiteFooter note="Admin foundation · No administrative access or platform data is connected." />
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <AdminApp />
  </StrictMode>,
);
