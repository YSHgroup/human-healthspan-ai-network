"use client";

import { Check, CircleDashed, Copy, Crown, Info, Lock } from "lucide-react";
import { useState } from "react";

import { Button } from "@healthspan/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@healthspan/ui/dialog";
import { toast } from "@healthspan/ui/sonner";
import { cn } from "@healthspan/ui/utils";

import { previewDuties, previewMonthly, previewReferralPath } from "../../lib/preview-data";
import { usePortalState } from "./portal-state";

function PreviewTag() {
  return (
    <span className="rounded-full border border-border bg-muted px-2 py-0.5 text-[0.65rem] font-semibold text-muted-foreground">
      Preview
    </span>
  );
}

function SoonLink({ children }: { children: string }) {
  return (
    <span
      aria-disabled="true"
      title="Arrives with Milestone 4"
      className="inline-flex min-h-8 cursor-default items-center gap-1.5 text-xs text-muted-foreground"
    >
      {children}
      <span className="rounded-full bg-muted px-1.5 py-0.5 text-[0.6rem] font-semibold">Soon</span>
    </span>
  );
}

/** Plan and VIP status card (design specification, section 6.1). */
function PlanStatusCard() {
  const { cardState, vipCard, startCard } = usePortalState();
  const [confirmOpen, setConfirmOpen] = useState(false);

  // Free members without a card do not see this card; progress shows in Monthly activity.
  if (cardState === "none") return null;
  const active = cardState === "active";

  return (
    <section
      aria-label="Plan and VIP status"
      className="glass overflow-hidden rounded-3xl border-tier-gold/30 bg-gradient-to-b from-tier-gold-muted/70 to-transparent"
    >
      <div className="flex items-center justify-between gap-2 px-4 pt-4">
        <h2 className="font-display text-lg">
          Your plan &amp; VIP status
        </h2>
        <SoonLink>Go to plan</SoonLink>
      </div>
      <div className="p-4 pt-3">
        <div
          className={cn(
            "relative grid min-h-24 place-items-center overflow-hidden rounded-2xl border border-tier-gold/40 bg-gradient-to-br from-[oklch(0.9_0.12_90)] via-[oklch(0.82_0.14_82)] to-[oklch(0.7_0.13_75)] text-tier-gold-foreground shadow-sm",
            active && "soft-pop",
          )}
        >
          <div className="flex items-center gap-2 font-display text-2xl">
            <Crown aria-hidden="true" className="size-6" />
            {vipCard.tier} VIP
          </div>
          <span className="absolute top-2 right-2 rounded-full bg-white/60 px-2 py-0.5 text-[0.65rem] font-semibold text-foreground">
            {active ? "Active" : "Ready to use"}
          </span>
        </div>

        {active ? (
          <div className="mt-3 text-sm">
            <p className="font-medium">
              <Check aria-hidden="true" className="mr-1 inline size-4 text-success" />
              {vipCard.tier} card active until {vipCard.endsOn}
            </p>
            <div
              role="progressbar"
              aria-label="VIP card days left"
              aria-valuemin={0}
              aria-valuemax={vipCard.totalDays}
              aria-valuenow={vipCard.daysLeft}
              className="mt-2 h-2 overflow-hidden rounded-full bg-muted"
            >
              <div
                className="h-full rounded-full bg-tier-gold"
                style={{ width: `${(vipCard.daysLeft / vipCard.totalDays) * 100}%` }}
              />
            </div>
            <p className="mt-1 text-xs text-muted-foreground">
              {vipCard.daysLeft} of {vipCard.totalDays} days left
            </p>
            <ul className="mt-2 grid gap-1 text-xs text-muted-foreground">
              {vipCard.unlocks.map((item) => (
                <li key={item} className="flex items-center gap-1.5">
                  <Check aria-hidden="true" className="size-3.5 text-success" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <div className="mt-3">
            <p className="text-sm">
              {vipCard.tier} card, ready to use.{" "}
              <span className="text-muted-foreground">Use it by {vipCard.useBy}.</span>
            </p>
            <Button
              className="mt-3 w-full rounded-full"
              size="lg"
              aria-label={`Use ${vipCard.tier} VIP card now`}
              onClick={() => setConfirmOpen(true)}
            >
              Use now
            </Button>
          </div>
        )}
        <p className="mt-3 flex items-center gap-1.5 text-[0.7rem] text-muted-foreground">
          <PreviewTag /> Cards and plans go live with Milestone 4.
        </p>
      </div>

      <Dialog open={confirmOpen} onOpenChange={setConfirmOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Start your {vipCard.tier} VIP card?</DialogTitle>
            <DialogDescription>
              It lasts {vipCard.totalDays} days. It starts now and cannot be paused.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setConfirmOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={() => {
                startCard();
                setConfirmOpen(false);
                toast.success(`${vipCard.tier} card active until ${vipCard.endsOn}`);
              }}
            >
              Start card
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </section>
  );
}

const shareChannels = [
  { id: "linkedin", label: "LinkedIn", glyph: "in", url: (u: string) => `https://www.linkedin.com/sharing/share-offsite/?url=${u}` },
  { id: "facebook", label: "Facebook", glyph: "f", url: (u: string) => `https://www.facebook.com/sharer/sharer.php?u=${u}` },
  { id: "x", label: "X", glyph: "X", url: (u: string) => `https://twitter.com/intent/tweet?url=${u}` },
  { id: "instagram", label: "Instagram", glyph: "IG", url: null },
  { id: "whatsapp", label: "WhatsApp", glyph: "WA", url: (u: string) => `https://wa.me/?text=${u}` },
  { id: "telegram", label: "Telegram", glyph: "TG", url: (u: string) => `https://t.me/share/url?url=${u}` },
] as const;

function ReferralCard({ socialUrl }: { socialUrl: string }) {
  const [copied, setCopied] = useState(false);
  const link = `${socialUrl.replace(/\/$/, "")}${previewReferralPath}`;

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(link);
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
      return true;
    } catch {
      toast.error("Could not copy the link.");
      return false;
    }
  };

  return (
    <section aria-label="Referral link" className="glass rounded-3xl p-4">
      <div className="flex items-center justify-between gap-2">
        <h2 className="font-display text-lg">
          Your referral link
        </h2>
        <PreviewTag />
      </div>
      <div className="mt-3 flex items-center gap-2">
        <input
          readOnly
          aria-label="Referral link"
          value={link}
          className="min-h-11 min-w-0 flex-1 rounded-full border border-border bg-card px-4 text-xs text-muted-foreground outline-none focus-visible:ring-[3px] focus-visible:ring-ring/30"
        />
        <Button variant="outline" size="icon" aria-label={copied ? "Link copied" : "Copy referral link"} onClick={copy}>
          {copied ? <Check aria-hidden="true" className="text-success" /> : <Copy aria-hidden="true" />}
        </Button>
      </div>
      <div className="mt-3 flex flex-wrap items-center gap-1.5" role="group" aria-label="Share your link">
        <span className="mr-1 text-xs text-muted-foreground">Share:</span>
        {shareChannels.map((channel) => {
          const className =
            "grid size-11 place-items-center rounded-full border border-border bg-card text-xs font-bold text-primary outline-none transition-colors hover:bg-accent focus-visible:ring-[3px] focus-visible:ring-ring/30";
          if (channel.url) {
            return (
              <a
                key={channel.id}
                href={channel.url(encodeURIComponent(link))}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={`Share on ${channel.label}`}
                className={className}
              >
                {channel.glyph}
              </a>
            );
          }
          // Instagram has no share URL: copy the link, then open Instagram.
          return (
            <button
              key={channel.id}
              type="button"
              aria-label="Copy link and open Instagram"
              className={className}
              onClick={async () => {
                if (await copy()) window.open("https://www.instagram.com/", "_blank", "noopener,noreferrer");
              }}
            >
              {channel.glyph}
            </button>
          );
        })}
      </div>
      <div className="mt-2">
        <SoonLink>See Affiliate</SoonLink>
      </div>
    </section>
  );
}

function MonthlyActivityCard() {
  const { points, band, nextCard } = previewMonthly;
  const percent = Math.min(100, Math.round((nextCard.have / nextCard.need) * 100));
  return (
    <section aria-label="Monthly activity" className="glass rounded-3xl p-4">
      <div className="flex items-center justify-between gap-2">
        <h2 className="font-display text-lg">
          Monthly activity
        </h2>
        <PreviewTag />
      </div>
      <div className="mt-2 flex items-end justify-between gap-2">
        <p className="font-display text-3xl">
          {points.toLocaleString("en-US")} <span className="font-sans text-sm text-muted-foreground">points</span>
        </p>
        <p className="text-sm font-medium text-primary">{band ?? "No rank yet"}</p>
      </div>
      <p className="mt-3 rounded-xl bg-muted/70 px-3 py-2 text-xs leading-relaxed text-muted-foreground">
        The top three appear here once members earn points this month.
      </p>
      <div className="mt-3">
        <div
          role="progressbar"
          aria-label={`Points toward ${nextCard.tier} card`}
          aria-valuemin={0}
          aria-valuemax={nextCard.need}
          aria-valuenow={nextCard.have}
          className="h-2 overflow-hidden rounded-full bg-muted"
        >
          <div className="h-full rounded-full bg-primary" style={{ width: `${percent}%` }} />
        </div>
        <p className="mt-1 text-xs text-muted-foreground">
          {nextCard.have} of {nextCard.need} points to {nextCard.tier}
        </p>
      </div>
      <div className="mt-2 flex items-center justify-between gap-2">
        <SoonLink>See people 1 to 50</SoonLink>
        <span className="text-[0.7rem] text-muted-foreground">Ranking resets on the 1st</span>
      </div>
    </section>
  );
}

function DailyRewardsCard() {
  return (
    <section aria-label="Daily rewards" className="glass rounded-3xl p-4">
      <div className="flex items-center justify-between gap-2">
        <h2 className="font-display text-lg">
          Daily rewards
        </h2>
        <PreviewTag />
      </div>
      <ul className="mt-3 grid gap-2">
        {previewDuties.map((duty) => (
          <li key={duty.id} className="flex items-center gap-2.5 text-sm">
            {duty.done ? (
              <Check aria-hidden="true" className="size-5 rounded-full bg-success p-1 text-success-foreground" />
            ) : (
              <CircleDashed aria-hidden="true" className="size-5 text-muted-foreground" />
            )}
            <span className="flex-1">{duty.label}</span>
            <span className="text-xs font-semibold text-primary">{duty.points}</span>
            <span className="sr-only">{duty.done ? "done" : "open"}</span>
          </li>
        ))}
      </ul>
      <p className="mt-3 border-t border-border pt-2 text-xs text-muted-foreground" aria-live="polite">
        Earned today: 0 of 100 activity points
      </p>
    </section>
  );
}

export function RightSidebar({ socialUrl }: { socialUrl: string }) {
  return (
    <div className="grid gap-4">
      <PlanStatusCard />
      <ReferralCard socialUrl={socialUrl} />
      <MonthlyActivityCard />
      <DailyRewardsCard />
      <p className="flex items-start gap-2 px-2 text-xs leading-relaxed text-muted-foreground">
        <Info aria-hidden="true" className="mt-0.5 size-3.5 shrink-0" />
        Rewards recognize contribution, not time on site. Nothing here is paid for sharing health
        information.
      </p>
      <p className="flex items-start gap-2 px-2 text-xs text-muted-foreground">
        <Lock aria-hidden="true" className="mt-0.5 size-3.5 shrink-0" />
        Health data never appears in rankings or rewards.
      </p>
    </div>
  );
}
