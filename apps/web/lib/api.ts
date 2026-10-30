export type PostClassification =
  | "personal_experience"
  | "opinion"
  | "scientific_evidence"
  | "expert_interpretation"
  | "research_hypothesis"
  | "ai_generated_hypothesis"
  | "speculation";

export interface PostCreate {
  body: string;
  content_type?: "post" | "question";
  classification?: PostClassification;
  community_id?: string;
}

export interface PostOut {
  id: string;
  author_id: string;
  community_id: string | null;
  body: string;
  content_type: string;
  classification: string;
  created_at: string;
}

export interface FeedPost extends PostOut {
  author_display_name: string;
  author_role: string;
  comment_count: number;
  reaction_count: number;
  is_reacted: boolean;
  is_bookmarked: boolean;
}

export interface Community {
  id: string;
  slug: string;
  name: string;
  description: string;
  topic: string;
  member_count: number;
  is_member: boolean;
}

export interface ResearchProject {
  id: string;
  owner_id: string;
  title: string;
  description: string;
  visibility: "private" | "team" | "public";
  status: string;
  created_at: string;
}

export interface Comment {
  id: string;
  post_id: string;
  author_id: string;
  author_display_name: string;
  body: string;
  created_at: string;
}

export interface SearchResults {
  posts: { id: string; body: string; classification: string }[];
  projects: { id: string; title: string; description: string }[];
  communities: { id: string; name: string; topic: string }[];
  people: { id: string; display_name: string; role: string }[];
}

export interface PublicMember {
  id: string;
  role: string;
  is_following: boolean;
  profile: {
    display_name: string;
    bio: string | null;
    location: string | null;
    timezone: string | null;
    interests: string[];
    topics: string[];
    expertise: string[];
    researcher_identifier: string | null;
    organization_affiliation: string | null;
    is_public: boolean;
  };
}

export interface ResearchQuestionCreate {
  project_id: string;
  title: string;
  description: string;
}

export interface ResearchQuestionOut extends ResearchQuestionCreate {
  id: string;
  evidence_status: string;
}

export interface HealthOut {
  status: string;
  service: string;
}

export interface DashboardSummary {
  active_members: number;
  active_communities: number;
  your_communities: number;
  accessible_projects: number;
  posts_last_7_days: number;
  activity: { day: string; post_count: number }[];
}

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api/backend${path}`, {
    ...init,
    headers: {
      ...(init?.body ? { "Content-Type": "application/json" } : {}),
      ...init?.headers,
    },
    credentials: "same-origin",
  });
  const responseText = await response.text();
  if (response.status === 204) return undefined as T;
  let result: unknown;

  try {
    result = responseText ? JSON.parse(responseText) : undefined;
  } catch {
    result = responseText;
  }

  if (!response.ok) {
    const detail =
      typeof result === "object" && result !== null && "detail" in result
        ? String(result.detail)
        : typeof result === "string" && result
          ? result
          : response.statusText;
    throw new ApiError(detail || `Request failed (${response.status})`, response.status);
  }

  return result as T;
}

export function getHealth(): Promise<HealthOut> {
  return request<HealthOut>("/health", { cache: "no-store" });
}

export function getFeed(limit = 25, offset = 0): Promise<FeedPost[]> {
  const parameters = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  return request<FeedPost[]>(`/api/v1/feed?${parameters.toString()}`, { cache: "no-store" });
}

export function getDashboardSummary(): Promise<DashboardSummary> {
  return request<DashboardSummary>("/api/v1/dashboard/summary", { cache: "no-store" });
}

export function getCommunities(): Promise<Community[]> {
  return request<Community[]>("/api/v1/communities", { cache: "no-store" });
}

export function getCommunity(communityId: string): Promise<Community> {
  return request<Community>(`/api/v1/communities/${communityId}`, { cache: "no-store" });
}

export function getCommunityFeed(communityId: string, limit = 25, offset = 0): Promise<FeedPost[]> {
  const parameters = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  return request<FeedPost[]>(`/api/v1/communities/${communityId}/feed?${parameters.toString()}`, { cache: "no-store" });
}

export function joinCommunity(communityId: string): Promise<void> {
  return request<void>(`/api/v1/communities/${communityId}/join`, { method: "POST" });
}

export function leaveCommunity(communityId: string): Promise<void> {
  return request<void>(`/api/v1/communities/${communityId}/join`, { method: "DELETE" });
}

export function createPost(payload: PostCreate): Promise<PostOut> {
  return request<PostOut>("/api/v1/posts", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getComments(postId: string): Promise<Comment[]> {
  return request<Comment[]>(`/api/v1/posts/${postId}/comments`, { cache: "no-store" });
}

export function createComment(postId: string, body: string): Promise<Comment> {
  return request<Comment>(`/api/v1/posts/${postId}/comments`, {
    method: "POST",
    body: JSON.stringify({ body }),
  });
}

export function reactToPost(postId: string): Promise<{ status: string; kind: string }> {
  return request(`/api/v1/posts/${postId}/reactions`, {
    method: "POST",
    body: JSON.stringify({ kind: "insightful" }),
  });
}

export function removePostReaction(postId: string): Promise<void> {
  return request<void>(`/api/v1/posts/${postId}/reactions`, { method: "DELETE" });
}

export function bookmarkPost(postId: string): Promise<void> {
  return request<void>(`/api/v1/posts/${postId}/bookmark`, { method: "POST" });
}

export function unbookmarkPost(postId: string): Promise<void> {
  return request<void>(`/api/v1/posts/${postId}/bookmark`, { method: "DELETE" });
}

export function reportPost(postId: string, reason: string): Promise<unknown> {
  return request("/api/v1/reports", {
    method: "POST",
    body: JSON.stringify({ target_type: "post", target_id: postId, reason }),
  });
}

export function searchNetwork(query: string): Promise<SearchResults> {
  return request<SearchResults>(`/api/v1/search?q=${encodeURIComponent(query)}`, { cache: "no-store" });
}

export function getPublicMember(userId: string): Promise<PublicMember> {
  return request<PublicMember>(`/api/v1/users/${userId}`, { cache: "no-store" });
}

export function followMember(userId: string): Promise<void> {
  return request<void>(`/api/v1/users/${userId}/follow`, { method: "POST" });
}

export function unfollowMember(userId: string): Promise<void> {
  return request<void>(`/api/v1/users/${userId}/follow`, { method: "DELETE" });
}

export function searchLiterature(query: string): Promise<
  { id: string; title: string; authors: string | null; publication_year: number | null; source_url: string | null; doi: string | null; source_type: string }[]
> {
  return request(`/api/v1/science/search?q=${encodeURIComponent(query)}`, { cache: "no-store" });
}

export function getResearchProjects(): Promise<ResearchProject[]> {
  return request<ResearchProject[]>("/api/v1/research/projects", { cache: "no-store" });
}

export function createResearchProject(payload: {
  title: string;
  description: string;
  visibility: ResearchProject["visibility"];
}): Promise<ResearchProject> {
  return request<ResearchProject>("/api/v1/research/projects", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function createResearchQuestion(
  payload: ResearchQuestionCreate,
): Promise<ResearchQuestionOut> {
  return request<ResearchQuestionOut>("/api/v1/research/questions", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
