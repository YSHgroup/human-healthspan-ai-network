import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const ACCESS_COOKIE = "healthspan_admin_access";
const REFRESH_COOKIE = "healthspan_admin_refresh";
let refreshInFlight:
  | Promise<{ accessToken: string; refreshToken: string; expiresIn: number } | undefined>
  | undefined;

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
  tokens: { access_token: string; refresh_token: string },
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
    maxAge: 60 * 60 * 24 * 30,
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

async function performRefresh(): Promise<
  { accessToken: string; refreshToken: string; expiresIn: number } | undefined
> {
  const { refreshToken } = await getSessionTokens();
  if (!refreshToken) return undefined;

  try {
    const response = await fetch(`${backendBaseUrl()}/api/v1/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
      cache: "no-store",
    });
    if (!response.ok) return undefined;
    const result = (await response.json()) as {
      access_token: string;
      refresh_token: string;
      expires_in: number;
    };
    return {
      accessToken: result.access_token,
      refreshToken: result.refresh_token,
      expiresIn: result.expires_in,
    };
  } catch {
    return undefined;
  }
}

export async function refreshBackendSession() {
  if (!refreshInFlight) {
    refreshInFlight = performRefresh().finally(() => {
      refreshInFlight = undefined;
    });
  }
  return refreshInFlight;
}

export function applyRefreshedSession(
  response: NextResponse,
  refreshed: { accessToken: string; refreshToken: string; expiresIn: number },
) {
  setSessionCookies(
    response,
    {
      access_token: refreshed.accessToken,
      refresh_token: refreshed.refreshToken,
    },
    refreshed.expiresIn,
  );
}
