/** Single source of truth for portal identity, local ports and cross-portal links (Architecture 2.1). */
export type PortalId = "social" | "personal" | "researcher" | "admin";

export interface PortalDefinition {
  id: PortalId;
  name: string;
  tagline: string;
  localPort: number;
}

export const PORTALS: Record<PortalId, PortalDefinition> = {
  social: { id: "social", name: "Social Network", tagline: "Community, discussion and events", localPort: 3000 },
  personal: { id: "personal", name: "Personal Space", tagline: "Identity, health data and privacy", localPort: 3001 },
  researcher: { id: "researcher", name: "Researcher Workspace", tagline: "Research, organizations and AI", localPort: 3002 },
  admin: { id: "admin", name: "Administration", tagline: "Platform operations", localPort: 3004 },
};

/**
 * Next.js only inlines NEXT_PUBLIC_* variables when they are referenced literally,
 * so each URL is read explicitly rather than through a dynamic lookup.
 */
const configured: Partial<Record<PortalId, string | undefined>> = {
  social: process.env.NEXT_PUBLIC_SOCIAL_APP_URL,
  personal: process.env.NEXT_PUBLIC_PERSONAL_APP_URL,
  researcher: process.env.NEXT_PUBLIC_RESEARCHER_APP_URL,
};

export function portalUrl(portal: PortalId, path = "/"): string {
  const base = (configured[portal] ?? `http://localhost:${PORTALS[portal].localPort}`).replace(/\/+$/, "");
  return `${base}${path.startsWith("/") ? path : `/${path}`}`;
}
