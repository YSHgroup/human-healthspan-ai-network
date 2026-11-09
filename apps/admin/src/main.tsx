import { StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  ArrowUpRight,
  ClipboardList,
  CircleDot,
  FileClock,
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
const apiUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const navigation = [
  { label: "Overview", href: "#overview", icon: LayoutDashboard },
  { label: "Community requests", href: "#communities", icon: UsersRound },
  { label: "Moderation", href: "#moderation", icon: ClipboardList },
  { label: "Audit & security", href: "#audit", icon: FileClock },
];

type CommunityRequest = {
  id: string;
  requester_display_name: string;
  slug: string;
  name: string;
  description: string;
  access_type: "open" | "restricted";
  created_at: string;
};

type ModerationReport = {
  id: string;
  reason: string;
  status: "pending" | "escalated";
  created_at: string;
  target_kind: "post" | "comment";
  target_body: string;
  target_author_display_name: string;
  community_name: string | null;
};

type ModerationAppeal = {
  id: string;
  reason: string;
  created_at: string;
  action: "hide" | "remove" | "warn" | "suspend";
  action_reason: string;
};

async function adminRequest<T>(path: string, body?: object): Promise<T> {
  const response = await fetch(`${apiUrl}/api/v1/admin${path}`, {
    method: body ? "POST" : "GET",
    credentials: "include",
    headers: body
      ? { Accept: "application/json", "Content-Type": "application/json" }
      : { Accept: "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  const result = (await response.json()) as { message?: string };
  if (!response.ok) {
    throw new Error(result.message ?? `Administration request failed (${response.status})`);
  }
  return result as T;
}

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
  const [communityRequests, setCommunityRequests] = useState<CommunityRequest[]>([]);
  const [reports, setReports] = useState<ModerationReport[]>([]);
  const [appeals, setAppeals] = useState<ModerationAppeal[]>([]);
  const [reportReasons, setReportReasons] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  async function loadQueues() {
    setLoading(true);
    setError(null);
    try {
      const [requests, pendingReports, pendingAppeals] = await Promise.all([
        adminRequest<CommunityRequest[]>("/communities/requests"),
        adminRequest<ModerationReport[]>("/moderation/reports"),
        adminRequest<ModerationAppeal[]>("/moderation/appeals"),
      ]);
      setCommunityRequests(requests);
      setReports(pendingReports);
      setAppeals(pendingAppeals);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to load platform operations.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadQueues();
  }, []);

  async function submitDecision(path: string, body: object, key: string, message: string) {
    setBusy(key);
    setError(null);
    setNotice(null);
    try {
      await adminRequest(path, body);
      setNotice(message);
      await loadQueues();
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "The platform action could not be completed.",
      );
    } finally {
      setBusy(null);
    }
  }

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
                  Community + safety
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
                  title="Community approval and platform safety."
                  description="Review community requests, global content reports, and escalations using your authenticated platform administrator account."
                />
                <Badge variant="outline" className="gap-1.5">
                  <Activity aria-hidden="true" />
                  Platform operations
                </Badge>
              </div>
              {error && (
                <Alert role="alert" className="mb-4 border-destructive/30 bg-destructive/5">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              {notice && (
                <Alert role="status" className="mb-4 border-success/30 bg-success/5">
                  <AlertDescription>{notice}</AlertDescription>
                </Alert>
              )}
              {loading && (
                <p className="mb-4 text-sm text-muted-foreground" role="status">
                  Loading platform queues…
                </p>
              )}
            </section>

            <section
              id="communities"
              aria-labelledby="communities-heading"
              className="mb-6 scroll-mt-24"
            >
              <Card className="overflow-hidden">
                <CardHeader className="flex flex-col gap-3 border-b border-border/70 bg-surface-raised/50 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex items-center justify-between gap-3">
                    <CardTitle id="communities-heading" className="font-display text-xl">
                      Community creation requests
                    </CardTitle>
                    <Badge variant="outline">{communityRequests.length} pending</Badge>
                  </div>
                  <Button
                    variant="outline"
                    onClick={() => void loadQueues()}
                    disabled={loading}
                    className="sm:w-auto"
                  >
                    <Activity aria-hidden="true" />
                    Refresh queues
                  </Button>
                </CardHeader>
                <CardContent className="grid gap-3 p-4">
                  {communityRequests.length === 0 && !loading ? (
                    <EmptyState
                      icon={UsersRound}
                      title="No pending community requests"
                      description="New requests will appear here for platform review."
                      className="min-h-40 border-0 bg-transparent"
                    />
                  ) : (
                    communityRequests.map((communityRequest) => (
                      <article
                        key={communityRequest.id}
                        className="rounded-xl border border-border/70 bg-card p-4"
                      >
                        <div className="flex flex-wrap items-start justify-between gap-3">
                          <div>
                            <h3 className="font-semibold">{communityRequest.name}</h3>
                            <p className="text-sm text-muted-foreground">
                              /{communityRequest.slug} · {communityRequest.access_type} · requested
                              by {communityRequest.requester_display_name}
                            </p>
                          </div>
                          <div className="flex gap-2">
                            <Button
                              variant="outline"
                              disabled={busy === communityRequest.id}
                              onClick={() =>
                                void submitDecision(
                                  `/communities/requests/${communityRequest.id}/decision`,
                                  { decision: "reject" },
                                  communityRequest.id,
                                  `${communityRequest.name} was rejected.`,
                                )
                              }
                            >
                              Reject
                            </Button>
                            <Button
                              disabled={busy === communityRequest.id}
                              onClick={() =>
                                void submitDecision(
                                  `/communities/requests/${communityRequest.id}/decision`,
                                  { decision: "approve" },
                                  communityRequest.id,
                                  `${communityRequest.name} was approved and provisioned with its requester as owner.`,
                                )
                              }
                            >
                              Approve & provision
                            </Button>
                          </div>
                        </div>
                        <p className="mt-3 whitespace-pre-wrap text-sm">
                          {communityRequest.description}
                        </p>
                      </article>
                    ))
                  )}
                </CardContent>
              </Card>
            </section>

            <section
              id="moderation"
              aria-labelledby="moderation-heading"
              className="mb-6 scroll-mt-24"
            >
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between gap-3">
                    <span className="grid size-10 place-items-center rounded-xl bg-accent text-accent-foreground">
                      <ClipboardList aria-hidden="true" className="size-5" />
                    </span>
                    <Badge variant="outline">
                      {reports.length} reports · {appeals.length} appeals
                    </Badge>
                  </div>
                  <CardTitle id="moderation-heading" className="pt-2 font-display text-xl">
                    Global and escalated moderation
                  </CardTitle>
                </CardHeader>
                <CardContent className="grid gap-4">
                  {reports.length === 0 && !loading ? (
                    <EmptyState
                      icon={ClipboardList}
                      title="No reports awaiting platform review"
                      description="Global reports and community escalations will appear here."
                      className="min-h-36 border-0 bg-surface-raised/50"
                    />
                  ) : (
                    reports.map((report) => (
                      <article
                        key={report.id}
                        className="rounded-xl border border-border/70 bg-card p-4"
                      >
                        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
                          <div className="flex flex-wrap items-center gap-2">
                            <Badge variant="outline">
                              {report.status === "escalated"
                                ? `Escalated · ${report.community_name ?? "community"}`
                                : "Global report"}
                            </Badge>
                            <span className="text-sm text-muted-foreground">
                              {report.target_kind} by {report.target_author_display_name}
                            </span>
                          </div>
                          <span className="text-xs text-muted-foreground">
                            Reported {new Date(report.created_at).toLocaleString()}
                          </span>
                        </div>
                        <blockquote className="whitespace-pre-wrap rounded-lg bg-muted/50 p-3 text-sm">
                          {report.target_body}
                        </blockquote>
                        <p className="mt-3 text-sm">
                          <span className="font-medium">Report reason: </span>
                          {report.reason}
                        </p>
                        <div className="mt-3 grid gap-2">
                          <label htmlFor={`reason-${report.id}`} className="text-sm font-medium">
                            Decision reason
                          </label>
                          <input
                            id={`reason-${report.id}`}
                            value={reportReasons[report.id] ?? ""}
                            onChange={(event) =>
                              setReportReasons({
                                ...reportReasons,
                                [report.id]: event.target.value,
                              })
                            }
                            minLength={3}
                            maxLength={500}
                            className="min-h-11 rounded-lg border border-border bg-background px-3 text-sm"
                            placeholder="Record why this report is being resolved"
                          />
                          <div className="flex flex-wrap gap-2">
                            {(["dismiss", "hide", "remove", "warn"] as const).map((action) => (
                              <Button
                                key={action}
                                variant={action === "remove" ? "default" : "outline"}
                                disabled={
                                  busy === report.id ||
                                  (reportReasons[report.id] ?? "").trim().length < 3
                                }
                                onClick={() =>
                                  void submitDecision(
                                    `/moderation/reports/${report.id}/actions`,
                                    { action, reason: (reportReasons[report.id] ?? "").trim() },
                                    report.id,
                                    `The report was ${
                                      {
                                        dismiss: "dismissed",
                                        hide: "hidden",
                                        remove: "removed",
                                        warn: "resolved with a warning",
                                      }[action]
                                    }.`,
                                  )
                                }
                              >
                                {action === "dismiss"
                                  ? "Dismiss report"
                                  : action === "warn"
                                    ? "Warn author"
                                    : `${action[0].toUpperCase()}${action.slice(1)} content`}
                              </Button>
                            ))}
                          </div>
                        </div>
                      </article>
                    ))
                  )}

                  {appeals.length > 0 && (
                    <div className="grid gap-3 border-t border-border/70 pt-4">
                      <h3 className="font-display text-lg">Appeals for global actions</h3>
                      {appeals.map((appeal) => (
                        <article
                          key={appeal.id}
                          className="rounded-xl border border-border/70 bg-card p-4"
                        >
                          <p className="text-sm">
                            Appeal of {appeal.action}: {appeal.action_reason}
                          </p>
                          <p className="mt-2 text-sm text-muted-foreground">{appeal.reason}</p>
                          <div className="mt-3 flex gap-2">
                            {(["upheld", "overturned"] as const).map((decision) => (
                              <Button
                                key={decision}
                                variant={decision === "overturned" ? "default" : "outline"}
                                disabled={busy === appeal.id}
                                onClick={() =>
                                  void submitDecision(
                                    `/moderation/appeals/${appeal.id}/decision`,
                                    { decision },
                                    appeal.id,
                                    `The appeal was ${decision}.`,
                                  )
                                }
                              >
                                {decision === "overturned" ? "Overturn action" : "Uphold action"}
                              </Button>
                            ))}
                          </div>
                        </article>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </section>

            <div className="grid gap-4 md:grid-cols-2">
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
                      description="Detailed audit event search and security operations remain outside this workflow."
                      className="min-h-40 border-0 bg-surface-raised/50"
                    />
                  </CardContent>
                </Card>
              </section>
            </div>
          </div>
        </PageShell>
      </main>
      <SiteFooter note="Platform operations require an authenticated account listed in PLATFORM_ADMIN_EMAILS." />
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <AdminApp />
  </StrictMode>,
);
