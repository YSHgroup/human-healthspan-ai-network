"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";

import { AuthPanel } from "@healthspan/ui/communication";
import { Alert, AlertDescription } from "@healthspan/ui/alert";
import { Button } from "@healthspan/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@healthspan/ui/card";
import { Label } from "@healthspan/ui/label";
import { Textarea } from "@healthspan/ui/textarea";

interface Member {
  id: string;
  display_name: string;
}

interface SocialPost {
  id: string;
  author_id: string;
  author_display_name: string;
  kind: "discussion" | "question";
  body: string;
  created_at: string;
}

class FeedRequestError extends Error {
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
    try {
      const payload: unknown = await response.json();
      if (typeof payload === "object" && payload !== null && "message" in payload) {
        const detail = payload.message;
        if (typeof detail === "string") message = detail;
      }
    } catch (error) {
      if (!(error instanceof SyntaxError)) throw error;
    }
    throw new FeedRequestError(message, response.status);
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function SocialFeed({ apiBaseUrl }: { apiBaseUrl: string }) {
  const [member, setMember] = useState<Member | null>(null);
  const [posts, setPosts] = useState<SocialPost[]>([]);
  const [draft, setDraft] = useState("");
  const [kind, setKind] = useState<SocialPost["kind"]>("discussion");
  const [reportingPostId, setReportingPostId] = useState<string | null>(null);
  const [reportReason, setReportReason] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const loadFeed = useCallback(async (signal?: AbortSignal) => {
    const items = await apiRequest<SocialPost[]>(
      apiBaseUrl,
      "/api/v1/user/social/feed",
      { signal },
    );
    setPosts(items);
  }, [apiBaseUrl]);

  useEffect(() => {
    const controller = new AbortController();
    void loadFeed(controller.signal)
      .catch((reason: unknown) => {
        if (!controller.signal.aborted) {
          setError(reason instanceof Error ? reason.message : "Unable to load the community feed.");
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [loadFeed]);

  useEffect(() => {
    const controller = new AbortController();
    void apiRequest<Member & { email: string; researcher_approved: boolean; ai_learning_consent: boolean }>(
      apiBaseUrl,
      "/api/v1/user/auth/me",
      { signal: controller.signal },
    )
      .then(setMember)
      .catch((reason: unknown) => {
        if (
          !controller.signal.aborted &&
          (!(reason instanceof FeedRequestError) || reason.status !== 401)
        ) {
          setError(reason instanceof Error ? reason.message : "Unable to check your sign-in.");
        }
      });
    return () => controller.abort();
  }, [apiBaseUrl]);

  async function publish(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    setNotice("");
    try {
      const post = await apiRequest<SocialPost>(apiBaseUrl, "/api/v1/user/social/posts", {
        method: "POST",
        body: JSON.stringify({ kind, body: draft }),
      });
      setPosts((current) => [post, ...current]);
      setDraft("");
      setNotice("Your post is now public.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to publish your post.");
    } finally {
      setSubmitting(false);
    }
  }

  async function report(postId: string) {
    setSubmitting(true);
    setError("");
    setNotice("");
    try {
      await apiRequest(apiBaseUrl, `/api/v1/user/social/posts/${encodeURIComponent(postId)}/reports`, {
        method: "POST",
        body: JSON.stringify({ reason: reportReason }),
      });
      setReportingPostId(null);
      setReportReason("");
      setNotice("Your report was submitted for moderation review.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to submit your report.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_20rem]">
      <section aria-labelledby="feed-heading" className="grid gap-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 id="feed-heading" className="font-display text-2xl">Community feed</h2>
          <Button
            type="button"
            variant="outline"
            onClick={() => {
              setLoading(true);
              void loadFeed()
                .catch((reason: unknown) =>
                  setError(reason instanceof Error ? reason.message : "Unable to refresh the feed."),
                )
                .finally(() => setLoading(false));
            }}
            disabled={loading}
          >
            Refresh
          </Button>
        </div>

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

        {loading ? (
          <p role="status" className="text-sm text-muted-foreground">Loading public discussions…</p>
        ) : posts.length ? (
          posts.map((post) => (
            <Card key={post.id}>
              <CardHeader>
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <CardTitle className="text-base">
                    {post.author_display_name}
                    <span className="ml-2 rounded-full bg-secondary px-2.5 py-1 text-xs font-medium text-secondary-foreground">
                      {post.kind === "question" ? "Question" : "Discussion"}
                    </span>
                  </CardTitle>
                  <CardDescription>{formatDate(post.created_at)}</CardDescription>
                </div>
              </CardHeader>
              <CardContent className="grid gap-4">
                <p className="whitespace-pre-wrap break-words leading-relaxed">{post.body}</p>
                {member && member.id !== post.author_id && (
                  reportingPostId === post.id ? (
                    <form
                      className="grid gap-3 border-t border-border pt-4"
                      onSubmit={(event) => {
                        event.preventDefault();
                        void report(post.id);
                      }}
                    >
                      <Label htmlFor={`report-reason-${post.id}`}>Why should moderators review this?</Label>
                      <Textarea
                        id={`report-reason-${post.id}`}
                        value={reportReason}
                        onChange={(event) => setReportReason(event.target.value)}
                        minLength={3}
                        maxLength={500}
                        required
                      />
                      <div className="flex flex-wrap gap-2">
                        <Button type="submit" isLoading={submitting}>Submit report</Button>
                        <Button
                          type="button"
                          variant="outline"
                          onClick={() => {
                            setReportingPostId(null);
                            setReportReason("");
                          }}
                        >
                          Cancel
                        </Button>
                      </div>
                    </form>
                  ) : (
                    <Button
                      type="button"
                      variant="ghost"
                      className="justify-self-start"
                      onClick={() => {
                        setReportingPostId(post.id);
                        setError("");
                        setNotice("");
                      }}
                    >
                      Report post
                    </Button>
                  )
                )}
              </CardContent>
            </Card>
          ))
        ) : (
          <Card>
            <CardContent className="py-8 text-center">
              <p className="font-medium">No posts yet</p>
              <p className="mt-1 text-sm text-muted-foreground">Be the first to start a discussion.</p>
            </CardContent>
          </Card>
        )}
      </section>

      <aside className="grid gap-4 lg:sticky lg:top-6">
        {member ? (
          <Card>
            <CardHeader>
              <CardTitle>Start a conversation</CardTitle>
              <CardDescription>Your post will be visible publicly.</CardDescription>
            </CardHeader>
            <CardContent>
              <form className="grid gap-4" onSubmit={publish}>
                <div className="grid gap-2">
                  <Label htmlFor="post-kind">Post type</Label>
                  <select
                    id="post-kind"
                    className="min-h-11 rounded-md border border-input bg-background px-3 text-sm"
                    value={kind}
                    onChange={(event) =>
                      setKind(event.target.value === "question" ? "question" : "discussion")
                    }
                  >
                    <option value="discussion">Discussion</option>
                    <option value="question">Question</option>
                  </select>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="post-body">What would you like to share?</Label>
                  <Textarea
                    id="post-body"
                    value={draft}
                    onChange={(event) => setDraft(event.target.value)}
                    minLength={1}
                    maxLength={5000}
                    placeholder="Share a question or start a discussion…"
                    required
                  />
                </div>
                <Button type="submit" isLoading={submitting}>Publish publicly</Button>
              </form>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-2">
            <p className="text-sm text-muted-foreground">
              Sign in to publish to the feed or report a post.
            </p>
            <AuthPanel
              apiBaseUrl={apiBaseUrl}
              onAuthenticated={setMember}
              showLearningConsent={false}
            />
          </div>
        )}
      </aside>
    </div>
  );
}
