"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import {
  Activity,
  ClipboardList,
  Database,
  History,
  LayoutDashboard,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  UsersRound,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";

type AdminUser = {
  id: string;
  email: string;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  profile?: { display_name: string };
};

type Report = {
  id: string;
  reporter_id: string;
  target_type: string;
  target_id: string;
  reason: string;
  details?: string | null;
  status: string;
  created_at: string;
};

type AuditEvent = {
  id: string;
  actor_id?: string | null;
  action: string;
  resource_type: string;
  resource_id?: string | null;
  details: Record<string, unknown>;
  created_at: string;
};

type AdminSession = {
  email: string;
  role: string;
  display_name: string;
};

type View = "overview" | "reports" | "users" | "audit";

const navItems: { id: View; label: string; icon: LucideIcon; roles: string[] }[] = [
  { id: "overview", label: "Overview", icon: LayoutDashboard, roles: [] },
  { id: "reports", label: "Moderation queue", icon: ClipboardList, roles: ["admin", "moderator", "scientific_reviewer", "support_operator"] },
  { id: "users", label: "User management", icon: UsersRound, roles: ["admin", "support_operator"] },
  { id: "audit", label: "Audit log", icon: History, roles: ["admin", "read_only_auditor"] },
];

const roleOptions = [
  ["user", "Member"],
  ["moderator", "Moderator"],
  ["scientific_reviewer", "Scientific reviewer"],
  ["support_operator", "Support operator"],
  ["read_only_auditor", "Read-only auditor"],
  ["admin", "Administrator"],
];

class ConsoleError extends Error {
  constructor(message: string, public readonly status: number) {
    super(message);
  }
}

async function adminRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api/backend/${path}`, {
    ...init,
    headers: {
      ...(init?.body ? { "Content-Type": "application/json" } : {}),
      ...init?.headers,
    },
    cache: "no-store",
  });
  const body = await response.json().catch(() => undefined);
  if (!response.ok) {
    throw new ConsoleError(body?.detail ?? `Request failed (${response.status}).`, response.status);
  }
  return body as T;
}

function initials(name: string) {
  return name
    .split(/[\s@._-]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join("");
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function humanize(value: string) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function badgeClass(value: string) {
  if (["active", "resolved", "verified"].includes(value)) return "badge badge-green";
  if (["open", "pending", "unverified"].includes(value)) return "badge badge-amber";
  if (["suspended", "dismissed", "inactive"].includes(value)) return "badge badge-red";
  return "badge badge-blue";
}

function ErrorBanner({ message }: { message: string }) {
  return <div className="error-banner" role="alert">{message}</div>;
}

function Login({ onLogin }: { onLogin: (user: AdminSession) => void }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const result = await response.json().catch(() => undefined);
      if (!response.ok) throw new Error(result?.detail ?? "Sign-in failed.");
      onLogin(result.user as AdminSession);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Sign-in failed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="login-shell">
      <form className="login-card" onSubmit={submit}>
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">HN</span>
          <span>Healthspan Network</span>
        </div>
        <h1>Admin sign in</h1>
        <p>Restricted access for authorized platform operators.</p>
        {error && <ErrorBanner message={error} />}
        <div className="field">
          <label htmlFor="admin-email">Email address</label>
          <Input
            autoComplete="username"
            className="text-input"
            id="admin-email"
            onChange={(event) => setEmail(event.target.value)}
            required
            type="email"
            value={email}
          />
        </div>
        <div className="field">
          <label htmlFor="admin-password">Password</label>
          <Input
            autoComplete="current-password"
            className="text-input"
            id="admin-password"
            onChange={(event) => setPassword(event.target.value)}
            required
            type="password"
            value={password}
          />
        </div>
        <Button className="button button-primary" disabled={busy} type="submit">
          {busy ? "Signing in…" : "Sign in"}
        </Button>
        <div className="login-footnote">
          Administrator access is audited. Never use a shared account. Contact your platform owner if you need access.
        </div>
      </form>
    </main>
  );
}

function Empty({ title, message }: { title: string; message: string }) {
  return (
    <div className="empty-state">
      <div className="empty-title">{title}</div>
      {message}
    </div>
  );
}

export default function AdminApp() {
  const [user, setUser] = useState<AdminSession | null>(null);
  const [checkingSession, setCheckingSession] = useState(true);
  const [view, setView] = useState<View>("overview");
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [reports, setReports] = useState<Report[]>([]);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [search, setSearch] = useState("");
  const [userQuery, setUserQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const visibleNavigation = useMemo(
    () => navItems.filter((item) => !item.roles.length || item.roles.includes(user?.role ?? "")),
    [user?.role],
  );

  const loadData = useCallback(async (target: View, query = "") => {
    setLoading(true);
    setError("");
    try {
      if (target === "overview" || target === "reports") {
        const queue = await adminRequest<Report[]>("moderation/queue?limit=50");
        setReports(user?.role === "scientific_reviewer"
          ? queue.filter((report) => report.target_type === "evidence")
          : user?.role === "support_operator"
            ? queue.filter((report) => report.target_type !== "evidence")
            : queue);
      }

      if (target === "overview" && user?.role === "admin") {
        setUsers(await adminRequest<AdminUser[]>("admin/users?limit=5"));
      } else if (target === "users") {
        const parameters = new URLSearchParams({ limit: "50" });
        if (query.trim().length >= 2) parameters.set("q", query.trim());
        setUsers(await adminRequest<AdminUser[]>(`admin/users?${parameters.toString()}`));
      }

      if (target === "overview" && ["admin", "read_only_auditor"].includes(user?.role ?? "")) {
        setAuditEvents(await adminRequest<AuditEvent[]>("admin/audit-logs?limit=6"));
      } else if (target === "audit") {
        setAuditEvents(await adminRequest<AuditEvent[]>("admin/audit-logs?limit=100"));
      }
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not load admin data.");
    } finally {
      setLoading(false);
    }
  }, [user?.role]);

  useEffect(() => {
    let active = true;
    fetch("/api/auth/session", { cache: "no-store" })
      .then(async (response) => {
        if (!response.ok) throw new Error("Could not verify the administrator session.");
        return response.json();
      })
      .then((result) => {
        if (active && result.user) setUser(result.user as AdminSession);
      })
      .catch(() => {
        if (active) setError("Could not verify the administrator session.");
      })
      .finally(() => {
        if (active) setCheckingSession(false);
      });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (user) void loadData(view);
  }, [user, view, loadData]);

  async function logout() {
    setError("");
    const response = await fetch("/api/auth/logout", { method: "POST" });
    if (!response.ok) {
      const result = await response.json().catch(() => undefined);
      setError(result?.detail ?? "Could not safely revoke the admin session.");
      return;
    }
    setUser(null);
    setUsers([]);
    setReports([]);
    setAuditEvents([]);
    setView("overview");
  }

  async function decideReport(report: Report, action: "dismiss" | "remove" | "restrict") {
    const reason = window.prompt(`Reason for ${action} on this report?`);
    if (!reason?.trim()) return;
    setError("");
    setNotice("");
    try {
      await adminRequest(`moderation/reports/${report.id}/decision`, {
        method: "POST",
        body: JSON.stringify({ action, reason: reason.trim() }),
      });
      setNotice("Moderation decision saved and audited.");
      await loadData(view);
    } catch (reasonError) {
      setError(reasonError instanceof Error ? reasonError.message : "Could not save the moderation decision.");
    }
  }

  async function updateUser(account: AdminUser, role?: string, isActive?: boolean) {
    const operation = isActive === undefined ? `assign role ${role}` : isActive ? "reactivate" : "suspend";
    const reason = window.prompt(`Reason to ${operation} for ${account.email}?`);
    if (!reason?.trim()) return;
    setError("");
    setNotice("");
    try {
      const updated = await adminRequest<AdminUser>(`admin/users/${account.id}`, {
        method: "PATCH",
        body: JSON.stringify({
          ...(role !== undefined ? { role } : {}),
          ...(isActive !== undefined ? { is_active: isActive } : {}),
          reason: reason.trim(),
        }),
      });
      setUsers((current) => current.map((item) => item.id === updated.id ? updated : item));
      setNotice("Account updated and audit event recorded.");
    } catch (reasonError) {
      setError(reasonError instanceof Error ? reasonError.message : "Could not update the account.");
    }
  }

  if (checkingSession) return <div className="loading">Checking administrator access…</div>;
  if (!user) return <Login onLogin={(nextUser) => { setError(""); setUser(nextUser); }} />;

  const titleByView: Record<View, [string, string]> = {
    overview: ["Overview", "Platform operations at a glance."],
    reports: ["Moderation queue", "Review reports and record reasoned decisions."],
    users: ["User management", "Look up accounts and apply safeguarded access changes."],
    audit: ["Audit log", "Review privileged actions and administrative access."],
  };
  const [title, subtitle] = titleByView[view];

  return (
    <div className="admin-layout">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">HN</span>
          <span>Network Admin</span>
        </div>
        <div className="nav-label">Workspace</div>
        <nav className="nav-list" aria-label="Admin navigation">
          {visibleNavigation.map((item) => (
            <Button
              aria-current={view === item.id ? "page" : undefined}
              className="nav-item"
              key={item.id}
              onClick={() => { setView(item.id); setError(""); setNotice(""); }}
              type="button"
              variant="ghost"
            >
              <item.icon className="nav-symbol size-4 shrink-0" aria-hidden="true" />
              {item.label}
              {item.id === "reports" && reports.length > 0 && (
                <Badge className="badge badge-amber" style={{ marginLeft: "auto" }}>{reports.length}</Badge>
              )}
            </Button>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="status-row"><span>Environment</span><strong>Admin console</strong></div>
          <div style={{ marginTop: 9 }}>Access and actions are audited.</div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <span className="topbar-context">Healthspan Network / Administration</span>
          <div className="admin-identity">
            <span className="identity-dot" aria-hidden="true" />
            <span>{user.display_name} · {humanize(user.role)}</span>
            <Button className="button button-small" onClick={() => void logout()} type="button" variant="outline">Sign out</Button>
          </div>
        </header>

        <div className="content">
          <div className="page-heading">
            <div>
              <h1>{title}</h1>
              <p>{subtitle}</p>
            </div>
            <div className="toolbar">
              <Button className="button" disabled={loading} onClick={() => void loadData(view, userQuery)} type="button" variant="outline">
                <RefreshCw aria-hidden="true" />
                {loading ? "Refreshing…" : "Refresh"}
              </Button>
            </div>
          </div>

          {error && <ErrorBanner message={error} />}
          {notice && <div className="success-banner" role="status">{notice}</div>}

          {view === "overview" && (
            <>
              <section className="metrics" aria-label="Operational metrics">
                {user.role === "admin" && (
                  <Card as="article" className="metric-card !gap-0">
                    <div className="metric-top"><span>Accounts loaded</span><span className="metric-icon" aria-hidden="true"><UsersRound /></span></div>
                    <div className="metric-value">{users.length}</div>
                    <div className="metric-note">Most recently created accounts</div>
                  </Card>
                )}
                <Card as="article" className="metric-card !gap-0">
                  <div className="metric-top"><span>Open reports</span><span className="metric-icon" aria-hidden="true"><ClipboardList /></span></div>
                  <div className="metric-value">{reports.length}</div>
                  <div className="metric-note">Current review queue</div>
                </Card>
                <Card as="article" className="metric-card !gap-0">
                  <div className="metric-top"><span>AI provider</span><span className="metric-icon" aria-hidden="true"><Sparkles /></span></div>
                  <div className="metric-value" style={{ fontSize: 17, marginTop: 13 }}>Not configured</div>
                  <div className="metric-note">AI endpoints remain disabled until enabled</div>
                </Card>
                <Card as="article" className="metric-card !gap-0">
                  <div className="metric-top"><span>Admin session</span><span className="metric-icon" aria-hidden="true"><ShieldCheck /></span></div>
                  <div className="metric-value" style={{ fontSize: 17, marginTop: 13 }}>Active</div>
                  <div className="metric-note">Protected by server-side session cookies</div>
                </Card>
              </section>

              <div className="overview-grid">
                <Card as="section" className="panel !gap-0 !py-0">
                  <div className="panel-header">
                    <div><h2>Recent open reports</h2><span>Action required</span></div>
                    {visibleNavigation.some((item) => item.id === "reports") && (
                      <Button className="button button-small" onClick={() => setView("reports")} type="button" variant="outline">View queue</Button>
                    )}
                  </div>
                  {loading && reports.length === 0 ? <div className="loading">Loading reports…</div> : reports.length ? (
                    <div className="activity-list">
                      {reports.slice(0, 5).map((report) => (
                        <div className="activity-row" key={report.id}>
                          <span className="activity-icon" aria-hidden="true">!</span>
                          <div>
                            <div className="activity-title">{humanize(report.target_type)} · {humanize(report.reason)}</div>
                            <div className="activity-meta">Target {report.target_id.slice(0, 8)} · Reported {formatDate(report.created_at)}</div>
                          </div>
                          <Badge className={badgeClass(report.status)}>{humanize(report.status)}</Badge>
                        </div>
                      ))}
                    </div>
                  ) : <Empty title="Queue is clear" message="New reports will appear here for review." />}
                </Card>

                <Card as="section" className="panel !gap-0 !py-0">
                  <div className="panel-header"><div><h2>Admin services</h2><span>Current integration status</span></div></div>
                  <div className="status-card">
                    <div className="status-row"><span>Admin API</span><span className="status-value"><span className="identity-dot" /> Connected</span></div>
                    <div className="status-row"><span>Role access</span><span>{humanize(user.role)}</span></div>
                    <div className="status-row"><span>AI provider</span><Badge className="badge badge-amber" variant="outline"><Sparkles />Not configured</Badge></div>
                    <div className="status-row"><span>Search integration</span><Badge className="badge" variant="outline"><Database />PostgreSQL</Badge></div>
                  </div>
                </Card>

                {auditEvents.length > 0 && (
                  <Card as="section" className="panel !gap-0 !py-0">
                    <div className="panel-header">
                      <div><h2>Recent administrative activity</h2><span>Latest recorded events</span></div>
                      {visibleNavigation.some((item) => item.id === "audit") && (
                        <Button className="button button-small" onClick={() => setView("audit")} type="button" variant="outline">View log</Button>
                      )}
                    </div>
                    <div className="activity-list">
                      {auditEvents.slice(0, 5).map((event) => (
                        <div className="activity-row" key={event.id}>
                          <span className="activity-icon" aria-hidden="true"><History /></span>
                          <div>
                            <div className="activity-title">{humanize(event.action)}</div>
                            <div className="activity-meta">{event.resource_type} · {event.resource_id?.slice(0, 8) ?? "System"}</div>
                          </div>
                          <span className="activity-time">{formatDate(event.created_at)}</span>
                        </div>
                      ))}
                    </div>
                  </Card>
                )}
              </div>
            </>
          )}

          {view === "reports" && (
            <Card as="section" className="panel !gap-0 !py-0">
              <div className="panel-header">
                <div><h2>Reports awaiting review</h2><span>{reports.length} open</span></div>
              </div>
              {loading && reports.length === 0 ? <div className="loading">Loading queue…</div> : reports.length ? (
                <div className="table-wrap">
                  <table>
                    <thead><tr><th>Report</th><th>Target</th><th>Reporter</th><th>Submitted</th><th>Actions</th></tr></thead>
                    <tbody>
                      {reports.map((report) => (
                        <tr key={report.id}>
                          <td>
                            <Badge className="badge badge-amber" variant="outline">{humanize(report.status)}</Badge>
                            <div className="report-reason" style={{ marginTop: 5 }}>{report.reason}</div>
                          </td>
                          <td>
                            <Badge className="badge badge-blue" variant="outline">{humanize(report.target_type)}</Badge>
                            <div className="user-email">{report.target_id}</div>
                          </td>
                          <td className="user-email">{report.reporter_id.slice(0, 8)}…</td>
                          <td>{formatDate(report.created_at)}</td>
                          <td>
                            <div className="row-actions">
                              <Button className="button button-small" disabled={loading} onClick={() => void decideReport(report, "dismiss")} type="button" variant="outline">Dismiss</Button>
                              {report.target_type === "evidence" ? (
                                <Button className="button button-small" disabled={loading} onClick={() => void decideReport(report, "restrict")} type="button" variant="outline">Flag</Button>
                              ) : (
                                <Button className="button button-danger button-small" disabled={loading} onClick={() => void decideReport(report, "remove")} type="button" variant="destructive">Remove</Button>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : <Empty title="No open reports" message="The moderation queue is clear." />}
            </Card>
          )}

          {view === "users" && (
            <Card as="section" className="panel !gap-0 !py-0">
              <div className="panel-header">
                <div><h2>Platform accounts</h2><span>{users.length} accounts in this result</span></div>
                <form
                  className="toolbar"
                  onSubmit={(event) => {
                    event.preventDefault();
                    setUserQuery(search);
                    void loadData("users", search);
                  }}
                >
                  <Input
                    aria-label="Search users by email"
                    className="search-input filter-input"
                    minLength={2}
                    onChange={(event) => setSearch(event.target.value)}
                    placeholder="Search email…"
                    value={search}
                  />
                  <Button className="button button-primary button-small" disabled={loading} type="submit">Search</Button>
                </form>
              </div>
              {loading && users.length === 0 ? <div className="loading">Loading accounts…</div> : users.length ? (
                <div className="table-wrap">
                  <table>
                    <thead><tr><th>Account</th><th>Role</th><th>Status</th><th>Joined</th><th>Actions</th></tr></thead>
                    <tbody>
                      {users.map((account) => (
                        <tr key={account.id}>
                          <td>
                            <div className="user-cell">
                              <span className="avatar">{initials(account.profile?.display_name ?? account.email)}</span>
                              <div>
                                <div className="user-name">{account.profile?.display_name ?? "Member"}</div>
                                <div className="user-email">{account.email}</div>
                              </div>
                            </div>
                          </td>
                          <td>
                            <Select
                              aria-label={`Role for ${account.email}`}
                              className="select-input inline-select"
                              disabled={user.role !== "admin"}
                              onChange={(event) => void updateUser(account, event.target.value)}
                              value={account.role}
                            >
                              {roleOptions.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                            </Select>
                          </td>
                          <td>
                            <Badge className={badgeClass(account.is_active ? "active" : "inactive")} variant="outline">
                              {account.is_active ? "Active" : "Suspended"}
                            </Badge>
                            <Badge className={badgeClass(account.is_verified ? "verified" : "unverified")} style={{ marginLeft: 5 }} variant="outline">
                              {account.is_verified ? "Verified" : "Unverified"}
                            </Badge>
                          </td>
                          <td>{formatDate(account.created_at)}</td>
                          <td>
                            <Button
                              className={`button button-small ${account.is_active ? "button-danger" : ""}`}
                              onClick={() => void updateUser(account, undefined, !account.is_active)}
                              type="button"
                              variant={account.is_active ? "destructive" : "outline"}
                            >
                              {account.is_active ? "Suspend" : "Reactivate"}
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : <Empty title="No accounts found" message="Try a different email search." />}
            </Card>
          )}

          {view === "audit" && (
            <Card as="section" className="panel !gap-0 !py-0">
              <div className="panel-header"><div><h2>Administrative events</h2><span>Most recent 100 records</span></div></div>
              {loading && auditEvents.length === 0 ? <div className="loading">Loading audit log…</div> : auditEvents.length ? (
                <div className="table-wrap">
                  <table>
                    <thead><tr><th>Action</th><th>Resource</th><th>Actor</th><th>Details</th><th>Time</th></tr></thead>
                    <tbody>
                      {auditEvents.map((event) => (
                        <tr key={event.id}>
                          <td className="audit-action"><Activity aria-hidden="true" />{event.action}</td>
                          <td>{event.resource_type}<div className="user-email">{event.resource_id ?? "—"}</div></td>
                          <td className="user-email">{event.actor_id?.slice(0, 8) ?? "System"}</td>
                          <td className="report-reason">{Object.entries(event.details ?? {}).map(([key, value]) => `${key}: ${String(value)}`).join(" · ") || "—"}</td>
                          <td>{formatDate(event.created_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : <Empty title="No audit events" message="Administrative actions will be recorded here." />}
            </Card>
          )}
        </div>
      </main>
    </div>
  );
}
