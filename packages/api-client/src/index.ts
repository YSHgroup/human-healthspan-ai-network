import type { ApiProblem } from "@healthspan/shared-types";

export class ApiRequestError extends Error {
  readonly status: number;
  readonly problem?: ApiProblem;

  constructor(status: number, message: string, problem?: ApiProblem) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
    this.problem = problem;
  }
}

export interface ApiClientOptions {
  baseUrl: string;
  fetcher?: typeof fetch;
}

/** Version prefix of the backend API (architecture section 5.2). */
export const API_VERSION_PATH = "/api/v1";

export function createApiClient({ baseUrl, fetcher = fetch }: ApiClientOptions) {
  const normalizedBaseUrl = baseUrl.replace(/\/+$/, "");

  return {
    async request<T>(path: string, init?: RequestInit): Promise<T | undefined> {
      const headers = new Headers(init?.headers);
      if (!headers.has("Accept")) {
        headers.set("Accept", "application/json");
      }

      const response = await fetcher(`${normalizedBaseUrl}/${path.replace(/^\/+/, "")}`, {
        // Sessions travel in secure cookies; tokens are never kept in browser storage.
        credentials: "include",
        ...init,
        headers,
      });

      if (!response.ok) {
        const contentType = response.headers.get("content-type") ?? "";
        let problem: ApiProblem | undefined;
        let message = response.statusText || `API request failed with status ${response.status}`;

        if (contentType.includes("application/json")) {
          const body: unknown = await response.json();
          if (typeof body === "object" && body !== null) {
            const payload = body as Record<string, unknown>;
            if (typeof payload.message === "string") {
              message = payload.message;
              if (typeof payload.code === "string") {
                problem = {
                  code: payload.code,
                  message: payload.message,
                  ...(typeof payload.requestId === "string" && { requestId: payload.requestId }),
                };
              }
            } else if (typeof payload.detail === "string") {
              message = payload.detail;
            }
          }
        } else {
          const responseText = await response.text();
          if (responseText) {
            message = responseText;
          }
        }

        throw new ApiRequestError(
          response.status,
          message,
          problem,
        );
      }

      if (response.status === 204) {
        return undefined;
      }

      return (await response.json()) as T;
    },
  };
}
