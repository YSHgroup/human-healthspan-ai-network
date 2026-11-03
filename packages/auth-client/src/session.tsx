"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

export interface MemberProfile {
  user_id: string;
  display_name: string;
  bio: string | null;
  location: string | null;
  timezone: string | null;
  interests: string[];
  topics: string[];
  expertise: string[];
  researcher_identifier: string | null;
  organization_affiliation: string | null;
  is_public: boolean;
}

export interface MemberUser {
  id: string;
  email: string;
  role: string;
  is_verified: boolean;
  profile: MemberProfile | null;
}

type SessionStatus = "loading" | "authenticated" | "unauthenticated" | "unavailable";
interface SessionContextValue {
  user: MemberUser | null;
  status: SessionStatus;
  error: string | null;
  refresh: () => Promise<MemberUser | null>;
  setUser: (user: MemberUser) => void;
}

const SessionContext = createContext<SessionContextValue | null>(null);

function responseError(payload: unknown, fallback: string): string {
  if (typeof payload === "object" && payload !== null && "detail" in payload) {
    return String(payload.detail);
  }
  return fallback;
}

export function isMemberUser(value: unknown): value is MemberUser {
  if (typeof value !== "object" || value === null) return false;
  if (
    !("id" in value) ||
    typeof value.id !== "string" ||
    !("email" in value) ||
    typeof value.email !== "string" ||
    !("role" in value) ||
    typeof value.role !== "string" ||
    !("is_verified" in value) ||
    typeof value.is_verified !== "boolean" ||
    !("profile" in value)
  ) {
    return false;
  }
  if (value.profile === null) return true;
  const profile = value.profile;
  return typeof profile === "object" &&
    profile !== null &&
    "user_id" in profile &&
    typeof profile.user_id === "string" &&
    "display_name" in profile &&
    typeof profile.display_name === "string" &&
    "bio" in profile &&
    (typeof profile.bio === "string" || profile.bio === null) &&
    "location" in profile &&
    (typeof profile.location === "string" || profile.location === null) &&
    "timezone" in profile &&
    (typeof profile.timezone === "string" || profile.timezone === null) &&
    "interests" in profile &&
    Array.isArray(profile.interests) &&
    profile.interests.every((item) => typeof item === "string") &&
    "topics" in profile &&
    Array.isArray(profile.topics) &&
    profile.topics.every((item) => typeof item === "string") &&
    "expertise" in profile &&
    Array.isArray(profile.expertise) &&
    profile.expertise.every((item) => typeof item === "string") &&
    "researcher_identifier" in profile &&
    (typeof profile.researcher_identifier === "string" || profile.researcher_identifier === null) &&
    "organization_affiliation" in profile &&
    (typeof profile.organization_affiliation === "string" || profile.organization_affiliation === null) &&
    "is_public" in profile &&
    typeof profile.is_public === "boolean";
}

export async function fetchCurrentSession(): Promise<MemberUser | null> {
  const response = await fetch("/api/auth/session", { cache: "no-store" });
  if (response.status === 401) return null;
  const payload: unknown = await response.json();
  if (!response.ok) throw new Error(responseError(payload, "Unable to load your account."));
  if (typeof payload === "object" && payload !== null && "user" in payload && payload.user === null) {
    return null;
  }
  if (!isMemberUser(payload)) throw new Error("The identity service returned an invalid account.");
  return payload;
}

export function SessionProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<MemberUser | null>(null);
  const [status, setStatus] = useState<SessionStatus>("loading");
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const currentUser = await fetchCurrentSession();
      setUser(currentUser);
      setStatus(currentUser ? "authenticated" : "unauthenticated");
      setError(null);
      return currentUser;
    } catch (sessionError) {
      setUser(null);
      setStatus("unavailable");
      setError(sessionError instanceof Error ? sessionError.message : "Unable to load your account.");
      return null;
    }
  }, []);
  const updateUser = useCallback((updatedUser: MemberUser) => {
    setUser(updatedUser);
    setStatus("authenticated");
    setError(null);
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return (
    <SessionContext.Provider value={{ user, status, error, refresh, setUser: updateUser }}>
      {children}
    </SessionContext.Provider>
  );
}

export function useSession(): SessionContextValue {
  const context = useContext(SessionContext);
  if (!context) throw new Error("useSession must be used within a SessionProvider.");
  return context;
}
