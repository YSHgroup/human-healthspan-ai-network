import "server-only";

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

export const ACCESS_COOKIE = "healthspan_member_access";
export const REFRESH_COOKIE = "healthspan_member_refresh";

export interface SessionTokens {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  refresh_expires_in: number;
  token_type: "bearer";
}

const backendBaseUrl = (process.env.API_INTERNAL_URL ?? "http://localhost:8000").replace(/\/+$/, "");

export async function backendFetch(path: string, init: RequestInit = {}): Promise<Response> {
  return fetch(`${backendBaseUrl}${path}`, {
    ...init,
    cache: "no-store",
    signal: AbortSignal.timeout(10_000),
  });
}

export async function getSessionTokens(): Promise<{
  accessToken?: string;
  refreshToken?: string;
}> {
  const cookieStore = await cookies();
  return {
    accessToken: cookieStore.get(ACCESS_COOKIE)?.value,
    refreshToken: cookieStore.get(REFRESH_COOKIE)?.value,
  };
}

export async function refreshSession(refreshToken: string): Promise<Response> {
  return backendFetch("/api/v1/auth/refresh", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
}

export async function applySessionCookies(
  response: NextResponse,
  tokens: SessionTokens,
): Promise<void> {
  const secure = process.env.NODE_ENV === "production";
  response.cookies.set(ACCESS_COOKIE, tokens.access_token, {
    httpOnly: true,
    secure,
    sameSite: "strict",
    path: "/api",
    maxAge: tokens.expires_in,
  });
  response.cookies.set(REFRESH_COOKIE, tokens.refresh_token, {
    httpOnly: true,
    secure,
    sameSite: "strict",
    path: "/api",
    maxAge: tokens.refresh_expires_in,
  });
}

export function clearSessionCookies(response: NextResponse): void {
  const secure = process.env.NODE_ENV === "production";
  for (const name of [ACCESS_COOKIE, REFRESH_COOKIE]) {
    response.cookies.set(name, "", {
      httpOnly: true,
      secure,
      sameSite: "strict",
      path: "/api",
      maxAge: 0,
    });
  }
}

export async function jsonFromResponse(response: Response): Promise<NextResponse> {
  const body = await response.text();
  return new NextResponse(body || null, {
    status: response.status,
    headers: {
      "Content-Type": response.headers.get("Content-Type") ?? "application/json",
      "Cache-Control": "no-store",
    },
  });
}

export function backendUnavailable(): NextResponse {
  return NextResponse.json(
    { detail: "The identity service is temporarily unavailable. Please try again." },
    { status: 502, headers: { "Cache-Control": "no-store" } },
  );
}

export function requestIsSameOrigin(request: { headers: Headers; nextUrl: URL }): boolean {
  const origin = request.headers.get("origin");
  const fetchSite = request.headers.get("sec-fetch-site");
  return (!origin || origin === request.nextUrl.origin) && fetchSite !== "cross-site";
}

export function tokensFromResponse(value: unknown): SessionTokens | null {
  if (
    typeof value !== "object" ||
    value === null ||
    !("access_token" in value) ||
    !("refresh_token" in value) ||
    !("expires_in" in value) ||
    !("refresh_expires_in" in value) ||
    typeof value.access_token !== "string" ||
    typeof value.refresh_token !== "string" ||
    typeof value.expires_in !== "number" ||
    typeof value.refresh_expires_in !== "number"
  ) {
    return null;
  }
  return {
    access_token: value.access_token,
    refresh_token: value.refresh_token,
    expires_in: value.expires_in,
    refresh_expires_in: value.refresh_expires_in,
    token_type: "bearer",
  };
}
