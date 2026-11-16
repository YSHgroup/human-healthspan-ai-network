import {
  Activity,
  Bookmark,
  CalendarDays,
  CircleHelp,
  CircleUserRound,
  CreditCard,
  Crown,
  FileClock,
  Gift,
  Handshake,
  HeartPulse,
  House,
  Inbox,
  LockKeyhole,
  MessageCircle,
  Settings2,
  Sparkles,
  Trophy,
  UsersRound,
  type LucideIcon,
} from "lucide-react";

export type Phase = "Now" | "M4" | "M5" | "Later";

export type NavItem = {
  label: string;
  /** Internal route. Items without an href have not launched and show a "Soon" tag. */
  href?: string;
  icon: LucideIcon;
  phase: Phase;
  /** Unread badge key, resolved by the shell from the portal state. */
  badge?: "inbox" | "chat";
};

export type NavGroup = { label: string; items: NavItem[] };

/** Every page of the Personal Portal (design specification, section 5.2). */
export const navGroups: NavGroup[] = [
  {
    label: "Home",
    items: [
      { label: "Overview", href: "/", icon: House, phase: "Now" },
      { label: "Favorites", href: "/favorites", icon: Bookmark, phase: "Now" },
      { label: "Inbox", icon: Inbox, phase: "Now", badge: "inbox" },
      { label: "Chat", href: "/messages", icon: MessageCircle, phase: "Now", badge: "chat" },
    ],
  },
  {
    label: "Me",
    items: [
      { label: "Profile", href: "/profile", icon: CircleUserRound, phase: "Now" },
      { label: "Connections", icon: Handshake, phase: "M4" },
      { label: "My activity", icon: Activity, phase: "Now" },
      { label: "Groups and organizations", icon: UsersRound, phase: "Now" },
      { label: "Events", icon: CalendarDays, phase: "M4" },
    ],
  },
  {
    label: "Health",
    items: [
      { label: "Health Data", icon: HeartPulse, phase: "M5" },
      { label: "Personal AI", icon: Sparkles, phase: "M5" },
    ],
  },
  {
    label: "Rewards",
    items: [
      { label: "Rewards", icon: Gift, phase: "M4" },
      { label: "VIP Club", icon: Crown, phase: "M4" },
      { label: "Affiliate", icon: Handshake, phase: "M4" },
      { label: "Rankings", icon: Trophy, phase: "M4" },
    ],
  },
  {
    label: "Account",
    items: [
      { label: "Premium and billing", icon: CreditCard, phase: "M5" },
      { label: "Privacy and consent", href: "/privacy", icon: LockKeyhole, phase: "Now" },
      { label: "Access log", icon: FileClock, phase: "Now" },
      { label: "Settings", icon: Settings2, phase: "Now" },
      { label: "Help", icon: CircleHelp, phase: "Now" },
    ],
  },
];

/** Bottom tab bar on phones. Inbox and Rewards take over once they launch. */
export const mobileTabs: { label: string; href: string; icon: LucideIcon }[] = [
  { label: "Overview", href: "/", icon: House },
  { label: "Favorites", href: "/favorites", icon: Bookmark },
  { label: "Chat", href: "/messages", icon: MessageCircle },
  { label: "Profile", href: "/profile", icon: CircleUserRound },
];

export type PortalMenuLink = { label: string; href?: string; soon?: boolean; external?: boolean };
export type PortalMenu = {
  id: "social" | "personal" | "researcher";
  label: string;
  links: PortalMenuLink[];
  locked?: boolean;
};

export type PortalUrls = { social: string; researcher: string };

/** Portals menu contents (design specification, section 4). */
export function buildPortalMenus(urls: PortalUrls): PortalMenu[] {
  const social = urls.social.replace(/\/$/, "");
  const researcher = urls.researcher.replace(/\/$/, "");
  return [
    {
      id: "social",
      label: "Social",
      links: [
        { label: "Communities", href: `${social}/communities`, external: true },
        { label: "Community feed", href: `${social}/feed`, external: true },
        { label: "Q&A", href: `${social}/feed`, external: true },
        { label: "Events", soon: true },
        { label: "General AI", href: `${social}/ai`, external: true },
      ],
    },
    {
      id: "personal",
      label: "Personal",
      links: [
        { label: "Overview", href: "/" },
        { label: "Favorites", href: "/favorites" },
        { label: "Inbox", soon: true },
        { label: "Chat", href: "/messages" },
        { label: "Profile", href: "/profile" },
        { label: "Connections", soon: true },
        { label: "Health Data", soon: true },
        { label: "Rewards", soon: true },
        { label: "VIP Club", soon: true },
        { label: "Affiliate", soon: true },
        { label: "Rankings", soon: true },
        { label: "Premium and billing", soon: true },
        { label: "Privacy", href: "/privacy" },
        { label: "Settings", soon: true },
      ],
    },
    {
      id: "researcher",
      label: "Researcher",
      locked: true,
      links: [
        { label: "Workspace", href: researcher, external: true },
        { label: "Projects", soon: true },
        { label: "Organizations", soon: true },
        { label: "Research events", soon: true },
        { label: "Profiles", soon: true },
        { label: "Scientist prototype", href: `${researcher}/ai`, external: true },
      ],
    },
  ];
}
