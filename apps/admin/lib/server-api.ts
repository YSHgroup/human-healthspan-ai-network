import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const ACCESS_COOKIE = "healthspan_admin_access";
const REFRESH_COOKIE = "healthspan_admin_refresh";
type RefreshedSession = {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
  refreshExpiresIn: number;
};
const refreshInFlight = new Map<string, Promise<RefreshedSession | undefined>>();

export function backendBaseUrl(): string {
  const configured = process.env.API_INTERNAL_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
  return configured.replace(/\/+$/, "");
}

export async function getSessionTokens() {
  const cookieStore = await cookies();
  return {
    accessToken: cookieStore.get(ACCESS_COOKIE)?.value,
    refreshToken: cookieStore.get(REFRESH_COOKIE)?.value,
  };
}

export function setSessionCookies(
  response: NextResponse,
  tokens: { access_token: string; refresh_token: string; refresh_expires_in: number },
  accessExpiresIn: number,
) {
  const common = {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "strict" as const,
    path: "/api",
  };
  response.cookies.set(ACCESS_COOKIE, tokens.access_token, {
    ...common,
    maxAge: Math.max(1, accessExpiresIn),
  });
  response.cookies.set(REFRESH_COOKIE, tokens.refresh_token, {
    ...common,
    maxAge: Math.max(1, tokens.refresh_expires_in),
  });
}

export function clearSessionCookies(response: NextResponse) {
  response.cookies.set(ACCESS_COOKIE, "", {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "strict",
    path: "/api",
    maxAge: 0,
  });
  response.cookies.set(REFRESH_COOKIE, "", {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "strict",
    path: "/api",
    maxAge: 0,
  });
}

async function performRefresh(refreshToken: string): Promise<RefreshedSession | undefined> {
  if (!refreshToken) return undefined;

  try {
    const response = await fetch(`${backendBaseUrl()}/api/v1/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
      cache: "no-store",
    });
    if (!response.ok) return undefined;
    const result: unknown = await response.json();
    if (
      typeof result !== "object" ||
      result === null ||
      !("access_token" in result) ||
      typeof result.access_token !== "string" ||
      !("refresh_token" in result) ||
      typeof result.refresh_token !== "string" ||
      !("expires_in" in result) ||
      typeof result.expires_in !== "number" ||
      !("refresh_expires_in" in result) ||
      typeof result.refresh_expires_in !== "number"
    ) return undefined;
    return {
      accessToken: result.access_token,
      refreshToken: result.refresh_token,
      expiresIn: result.expires_in,
      refreshExpiresIn: result.refresh_expires_in,
    };
  } catch {
    return undefined;
  }
}

export async function refreshBackendSession() {
  const { refreshToken } = await getSessionTokens();
  if (!refreshToken) return undefined;

  // Deduplicate rotation only for callers holding the same session cookie; never share tokens across admins.
  let pending = refreshInFlight.get(refreshToken);
  if (!pending) {
    pending = performRefresh(refreshToken);
    refreshInFlight.set(refreshToken, pending);
    void pending.finally(() => {
      if (refreshInFlight.get(refreshToken) === pending) refreshInFlight.delete(refreshToken);
    });
  }
  return pending;
}

export function applyRefreshedSession(
  response: NextResponse,
  refreshed: RefreshedSession,
) {
  setSessionCookies(
    response,
    {
      access_token: refreshed.accessToken,
      refresh_token: refreshed.refreshToken,
      refresh_expires_in: refreshed.refreshExpiresIn,
    },
    refreshed.expiresIn,
  );
}
