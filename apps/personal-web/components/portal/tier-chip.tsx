import { BadgeCheck, Crown } from "lucide-react";

import { cn } from "@healthspan/ui/utils";

/**
 * The tier chip is a rounded rectangle with a crown. Contributor and verification badges are
 * full pills, so a tier is never mistaken for credibility (Logic Spec Z2). The text label is
 * always present; color is never the only signal.
 */
export function TierChip({
  tier,
  detail,
  className,
}: {
  tier: "Free" | "Silver" | "Gold";
  detail?: string;
  className?: string;
}) {
  const tone =
    tier === "Gold"
      ? "border-tier-gold/40 bg-tier-gold-muted text-tier-gold-foreground"
      : tier === "Silver"
        ? "border-tier-silver/40 bg-tier-silver-muted text-foreground"
        : "border-border bg-tier-free-muted text-muted-foreground";
  return (
    <span
      className={cn(
        "inline-flex min-h-6 items-center gap-1 rounded-md border px-2 text-xs font-semibold",
        tone,
        className,
      )}
    >
      <Crown aria-hidden="true" className="size-3.5" />
      {tier === "Free" ? "Free" : `${tier} VIP`}
      {detail && <span className="font-normal opacity-80">· {detail}</span>}
    </span>
  );
}

export function PersonBadge({
  children,
  tone = "contributor",
}: {
  children: string;
  tone?: "contributor" | "verified";
}) {
  return (
    <span
      className={cn(
        "inline-flex min-h-6 items-center gap-1 rounded-full border px-2 text-xs font-medium",
        tone === "verified"
          ? "border-success/25 bg-success-muted text-success"
          : "border-primary/20 bg-secondary text-secondary-foreground",
      )}
    >
      <BadgeCheck aria-hidden="true" className="size-3.5" />
      {children}
    </span>
  );
}
