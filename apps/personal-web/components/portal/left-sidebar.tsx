"use client";

import { Check, Copy } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

import { ProfileAvatar } from "@healthspan/ui/composites";
import { cn } from "@healthspan/ui/utils";

import { navGroups } from "../../lib/portal-nav";
import { previewSummary } from "../../lib/preview-data";
import { presenceStatuses, profileInitials, usePortalState, type PresenceStatus } from "./portal-state";
import { TierChip } from "./tier-chip";

const statusDot: Record<PresenceStatus, string> = {
  Available: "bg-success",
  Away: "bg-warning",
  "Do Not Disturb": "bg-danger",
};

function usernameFor(name: string) {
  const handle = name.toLowerCase().replace(/[^a-z0-9]+/g, "");
  return `@${handle || "member"}`;
}

function ProfileCard() {
  const { profile, status, setStatus, cardState, vipCard } = usePortalState();
  const [copied, setCopied] = useState(false);
  const username = usernameFor(profile.name);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(username);
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    } catch {
      setCopied(false);
    }
  };

  return (
    <section aria-label="Your profile" className="glass overflow-hidden rounded-3xl">
      <div
        aria-hidden="true"
        className="h-20 bg-gradient-to-br from-[color-mix(in_oklch,var(--primary)_55%,white)] via-[color-mix(in_oklch,var(--ring)_45%,white)] to-[color-mix(in_oklch,var(--secondary)_90%,white)]"
      />
      <div className="px-4 pb-4">
        <div className="-mt-8 flex items-end justify-between">
          <span className="relative">
            <ProfileAvatar initials={profileInitials(profile.name)} className="size-16 text-lg" />
            <span
              role="img"
              aria-label={`Status: ${status}`}
              className={cn("absolute right-0 bottom-0.5 size-3.5 rounded-full ring-2 ring-card", statusDot[status])}
            />
          </span>
          <Link
            href="/profile"
            className="mb-1 inline-flex min-h-11 items-center rounded-full px-3 text-xs font-semibold text-primary outline-none hover:bg-accent focus-visible:ring-[3px] focus-visible:ring-ring/30"
          >
            Edit profile
          </Link>
        </div>
        <p className="mt-1 font-display text-lg leading-tight">{profile.name}</p>
        <p className="text-xs leading-snug text-muted-foreground">{profile.title}</p>
        <button
          type="button"
          onClick={copy}
          aria-label={copied ? "Username copied" : `Copy username ${username}`}
          className="mt-1.5 inline-flex min-h-8 items-center gap-1.5 rounded-md text-xs text-muted-foreground outline-none hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/30"
        >
          {username}
          {copied ? <Check aria-hidden="true" className="size-3.5 text-success" /> : <Copy aria-hidden="true" className="size-3.5" />}
          <span aria-live="polite" className="text-success">
            {copied ? "Copied" : ""}
          </span>
        </button>

        <div className="mt-2 flex flex-wrap items-center gap-2">
          <TierChip
            tier={cardState === "active" ? vipCard.tier : "Free"}
            detail={cardState === "active" ? `${vipCard.daysLeft} days left` : undefined}
          />
        </div>

        <div className="mt-3 flex items-center justify-between gap-2 text-xs">
          <span className="font-medium text-foreground">No connections yet</span>
          <label className="flex items-center gap-2 text-muted-foreground">
            <span className="sr-only">Status</span>
            <select
              value={status}
              onChange={(event) => setStatus(event.target.value as PresenceStatus)}
              className="min-h-11 rounded-full border border-border bg-card px-3 text-xs text-foreground outline-none focus-visible:ring-[3px] focus-visible:ring-ring/30"
            >
              {presenceStatuses.map((option) => (
                <option key={option}>{option}</option>
              ))}
            </select>
          </label>
        </div>
        {status === "Do Not Disturb" && (
          <p className="mt-2 rounded-xl bg-muted px-3 py-2 text-xs leading-relaxed text-muted-foreground">
            Push alerts and the chat dock stay quiet. Items still arrive in your Inbox.
          </p>
        )}
      </div>
    </section>
  );
}

export function NavList({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();
  const badges = { inbox: previewSummary.inboxUnread, chat: previewSummary.chatUnread };

  return (
    <nav aria-label="Personal portal pages" className="grid gap-4">
      {navGroups.map((group) => (
        <div key={group.label}>
          <p className="px-3 pb-1 text-[0.7rem] font-semibold tracking-[0.14em] text-primary uppercase">
            {group.label}
          </p>
          <ul className="grid gap-0.5">
            {group.items.map(({ label, href, icon: Icon, badge }) => {
              const active = href ? (href === "/" ? pathname === "/" : pathname.startsWith(href)) : false;
              const count = badge ? badges[badge] : 0;
              const body = (
                <>
                  <Icon aria-hidden="true" className="size-4 shrink-0" />
                  <span className="flex-1 truncate">{label}</span>
                  {count > 0 && (
                    <span className="grid min-w-5 place-items-center rounded-full bg-danger px-1.5 text-[0.65rem] font-bold text-danger-foreground">
                      {count}
                      <span className="sr-only"> unread</span>
                    </span>
                  )}
                  {!href && (
                    <span className="rounded-full bg-muted px-2 py-0.5 text-[0.65rem] font-semibold text-muted-foreground">
                      Soon
                    </span>
                  )}
                </>
              );
              return (
                <li key={label}>
                  {href ? (
                    <Link
                      href={href}
                      onClick={onNavigate}
                      aria-current={active ? "page" : undefined}
                      className={cn(
                        "flex min-h-11 items-center gap-3 rounded-xl border-l-[3px] px-3 text-sm outline-none transition-colors focus-visible:ring-[3px] focus-visible:ring-ring/30",
                        active
                          ? "border-primary bg-accent font-semibold text-accent-foreground"
                          : "border-transparent text-foreground/80 hover:bg-accent/60",
                      )}
                    >
                      {body}
                    </Link>
                  ) : (
                    <span
                      aria-disabled="true"
                      className="flex min-h-11 cursor-default items-center gap-3 rounded-xl border-l-[3px] border-transparent px-3 text-sm text-muted-foreground"
                    >
                      {body}
                    </span>
                  )}
                </li>
              );
            })}
          </ul>
        </div>
      ))}
    </nav>
  );
}

/** Profile card plus the page list. Used as the sticky desktop column and inside the drawer. */
export function LeftSidebar({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <div className="grid gap-4">
      <ProfileCard />
      <div className="glass rounded-3xl p-2 pb-3">
        <NavList onNavigate={onNavigate} />
      </div>
    </div>
  );
}
