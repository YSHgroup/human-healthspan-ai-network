import { NextResponse } from "next/server";

import {
  applyRefreshedSession,
  backendBaseUrl,
  clearSessionCookies,
  getSessionTokens,
  refreshBackendSession,
} from "@/lib/server-api";

export const runtime = "nodejs";

export async function POST() {
  const tokens = await getSessionTokens();
  let accessToken = tokens.accessToken;
  let refreshed: Awaited<ReturnType<typeof refreshBackendSession>> = undefined;

  if (accessToken) {
    let logout = await fetch(`${backendBaseUrl()}/api/v1/auth/logout`, {
      method: "POST",
      headers: { Authorization: `Bearer ${accessToken}` },
      cache: "no-store",
    });
    if (logout.status === 401) {
      refreshed = await refreshBackendSession();
      if (refreshed) {
        accessToken = refreshed.accessToken;
        logout = await fetch(`${backendBaseUrl()}/api/v1/auth/logout`, {
          method: "POST",
          headers: { Authorization: `Bearer ${accessToken}` },
          cache: "no-store",
        });
      }
    }
    if (!logout.ok && logout.status !== 401) {
      return NextResponse.json({ detail: "Could not revoke the admin session." }, { status: 502 });
    }
  }

  const response = NextResponse.json({ status: "logged_out" });
  if (refreshed) applyRefreshedSession(response, refreshed);
  clearSessionCookies(response);
  return response;
}
