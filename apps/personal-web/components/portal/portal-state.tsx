"use client";

import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";

import { previewVipCard, type VipCard } from "../../lib/preview-data";

/**
 * Session-local portal state.
 *
 * Profile details, consent choices and saved items stay in memory until secure backend
 * persistence is enabled (Milestone 2 behavior, unchanged). The state lives in the layout so
 * it survives moving between pages of the portal.
 */

export const initialProfile = {
  name: "Harper Stone",
  title: "Health & longevity enthusiast",
  location: "Seattle, WA",
  bio: "I am exploring sleep, mobility, and evidence-based healthy aging with a focus on sustainable routines.",
};

export type Profile = typeof initialProfile;

export const initialPrivacy = {
  profileVisible: true,
  communityActivityVisible: true,
  researchFollowupsAllowed: false,
  shareHealthPreferences: false,
  consentForDataReview: false,
};

export type Privacy = typeof initialPrivacy;
export type PrivacyKey = keyof Privacy;

export const privacyLabels: Record<PrivacyKey, string> = {
  profileVisible: "Make profile visible to trusted community members",
  communityActivityVisible: "Share community activity in my profile",
  researchFollowupsAllowed: "Allow follow-up invitations from verified researchers",
  shareHealthPreferences: "Share health goals and interests with the network",
  consentForDataReview: "Consent to a limited review of my data preferences",
};

export type SavedItem = { title: string; meta: string; tag: string };

export const initialSaved: SavedItem[] = [
  { title: "Sleep quality checklist", meta: "10 min read · Wellbeing", tag: "Personal" },
  { title: "Evidence summary: recovery trends", meta: "Research note · 2 attachments", tag: "Research" },
  { title: "Morning routine template", meta: "Saved from community · 1 review", tag: "Routine" },
];

export type PresenceStatus = "Available" | "Away" | "Do Not Disturb";
export const presenceStatuses: PresenceStatus[] = ["Available", "Away", "Do Not Disturb"];

export const profileInitials = (name: string) =>
  name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("") || "HS";

type CardState = "none" | "unused" | "active";

type PortalState = {
  profile: Profile;
  setProfileField: (field: keyof Profile, value: string) => void;
  savedMessage: string;
  saveProfile: () => void;
  privacy: Privacy;
  togglePrivacy: (key: PrivacyKey) => void;
  consentCount: number;
  savedItems: SavedItem[];
  status: PresenceStatus;
  setStatus: (status: PresenceStatus) => void;
  vipCard: VipCard;
  cardState: CardState;
  startCard: () => void;
  bannerDismissed: boolean;
  dismissBanner: () => void;
};

const PortalStateContext = createContext<PortalState | null>(null);

export function PortalStateProvider({ children }: { children: ReactNode }) {
  const [profile, setProfile] = useState<Profile>(initialProfile);
  const [savedItems] = useState<SavedItem[]>(initialSaved);
  const [privacy, setPrivacy] = useState<Privacy>(initialPrivacy);
  const [savedMessage, setSavedMessage] = useState(
    "Profile changes are only stored in this browser session.",
  );
  const [status, setStatus] = useState<PresenceStatus>("Available");
  const [cardState, setCardState] = useState<CardState>("unused");
  const [bannerDismissed, setBannerDismissed] = useState(false);

  const consentCount = useMemo(() => Object.values(privacy).filter(Boolean).length, [privacy]);

  const setProfileField = useCallback((field: keyof Profile, value: string) => {
    setProfile((current) => ({ ...current, [field]: value }));
  }, []);

  const saveProfile = useCallback(() => {
    setSavedMessage(
      "Profile saved locally for this session. Consent and data-sharing settings remain private by default.",
    );
  }, []);

  const togglePrivacy = useCallback((key: PrivacyKey) => {
    setPrivacy((current) => ({ ...current, [key]: !current[key] }));
  }, []);

  const startCard = useCallback(() => setCardState("active"), []);
  const dismissBanner = useCallback(() => setBannerDismissed(true), []);

  const value = useMemo<PortalState>(
    () => ({
      profile,
      setProfileField,
      savedMessage,
      saveProfile,
      privacy,
      togglePrivacy,
      consentCount,
      savedItems,
      status,
      setStatus,
      vipCard: previewVipCard,
      cardState,
      startCard,
      bannerDismissed,
      dismissBanner,
    }),
    [
      profile,
      setProfileField,
      savedMessage,
      saveProfile,
      privacy,
      togglePrivacy,
      consentCount,
      savedItems,
      status,
      cardState,
      startCard,
      bannerDismissed,
      dismissBanner,
    ],
  );

  return <PortalStateContext.Provider value={value}>{children}</PortalStateContext.Provider>;
}

export function usePortalState() {
  const context = useContext(PortalStateContext);
  if (!context) throw new Error("usePortalState must be used inside PortalStateProvider");
  return context;
}
