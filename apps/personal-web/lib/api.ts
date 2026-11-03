/** Personal portal API access. Feature calls go through the shared typed client. */
export interface HealthOut {
  status: string;
  service: string;
}

export async function getHealth(): Promise<HealthOut> {
  const response = await fetch("/api/backend/health", { cache: "no-store" });
  if (!response.ok) throw new Error("API unavailable");
  return (await response.json()) as HealthOut;
}
