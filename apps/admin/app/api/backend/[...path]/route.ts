import { NextRequest, NextResponse } from "next/server";

import {
  applyRefreshedSession,
  backendBaseUrl,
  getSessionTokens,
  refreshBackendSession,
} from "@/lib/server-api";

export const runtime = "nodejs";

type RouteContext = { params: Promise<{ path: string[] }> };

function isAllowedPath(path: string[]): boolean {
  if (!path.length || !["admin", "moderation"].includes(path[0])) return false;
  return path.every((part) => /^[A-Za-z0-9_-]+$/.test(part));
}

async function forward(
  request: NextRequest,
  path: string[],
  accessToken: string,
): Promise<Response> {
  const target = new URL(`/api/v1/${path.join("/")}`, backendBaseUrl());
  target.search = request.nextUrl.search;
  const body = ["GET", "HEAD"].includes(request.method) ? undefined : await request.text();
  return fetch(target, {
    method: request.method,
    headers: {
      Authorization: `Bearer ${accessToken}`,
      ...(body ? { "Content-Type": request.headers.get("content-type") ?? "application/json" } : {}),
    },
    body,
    cache: "no-store",
  });
}

async function handle(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  if (!isAllowedPath(path)) {
    return NextResponse.json({ detail: "This admin endpoint is not available through the console." }, { status: 404 });
  }
  const origin = request.headers.get("origin");
  if (origin && origin !== request.nextUrl.origin) {
    return NextResponse.json({ detail: "Cross-origin admin requests are not allowed." }, { status: 403 });
  }

  const { accessToken } = await getSessionTokens();
  if (!accessToken) return NextResponse.json({ detail: "Administrator sign-in is required." }, { status: 401 });

  let upstream: Response;
  try {
    upstream = await forward(request, path, accessToken);
  } catch {
    return NextResponse.json({ detail: "The admin API is unavailable." }, { status: 503 });
  }
  let refreshed: Awaited<ReturnType<typeof refreshBackendSession>> = undefined;
  if (upstream.status === 401) {
    refreshed = await refreshBackendSession();
    if (refreshed) {
      try {
        upstream = await forward(request, path, refreshed.accessToken);
      } catch {
        return NextResponse.json({ detail: "The admin API is unavailable." }, { status: 503 });
      }
    }
  }

  const contentType = upstream.headers.get("content-type") ?? "application/json";
  const body = await upstream.arrayBuffer();
  const response = new NextResponse(body, {
    status: upstream.status,
    headers: { "Content-Type": contentType, "Cache-Control": "no-store" },
  });
  if (refreshed && upstream.status !== 401) applyRefreshedSession(response, refreshed);
  return response;
}

export const GET = handle;
export const POST = handle;
export const PATCH = handle;
