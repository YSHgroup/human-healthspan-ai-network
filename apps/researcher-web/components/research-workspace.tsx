"use client";

import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import {
  ArrowUpRight,
  CalendarDays,
  FileText,
  FlaskConical,
  FolderKanban,
  LockKeyhole,
  Microscope,
  UsersRound,
} from "lucide-react";

import { Alert, AlertDescription } from "@healthspan/ui/alert";
import { Badge } from "@healthspan/ui/badge";
import { Button } from "@healthspan/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@healthspan/ui/card";
import { PageShell, SectionHeading, SiteFooter, SiteHeader } from "@healthspan/ui/composites";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const socialPortalUrl = process.env.NEXT_PUBLIC_SOCIAL_APP_URL ?? "http://localhost:3000";
const apiBase = "/api/v1/user/researcher";

type ResearcherStatus = {
  email_verified: boolean;
  approved: boolean;
  application_status: "none" | "pending" | "approved" | "rejected";
};

type Organization = {
  id: string;
  name: string;
  slug: string;
  website: string;
  role: "owner" | "admin" | "member";
};

type OrganizationInvitation = {
  id: string;
  organization_id: string;
  organization_name: string;
  email: string;
  role: "admin" | "member";
  expires_at: string;
};

type Project = {
  id: string;
  organization_id: string | null;
  title: string;
  description: string;
  objectives: string;
  research_questions: string;
  visibility: "private" | "team" | "invited" | "community" | "public";
  status: string;
};

type ResearchTask = {
  id: string;
  title: string;
  description: string;
  status: "open" | "in_progress" | "completed" | "cancelled";
  assignee_display_name: string | null;
};

type ResearchDocument = {
  id: string;
  title: string;
  filename: string;
  content: string;
  access_scope: "private" | "project";
  media_type: string | null;
  file_size: number | null;
};

type ResearchEvent = {
  id: string;
  organization_name: string | null;
  title: string;
  description: string;
  location: string;
  starts_at: string;
  ends_at: string;
  registration_count: number;
  registered: boolean;
};

type ResearcherProfile = {
  user_id: string;
  display_name: string;
  biography: string;
  research_interests: string;
  affiliation: string | null;
  profile_public: boolean;
};

async function researcherRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${apiUrl}${apiBase}${path}`, {
      credentials: "include",
      ...init,
      headers: {
        Accept: "application/json",
        ...(init.body && !(init.body instanceof FormData)
          ? { "Content-Type": "application/json" }
          : {}),
        ...init.headers,
      },
    });
  } catch {
    throw new Error("The Researcher Portal could not connect to the API.");
  }

  let result: unknown;
  if (response.status !== 204) {
    result = await response.json().catch(() => undefined);
  }
  if (!response.ok) {
    const body =
      typeof result === "object" && result !== null
        ? (result as Record<string, unknown>)
        : undefined;
    const message =
      typeof body?.message === "string"
        ? body.message
        : typeof body?.detail === "string"
          ? body.detail
          : `Research request failed (${response.status})`;
    throw new Error(message);
  }
  return result as T;
}

function formBody(
  form: HTMLFormElement,
  booleans: string[] = [],
): Record<string, string | boolean> {
  const formData = new FormData(form);
  const body: Record<string, string | boolean> = Object.fromEntries(
    [...formData.entries()]
      .filter(([, value]) => value !== "")
      .map(([key, value]) => [key, String(value)]),
  );
  for (const field of booleans) {
    body[field] = formData.has(field);
  }
  for (const key of ["starts_at", "ends_at", "due_at"]) {
    if (typeof body[key] === "string") {
      body[key] = new Date(body[key] as string).toISOString();
    }
  }
  return body;
}

function FormField({
  label,
  name,
  required = false,
  type = "text",
  ...props
}: {
  label: string;
  name: string;
  required?: boolean;
  type?: string;
  maxLength?: number;
  minLength?: number;
  placeholder?: string;
  defaultValue?: string;
}) {
  return (
    <label className="grid gap-1.5 text-sm font-medium">
      {label}
      <input
        name={name}
        type={type}
        required={required}
        maxLength={props.maxLength}
        minLength={props.minLength}
        placeholder={props.placeholder}
        defaultValue={props.defaultValue}
        className="min-h-11 rounded-lg border border-border bg-background px-3 font-normal"
      />
    </label>
  );
}

function FormText({
  label,
  name,
  required = false,
  rows = 3,
  maxLength,
  minLength,
  defaultValue,
}: {
  label: string;
  name: string;
  required?: boolean;
  rows?: number;
  maxLength: number;
  minLength?: number;
  defaultValue?: string;
}) {
  return (
    <label className="grid gap-1.5 text-sm font-medium">
      {label}
      <textarea
        name={name}
        required={required}
        rows={rows}
        maxLength={maxLength}
        minLength={minLength}
        defaultValue={defaultValue}
        className="rounded-lg border border-border bg-background px-3 py-2 font-normal"
      />
    </label>
  );
}

function Panel({
  id,
  title,
  description,
  icon,
  children,
}: {
  id: string;
  title: string;
  description: string;
  icon: ReactNode;
  children: ReactNode;
}) {
  return (
    <section id={id} className="scroll-mt-24">
      <Card>
        <CardHeader>
          <div className="mb-1 grid size-10 place-items-center rounded-xl bg-accent text-accent-foreground">
            {icon}
          </div>
          <CardTitle className="font-display text-xl">{title}</CardTitle>
          <CardDescription>{description}</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4">{children}</CardContent>
      </Card>
    </section>
  );
}

export function ResearchWorkspace() {
  const [researchStatus, setResearchStatus] = useState<ResearcherStatus | null>(null);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [organizationRequests, setOrganizationRequests] = useState<
    Array<{ id: string; name: string; status: string }>
  >([]);
  const [invitations, setInvitations] = useState<OrganizationInvitation[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [tasksByProject, setTasksByProject] = useState<Record<string, ResearchTask[]>>({});
  const [documentsByProject, setDocumentsByProject] = useState<Record<string, ResearchDocument[]>>(
    {},
  );
  const [events, setEvents] = useState<ResearchEvent[]>([]);
  const [profiles, setProfiles] = useState<ResearcherProfile[]>([]);
  const [profile, setProfile] = useState<ResearcherProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  async function loadWorkspace() {
    setLoading(true);
    setError(null);
    try {
      const [status, orgs, requests, pendingInvitations] = await Promise.all([
        researcherRequest<ResearcherStatus>("/me"),
        researcherRequest<Organization[]>("/organizations"),
        researcherRequest<Array<{ id: string; name: string; status: string }>>(
          "/organizations/requests/me",
        ),
        researcherRequest<OrganizationInvitation[]>("/organizations/invitations"),
      ]);
      setResearchStatus(status);
      setOrganizations(orgs);
      setOrganizationRequests(requests);
      setInvitations(pendingInvitations);
      if (status.approved) {
        const [projectList, eventList, profileList, ownProfile] = await Promise.all([
          researcherRequest<Project[]>("/projects"),
          researcherRequest<ResearchEvent[]>("/events"),
          researcherRequest<ResearcherProfile[]>("/profiles"),
          researcherRequest<ResearcherProfile>("/profile"),
        ]);
        setProjects(projectList);
        setEvents(eventList);
        setProfiles(profileList);
        setProfile(ownProfile);
        const taskEntries = await Promise.all(
          projectList.map(
            async (project) =>
              [
                project.id,
                await researcherRequest<ResearchTask[]>(`/projects/${project.id}/tasks`),
              ] as const,
          ),
        );
        const documentEntries = await Promise.all(
          projectList.map(
            async (project) =>
              [
                project.id,
                await researcherRequest<ResearchDocument[]>(`/projects/${project.id}/documents`),
              ] as const,
          ),
        );
        setTasksByProject(Object.fromEntries(taskEntries));
        setDocumentsByProject(Object.fromEntries(documentEntries));
      } else {
        setProjects([]);
        setEvents([]);
        setProfiles([]);
        setProfile(null);
        setTasksByProject({});
        setDocumentsByProject({});
      }
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Research workspace data could not be loaded.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadWorkspace();
  }, []);

  async function submit(
    event: FormEvent<HTMLFormElement>,
    path: string,
    successMessage: string,
    method = "POST",
    booleanFields: string[] = [],
  ) {
    event.preventDefault();
    const form = event.currentTarget;
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      await researcherRequest(path, {
        method,
        body: JSON.stringify(formBody(form, booleanFields)),
      });
      form.reset();
      setNotice(successMessage);
      await loadWorkspace();
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "The requested action could not be completed.",
      );
    } finally {
      setBusy(false);
    }
  }

  async function action(path: string, successMessage: string) {
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      await researcherRequest(path, { method: "POST" });
      setNotice(successMessage);
      await loadWorkspace();
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "The requested action could not be completed.",
      );
    } finally {
      setBusy(false);
    }
  }

  async function uploadDocument(event: FormEvent<HTMLFormElement>, projectId: string) {
    event.preventDefault();
    const form = event.currentTarget;
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      await researcherRequest(`/projects/${projectId}/documents/upload`, {
        method: "POST",
        body: new FormData(form),
      });
      form.reset();
      setNotice("Project file uploaded.");
      await loadWorkspace();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "The file upload failed.");
    } finally {
      setBusy(false);
    }
  }

  const navigation = [
    { label: "Projects", href: "#projects" },
    { label: "Organizations", href: "#organizations" },
    { label: "Research events", href: "#events" },
    { label: "Profiles", href: "#profiles" },
  ];

  return (
    <div className="min-h-screen bg-background text-foreground">
      <SiteHeader
        title="Research workspace"
        eyebrow="Researcher Portal"
        homeHref="#overview"
        links={navigation}
        actions={
          <a
            href="/ai"
            className="inline-flex min-h-11 items-center rounded-full border border-border bg-card px-3 text-sm font-medium transition-colors hover:bg-accent"
          >
            Scientist prototype
          </a>
        }
      />
      <main id="overview">
        <PageShell wide className="grid gap-6 py-7">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <SectionHeading
              as="h1"
              eyebrow="Research collaboration"
              title="A controlled space for careful work."
              description="Access to this portal is not access to every project. The API checks researcher approval, organization membership, and project permissions on each request."
            />
            <a
              href={socialPortalUrl}
              className="inline-flex min-h-11 items-center gap-2 rounded-full border border-border bg-card px-4 text-sm font-medium hover:bg-accent"
            >
              Network principles <ArrowUpRight aria-hidden="true" className="size-4" />
            </a>
          </div>

          {error && (
            <Alert role="alert" className="border-destructive/30 bg-destructive/5">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          {notice && (
            <Alert role="status" className="border-success/30 bg-success/5">
              <AlertDescription>{notice}</AlertDescription>
            </Alert>
          )}
          {loading && (
            <p role="status" className="text-sm text-muted-foreground">
              Loading your workspace…
            </p>
          )}
          {!loading && researchStatus && (
            <div className="flex flex-wrap items-center gap-3 rounded-xl border border-border bg-card p-4">
              <Badge variant={researchStatus.approved ? "default" : "outline"}>
                {researchStatus.approved ? "Researcher approved" : "Research access restricted"}
              </Badge>
              <span className="text-sm text-muted-foreground">
                Email {researchStatus.email_verified ? "verified" : "not verified"} · application{" "}
                {researchStatus.application_status}
              </span>
            </div>
          )}
          {!loading && !researchStatus && !error && (
            <Alert>
              <AlertDescription>
                Sign in through the Social Portal to access your researcher application and
                workspace.
              </AlertDescription>
            </Alert>
          )}

          {researchStatus && !researchStatus.approved && (
            <Panel
              id="application"
              title="Researcher access"
              description={
                researchStatus.application_status === "pending"
                  ? "Your application is awaiting platform review."
                  : "Submit your background and research interests for review. Approval requires a verified account."
              }
              icon={<ShieldCheckIcon />}
            >
              {researchStatus.application_status !== "pending" && (
                <form
                  className="grid gap-3"
                  onSubmit={(event) =>
                    void submit(
                      event,
                      "/applications",
                      "Researcher application submitted for review.",
                      "POST",
                      ["profile_public"],
                    )
                  }
                >
                  <FormText
                    label="Professional biography"
                    name="biography"
                    required
                    minLength={30}
                    maxLength={3000}
                  />
                  <FormField
                    label="Research interests"
                    name="research_interests"
                    required
                    minLength={3}
                    maxLength={500}
                    placeholder="Healthy aging, longitudinal studies"
                  />
                  <FormField label="Affiliation (optional)" name="affiliation" maxLength={200} />
                  <label className="flex items-center gap-2 text-sm">
                    <input type="checkbox" name="profile_public" />
                    Show my approved profile in researcher discovery
                  </label>
                  <Button type="submit" disabled={busy || !researchStatus.email_verified}>
                    Submit application
                  </Button>
                  {!researchStatus.email_verified && (
                    <p className="text-sm text-muted-foreground">
                      Email verification is required; contact a platform administrator in this
                      development environment.
                    </p>
                  )}
                </form>
              )}
            </Panel>
          )}

          {researchStatus?.approved && profile && (
            <Panel
              id="profile"
              title="Researcher profile"
              description="Discovery is opt-in. Your profile remains hidden until you enable public discovery."
              icon={<UsersRound aria-hidden="true" className="size-5" />}
            >
              <form
                className="grid gap-3"
                onSubmit={(event) =>
                  void submit(event, "/profile", "Researcher profile updated.", "PUT", [
                    "profile_public",
                  ])
                }
              >
                <FormText
                  label="Professional biography"
                  name="biography"
                  required
                  minLength={30}
                  maxLength={3000}
                  defaultValue={profile.biography}
                />
                <FormField
                  label="Research interests"
                  name="research_interests"
                  required
                  minLength={3}
                  maxLength={500}
                  defaultValue={profile.research_interests}
                />
                <FormField
                  label="Affiliation (optional)"
                  name="affiliation"
                  maxLength={200}
                  defaultValue={profile.affiliation ?? ""}
                />
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    name="profile_public"
                    defaultChecked={profile?.profile_public ?? false}
                  />
                  Show my approved profile in researcher discovery
                </label>
                <Button type="submit" disabled={busy}>
                  Save profile
                </Button>
              </form>
            </Panel>
          )}

          {researchStatus?.approved && (
            <Panel
              id="projects"
              title="Research projects"
              description="Projects are limited to explicitly authorized researchers. Organization membership alone does not grant project access."
              icon={<FolderKanban aria-hidden="true" className="size-5" />}
            >
              <form
                className="grid gap-3 md:grid-cols-2"
                onSubmit={(event) => void submit(event, "/projects", "Project created.")}
              >
                <FormField
                  label="Project title"
                  name="title"
                  required
                  minLength={3}
                  maxLength={200}
                />
                <label className="grid gap-1.5 text-sm font-medium">
                  Organization
                  <select
                    name="organization_id"
                    className="min-h-11 rounded-lg border border-border bg-background px-3 font-normal"
                  >
                    <option value="">Independent project</option>
                    {organizations.map((organization) => (
                      <option key={organization.id} value={organization.id}>
                        {organization.name}
                      </option>
                    ))}
                  </select>
                </label>
                <FormText
                  label="Description"
                  name="description"
                  required
                  minLength={10}
                  maxLength={2000}
                />
                <FormText label="Objectives" name="objectives" maxLength={2000} />
                <FormText label="Research questions" name="research_questions" maxLength={2000} />
                <label className="grid gap-1.5 text-sm font-medium">
                  Visibility
                  <select
                    name="visibility"
                    className="min-h-11 rounded-lg border border-border bg-background px-3 font-normal"
                  >
                    <option value="private">Private</option>
                    <option value="team">Team</option>
                    <option value="public">Public to approved researchers</option>
                  </select>
                </label>
                <Button type="submit" disabled={busy} className="md:col-span-2">
                  Create project
                </Button>
              </form>
              <div className="grid gap-4">
                {projects.length === 0 && (
                  <p className="text-sm text-muted-foreground">
                    No projects are available to this account.
                  </p>
                )}
                {projects.map((project) => (
                  <ProjectCard
                    key={project.id}
                    project={project}
                    tasks={tasksByProject[project.id] ?? []}
                    documents={documentsByProject[project.id] ?? []}
                    busy={busy}
                    onSubmit={submit}
                    onUpload={uploadDocument}
                  />
                ))}
              </div>
            </Panel>
          )}

          <Panel
            id="organizations"
            title="Organizations"
            description="Organization creation is a free request followed by administrator verification. Development creation entitlements are granted by administrators; no checkout is available."
            icon={<UsersRound aria-hidden="true" className="size-5" />}
          >
            {invitations.length > 0 && (
              <div className="grid gap-2">
                <h3 className="font-medium">Invitations</h3>
                {invitations.map((invitation) => (
                  <article
                    key={invitation.id}
                    className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-border p-3"
                  >
                    <p className="text-sm">
                      {invitation.organization_name} invited you as {invitation.role}.
                    </p>
                    <div className="flex gap-2">
                      <Button
                        disabled={busy}
                        onClick={() =>
                          void action(
                            `/organizations/invitations/${invitation.id}/accept`,
                            "Organization invitation accepted.",
                          )
                        }
                      >
                        Accept
                      </Button>
                      <Button
                        variant="outline"
                        disabled={busy}
                        onClick={() =>
                          void action(
                            `/organizations/invitations/${invitation.id}/decline`,
                            "Organization invitation declined.",
                          )
                        }
                      >
                        Decline
                      </Button>
                    </div>
                  </article>
                ))}
              </div>
            )}
            {organizations.length > 0 && (
              <div className="grid gap-3">
                {organizations.map((organization) => (
                  <article
                    key={organization.id}
                    className="grid gap-2 rounded-lg border border-border p-3"
                  >
                    <div>
                      <h3 className="font-medium">{organization.name}</h3>
                      <p className="text-sm text-muted-foreground">
                        {organization.website} · {organization.role}
                      </p>
                    </div>
                    <form
                      className="flex flex-wrap gap-2"
                      onSubmit={(event) =>
                        void submit(
                          event,
                          `/organizations/${organization.id}/invitations`,
                          "Organization invitation sent.",
                        )
                      }
                    >
                      <input
                        name="email"
                        type="email"
                        required
                        placeholder="researcher@example.org"
                        className="min-h-10 rounded-lg border border-border bg-background px-3 text-sm"
                      />
                      <select
                        name="role"
                        className="min-h-10 rounded-lg border border-border bg-background px-3 text-sm"
                      >
                        <option value="member">Member</option>
                        {organization.role === "owner" && <option value="admin">Admin</option>}
                      </select>
                      <Button
                        type="submit"
                        size="sm"
                        disabled={busy || organization.role === "member"}
                      >
                        Invite
                      </Button>
                    </form>
                  </article>
                ))}
              </div>
            )}
            <form
              className="grid gap-3 md:grid-cols-2"
              onSubmit={(event) =>
                void submit(event, "/organizations/requests", "Organization request submitted.")
              }
            >
              <FormField
                label="Organization name"
                name="name"
                required
                minLength={2}
                maxLength={160}
              />
              <FormField
                label="Unique URL slug"
                name="slug"
                required
                minLength={3}
                maxLength={80}
                placeholder="healthy-aging-lab"
              />
              <FormField
                label="Organization website"
                name="website"
                type="url"
                required
                maxLength={500}
                placeholder="https://example.org"
              />
              <FormText
                label="Description"
                name="description"
                required
                minLength={10}
                maxLength={2000}
              />
              <Button type="submit" disabled={busy} className="md:col-span-2">
                Request organization
              </Button>
            </form>
            {organizationRequests.length > 0 && (
              <div className="grid gap-2">
                <h3 className="font-medium">Your requests</h3>
                {organizationRequests.map((item) => (
                  <p key={item.id} className="text-sm text-muted-foreground">
                    {item.name} · {item.status}
                  </p>
                ))}
              </div>
            )}
          </Panel>

          {researchStatus?.approved && (
            <>
              <Panel
                id="events"
                title="Research events"
                description="Create, discover, and register for research-focused events."
                icon={<CalendarDays aria-hidden="true" className="size-5" />}
              >
                <form
                  className="grid gap-3 md:grid-cols-2"
                  onSubmit={(event) => void submit(event, "/events", "Research event published.")}
                >
                  <FormField
                    label="Event title"
                    name="title"
                    required
                    minLength={3}
                    maxLength={200}
                  />
                  <FormField
                    label="Location or online link"
                    name="location"
                    maxLength={300}
                    placeholder="Online"
                  />
                  <FormText
                    label="Description"
                    name="description"
                    required
                    minLength={10}
                    maxLength={2000}
                  />
                  <label className="grid gap-1.5 text-sm font-medium">
                    Organization (optional)
                    <select
                      name="organization_id"
                      className="min-h-11 rounded-lg border border-border bg-background px-3 font-normal"
                    >
                      <option value="">Independent event</option>
                      {organizations.map((organization) => (
                        <option key={organization.id} value={organization.id}>
                          {organization.name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <FormField label="Starts" name="starts_at" type="datetime-local" required />
                  <FormField label="Ends" name="ends_at" type="datetime-local" required />
                  <Button type="submit" disabled={busy} className="md:col-span-2">
                    Publish event
                  </Button>
                </form>
                <div className="grid gap-3">
                  {events.map((event) => (
                    <article
                      key={event.id}
                      className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-border p-3"
                    >
                      <div>
                        <h3 className="font-medium">{event.title}</h3>
                        <p className="text-sm text-muted-foreground">
                          {new Date(event.starts_at).toLocaleString()} · {event.location}
                          {event.organization_name ? ` · ${event.organization_name}` : ""}
                        </p>
                        <p className="mt-1 text-sm">{event.description}</p>
                      </div>
                      <Button
                        variant={event.registered ? "outline" : "default"}
                        disabled={busy || event.registered}
                        onClick={() =>
                          void action(
                            `/events/${event.id}/registration`,
                            "Registered for research event.",
                          )
                        }
                      >
                        {event.registered ? "Registered" : `Register · ${event.registration_count}`}
                      </Button>
                    </article>
                  ))}
                  {events.length === 0 && (
                    <p className="text-sm text-muted-foreground">No upcoming research events.</p>
                  )}
                </div>
              </Panel>

              <Panel
                id="profiles"
                title="Researcher discovery"
                description="Only approved profiles whose owners opted into public discovery appear here."
                icon={<Microscope aria-hidden="true" className="size-5" />}
              >
                {profiles.map((researcher) => (
                  <article key={researcher.user_id} className="rounded-lg border border-border p-3">
                    <h3 className="font-medium">{researcher.display_name}</h3>
                    <p className="text-sm text-muted-foreground">
                      {researcher.affiliation ?? "Independent"} · {researcher.research_interests}
                    </p>
                    <p className="mt-2 text-sm">{researcher.biography}</p>
                  </article>
                ))}
                {profiles.length === 0 && (
                  <p className="text-sm text-muted-foreground">
                    No public researcher profiles yet.
                  </p>
                )}
              </Panel>
            </>
          )}

          <Alert className="border-warning/25 bg-warning-muted/60">
            <LockKeyhole aria-hidden="true" className="size-4 text-warning-foreground" />
            <AlertDescription>
              PDF, CSV, and UTF-8 text uploads are stored outside public assets and downloads are
              permission-checked. Malware scanning and production object storage are not yet
              available; do not upload untrusted files or production-sensitive data.
            </AlertDescription>
          </Alert>
        </PageShell>
      </main>
      <SiteFooter note="Private research access is enforced by the API on every request." />
    </div>
  );
}

function ProjectCard({
  project,
  tasks,
  documents,
  busy,
  onSubmit,
  onUpload,
}: {
  project: Project;
  tasks: ResearchTask[];
  documents: ResearchDocument[];
  busy: boolean;
  onSubmit: (
    event: FormEvent<HTMLFormElement>,
    path: string,
    successMessage: string,
    method?: string,
    booleanFields?: string[],
  ) => Promise<void>;
  onUpload: (event: FormEvent<HTMLFormElement>, projectId: string) => Promise<void>;
}) {
  return (
    <article className="grid gap-4 rounded-xl border border-border/70 bg-card p-4">
      <div>
        <div className="flex flex-wrap items-center gap-2">
          <h3 className="font-display text-lg">{project.title}</h3>
          <Badge variant="outline">{project.visibility}</Badge>
        </div>
        <p className="text-sm text-muted-foreground">{project.description}</p>
        {project.objectives && (
          <p className="mt-2 text-sm">
            <strong>Objectives:</strong> {project.objectives}
          </p>
        )}
        {project.research_questions && (
          <p className="mt-1 text-sm">
            <strong>Questions:</strong> {project.research_questions}
          </p>
        )}
      </div>

      <div className="grid gap-2">
        <h4 className="font-medium">Tasks</h4>
        {tasks.map((task) => (
          <div
            key={task.id}
            className="flex flex-wrap justify-between gap-2 rounded-lg bg-muted/40 p-2 text-sm"
          >
            <span>
              {task.title} · {task.status}
              {task.assignee_display_name ? ` · ${task.assignee_display_name}` : ""}
            </span>
            {task.status !== "completed" && (
              <form
                onSubmit={(event) =>
                  void onSubmit(
                    event,
                    `/projects/${project.id}/tasks/${task.id}`,
                    "Task status updated.",
                    "PATCH",
                  )
                }
              >
                <input type="hidden" name="status" value="completed" />
                <Button type="submit" size="sm" variant="outline" disabled={busy}>
                  Complete
                </Button>
              </form>
            )}
          </div>
        ))}
        <form
          className="grid gap-2 sm:grid-cols-3"
          onSubmit={(event) => void onSubmit(event, `/projects/${project.id}/tasks`, "Task added.")}
        >
          <input
            name="title"
            required
            minLength={3}
            maxLength={200}
            placeholder="Task title"
            className="min-h-10 rounded-lg border border-border bg-background px-3 text-sm"
          />
          <input
            name="assignee_email"
            type="email"
            placeholder="Assignee email (optional)"
            className="min-h-10 rounded-lg border border-border bg-background px-3 text-sm"
          />
          <Button type="submit" size="sm" disabled={busy}>
            Add task
          </Button>
        </form>
        <form
          className="flex flex-wrap gap-2"
          onSubmit={(event) =>
            void onSubmit(event, `/projects/${project.id}/members`, "Researcher added to project.")
          }
        >
          <input
            name="email"
            type="email"
            required
            placeholder="Approved researcher email"
            className="min-h-10 rounded-lg border border-border bg-background px-3 text-sm"
          />
          <Button type="submit" size="sm" variant="outline" disabled={busy}>
            Add collaborator
          </Button>
        </form>
      </div>

      <div className="grid gap-2">
        <h4 className="flex items-center gap-2 font-medium">
          <FileText aria-hidden="true" className="size-4" /> Documents
        </h4>
        {documents.map((document) => (
          <details key={document.id} className="rounded-lg border border-border p-2">
            <summary className="cursor-pointer text-sm">
              {document.title} · {document.filename} · {document.access_scope}
            </summary>
            {document.file_size !== null ? (
              <a
                href={`${apiUrl}${apiBase}/projects/${project.id}/documents/${document.id}/download`}
                className="mt-2 inline-flex min-h-10 items-center text-sm underline"
              >
                Download file ({(document.file_size / 1024).toFixed(1)} KiB)
              </a>
            ) : (
              <pre className="mt-2 max-h-48 overflow-auto whitespace-pre-wrap text-xs">
                {document.content}
              </pre>
            )}
          </details>
        ))}
        <form
          className="grid gap-2 rounded-lg border border-border p-3"
          onSubmit={(event) => void onUpload(event, project.id)}
        >
          <p className="text-sm font-medium">Upload a file (PDF, CSV, or UTF-8 text; max 10 MiB)</p>
          <input
            name="title"
            required
            minLength={2}
            maxLength={200}
            placeholder="Document title"
            className="min-h-10 rounded-lg border border-border bg-background px-3 text-sm"
          />
          <input
            name="file"
            type="file"
            accept=".pdf,.csv,.txt,application/pdf,text/csv,text/plain"
            required
            className="min-h-10 rounded-lg border border-border bg-background px-3 text-sm"
          />
          <label className="grid gap-1.5 text-sm font-medium">
            File access
            <select
              name="access_scope"
              className="min-h-10 rounded-lg border border-border bg-background px-3 text-sm font-normal"
            >
              <option value="private">Private to uploader and project owner</option>
              <option value="project">Share with authorized project members</option>
            </select>
          </label>
          <Button type="submit" size="sm" variant="outline" disabled={busy}>
            Upload file
          </Button>
        </form>
        <form
          className="grid gap-2"
          onSubmit={(event) =>
            void onSubmit(event, `/projects/${project.id}/documents`, "Project document added.")
          }
        >
          <input
            name="title"
            required
            minLength={2}
            maxLength={200}
            placeholder="Document title"
            className="min-h-10 rounded-lg border border-border bg-background px-3 text-sm"
          />
          <input
            name="filename"
            required
            maxLength={255}
            placeholder="Filename, e.g. protocol.txt"
            className="min-h-10 rounded-lg border border-border bg-background px-3 text-sm"
          />
          <textarea
            name="content"
            required
            maxLength={100_000}
            placeholder="Text document content"
            rows={3}
            className="rounded-lg border border-border bg-background px-3 py-2 text-sm"
          />
          <label className="grid gap-1.5 text-sm font-medium">
            Document access
            <select
              name="access_scope"
              className="min-h-10 rounded-lg border border-border bg-background px-3 text-sm font-normal"
            >
              <option value="private">Private to uploader and project owner</option>
              <option value="project">Share with authorized project members</option>
            </select>
          </label>
          <Button type="submit" size="sm" variant="outline" disabled={busy}>
            Attach text document
          </Button>
        </form>
      </div>
    </article>
  );
}

function ShieldCheckIcon() {
  return <FlaskConical aria-hidden="true" className="size-5" />;
}
