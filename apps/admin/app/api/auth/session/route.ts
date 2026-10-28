import { NextResponse } from "next/server";

import {
  applyRefreshedSession,
  backendBaseUrl,
  getSessionTokens,
  refreshBackendSession,
} from "@/lib/server-api";

export const runtime = "nodejs";

const adminRoles = new Set([
  "admin",
  "moderator",
  "scientific_reviewer",
  "support_operator",
  "read_only_auditor",
]);

export async function GET() {
  const { accessToken } = await getSessionTokens();
  if (!accessToken) return NextResponse.json({ user: null }, { status: 200 });

  let token = accessToken;
  let refreshed: Awaited<ReturnType<typeof refreshBackendSession>> = undefined;
  let profile: Response;
  try {
    profile = await fetch(`${backendBaseUrl()}/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
  } catch {
    return NextResponse.json({ detail: "The authentication service is unavailable." }, { status: 503 });
  }
  if (profile.status === 401) {
    refreshed = await refreshBackendSession();
    if (refreshed) {
      token = refreshed.accessToken;
      try {
        profile = await fetch(`${backendBaseUrl()}/api/v1/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
          cache: "no-store",
        });
      } catch {
        return NextResponse.json({ detail: "The authentication service is unavailable." }, { status: 503 });
      }
    }
  }
  if (!profile.ok) return NextResponse.json({ user: null }, { status: 200 });

  const user = await profile.json();
  if (!adminRoles.has(user.role)) return NextResponse.json({ user: null }, { status: 200 });

  const response = NextResponse.json({
    user: {
      email: user.email,
      role: user.role,
      display_name: user.profile?.display_name ?? user.email,
    },
  });
  if (refreshed) applyRefreshedSession(response, refreshed);
  return response;
}
