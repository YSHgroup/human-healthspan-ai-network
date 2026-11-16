/**
 * Preview values for the rewards, VIP and ranking surfaces.
 *
 * Rewards, VIP cards, referrals and rankings arrive in Milestone 4 and have no backend yet.
 * Every card that reads this file is labelled "Preview data" so the interface never presents
 * these numbers as real (design principle P4: honest numbers). Replace each export with an API
 * call when the matching endpoint exists.
 */

export type VipCardState = "unused" | "active";

export type VipCard = {
  tier: "Gold" | "Silver";
  state: VipCardState;
  useBy: string;
  endsOn: string;
  daysLeft: number;
  totalDays: number;
  unlocks: string[];
};

export const previewVipCard: VipCard = {
  tier: "Gold",
  state: "unused",
  useBy: "31 Dec 2026",
  endsOn: "16 Dec 2026",
  daysLeft: 30,
  totalDays: 30,
  unlocks: ["15 requests a day", "Start chats first", "Posts and events"],
};

export type DailyDuty = { id: string; label: string; points: string; done: boolean };

export const previewDuties: DailyDuty[] = [
  { id: "checkin", label: "Daily check-in", points: "+10", done: false },
  { id: "contribute", label: "Ask, answer or comment", points: "+3 to +15", done: false },
  { id: "event", label: "Attend an event", points: "+15", done: false },
  { id: "ai", label: "Use AI", points: "+5", done: false },
  { id: "starter", label: "Try something new", points: "+20", done: false },
];

export const previewMonthly = {
  points: 0,
  band: null as string | null,
  nextCard: { tier: "Silver", have: 0, need: 700 },
  topThree: [] as { name: string; points: string }[],
};

export const previewSummary = {
  rewardBalance: 0,
  rewardDelta: 0,
  streakDays: 0,
  streakFrozen: false,
  inboxUnread: 0,
  connectionRequests: 0,
  chatUnread: 0,
};

export const previewContribution = [
  { label: "Questions asked", value: 0 },
  { label: "Answers given", value: 0 },
  { label: "Accepted answers", value: 0 },
  { label: "Evidence-linked posts", value: 0 },
  { label: "Events attended", value: 0 },
];

export const previewReferralPath = "/join?ref=harper";
