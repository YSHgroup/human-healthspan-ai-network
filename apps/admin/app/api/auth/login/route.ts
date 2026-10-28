import { NextRequest, NextResponse } from "next/server";

import {
  backendBaseUrl,
  setSessionCookies,
} from "@/lib/server-api";

export const runtime = "nodejs";

const adminRoles = new Set([
  "admin",
  "moderator",
  "scientific_reviewer",
  "support_operator",
  "read_only_auditor",
]);

export async function POST(request: NextRequest) {
  const credentials = await request.json().catch(() => undefined);
  if (
    typeof credentials?.email !== "string" ||
    typeof credentials?.password !== "string"
  ) {
    return NextResponse.json({ detail: "Enter a valid email and password." }, { status: 422 });
  }

  let login: Response;
  try {
    login = await fetch(`${backendBaseUrl()}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(credentials),
      cache: "no-store",
    });
  } catch {
    return NextResponse.json({ detail: "The authentication service is unavailable." }, { status: 503 });
  }
  const loginResult = await login.json().catch(() => ({}));
  if (!login.ok) {
    return NextResponse.json(
      { detail: loginResult.detail ?? "Administrator sign-in failed." },
      { status: login.status },
    );
  }

  let profile: Response;
  try {
    profile = await fetch(`${backendBaseUrl()}/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${loginResult.access_token}` },
      cache: "no-store",
    });
  } catch {
    return NextResponse.json({ detail: "The authentication service is unavailable." }, { status: 503 });
  }
  const user = await profile.json().catch(() => ({}));
  if (!profile.ok || !adminRoles.has(user.role)) {
    try {
      await fetch(`${backendBaseUrl()}/api/v1/auth/logout`, {
        method: "POST",
        headers: { Authorization: `Bearer ${loginResult.access_token}` },
        cache: "no-store",
      });
    } catch {
      return NextResponse.json({ detail: "The authentication service is unavailable." }, { status: 503 });
    }
    return NextResponse.json(
      { detail: "This account does not have administrator access." },
      { status: 403 },
    );
  }

  const response = NextResponse.json({
    user: {
      email: user.email,
      role: user.role,
      display_name: user.profile?.display_name ?? user.email,
    },
  });
  setSessionCookies(response, loginResult, loginResult.expires_in);
  return response;
}
