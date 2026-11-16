"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";

import { Alert, AlertDescription } from "@healthspan/ui/alert";
import { AuthPanel } from "@healthspan/ui/communication";
import { Button } from "@healthspan/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@healthspan/ui/card";
import { Input } from "@healthspan/ui/input";
import { Label } from "@healthspan/ui/label";
import { Textarea } from "@healthspan/ui/textarea";

interface Member {
  id: string;
  display_name: string;
}

interface AuthenticatedMember extends Member {
  email: string;
  researcher_approved: boolean;
  ai_learning_consent: boolean;
}

interface Community {
  id: string;
  slug: string;
  name: string;
  description: string;
  rules: string;
  access_type: "open" | "restricted";
  membership_status: "none" | "pending" | "active" | "rejected";
  membership_role: "owner" | "moderator" | "member" | null;
}

interface Post {
  id: string;
  author_id: string;
  author_display_name: string;
  kind: "discussion" | "question";
  body: string;
  created_at: string;
}

interface Comment {
  id: string;
  post_id: string;
  author_id: string;
  author_display_name: string;
  body: string;
  created_at: string;
}

interface Membership {
  id: string;
  user_id: string;
  display_name: string;
  application_message: string | null;
}

interface ModerationReport {
  id: string;
  post_id: string | null;
  comment_id: string | null;
  reporter_display_name: string;
  reason: string;
}

interface ModerationAction {
  id: string;
  community_id: string;
  report_id: string;
  action: "hide" | "remove" | "warn" | "suspend" | "escalate" | "dismiss";
  reason: string;
  appeal_status: "pending" | "upheld" | "overturned" | null;
}

interface Appeal {
  id: string;
  action_id: string;
  appellant_id: string;
  reason: string;
}

interface Reaction {
  count: number;
  current_user_reaction: "like" | "agree" | "curious" | null;
}

class CommunityRequestError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

async function apiRequest<T>(
  apiBaseUrl: string,
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${apiBaseUrl.replace(/\/$/, "")}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      ...(init.body ? { "Content-Type": "application/json" } : {}),
      ...init.headers,
    },
  });
  if (!response.ok) {
    let message = response.statusText || `Request failed (${response.status})`;
    const text = await response.text();
    if (text) {
      try {
        const payload: unknown = JSON.parse(text);
        if (typeof payload === "object" && payload !== null) {
          if ("message" in payload && typeof payload.message === "string") {
            message = payload.message;
          } else if ("detail" in payload && typeof payload.detail === "string") {
            message = payload.detail;
          } else {
            message = text;
          }
        } else {
          message = text;
        }
      } catch (error) {
        if (!(error instanceof SyntaxError)) throw error;
        message = text;
      }
    }
    throw new CommunityRequestError(message, response.status);
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

function communityPath(communityId: string, ...segments: string[]): string {
  const path = [communityId, ...segments].map(encodeURIComponent).join("/");
  return `/api/v1/user/social/communities/${path}`;
}

function dateLabel(value: string): string {
  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(
    new Date(value),
  );
}

export function CommunityHub({ apiBaseUrl }: { apiBaseUrl: string }) {
  const [member, setMember] = useState<Member | null>(null);
  const [communities, setCommunities] = useState<Community[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [posts, setPosts] = useState<Post[]>([]);
  const [comments, setComments] = useState<Record<string, Comment[]>>({});
  const [reactions, setReactions] = useState<Record<string, Reaction>>({});
  const [pendingMembers, setPendingMembers] = useState<Membership[]>([]);
  const [reports, setReports] = useState<ModerationReport[]>([]);
  const [actions, setActions] = useState<ModerationAction[]>([]);
  const [appeals, setAppeals] = useState<Appeal[]>([]);
  const [postDraft, setPostDraft] = useState("");
  const [postKind, setPostKind] = useState<Post["kind"]>("discussion");
  const [commentDrafts, setCommentDrafts] = useState<Record<string, string>>({});
  const [requestForm, setRequestForm] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);

  const loadCommunities = useCallback(async () => {
    const items = await apiRequest<Community[]>(apiBaseUrl, "/api/v1/user/social/communities");
    setCommunities(items);
    setSelectedId((current) => current || items[0]?.id || "");
  }, [apiBaseUrl]);

  const loadModeration = useCallback(async (communityId: string, canModerate: boolean) => {
    const memberActions = await apiRequest<ModerationAction[]>(
      apiBaseUrl,
      "/api/v1/user/social/me/moderation/actions",
    );
    setActions(memberActions);
    if (!canModerate) {
      setPendingMembers([]);
      setReports([]);
      setAppeals([]);
      return;
    }
    const [memberships, pendingReports, pendingAppeals] = await Promise.all([
      apiRequest<Membership[]>(
        apiBaseUrl,
        communityPath(communityId, "memberships", "pending"),
      ),
      apiRequest<ModerationReport[]>(
        apiBaseUrl,
        communityPath(communityId, "moderation", "reports"),
      ),
      apiRequest<Appeal[]>(
        apiBaseUrl,
        communityPath(communityId, "moderation", "appeals"),
      ),
    ]);
    setPendingMembers(memberships);
    setReports(pendingReports);
    setAppeals(pendingAppeals);
  }, [apiBaseUrl]);

  const loadPosts = useCallback(async (communityId: string) => {
    const items = await apiRequest<Post[]>(
      apiBaseUrl,
      communityPath(communityId, "posts"),
    );
    setPosts(items);
    const commentPairs = await Promise.all(
      items.map(async (post) => {
        const postComments = await apiRequest<Comment[]>(
          apiBaseUrl,
          `/api/v1/user/social/posts/${encodeURIComponent(post.id)}/comments`,
        );
        return [post.id, postComments] as const;
      }),
    );
    setComments(Object.fromEntries(commentPairs));
    const reactionPairs = await Promise.all(
      items.map(async (post) => {
        const reaction = await apiRequest<Reaction>(
          apiBaseUrl,
          `/api/v1/user/social/posts/${encodeURIComponent(post.id)}/reactions`,
        );
        return [post.id, reaction] as const;
      }),
    );
    setReactions(Object.fromEntries(reactionPairs));
  }, [apiBaseUrl]);

  useEffect(() => {
    const controller = new AbortController();
    void apiRequest<AuthenticatedMember>(apiBaseUrl, "/api/v1/user/auth/me", {
      signal: controller.signal,
    })
      .then(setMember)
      .catch((reason: unknown) => {
        if (
          !controller.signal.aborted &&
          (!(reason instanceof CommunityRequestError) || reason.status !== 401)
        ) {
          setError(reason instanceof Error ? reason.message : "Unable to check your sign-in.");
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [apiBaseUrl]);

  useEffect(() => {
    if (!member) {
      setCommunities([]);
      setSelectedId("");
      return;
    }
    void loadCommunities().catch((reason: unknown) =>
      setError(reason instanceof Error ? reason.message : "Unable to load communities."),
    );
  }, [loadCommunities, member]);

  const selected = communities.find((community) => community.id === selectedId) ?? null;
  const canModerateSelected =
    selected?.membership_role === "owner" || selected?.membership_role === "moderator";

  useEffect(() => {
    if (!selected || selected.membership_status !== "active") {
      setPosts([]);
      setComments({});
      setReactions({});
      setPendingMembers([]);
      setReports([]);
      setAppeals([]);
      return;
    }
    void Promise.all([
      loadPosts(selected.id),
      loadModeration(selected.id, canModerateSelected),
    ]).catch(
      (reason: unknown) => {
        setError(reason instanceof Error ? reason.message : "Unable to load community activity.");
      },
    );
  }, [canModerateSelected, loadModeration, loadPosts, selected]);

  async function submitRequest(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setNotice("");
    const form = new FormData(event.currentTarget);
    try {
      const request = await apiRequest<{ status: string }>(
        apiBaseUrl,
        "/api/v1/user/social/communities/requests",
        {
          method: "POST",
          body: JSON.stringify({
            slug: String(form.get("slug") ?? ""),
            name: String(form.get("name") ?? ""),
            description: String(form.get("description") ?? ""),
            access_type: String(form.get("access_type") ?? "open"),
          }),
        },
      );
      setRequestForm(false);
      setNotice(
        `Community request submitted (${request.status}). Platform approval is required before it appears here.`,
      );
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : "Unable to submit your community request.",
      );
    } finally {
      setBusy(false);
    }
  }

  async function joinSelected() {
    if (!selected) return;
    setBusy(true);
    setError("");
    try {
      const result = await apiRequest<{ status: "active" | "pending" }>(
        apiBaseUrl,
        communityPath(selected.id, "join"),
        { method: "POST", body: JSON.stringify({}) },
      );
      await loadCommunities();
      setNotice(
        result.status === "active"
          ? "You joined this community."
          : "Your membership application is pending moderator approval.",
      );
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to join this community.");
    } finally {
      setBusy(false);
    }
  }

  async function publishPost(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selected) return;
    setBusy(true);
    setError("");
    try {
      await apiRequest<Post>(
        apiBaseUrl,
        communityPath(selected.id, "posts"),
        {
          method: "POST",
          body: JSON.stringify({ kind: postKind, body: postDraft }),
        },
      );
      setPostDraft("");
      setPostKind("discussion");
      await loadPosts(selected.id);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to publish.");
    } finally {
      setBusy(false);
    }
  }

  async function addComment(postId: string) {
    const body = commentDrafts[postId] ?? "";
    setBusy(true);
    setError("");
    try {
      await apiRequest<Comment>(
        apiBaseUrl,
        `/api/v1/user/social/posts/${encodeURIComponent(postId)}/comments`,
        { method: "POST", body: JSON.stringify({ body }) },
      );
      setCommentDrafts((current) => ({ ...current, [postId]: "" }));
      if (selected) await loadPosts(selected.id);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to add a comment.");
    } finally {
      setBusy(false);
    }
  }

  async function react(postId: string) {
    setBusy(true);
    setError("");
    try {
      const current = reactions[postId]?.current_user_reaction;
      const result = current
        ? await apiRequest<Reaction>(
            apiBaseUrl,
            `/api/v1/user/social/posts/${encodeURIComponent(postId)}/reactions`,
            { method: "DELETE" },
          )
        : await apiRequest<Reaction>(
            apiBaseUrl,
            `/api/v1/user/social/posts/${encodeURIComponent(postId)}/reactions`,
            {
              method: "PUT",
              body: JSON.stringify({ kind: "like" }),
            },
          );
      setReactions((items) => ({ ...items, [postId]: result }));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to update your reaction.");
    } finally {
      setBusy(false);
    }
  }

  async function reviewMembership(membershipId: string, decision: "approve" | "reject") {
    if (!selected) return;
    setError("");
    try {
      await apiRequest(
        apiBaseUrl,
        communityPath(selected.id, "memberships", membershipId, "decision"),
        { method: "POST", body: JSON.stringify({ decision }) },
      );
      await loadModeration(selected.id, true);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to review membership.");
    }
  }

  async function moderate(report: ModerationReport, action: ModerationAction["action"]) {
    if (!selected) return;
    const reason = window.prompt(`Reason for ${action}:`);
    if (!reason?.trim()) return;
    setError("");
    try {
      await apiRequest(
        apiBaseUrl,
        communityPath(selected.id, "moderation", "reports", report.id, "actions"),
        {
          method: "POST",
          body: JSON.stringify({
            action,
            reason,
            ...(action === "suspend" ? { duration_hours: 24 } : {}),
          }),
        },
      );
      await Promise.all([loadModeration(selected.id, true), loadPosts(selected.id)]);
    } catch (reasonValue) {
      setError(reasonValue instanceof Error ? reasonValue.message : "Unable to apply moderation.");
    }
  }

  async function appeal(actionId: string) {
    const reason = window.prompt("Why should this moderation action be reviewed?");
    if (!reason?.trim()) return;
    try {
      await apiRequest(
        apiBaseUrl,
        `/api/v1/user/social/me/moderation/actions/${encodeURIComponent(actionId)}/appeals`,
        { method: "POST", body: JSON.stringify({ reason }) },
      );
      if (selected) await loadModeration(selected.id, canModerateSelected);
    } catch (reasonValue) {
      setError(reasonValue instanceof Error ? reasonValue.message : "Unable to submit an appeal.");
    }
  }

  async function reviewAppeal(appealId: string, decision: "upheld" | "overturned") {
    if (!selected) return;
    try {
      await apiRequest(
        apiBaseUrl,
        communityPath(selected.id, "moderation", "appeals", appealId, "decision"),
        { method: "POST", body: JSON.stringify({ decision }) },
      );
      await Promise.all([loadModeration(selected.id, true), loadPosts(selected.id)]);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to review the appeal.");
    }
  }

  return (
    <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_20rem]">
      <div className="grid gap-6">
        {error && (
          <Alert className="border-danger/30 bg-danger-muted">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        {notice && (
          <Alert>
            <AlertDescription>{notice}</AlertDescription>
          </Alert>
        )}
        <Card>
          <CardHeader>
            <CardTitle>Community directory</CardTitle>
            <CardDescription>Membership and posts are scoped to each community.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3">
            {!member ? (
              loading ? (
                <p role="status">Checking your account…</p>
              ) : (
                <AuthPanel
                  apiBaseUrl={apiBaseUrl}
                  showLearningConsent={false}
                  onAuthenticated={setMember}
                />
              )
            ) : communities.length ? (
              communities.map((community) => (
                <button
                  type="button"
                  key={community.id}
                  onClick={() => setSelectedId(community.id)}
                  className={`grid gap-1 rounded-lg border p-4 text-left transition hover:border-primary/40 ${
                    community.id === selectedId ? "border-primary bg-primary/5" : "border-border"
                  }`}
                >
                  <span className="flex flex-wrap items-center gap-2 font-semibold">
                    {community.name}
                    <span
                      className="rounded-full bg-secondary px-2 py-0.5 text-xs font-medium text-secondary-foreground"
                    >
                      {community.access_type === "open" ? "Open" : "Restricted"}
                    </span>
                  </span>
                  <span className="text-sm text-muted-foreground">{community.description}</span>
                  <span className="text-xs text-muted-foreground">
                    Membership: {community.membership_status}
                    {community.membership_role ? ` · ${community.membership_role}` : ""}
                  </span>
                </button>
              ))
            ) : (
              <p className="text-sm text-muted-foreground">
                No communities are active yet. Submit a free creation request; platform review tools
                are still being built.
              </p>
            )}
            {member && (
              <Button
                type="button"
                variant="outline"
                onClick={() => setRequestForm((value) => !value)}
              >
                Request a community
              </Button>
            )}
            {requestForm && (
              <form
                className="grid gap-3 rounded-lg border border-border p-4"
                onSubmit={submitRequest}
              >
                <div className="grid gap-2">
                  <Label htmlFor="community-name">Name</Label>
                  <Input id="community-name" name="name" minLength={3} maxLength={120} required />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="community-slug">URL slug</Label>
                  <Input
                    id="community-slug"
                    name="slug"
                    pattern="[a-z0-9]+(-[a-z0-9]+)*"
                    minLength={3}
                    maxLength={80}
                    required
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="community-description">Description</Label>
                  <Textarea
                    id="community-description"
                    name="description"
                    minLength={10}
                    maxLength={1000}
                    required
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="community-access">Access</Label>
                  <select
                    id="community-access"
                    name="access_type"
                    className="min-h-11 rounded-md border border-input bg-background px-3 text-sm"
                  >
                    <option value="open">Open to members</option>
                    <option value="restricted">Restricted; moderator approval</option>
                  </select>
                </div>
                <Button type="submit" isLoading={busy}>Submit request</Button>
              </form>
            )}
          </CardContent>
        </Card>

        {selected && member && (
          <section className="grid gap-4" aria-labelledby="selected-community-heading">
            <div>
              <h2 id="selected-community-heading" className="font-display text-2xl">
                {selected.name}
              </h2>
              <p className="mt-1 text-sm text-muted-foreground">
                {selected.rules || selected.description}
              </p>
            </div>
            {selected.membership_status === "none" || selected.membership_status === "rejected" ? (
              <Button type="button" onClick={() => void joinSelected()} isLoading={busy}>
                {selected.access_type === "open" ? "Join community" : "Apply to join"}
              </Button>
            ) : selected.membership_status === "pending" ? (
              <p role="status" className="text-sm text-muted-foreground">
                Your application is awaiting moderator review.
              </p>
            ) : (
              <>
                <Card>
                  <CardHeader>
                    <CardTitle>Start a discussion</CardTitle>
                    <CardDescription>
                      Only active community members can publish here.
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <form className="grid gap-3" onSubmit={publishPost}>
                      <Label htmlFor="community-post">Your question or discussion</Label>
                      <Textarea
                        id="community-post"
                        value={postDraft}
                        onChange={(event) => setPostDraft(event.target.value)}
                        maxLength={5000}
                        required
                      />
                      <div className="grid gap-2">
                        <Label htmlFor="community-post-kind">Post type</Label>
                        <select
                          id="community-post-kind"
                          value={postKind}
                          onChange={(event) => setPostKind(event.target.value as Post["kind"])}
                          className="min-h-11 rounded-md border border-input bg-background px-3 text-sm"
                        >
                          <option value="discussion">Discussion</option>
                          <option value="question">Question</option>
                        </select>
                      </div>
                      <Button type="submit" isLoading={busy}>Publish</Button>
                    </form>
                  </CardContent>
                </Card>
                {posts.length ? posts.map((post) => (
                  <Card key={post.id}>
                    <CardHeader>
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <CardTitle className="text-base">
                          {post.author_display_name} · {post.kind}
                        </CardTitle>
                        <CardDescription>{dateLabel(post.created_at)}</CardDescription>
                      </div>
                    </CardHeader>
                    <CardContent className="grid gap-4">
                      <p className="whitespace-pre-wrap break-words">{post.body}</p>
                      <div className="flex items-center gap-3">
                        <Button
                          type="button"
                          variant="outline"
                          onClick={() => void react(post.id)}
                          disabled={busy}
                        >
                          {reactions[post.id]?.current_user_reaction ? "Unlike" : "Like"} ·{" "}
                          {reactions[post.id]?.count ?? 0}
                        </Button>
                        {member.id !== post.author_id && (
                          <Button type="button" variant="ghost" onClick={() => {
                            const reason = window.prompt("Why should moderators review this post?");
                            if (reason?.trim()) {
                              void apiRequest(
                                apiBaseUrl,
                                `/api/v1/user/social/posts/${encodeURIComponent(post.id)}/reports`,
                                {
                                  method: "POST",
                                  body: JSON.stringify({ reason }),
                                },
                              )
                                .then(() =>
                                  setNotice("Report submitted for moderator review."),
                                )
                                .catch((reasonValue: unknown) =>
                                  setError(
                                    reasonValue instanceof Error
                                      ? reasonValue.message
                                      : "Unable to report post.",
                                  ),
                                );
                            }
                          }}>Report post</Button>
                        )}
                      </div>
                      <div className="grid gap-3 border-t border-border pt-3">
                        {(comments[post.id] ?? []).map((comment) => (
                          <div
                            key={comment.id}
                            className="grid gap-1 rounded-md bg-muted/40 p-3 text-sm"
                          >
                            <span className="font-medium">{comment.author_display_name}</span>
                            <span className="whitespace-pre-wrap">{comment.body}</span>
                            {member.id !== comment.author_id && (
                              <button
                                type="button"
                                className="justify-self-start text-xs text-primary underline"
                                onClick={() => {
                                  const reason = window.prompt(
                                    "Why should moderators review this comment?",
                                  );
                                  if (reason?.trim()) {
                                    void apiRequest(
                                      apiBaseUrl,
                                      `/api/v1/user/social/comments/${encodeURIComponent(comment.id)}/reports`,
                                      {
                                        method: "POST",
                                        body: JSON.stringify({ reason }),
                                      },
                                    )
                                      .then(() =>
                                        setNotice(
                                          "Comment report submitted for moderator review.",
                                        ),
                                      )
                                      .catch((reasonValue: unknown) =>
                                        setError(
                                          reasonValue instanceof Error
                                            ? reasonValue.message
                                            : "Unable to report comment.",
                                        ),
                                      );
                                  }
                                }}
                              >
                                Report comment
                              </button>
                            )}
                          </div>
                        ))}
                        <div className="flex flex-col gap-2 sm:flex-row">
                          <Textarea
                            aria-label="Add a comment"
                            value={commentDrafts[post.id] ?? ""}
                            onChange={(event) =>
                              setCommentDrafts((current) => ({
                                ...current,
                                [post.id]: event.target.value,
                              }))
                            }
                            maxLength={2000}
                            placeholder="Add a comment…"
                          />
                          <Button
                            type="button"
                            variant="outline"
                            onClick={() => void addComment(post.id)}
                            disabled={busy || !(commentDrafts[post.id] ?? "").trim()}
                          >
                            Comment
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )) : <p className="text-sm text-muted-foreground">No community posts yet.</p>}
              </>
            )}
          </section>
        )}
      </div>

      {selected &&
        member &&
        selected.membership_role &&
        ["owner", "moderator"].includes(selected.membership_role) && (
        <aside className="grid gap-4 lg:sticky lg:top-6">
          <Card>
            <CardHeader><CardTitle>Membership applications</CardTitle></CardHeader>
            <CardContent className="grid gap-3">
              {pendingMembers.length ? pendingMembers.map((application) => (
                <div
                  key={application.id}
                  className="grid gap-2 border-b border-border pb-3 last:border-0"
                >
                  <p className="text-sm">
                    <strong>{application.display_name}</strong>
                    {application.application_message ? `: ${application.application_message}` : ""}
                  </p>
                  <div className="flex gap-2">
                    <Button
                      type="button"
                      size="sm"
                      onClick={() => void reviewMembership(application.id, "approve")}
                    >
                      Approve
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      onClick={() => void reviewMembership(application.id, "reject")}
                    >
                      Reject
                    </Button>
                  </div>
                </div>
              )) : <p className="text-sm text-muted-foreground">No pending applications.</p>}
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Pending reports</CardTitle></CardHeader>
            <CardContent className="grid gap-3">
              {reports.length ? reports.map((report) => (
                <div
                  key={report.id}
                  className="grid gap-2 border-b border-border pb-3 last:border-0"
                >
                  <p className="text-sm">
                    <strong>{report.reporter_display_name}</strong> reported{" "}
                    {report.post_id ? "a post" : "a comment"}: {report.reason}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {(["hide", "remove", "warn", "suspend", "escalate", "dismiss"] as const).map((action) => (
                      <Button
                        key={action}
                        type="button"
                        size="sm"
                        variant={action === "remove" ? "destructive" : "outline"}
                        onClick={() => void moderate(report, action)}
                      >
                        {action}
                      </Button>
                    ))}
                  </div>
                </div>
              )) : <p className="text-sm text-muted-foreground">No pending reports.</p>}
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Appeals</CardTitle></CardHeader>
            <CardContent className="grid gap-3">
              {appeals.length ? appeals.map((item) => (
                <div key={item.id} className="grid gap-2 border-b border-border pb-3 last:border-0">
                  <p className="text-sm">{item.reason}</p>
                  <div className="flex gap-2">
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      onClick={() => void reviewAppeal(item.id, "upheld")}
                    >
                      Uphold
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      onClick={() => void reviewAppeal(item.id, "overturned")}
                    >
                      Overturn
                    </Button>
                  </div>
                </div>
              )) : <p className="text-sm text-muted-foreground">No pending appeals.</p>}
            </CardContent>
          </Card>
        </aside>
      )}

      {member && actions.some((action) => action.appeal_status === null) && (
        <section className="grid gap-3 lg:col-span-2" aria-label="Your moderation actions">
          <h2 className="font-display text-xl">Your moderation actions</h2>
          {actions.filter((action) => action.appeal_status === null).map((action) => (
            <Card key={action.id}>
              <CardContent className="flex flex-wrap items-center justify-between gap-3">
                <p className="text-sm">{action.action}: {action.reason}</p>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => void appeal(action.id)}
                >
                  Appeal
                </Button>
              </CardContent>
            </Card>
          ))}
        </section>
      )}
    </div>
  );
}
