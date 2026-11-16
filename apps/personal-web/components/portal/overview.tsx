"use client";

import {
  ArrowRight,
  Bookmark,
  CalendarDays,
  Compass,
  Crown,
  Flame,
  Handshake,
  Inbox,
  LockKeyhole,
  MessageCircle,
  Sparkles,
  Trophy,
  UserPlus,
  UsersRound,
  X,
  type LucideIcon,
} from "lucide-react";
import Link from "next/link";
import type { ReactNode } from "react";

import { Button } from "@healthspan/ui/button";
import { EmptyState } from "@healthspan/ui/composites";
import { cn } from "@healthspan/ui/utils";

import { previewContribution, previewSummary } from "../../lib/preview-data";
import { GlassSection } from "./page-header";
import { usePortalState } from "./portal-state";
import { TierChip } from "./tier-chip";

function SummaryCard({
  icon: Icon,
  value,
  label,
  note,
  tone,
}: {
  icon: LucideIcon;
  value: string;
  label: string;
  note?: ReactNode;
  tone: string;
}) {
  return (
    <div className="glass rounded-2xl p-4">
      <span className={cn("mb-3 grid size-10 place-items-center rounded-xl", tone)}>
        <Icon aria-hidden="true" className="size-5" />
      </span>
      <p className="font-display text-2xl leading-none">{value}</p>
      <p className="mt-1 text-sm text-muted-foreground">{label}</p>
      {note && <div className="mt-2 text-xs">{note}</div>}
    </div>
  );
}

type QuickAction = { label: string; icon: LucideIcon; href?: string; tone: string };

const quickActions: QuickAction[] = [
  { label: "Ask a question", icon: MessageCircle, tone: "bg-promise-power/10 text-promise-power" },
  { label: "Find a community", icon: UsersRound, tone: "bg-promise-health/10 text-promise-health" },
  { label: "Invite a friend", icon: UserPlus, tone: "bg-promise-potential/10 text-promise-potential" },
  { label: "Open chat", icon: Inbox, href: "/messages", tone: "bg-promise-power/10 text-promise-power" },
  { label: "Use AI", icon: Sparkles, tone: "bg-promise-health/10 text-promise-health" },
];

export function Overview({ socialUrl, researcherUrl }: { socialUrl: string; researcherUrl: string }) {
  const { profile, privacy, consentCount, savedItems, cardState, vipCard, startCard, bannerDismissed, dismissBanner, status } =
    usePortalState();
  const social = socialUrl.replace(/\/$/, "");
  const sharedFields = [privacy.profileVisible, privacy.communityActivityVisible].filter(Boolean).length;
  const firstName = profile.name.split(" ")[0] || "there";

  return (
    <div className="grid gap-5">
      {/* Welcome strip */}
      <section
        aria-labelledby="welcome-heading"
        className="glass-strong relative overflow-hidden rounded-3xl p-6 sm:p-8"
      >
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_85%_20%,color-mix(in_oklch,var(--ring)_30%,transparent),transparent_55%)]"
        />
        <div className="relative flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="mb-3 flex flex-wrap items-center gap-2">
              <TierChip
                tier={cardState === "active" ? vipCard.tier : "Free"}
                detail={cardState === "active" ? `${vipCard.daysLeft} days left` : undefined}
              />
              <span className="text-xs text-muted-foreground">{status}</span>
            </div>
            <h1 id="welcome-heading" className="font-display text-4xl leading-tight tracking-tight sm:text-5xl">
              Welcome back, {firstName}!
            </h1>
            <p className="mt-2 text-base text-muted-foreground">Explore. Learn. Connect. Grow.</p>
          </div>
          <Link
            href="/privacy"
            className="glass inline-flex min-h-11 items-center gap-2 rounded-full px-4 text-sm outline-none transition-colors hover:bg-accent focus-visible:ring-[3px] focus-visible:ring-ring/30"
          >
            <LockKeyhole aria-hidden="true" className="size-4 text-success" />
            Health data private. {sharedFields} profile field{sharedFields === 1 ? "" : "s"} shared
            <ArrowRight aria-hidden="true" className="size-4" />
          </Link>
        </div>
      </section>

      {/* Unused VIP card banner: same action as the status card. */}
      {cardState === "unused" && !bannerDismissed && (
        <section
          aria-label="VIP card ready"
          className="glass flex flex-wrap items-center gap-4 rounded-3xl border-tier-gold/30 bg-gradient-to-r from-tier-gold-muted/70 to-transparent p-4 pr-3"
        >
          <span className="grid size-12 place-items-center rounded-2xl bg-tier-gold text-tier-gold-foreground">
            <Crown aria-hidden="true" className="size-6" />
          </span>
          <div className="min-w-0 flex-1">
            <p className="font-display text-lg">Your {vipCard.tier} card is ready</p>
            <p className="text-sm text-muted-foreground">Unlock more benefits and exclusive features.</p>
          </div>
          <Button size="lg" className="rounded-full" aria-label={`Use ${vipCard.tier} VIP card now`} onClick={startCard}>
            Use now
          </Button>
          <button
            type="button"
            aria-label="Dismiss banner"
            onClick={dismissBanner}
            className="grid size-11 place-items-center rounded-full text-muted-foreground outline-none hover:bg-accent focus-visible:ring-[3px] focus-visible:ring-ring/30"
          >
            <X aria-hidden="true" className="size-4" />
          </button>
        </section>
      )}

      {/* Summary cards: honest numbers, empty until the backend provides them. */}
      <section aria-label="Summary" className="grid grid-cols-2 gap-3 md:grid-cols-3 2xl:grid-cols-5">
        <SummaryCard icon={Trophy} tone="bg-tier-gold-muted text-tier-gold-foreground" value={previewSummary.rewardBalance.toLocaleString("en-US")} label="Reward balance" note={<span className="text-muted-foreground">Preview</span>} />
        <SummaryCard icon={Sparkles} tone="bg-promise-health/10 text-promise-health" value="No rank yet" label="Monthly rank" note={<span className="text-muted-foreground">Earn points to appear</span>} />
        <SummaryCard icon={Flame} tone="bg-promise-life/15 text-promise-life" value={`${previewSummary.streakDays} days`} label="Streak" note={previewSummary.streakFrozen ? <span className="rounded-full bg-secondary px-2 py-0.5 font-semibold">Frozen</span> : <span className="text-muted-foreground">One freeze a month</span>} />
        <SummaryCard icon={Inbox} tone="bg-promise-power/10 text-promise-power" value={String(previewSummary.inboxUnread)} label="Inbox unread" />
        <SummaryCard icon={Handshake} tone="bg-promise-potential/10 text-promise-potential" value={String(previewSummary.connectionRequests)} label="Connection requests" />
      </section>

      {/* My contribution */}
      <GlassSection title="My contribution this month">
        <dl className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
          {previewContribution.map((item) => (
            <div key={item.label} className="rounded-2xl bg-muted/60 p-3">
              <dd className="font-display text-2xl leading-none">{item.value}</dd>
              <dt className="mt-1 text-xs text-muted-foreground">{item.label}</dt>
            </div>
          ))}
        </dl>
        <p className="mt-3 text-xs text-muted-foreground">
          Contribution counts questions, answers and evidence, never time spent.
        </p>
      </GlassSection>

      {/* For me: saved knowledge is the one real feed today. */}
      <GlassSection
        title="For me"
        action={
          <Link href="/favorites" className="inline-flex min-h-11 items-center gap-1 text-sm font-medium text-primary hover:underline">
            View favorites <ArrowRight aria-hidden="true" className="size-4" />
          </Link>
        }
      >
        <div className="grid gap-4 lg:grid-cols-3">
          <div className="rounded-2xl border border-border bg-card/60 p-4">
            <p className="flex items-center gap-2 text-sm font-semibold">
              <Bookmark aria-hidden="true" className="size-4 text-primary" /> Saved knowledge
            </p>
            <ul className="mt-3 grid gap-2">
              {savedItems.map((item) => (
                <li key={item.title} className="text-sm">
                  <p className="font-medium leading-snug">{item.title}</p>
                  <p className="text-xs text-muted-foreground">{item.meta}</p>
                </li>
              ))}
            </ul>
          </div>
          <EmptyState
            className="min-h-0 py-6"
            icon={UsersRound}
            title="Followed communities"
            description="Communities you follow will show new activity here."
            action={
              <a className="text-sm font-medium text-primary hover:underline" href={`${social}/communities`}>
                Find a community
              </a>
            }
          />
          <EmptyState
            className="min-h-0 py-6"
            icon={CalendarDays}
            title="Upcoming events"
            description="Events you join will appear here."
          />
        </div>
      </GlassSection>

      {/* Quick actions */}
      <GlassSection title="Quick actions">
        <div className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-5">
          {quickActions.map(({ label, icon: Icon, href, tone }) => {
            const className =
              "flex min-h-14 items-center gap-3 rounded-2xl border border-border bg-card/70 px-4 text-sm font-medium outline-none transition-[transform,box-shadow] hover:-translate-y-0.5 hover:shadow-sm focus-visible:ring-[3px] focus-visible:ring-ring/30 motion-reduce:transform-none";
            const inner = (
              <>
                <span className={cn("grid size-9 shrink-0 place-items-center rounded-xl", tone)}>
                  <Icon aria-hidden="true" className="size-4" />
                </span>
                {label}
              </>
            );
            return href ? (
              <Link key={label} href={href} className={className}>
                {inner}
              </Link>
            ) : (
              <a
                key={label}
                href={label === "Find a community" ? `${social}/communities` : label === "Use AI" ? `${social}/ai` : label === "Ask a question" ? `${social}/feed` : `${social}`}
                className={className}
              >
                {inner}
              </a>
            );
          })}
        </div>
      </GlassSection>

      {/* Privacy summary keeps the consent count from the earlier overview. */}
      <section aria-label="Privacy summary" className="glass flex flex-wrap items-center justify-between gap-3 rounded-3xl p-4">
        <p className="flex items-center gap-2 text-sm">
          <LockKeyhole aria-hidden="true" className="size-4 text-success" />
          <span>
            <strong className="font-semibold">{consentCount}/5</strong> consent checks enabled. Health data stays
            private by default.
          </span>
        </p>
        <Link href="/privacy" className="inline-flex min-h-11 items-center gap-1 text-sm font-medium text-primary hover:underline">
          Review privacy <ArrowRight aria-hidden="true" className="size-4" />
        </Link>
      </section>

      {/* Research prompt */}
      <section aria-label="Research access" className="glass flex flex-wrap items-center justify-between gap-3 rounded-3xl p-4">
        <p className="flex items-center gap-2 text-sm">
          <Compass aria-hidden="true" className="size-4 text-primary" />
          Want to access research features? Apply for researcher access.
        </p>
        <a href={researcherUrl} className="inline-flex min-h-11 items-center gap-1 text-sm font-medium text-primary hover:underline">
          Learn more <ArrowRight aria-hidden="true" className="size-4" />
        </a>
      </section>
    </div>
  );
}
