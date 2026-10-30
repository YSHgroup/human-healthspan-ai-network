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

type RouteContext = { params: Promise<{ action: string[] }> };

function unauthorized(): NextResponse {
  return NextResponse.json({ detail: "Your session has expired. Please sign in again." }, { status: 401 });
}

export async function GET(request: NextRequest, context: RouteContext) {
  const { action } = await context.params;
  if (action.length !== 1 || action[0] !== "session") {
    return NextResponse.json({ detail: "Not found." }, { status: 404 });
  }

  try {
    const { accessToken, refreshToken } = await getSessionTokens();
    if (!accessToken && !refreshToken) {
      return NextResponse.json({ user: null }, { headers: { "Cache-Control": "no-store" } });
    }

    let activeAccessToken = accessToken;
    let upstream = activeAccessToken
      ? await backendFetch("/api/v1/auth/me", {
          headers: { Authorization: `Bearer ${activeAccessToken}` },
        })
      : null;
    let rotatedTokens: SessionTokens | null = null;
    let refreshRejected = false;

    if ((!upstream || upstream.status === 401) && refreshToken) {
      const refreshed = await refreshSession(refreshToken);
      if (refreshed.ok) {
        rotatedTokens = tokensFromResponse(await refreshed.json());
        if (!rotatedTokens) {
          return NextResponse.json({ detail: "The identity service returned an invalid session." }, { status: 502 });
        }
        activeAccessToken = rotatedTokens.access_token;
        upstream = await backendFetch("/api/v1/auth/me", {
          headers: { Authorization: `Bearer ${activeAccessToken}` },
        });
      } else if (refreshed.status !== 401) {
        return await jsonFromResponse(refreshed);
      } else {
        refreshRejected = true;
      }
    }

    if (!upstream || upstream.status === 401) {
      const response = unauthorized();
      if (refreshRejected || !refreshToken) clearSessionCookies(response);
      return response;
    }
    const response = await jsonFromResponse(upstream);
    if (rotatedTokens) await applySessionCookies(response, rotatedTokens);
    return response;
  } catch {
    return backendUnavailable();
  }
}

export async function POST(request: NextRequest, context: RouteContext) {
  if (!requestIsSameOrigin(request)) {
    return NextResponse.json({ detail: "Cross-origin requests are not allowed." }, { status: 403 });
  }
  const { action } = await context.params;
  if (action.length !== 1) return NextResponse.json({ detail: "Not found." }, { status: 404 });

  const backendActions: Record<string, string> = {
    register: "/api/v1/auth/register",
    "verify-email": "/api/v1/auth/verify-email",
    "resend-verification": "/api/v1/auth/resend-verification",
    "password-reset": "/api/v1/auth/password-reset",
    "password-reset-confirm": "/api/v1/auth/password-reset/confirm",
  };
  const actionName = action[0];
  if (actionName === "logout") {
    try {
      const { accessToken, refreshToken } = await getSessionTokens();
      let token = accessToken;
      if (token) {
        let upstream = await backendFetch("/api/v1/auth/logout", {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
        });
        let rotatedTokens: SessionTokens | null = null;
        if (upstream.status === 401 && refreshToken) {
          const refreshed = await refreshSession(refreshToken);
          if (refreshed.ok) {
            rotatedTokens = tokensFromResponse(await refreshed.json());
            if (!rotatedTokens) {
              return NextResponse.json({ detail: "The identity service returned an invalid session." }, { status: 502 });
            }
            token = rotatedTokens.access_token;
            upstream = await backendFetch("/api/v1/auth/logout", {
              method: "POST",
              headers: { Authorization: `Bearer ${token}` },
            });
          } else if (refreshed.status !== 401) {
            return await jsonFromResponse(refreshed);
          }
        }
        if (!upstream.ok && upstream.status !== 401) return await jsonFromResponse(upstream);
      } else if (refreshToken) {
        const refreshed = await refreshSession(refreshToken);
        if (!refreshed.ok && refreshed.status !== 401) return await jsonFromResponse(refreshed);
        if (refreshed.ok) {
          const tokens = tokensFromResponse(await refreshed.json());
          if (!tokens) {
            return NextResponse.json({ detail: "The identity service returned an invalid session." }, { status: 502 });
          }
          const upstream = await backendFetch("/api/v1/auth/logout", {
            method: "POST",
            headers: { Authorization: `Bearer ${tokens.access_token}` },
          });
          if (!upstream.ok && upstream.status !== 401) return await jsonFromResponse(upstream);
        }
      }
      const response = NextResponse.json({ status: "logged_out" }, { headers: { "Cache-Control": "no-store" } });
      clearSessionCookies(response);
      return response;
    } catch {
      return backendUnavailable();
    }
  }

  if (actionName === "login") {
    try {
      const loginResponse = await backendFetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: await request.text(),
      });
      if (!loginResponse.ok) return await jsonFromResponse(loginResponse);
      const tokens = tokensFromResponse(await loginResponse.json());
      if (!tokens) {
        return NextResponse.json({ detail: "The identity service returned an invalid session." }, { status: 502 });
      }
      const userResponse = await backendFetch("/api/v1/auth/me", {
        headers: { Authorization: `Bearer ${tokens.access_token}` },
      });
      if (!userResponse.ok) {
        await backendFetch("/api/v1/auth/logout", {
          method: "POST",
          headers: { Authorization: `Bearer ${tokens.access_token}` },
        });
        return await jsonFromResponse(userResponse);
      }
      const response = await jsonFromResponse(userResponse);
      await applySessionCookies(response, tokens);
      return response;
    } catch {
      return backendUnavailable();
    }
  }

  if (actionName === "password-change") {
    try {
      const { accessToken, refreshToken } = await getSessionTokens();
      if (!accessToken && !refreshToken) return unauthorized();
      let activeAccessToken = accessToken;
      let rotatedTokens: SessionTokens | null = null;
      if (!activeAccessToken && refreshToken) {
        const refreshed = await refreshSession(refreshToken);
        if (!refreshed.ok) return await jsonFromResponse(refreshed);
        rotatedTokens = tokensFromResponse(await refreshed.json());
        if (!rotatedTokens) {
          return NextResponse.json({ detail: "The identity service returned an invalid session." }, { status: 502 });
        }
        activeAccessToken = rotatedTokens.access_token;
      }

      const body = await request.text();
      let upstream = await backendFetch("/api/v1/auth/password-change", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${activeAccessToken}`,
        },
        body,
      });
      if (upstream.status === 401 && refreshToken && !rotatedTokens) {
        const refreshed = await refreshSession(refreshToken);
        if (refreshed.ok) {
          rotatedTokens = tokensFromResponse(await refreshed.json());
          if (!rotatedTokens) {
            return NextResponse.json({ detail: "The identity service returned an invalid session." }, { status: 502 });
          }
          activeAccessToken = rotatedTokens.access_token;
          upstream = await backendFetch("/api/v1/auth/password-change", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${activeAccessToken}`,
            },
            body,
          });
        } else if (refreshed.status !== 401) {
          return await jsonFromResponse(refreshed);
        }
      }
      const response = await jsonFromResponse(upstream);
      if (upstream.ok) clearSessionCookies(response);
      else if (rotatedTokens) await applySessionCookies(response, rotatedTokens);
      return response;
    } catch {
      return backendUnavailable();
    }
  }

  const backendPath = backendActions[actionName];
  if (!backendPath) return NextResponse.json({ detail: "Not found." }, { status: 404 });
  try {
    const upstream = await backendFetch(backendPath, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: await request.text(),
    });
    return await jsonFromResponse(upstream);
  } catch {
    return backendUnavailable();
  }
}
