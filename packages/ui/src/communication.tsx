"use client";

import { useCallback, useEffect, useRef, useState, type FormEvent } from "react";

import { Alert, AlertDescription } from "./alert";
import { Badge } from "./badge";
import { Button } from "./button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./card";
import { Input } from "./input";
import { Label } from "./label";
import { Textarea } from "./textarea";
import { cn } from "./utils";

interface ApiProblem {
  message?: string;
}

class ApiRequestError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

interface PortalUser {
  id: string;
  email: string;
  display_name: string;
  researcher_approved: boolean;
  ai_learning_consent: boolean;
}

interface Participant {
  id: string;
  email: string;
  display_name: string;
}

interface Conversation {
  id: string;
  participants: Participant[];
  created_at: string;
}

interface Message {
  id: string;
  conversation_id: string;
  sender_id: string;
  sender_display_name: string;
  body: string;
  created_at: string;
}

function mergeMessages(current: Message[], incoming: Message[]): Message[] {
  const messages = new Map(current.map((message) => [message.id, message]));
  for (const message of incoming) messages.set(message.id, message);
  return [...messages.values()].sort(
    (first, second) =>
      Date.parse(first.created_at) - Date.parse(second.created_at) ||
      first.id.localeCompare(second.id),
  );
}

function isMessage(value: unknown): value is Message {
  if (typeof value !== "object" || value === null) return false;
  const message = value as Record<string, unknown>;
  return (
    typeof message.id === "string" &&
    typeof message.conversation_id === "string" &&
    typeof message.sender_id === "string" &&
    typeof message.sender_display_name === "string" &&
    typeof message.body === "string" &&
    typeof message.created_at === "string"
  );
}

interface ChatTurn {
  role: "user" | "assistant";
  content: string;
}

interface ChatResult {
  answer: string;
  provider: string;
  model: string | null;
  sources: string[];
  source_notice: string;
}

async function apiRequest<T>(
  apiBaseUrl: string,
  path: string,
  init: RequestInit = {},
): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl.replace(/\/$/, "")}${path}`, {
      ...init,
      credentials: "include",
      headers: {
        ...(init.body ? { "Content-Type": "application/json" } : {}),
        ...init.headers,
      },
    });
  } catch {
    throw new Error("The API is unavailable. Check that the backend is running on localhost:8000.");
  }

  if (!response.ok) {
    const problem = (await response.json().catch(() => ({}))) as ApiProblem;
    throw new ApiRequestError(problem.message ?? `Request failed (${response.status})`, response.status);
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export function AuthPanel({
  apiBaseUrl,
  onAuthenticated,
  showLearningConsent = true,
}: {
  apiBaseUrl: string;
  onAuthenticated?: (user: PortalUser | null) => void;
  showLearningConsent?: boolean;
}) {
  const [user, setUser] = useState<PortalUser | null>(null);
  const [mode, setMode] = useState<"login" | "register">("login");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const acceptUser = useCallback(
    (nextUser: PortalUser | null) => {
      setUser(nextUser);
      onAuthenticated?.(nextUser);
    },
    [onAuthenticated],
  );

  useEffect(() => {
    const controller = new AbortController();
    apiRequest<PortalUser>(apiBaseUrl, "/api/v1/user/auth/me", { signal: controller.signal })
      .then(acceptUser)
      .catch((reason: unknown) => {
        if (reason instanceof ApiRequestError && reason.status !== 401) {
          setError(reason.message);
        } else if (reason instanceof Error && !(reason instanceof ApiRequestError)) {
          setError(reason.message);
        }
      })
      .finally(() => setLoading(false));
    return () => controller.abort();
  }, [acceptUser, apiBaseUrl]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    const form = new FormData(event.currentTarget);
    const body = {
      email: String(form.get("email") ?? ""),
      password: String(form.get("password") ?? ""),
      ...(mode === "register" ? { display_name: String(form.get("display_name") ?? "") } : {}),
    };
    try {
      const nextUser = await apiRequest<PortalUser>(
        apiBaseUrl,
        `/api/v1/user/auth/${mode}`,
        { method: "POST", body: JSON.stringify(body) },
      );
      acceptUser(nextUser);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to authenticate");
    } finally {
      setSubmitting(false);
    }
  }

  async function signOut() {
    setError("");
    try {
      await apiRequest<void>(apiBaseUrl, "/api/v1/user/auth/logout", { method: "POST" });
      acceptUser(null);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to sign out");
    }
  }

  async function updateLearningConsent(allowed: boolean) {
    if (!user) return;
    setError("");
    try {
      const nextUser = await apiRequest<PortalUser>(
        apiBaseUrl,
        "/api/v1/user/auth/ai-learning-consent",
        { method: "PUT", body: JSON.stringify({ allowed }) },
      );
      acceptUser(nextUser);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to update consent");
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="font-display text-xl">
          {loading ? "Checking your session" : user ? `Welcome, ${user.display_name}` : "Your account"}
        </CardTitle>
        <CardDescription>
          Shared sign-in works across the localhost portals using an HttpOnly session cookie.
        </CardDescription>
      </CardHeader>
      <CardContent className="grid gap-4">
        {error && (
          <Alert className="border-danger/30 bg-danger-muted">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        {loading ? (
          <p role="status" className="text-sm text-muted-foreground">Checking session…</p>
        ) : user ? (
          <>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <p className="min-w-0 break-all text-sm text-muted-foreground">{user.email}</p>
              <Button type="button" variant="outline" onClick={signOut}>Sign out</Button>
            </div>
            {showLearningConsent && (
              <div className="grid gap-2 rounded-lg border border-border bg-surface-raised p-4">
                <Label className="flex items-start gap-3 leading-relaxed">
                  <input
                    type="checkbox"
                    className="mt-1 size-4 accent-primary"
                    checked={user.ai_learning_consent}
                    onChange={(event) => void updateLearningConsent(event.target.checked)}
                  />
                  <span>
                    Allow my AI prompts and responses to be retained for review to improve AI.
                    This consent is optional and can be withdrawn.
                  </span>
                </Label>
                <p className="text-xs leading-relaxed text-muted-foreground">
                  Training is not active. With consent off, prompt and response content is not
                  retained for learning; operational usage metadata is still recorded.
                </p>
              </div>
            )}
          </>
        ) : (
          <form onSubmit={submit} className="grid gap-4">
            {mode === "register" && (
              <div className="grid gap-2">
                <Label htmlFor="account-display-name">Display name</Label>
                <Input
                  id="account-display-name"
                  name="display_name"
                  autoComplete="name"
                  maxLength={80}
                  required
                />
              </div>
            )}
            <div className="grid gap-2">
              <Label htmlFor="account-email">Email</Label>
              <Input
                id="account-email"
                name="email"
                type="email"
                autoComplete="email"
                maxLength={320}
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="account-password">Password</Label>
              <Input
                id="account-password"
                name="password"
                type="password"
                autoComplete={mode === "register" ? "new-password" : "current-password"}
                minLength={mode === "register" ? 12 : 1}
                maxLength={128}
                required
              />
              {mode === "register" && (
                <p className="text-xs text-muted-foreground">Use at least 12 characters.</p>
              )}
            </div>
            <Button type="submit" isLoading={submitting}>
              {mode === "register" ? "Create account" : "Sign in"}
            </Button>
            <button
              type="button"
              className="min-h-11 text-sm text-primary underline-offset-4 hover:underline"
              onClick={() => setMode(mode === "register" ? "login" : "register")}
            >
              {mode === "register" ? "Already registered? Sign in" : "New here? Create an account"}
            </button>
          </form>
        )}
      </CardContent>
    </Card>
  );
}

export function MessagingPanel({ apiBaseUrl }: { apiBaseUrl: string }) {
  const [user, setUser] = useState<PortalUser | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [participants, setParticipants] = useState("");
  const [draft, setDraft] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const threadRef = useRef<HTMLDivElement>(null);

  const acceptUser = useCallback((nextUser: PortalUser | null) => {
    setUser(nextUser);
    setConversations([]);
    setSelectedId("");
    setMessages([]);
    setError("");
  }, []);

  const refreshConversations = useCallback(async () => {
    const items = await apiRequest<Conversation[]>(
      apiBaseUrl,
      "/api/v1/user/social/messages/conversations",
    );
    setConversations(items);
    if (!selectedId && items.length) setSelectedId(items[0].id);
  }, [apiBaseUrl, selectedId]);

  useEffect(() => {
    if (!user) return;
    refreshConversations().catch((reason: unknown) =>
      setError(reason instanceof Error ? reason.message : "Unable to load conversations"),
    );
  }, [refreshConversations, user]);

  useEffect(() => {
    if (!selectedId) {
      setMessages([]);
      return;
    }
    const controller = new AbortController();
    apiRequest<Message[]>(
      apiBaseUrl,
      `/api/v1/user/social/messages/conversations/${encodeURIComponent(selectedId)}/messages`,
      { signal: controller.signal },
    )
      .then(setMessages)
      .catch((reason: unknown) => {
        if (reason instanceof Error && !reason.message.includes("(404)")) setError(reason.message);
      });
    return () => controller.abort();
  }, [apiBaseUrl, selectedId]);

  useEffect(() => {
    if (!user || !selectedId) return;

    let disposed = false;
    let retryTimer: ReturnType<typeof setTimeout> | undefined;
    let retryDelay = 1000;
    let socket: WebSocket | undefined;
    const websocketBaseUrl = apiBaseUrl.replace(/^http/, "ws").replace(/\/+$/, "");
    const path = `/api/v1/user/social/messages/conversations/${encodeURIComponent(selectedId)}/ws`;

    function connect() {
      if (disposed) return;
      socket = new WebSocket(`${websocketBaseUrl}${path}`);
      socket.onopen = () => {
        retryDelay = 1000;
        void apiRequest<Message[]>(
          apiBaseUrl,
          `/api/v1/user/social/messages/conversations/${encodeURIComponent(selectedId)}/messages`,
        )
          .then((items) => {
            setMessages((current) => mergeMessages(current, items));
          })
          .catch((reason: unknown) => {
            setError(reason instanceof Error ? reason.message : "Unable to refresh messages");
          });
      };
      socket.onmessage = (event: MessageEvent<string>) => {
        let message: unknown;
        try {
          message = JSON.parse(event.data);
        } catch {
          setError("Received an invalid real-time message.");
          return;
        }
        if (!isMessage(message) || message.conversation_id !== selectedId) {
          setError("Received an invalid real-time message.");
          return;
        }
        setMessages((current) => mergeMessages(current, [message]));
      };
      socket.onclose = (event) => {
        if (disposed) return;
        if (event.code === 4401) {
          setUser(null);
          setError("Your session expired. Sign in again to continue messaging.");
          return;
        }
        if (event.code === 4403 || event.code === 4404) {
          setError(event.reason || "Unable to access this conversation.");
          return;
        }
        setError("Real-time messaging disconnected. Reconnecting…");
        retryTimer = setTimeout(connect, retryDelay);
        retryDelay = Math.min(retryDelay * 2, 15000);
      };
      socket.onerror = () => socket?.close();
    }

    connect();
    return () => {
      disposed = true;
      if (retryTimer) clearTimeout(retryTimer);
      socket?.close();
    };
  }, [apiBaseUrl, selectedId, user]);

  useEffect(() => {
    threadRef.current?.scrollTo({ top: threadRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  async function startConversation(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const conversation = await apiRequest<Conversation>(
        apiBaseUrl,
        "/api/v1/user/social/messages/conversations",
        {
          method: "POST",
          body: JSON.stringify({
            participant_emails: participants.split(",").map((email) => email.trim()),
          }),
        },
      );
      setSelectedId(conversation.id);
      setParticipants("");
      await refreshConversations();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to start conversation");
    } finally {
      setBusy(false);
    }
  }

  async function sendMessage(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedId || !draft.trim()) return;
    setBusy(true);
    setError("");
    try {
      const sent = await apiRequest<Message>(
        apiBaseUrl,
        `/api/v1/user/social/messages/conversations/${encodeURIComponent(selectedId)}/messages`,
        { method: "POST", body: JSON.stringify({ body: draft.trim() }) },
      );
      setMessages((current) => mergeMessages(current, [sent]));
      setDraft("");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to send message");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid gap-5">
      <AuthPanel apiBaseUrl={apiBaseUrl} onAuthenticated={acceptUser} showLearningConsent={false} />
      {user && (
        <Card>
          <CardHeader>
            <CardTitle className="font-display text-xl">Text messages</CardTitle>
            <CardDescription>
              Direct and group text only. Attachments, audio, and video are not supported.
            </CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4">
            {error && (
              <Alert className="border-danger/30 bg-danger-muted">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            <form onSubmit={startConversation} className="grid gap-2 sm:grid-cols-[1fr_auto]">
              <div className="grid gap-2">
                <Label htmlFor="message-participants">Participant emails</Label>
                <Input
                  id="message-participants"
                  value={participants}
                  onChange={(event) => setParticipants(event.target.value)}
                  placeholder="person@example.com, another@example.com"
                  required
                />
              </div>
              <Button type="submit" className="self-end" isLoading={busy}>New conversation</Button>
            </form>
            <div className="grid min-h-[26rem] overflow-hidden rounded-xl border border-border md:grid-cols-[14rem_minmax(0,1fr)]">
              <nav aria-label="Conversations" className="grid content-start gap-1 border-b border-border p-2 md:border-r md:border-b-0">
                {conversations.map((conversation) => (
                  <button
                    key={conversation.id}
                    type="button"
                    aria-current={selectedId === conversation.id ? "true" : undefined}
                    className={cn(
                      "min-h-11 rounded-lg px-3 text-left text-sm hover:bg-accent",
                      selectedId === conversation.id && "bg-accent text-accent-foreground",
                    )}
                    onClick={() => setSelectedId(conversation.id)}
                  >
                    {conversation.participants
                      .filter((participant) => participant.id !== user.id)
                      .map((participant) => participant.display_name)
                      .join(", ")}
                  </button>
                ))}
                {!conversations.length && (
                  <p className="p-3 text-sm text-muted-foreground">No conversations yet.</p>
                )}
              </nav>
              <div className="flex min-w-0 flex-col">
                <div
                  ref={threadRef}
                  aria-live="polite"
                  className="grid max-h-[22rem] flex-1 content-start gap-3 overflow-y-auto p-4"
                >
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={cn(
                        "max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed",
                        message.sender_id === user.id
                          ? "ml-auto bg-chat-user-message text-chat-user-foreground"
                          : "bg-chat-assistant-message text-chat-assistant-foreground",
                      )}
                    >
                      {message.sender_id !== user.id && (
                        <p className="mb-1 text-xs font-semibold">{message.sender_display_name}</p>
                      )}
                      <p className="whitespace-pre-wrap break-words">{message.body}</p>
                    </div>
                  ))}
                  {!messages.length && (
                    <p className="m-auto text-center text-sm text-muted-foreground">
                      Choose a conversation or start one above.
                    </p>
                  )}
                </div>
                <form onSubmit={sendMessage} className="flex gap-2 border-t border-border p-3">
                  <Label className="sr-only" htmlFor="message-draft">Message</Label>
                  <Input
                    id="message-draft"
                    value={draft}
                    onChange={(event) => setDraft(event.target.value)}
                    maxLength={5000}
                    placeholder="Write a text message"
                    disabled={!selectedId}
                  />
                  <Button type="submit" isLoading={busy} disabled={!selectedId || !draft.trim()}>
                    Send
                  </Button>
                </form>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export function AIChatPanel({
  apiBaseUrl,
  environment,
}: {
  apiBaseUrl: string;
  environment: "general" | "scientist";
}) {
  const [user, setUser] = useState<PortalUser | null>(null);
  const [messages, setMessages] = useState<ChatTurn[]>([]);
  const [draft, setDraft] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const endpoint =
    environment === "general"
      ? "/api/v1/user/social/ai/chat"
      : "/api/v1/user/researcher/ai/chat";
  const acceptUser = useCallback((nextUser: PortalUser | null) => {
    setUser(nextUser);
    setMessages([]);
    setError("");
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const content = draft.trim();
    if (!content || busy) return;
    const nextMessages = [...messages, { role: "user" as const, content }];
    setMessages(nextMessages);
    setDraft("");
    setBusy(true);
    setError("");
    try {
      const result = await apiRequest<ChatResult>(apiBaseUrl, endpoint, {
        method: "POST",
        body: JSON.stringify({ messages: nextMessages }),
      });
      setMessages([
        ...nextMessages,
        {
          role: "assistant",
          content: `${result.answer}\n\n${result.source_notice}`,
        },
      ]);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The AI request failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid gap-5">
      <AuthPanel apiBaseUrl={apiBaseUrl} onAuthenticated={acceptUser} />
      {environment === "scientist" && (
        <Alert>
          <AlertDescription>
            Restricted prototype: only explicitly approved researchers can use it. It has no
            literature corpus, project retrieval, or research tools connected.
          </AlertDescription>
        </Alert>
      )}
      {user && (
        <Card>
          <CardHeader>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <CardTitle className="font-display text-xl">
                  {environment === "general" ? "General Platform AI" : "Private AI Scientist"}
                </CardTitle>
                <CardDescription className="mt-1">
                  {environment === "general"
                    ? "General science and learning assistance. Do not enter private health or research information."
                    : "A restricted prototype. No scientific corpus is connected."}
                </CardDescription>
              </div>
              <Badge variant="outline">
                {environment === "general" ? "General knowledge" : "Prototype"}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="grid gap-4">
            {error && (
              <Alert className="border-danger/30 bg-danger-muted">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            <div
              role="log"
              aria-live="polite"
              className="grid min-h-72 max-h-[32rem] content-start gap-3 overflow-y-auto rounded-xl border border-border bg-surface-sunken p-4"
            >
              {!messages.length && (
                <p className="m-auto max-w-sm text-center text-sm text-muted-foreground">
                  Ask a question to begin. The backend provider must be configured before responses
                  are available.
                </p>
              )}
              {messages.map((message, index) => (
                <div
                  key={`${index}-${message.role}`}
                  className={cn(
                    "max-w-[90%] whitespace-pre-wrap break-words rounded-2xl px-4 py-3 text-sm leading-relaxed",
                    message.role === "user"
                      ? "ml-auto bg-chat-user-message text-chat-user-foreground"
                      : "bg-chat-assistant-message text-chat-assistant-foreground",
                  )}
                >
                  <p className="mb-1 text-xs font-semibold">
                    {message.role === "user" ? user.display_name : "AI assistant"}
                  </p>
                  {message.content}
                </div>
              ))}
            </div>
            <form onSubmit={submit} className="grid gap-2">
              <Label htmlFor={`ai-prompt-${environment}`}>Your question</Label>
              <Textarea
                id={`ai-prompt-${environment}`}
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                maxLength={4000}
                rows={3}
                placeholder="Ask a science or healthspan question"
              />
              <div className="flex justify-end">
                <Button type="submit" isLoading={busy} disabled={!draft.trim()}>
                  Send question
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
