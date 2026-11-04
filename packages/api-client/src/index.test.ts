import { describe, expect, it, vi } from "vitest";

import { ApiRequestError, createApiClient } from "./index";

const json = (body: unknown, init?: ResponseInit) =>
  new Response(JSON.stringify(body), {
    headers: { "content-type": "application/json" },
    ...init,
  });

describe("createApiClient", () => {
  it("sends credentials and normalizes the URL", async () => {
    const fetcher = vi.fn(async () => json({ status: "ok" }));
    const client = createApiClient({ baseUrl: "http://api.test/", fetcher });

    await expect(client.request("/healthz")).resolves.toEqual({ status: "ok" });
    expect(fetcher).toHaveBeenCalledWith(
      "http://api.test/healthz",
      expect.objectContaining({ credentials: "include" }),
    );
  });

  it("returns undefined for 204 responses", async () => {
    const client = createApiClient({
      baseUrl: "http://api.test",
      fetcher: async () => new Response(null, { status: 204 }),
    });
    await expect(client.request("x")).resolves.toBeUndefined();
  });

  it("raises a typed error with the problem payload", async () => {
    const client = createApiClient({
      baseUrl: "http://api.test",
      fetcher: async () =>
        json({ code: "forbidden", message: "No access", requestId: "r1" }, { status: 403 }),
    });

    const error = await client.request("x").catch((e: unknown) => e);
    expect(error).toBeInstanceOf(ApiRequestError);
    expect((error as ApiRequestError).status).toBe(403);
    expect((error as ApiRequestError).problem).toEqual({
      code: "forbidden",
      message: "No access",
      requestId: "r1",
    });
  });
});
