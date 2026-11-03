import type { PortalId } from "@healthspan/shared-types";

export interface AuthenticatedMember {
  id: string;
  displayName: string;
  availablePortals: readonly PortalId[];
}

export interface AuthSession {
  member: AuthenticatedMember;
  expiresAt: string;
}

export type AuthState =
  | { status: "loading" }
  | { status: "anonymous" }
  | { status: "authenticated"; session: AuthSession };

// Session transport and lifecycle remain unimplemented until backend identity is established.
