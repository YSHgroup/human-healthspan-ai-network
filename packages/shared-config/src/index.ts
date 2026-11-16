import type { PortalId } from "@healthspan/shared-types";

export interface PortalConfig {
  id: PortalId;
  name: string;
  localUrl: string;
}

export const portals: readonly PortalConfig[] = [
  { id: "social", name: "Social Portal", localUrl: "http://localhost:3000" },
  { id: "personal", name: "Personal Portal", localUrl: "http://localhost:3001" },
  { id: "researcher", name: "Researcher Portal", localUrl: "http://localhost:3002" },
  { id: "admin", name: "Admin Application", localUrl: "http://localhost:3003" },
];
