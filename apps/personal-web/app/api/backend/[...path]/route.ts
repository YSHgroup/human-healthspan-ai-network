import { NextRequest, NextResponse } from "next/server";
import {
  applySessionCookies,
  backendFetch,
  backendUnavailable,
  clearSessionCookies,
  getSessionTokens,
  jsonFromResponse,
  refreshSession,
  requestIsSameOrigin,
  tokensFromResponse,
  type SessionTokens,
} from "@/lib/server-auth";

type RouteContext = { params: Promise<{ path: string[] }> };
const allowedMethods = new Set(["GET", "POST", "PATCH", "DELETE"]);

async function proxy(
  request: NextRequest,
  context: RouteContext,
  method: string,
) {
  if (!allowedMethods.has(method)) {
    return NextResponse.json({ detail: "Method not allowed." }, { status: 405 });
  }
  if (method !== "GET" && !requestIsSameOrigin(request)) {
    return NextResponse.json({ detail: "Cross-origin requests are not allowed." }, { status: 403 });
  }

  const { path } = await context.params;
  if (
    path.length === 0 ||
    path.some((segment) => !/^[A-Za-z0-9_-]+$/.test(segment)) ||
    (path[0] !== "health" && !(path[0] === "api" && path[1] === "v1")) ||
    (path[0] === "health" && path.length !== 1) ||
    (path[0] === "api" && path[1] === "v1" && path[2] === "auth")
  ) {
    return NextResponse.json({ detail: "Not found." }, { status: 404 });
  }
  const backendPath = `/${path.join("/")}${request.nextUrl.search}`;

  try {
    const { accessToken, refreshToken } = await getSessionTokens();
    const headers = new Headers();
    const contentType = request.headers.get("content-type");
    if (contentType) headers.set("Content-Type", contentType);
    if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);
    const body = method === "GET" ? undefined : await request.text();
    let upstream = await backendFetch(backendPath, { method, headers, body });
    let rotatedTokens: SessionTokens | null = null;
    let refreshRejected = false;

    if (upstream.status === 401 && refreshToken) {
      const refreshed = await refreshSession(refreshToken);
      if (refreshed.ok) {
        rotatedTokens = tokensFromResponse(await refreshed.json());
        if (!rotatedTokens) {
          return NextResponse.json({ detail: "The identity service returned an invalid session." }, { status: 502 });
        }
        headers.set("Authorization", `Bearer ${rotatedTokens.access_token}`);
        upstream = await backendFetch(backendPath, { method, headers, body });
      } else if (refreshed.status !== 401) {
        return await jsonFromResponse(refreshed);
      } else {
        refreshRejected = true;
      }
    }

    const response = await jsonFromResponse(upstream);
    if (upstream.status === 401 && refreshRejected) clearSessionCookies(response);
    if (rotatedTokens) await applySessionCookies(response, rotatedTokens);
    return response;
  } catch {
    return backendUnavailable();
  }
}

export const GET = (request: NextRequest, context: RouteContext) =>
  proxy(request, context, "GET");
export const POST = (request: NextRequest, context: RouteContext) =>
  proxy(request, context, "POST");
export const PATCH = (request: NextRequest, context: RouteContext) =>
  proxy(request, context, "PATCH");
export const DELETE = (request: NextRequest, context: RouteContext) =>
  proxy(request, context, "DELETE");
