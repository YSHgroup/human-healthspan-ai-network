import type {
  ActivityItem, AIAnswer, Badge, Consent, Conversation, Entitlement, EventItem, HealthRecord, HealthShare,
  Invitation, Message, NotificationItem, OrgAIInstance, OrgDocument, Organization, OrganizationMember,
  ProfessionalRecord, ResearchMembershipState, ResearchTask, WorkHistoryEntry,
} from "@healthspan/shared-types";

export class ApiError extends Error {
  constructor(public readonly status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

export interface ApiClientOptions {
  /** Same-origin BFF proxy that attaches the HttpOnly session cookie. */
  proxyBase?: string;
}

function describeDetail(result: unknown, fallback: string): string {
  if (typeof result === "object" && result !== null && "detail" in result) {
    const detail = (result as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail.map((item) => (typeof item === "object" && item && "msg" in item ? String((item as { msg: unknown }).msg) : String(item))).join(" ");
    }
  }
  return typeof result === "string" && result ? result : fallback;
}

const q = (params: Record<string, string | number | boolean | undefined | null>): string => {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) if (value !== undefined && value !== null && value !== "") search.set(key, String(value));
  const text = search.toString();
  return text ? `?${text}` : "";
};

export function createApiClient(options: ApiClientOptions = {}) {
  const proxy = (options.proxyBase ?? "/api/backend").replace(/\/+$/, "");

  async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
    const response = await fetch(`${proxy}/api/v1${path}`, {
      cache: "no-store",
      credentials: "same-origin",
      ...init,
      headers: { ...(init.body ? { "Content-Type": "application/json" } : {}), ...init.headers },
    });
    const text = await response.text();
    if (response.status === 204) return undefined as T;
    let result: unknown;
    try {
      result = text ? JSON.parse(text) : undefined;
    } catch {
      result = text;
    }
    if (!response.ok) throw new ApiError(response.status, describeDetail(result, response.statusText || "Request failed."));
    return result as T;
  }
  const get = <T>(path: string) => request<T>(path);
  const post = <T>(path: string, body?: unknown) => request<T>(path, { method: "POST", body: body === undefined ? undefined : JSON.stringify(body) });
  const patch = <T>(path: string, body: unknown) => request<T>(path, { method: "PATCH", body: JSON.stringify(body) });
  const del = <T = void>(path: string) => request<T>(path, { method: "DELETE" });

  const social = "/user/social";
  const personal = "/user/personal";
  const researcher = "/user/researcher";

  return {
    request,
    ai: {
      general: (prompt: string, conversationId?: string) => post<AIAnswer>("/user/ai/general/chat", { prompt, conversation_id: conversationId }),
      scientist: (prompt: string, conversationId?: string) => post<AIAnswer>(`${researcher}/ai-scientist/chat`, { prompt, conversation_id: conversationId }),
      organization: (organizationId: string, prompt: string, conversationId?: string) =>
        post<AIAnswer>(`${researcher}/organization-ai/${organizationId}/chat`, { prompt, conversation_id: conversationId }),
      feedback: (runId: string, rating: "up" | "down", comment?: string) =>
        post<void>(`/user/ai/general/runs/${runId}/feedback`, { rating, comment }),
    },
    social: {
      events: (params: { mine?: boolean; include_past?: boolean } = {}) => get<EventItem[]>(`${social}/events${q(params)}`),
      createEvent: (body: Record<string, unknown>) => post<EventItem>(`${social}/events`, body),
      register: (id: string) => post<EventItem>(`${social}/events/${id}/register`),
      unregister: (id: string) => del<EventItem>(`${social}/events/${id}/register`),
      notifications: (unreadOnly = false) => get<NotificationItem[]>(`${social}/notifications${q({ unread_only: unreadOnly })}`),
      unreadCount: () => get<{ unread: number }>(`${social}/notifications/unread-count`),
      markRead: (id: string) => post<NotificationItem>(`${social}/notifications/${id}/read`),
      markAllRead: () => post<void>(`${social}/notifications/read-all`),
      invitations: () => get<Invitation[]>(`${social}/invitations`),
      respondInvitation: (id: string, accept: boolean) => post<{ status: string }>(`${social}/invitations/${id}/${accept ? "accept" : "decline"}`),
      connections: () => get<{ following: Array<{ user_id: string; display_name: string; mutual: boolean }>; followers: Array<{ user_id: string; display_name: string; mutual: boolean }>; connection_count: number }>(`${social}/connections`),
    },
    messages: {
      conversations: () => get<Conversation[]>(`${personal}/messages/conversations`),
      thread: (id: string) => get<Message[]>(`${personal}/messages/conversations/${id}/messages`),
      send: (body: { recipient_id?: string; conversation_id?: string; body: string }) => post<Message>(`${personal}/messages`, body),
    },
    personal: {
      activity: () => get<ActivityItem[]>(`${personal}/activity`),
      professional: () => get<ProfessionalRecord[]>(`${personal}/professional`),
      addProfessional: (body: Record<string, unknown>) => post<ProfessionalRecord>(`${personal}/professional`, body),
      deleteProfessional: (id: string) => del(`${personal}/professional/${id}`),
      workHistory: () => get<WorkHistoryEntry[]>(`${personal}/professional/work-history/entries`),
      amendWorkHistory: (id: string, summary: string) => post<WorkHistoryEntry>(`${personal}/professional/work-history/entries/${id}/amend`, { summary }),
      badges: () => get<Badge[]>(`${personal}/me/badges`),
      healthRecords: (category?: string) => get<HealthRecord[]>(`${personal}/health/records${q({ category })}`),
      addHealthRecord: (body: Record<string, unknown>) => post<HealthRecord>(`${personal}/health/records`, body),
      deleteHealthRecord: (id: string) => del(`${personal}/health/records/${id}`),
      healthTrend: (metric: string) => get<{ metric: string; unit: string | null; points: Array<{ recorded_at: string; value: number }>; count: number; min: number | null; max: number | null; average: number | null; latest: number | null; note: string }>(`${personal}/health/trends${q({ metric })}`),
      healthAccessLog: () => get<Array<{ action: string; accessor_id: string | null; share_id: string | null; record_count: number | null; created_at: string }>>(`${personal}/health/access-log`),
      shares: () => get<HealthShare[]>(`${personal}/sharing`),
      createShare: (body: Record<string, unknown>) => post<HealthShare>(`${personal}/sharing`, body),
      revokeShare: (id: string) => del(`${personal}/sharing/${id}`),
      receivedShares: () => get<HealthShare[]>(`${personal}/sharing/received`),
      receivedRecords: (id: string) => get<HealthRecord[]>(`${personal}/sharing/received/${id}/records`),
      consents: () => get<Consent[]>(`${personal}/consents`),
      setConsent: (purpose: string, granted: boolean) => post<Consent>(`${personal}/consents/${purpose}`, { granted }),
      entitlements: () => get<{ subscription_features: string[]; entitlements: Entitlement[] }>(`${personal}/entitlements`),
      requestPurchase: (feature: string, organizationId?: string) => post<{ id: string; status: string }>(`${personal}/purchases`, { feature, organization_id: organizationId }),
    },
    researcher: {
      membership: () => get<ResearchMembershipState>(`${researcher}/membership`),
      applyMembership: (statement: string) => post(`${researcher}/membership/apply`, { statement }),
      workspace: () => get<{ has_research_access: boolean; owned_projects: number; accessible_projects: number; assigned_tasks: Record<string, number>; recent_evidence: Array<{ id: string; project_id: string; label: string; summary: string; review_status: string }> }>(`${researcher}/workspace/summary`),
      tasks: (projectId: string) => get<ResearchTask[]>(`${researcher}/projects/${projectId}/tasks`),
      createTask: (projectId: string, body: { title: string; description?: string; assignee_id?: string }) => post<ResearchTask>(`${researcher}/projects/${projectId}/tasks`, body),
      updateTask: (taskId: string, body: Record<string, unknown>) => patch<ResearchTask>(`${researcher}/tasks/${taskId}`, body),
      progress: (projectId: string, period: "day" | "week" | "month" = "week") => get<{ total_tasks: number; by_status: Record<string, number>; completed_in_period: number; completion_rate: number }>(`${researcher}/projects/${projectId}/progress${q({ period })}`),
      organizations: () => get<Organization[]>(`${researcher}/organizations`),
      discoverOrganizations: (query?: string) => get<Organization[]>(`${researcher}/organizations/discover${q({ q: query })}`),
      organization: (id: string) => get<Organization>(`${researcher}/organizations/${id}`),
      createOrganization: (body: { name: string; description?: string; website?: string }) => post<Organization>(`${researcher}/organizations`, body),
      members: (id: string) => get<OrganizationMember[]>(`${researcher}/organizations/${id}/members`),
      invite: (id: string, userId: string, role: string) => post(`${researcher}/organizations/${id}/invitations`, { user_id: userId, role }),
      orgBadges: (id: string) => get<Badge[]>(`${researcher}/organizations/${id}/badges`),
      orgAi: (id: string) => get<OrgAIInstance>(`${researcher}/organization-ai/${id}`),
      createOrgAi: (id: string, name: string, instructions = "") => post<OrgAIInstance>(`${researcher}/organization-ai/${id}`, { name, instructions }),
      orgDocuments: (id: string) => get<OrgDocument[]>(`${researcher}/organization-ai/${id}/documents`),
      addOrgDocument: (id: string, body: { title: string; content: string; source_label?: string }) => post<OrgDocument>(`${researcher}/organization-ai/${id}/documents`, body),
      removeOrgDocument: (id: string, documentId: string) => del(`${researcher}/organization-ai/${id}/documents/${documentId}`),
    },
  };
}

export type ApiClient = ReturnType<typeof createApiClient>;
