export interface PostCreate {
  body: string;
}

export interface PostOut {
  id: string;
  author_id: string;
  body: string;
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

export function createPost(payload: PostCreate): Promise<PostOut> {
  return request<PostOut>("/api/v1/posts", {
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
