import {
  Activity,
  Atom,
  BookOpenCheck,
  CircleHelp,
  CircleUserRound,
  FlaskConical,
  FlaskRound,
  Microscope,
  Network,
  PawPrint,
  ShieldCheck,
  Sparkles,
  UsersRound,
  type LucideIcon,
} from "lucide-react";
import type { EvidenceClass, VerificationState } from "@healthspan/shared-types";
import type { ReactNode } from "react";

import { Avatar, AvatarFallback } from "./avatar";
import { Badge } from "./badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./card";
import { Separator } from "./separator";
import { cn } from "./utils";

function PageShell({
  className,
  children,
  wide = false,
}: {
  className?: string;
  children: ReactNode;
  wide?: boolean;
}) {
  return (
    <div
      className={cn(
        "min-h-[calc(100dvh-4.5rem)] w-full px-4 py-8 sm:px-6 sm:py-10 lg:px-8",
        wide ? "mx-auto max-w-screen-2xl" : "mx-auto max-w-7xl",
        className,
      )}
    >
      {children}
    </div>
  );
}

type HeaderLink = { label: string; href: string };

function SiteHeader({
  title = "Healthspan Network",
  eyebrow,
  brand,
  links = [],
  actions,
  themeToggle,
  homeHref = "/",
  className,
}: {
  title?: string;
  eyebrow?: string;
  brand?: ReactNode;
  links?: HeaderLink[];
  actions?: ReactNode;
  themeToggle?: ReactNode;
  homeHref?: string;
  className?: string;
}) {
  return (
    <header
      className={cn(
        "sticky top-0 z-40 border-b border-border/70 bg-background/85 backdrop-blur-xl",
        className,
      )}
    >
      <div className="mx-auto flex min-h-[4.5rem] max-w-screen-2xl items-center justify-between gap-3 px-4 sm:px-6 lg:px-8">
        <a
          href={homeHref}
          aria-label={`${title} home`}
          className="group flex min-h-11 min-w-0 items-center gap-3 rounded-lg outline-none focus-visible:ring-[3px] focus-visible:ring-ring/30"
        >
          {brand ?? (
            <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-primary/10 text-primary transition-transform group-hover:rotate-[-5deg]">
              <Network aria-hidden="true" className="size-5" />
            </span>
          )}
          <span className="grid min-w-0">
            {eyebrow && (
              <span className="truncate text-[0.625rem] font-semibold tracking-[0.16em] text-muted-foreground uppercase">
                {eyebrow}
              </span>
            )}
            <span className="truncate text-sm font-semibold tracking-tight text-foreground sm:text-base">
              {title}
            </span>
          </span>
        </a>

        <nav className="hidden items-center gap-1 lg:flex" aria-label="Primary navigation">
          {links.map(({ label, href }) => (
            <a
              key={label}
              href={href}
              className="inline-flex min-h-11 items-center rounded-lg px-3 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/30"
            >
              {label}
            </a>
          ))}
        </nav>

        <div className="flex shrink-0 items-center gap-2">
          {actions}
          {themeToggle}
          {links.length > 0 && (
            <details className="group relative lg:hidden">
              <summary
                aria-label="Open navigation"
                className="grid size-11 cursor-pointer list-none place-items-center rounded-lg border border-border bg-card text-foreground outline-none focus-visible:ring-[3px] focus-visible:ring-ring/30 [&::-webkit-details-marker]:hidden"
              >
                <span aria-hidden="true" className="grid gap-1">
                  <span className="h-0.5 w-4 rounded-full bg-current" />
                  <span className="h-0.5 w-4 rounded-full bg-current" />
                  <span className="h-0.5 w-4 rounded-full bg-current" />
                </span>
              </summary>
              <nav
                aria-label="Mobile navigation"
                className="absolute top-[calc(100%+0.65rem)] right-0 grid min-w-56 gap-1 rounded-xl border border-border bg-popover p-2 text-popover-foreground shadow-lg"
              >
                {links.map(({ label, href }) => (
                  <a
                    key={label}
                    href={href}
                    className="flex min-h-11 items-center rounded-lg px-3 text-sm outline-none transition-colors hover:bg-accent focus-visible:ring-[3px] focus-visible:ring-ring/30"
                  >
                    {label}
                  </a>
                ))}
              </nav>
            </details>
          )}
        </div>
      </div>
    </header>
  );
}

function SiteFooter({
  note = "Better people. Better science. A healthier future.",
  children,
}: {
  note?: string;
  children?: ReactNode;
}) {
  return (
    <footer className="border-t border-border/70 bg-surface-raised/60">
      <div className="mx-auto flex max-w-screen-2xl flex-col gap-4 px-4 py-6 text-sm text-muted-foreground sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
        <span>{note}</span>
        {children}
      </div>
    </footer>
  );
}

function SectionHeading({
  eyebrow,
  title,
  description,
  className,
  centered = false,
  as = "h2",
  id,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  className?: string;
  centered?: boolean;
  as?: "h1" | "h2";
  id?: string;
}) {
  const Heading = as;
  return (
    <div className={cn("max-w-2xl", centered && "mx-auto text-center", className)}>
      {eyebrow && (
        <p className="mb-3 text-xs font-semibold tracking-[0.16em] text-primary uppercase">
          {eyebrow}
        </p>
      )}
      <Heading
        id={id}
        className="font-display text-3xl leading-tight tracking-tight text-foreground sm:text-4xl"
      >
        {title}
      </Heading>
      {description && (
        <p className="mt-3 text-base leading-relaxed text-muted-foreground">{description}</p>
      )}
    </div>
  );
}

function FeatureCard({
  title,
  description,
  icon: Icon,
  eyebrow,
  className,
  children,
}: {
  title: string;
  description: string;
  icon: LucideIcon;
  eyebrow?: string;
  className?: string;
  children?: ReactNode;
}) {
  return (
    <Card
      className={cn(
        "group h-full border-border/80 bg-gradient-to-br from-card to-surface-raised/75 shadow-xs transition-[transform,box-shadow,border-color] duration-200 hover:-translate-y-1 hover:border-primary/25 hover:shadow-md motion-reduce:transform-none",
        className,
      )}
    >
      <CardHeader>
        <span className="mb-2 grid size-11 place-items-center rounded-xl bg-accent text-accent-foreground transition-transform duration-200 group-hover:scale-105">
          <Icon aria-hidden="true" className="size-5" />
        </span>
        {eyebrow && (
          <p className="text-xs font-semibold tracking-wide text-primary uppercase">{eyebrow}</p>
        )}
        <CardTitle className="font-display text-xl">{title}</CardTitle>
        <CardDescription className="leading-relaxed">{description}</CardDescription>
      </CardHeader>
      {children && <CardContent className="pt-0">{children}</CardContent>}
    </Card>
  );
}

function EmptyState({
  title,
  description,
  icon: Icon = BookOpenCheck,
  action,
  className,
}: {
  title: string;
  description: string;
  icon?: LucideIcon;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "flex min-h-52 flex-col items-center justify-center rounded-xl border border-dashed border-border bg-card/55 px-5 py-8 text-center",
        className,
      )}
    >
      <span className="relative mb-4 grid size-14 place-items-center rounded-2xl bg-accent text-accent-foreground">
        <span className="absolute -top-1 -right-1 size-3 rounded-full bg-success/65" />
        <Icon aria-hidden="true" className="size-6" />
      </span>
      <h3 className="font-display text-lg text-foreground">{title}</h3>
      <p className="mt-1 max-w-md text-sm leading-relaxed text-muted-foreground">{description}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

type PortalLink = {
  title: string;
  description: string;
  href: string;
  icon: LucideIcon;
};

function PortalSwitcher({ portals, className }: { portals: PortalLink[]; className?: string }) {
  return (
    <div className={cn("grid gap-3 sm:grid-cols-3", className)}>
      {portals.map(({ title, description, href, icon: Icon }) => (
        <a
          key={title}
          href={href}
          className="group flex min-h-16 items-center gap-3 rounded-xl border border-border bg-card p-3 transition-[transform,box-shadow,border-color] hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-sm focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/30"
        >
          <span className="grid size-10 shrink-0 place-items-center rounded-lg bg-accent text-accent-foreground">
            <Icon aria-hidden="true" className="size-5" />
          </span>
          <span className="grid min-w-0">
            <span className="truncate text-sm font-semibold text-foreground">{title}</span>
            <span className="truncate text-xs text-muted-foreground">{description}</span>
          </span>
        </a>
      ))}
    </div>
  );
}

const evidenceBadgeConfig: Record<
  EvidenceClass,
  { label: string; icon: LucideIcon; tone: "success" | "primary" | "warning" | "danger" }
> = {
  peer_reviewed: { label: "Peer reviewed", icon: BookOpenCheck, tone: "success" },
  clinical_trial: { label: "Clinical trial", icon: FlaskConical, tone: "success" },
  human_observational: { label: "Human observational", icon: UsersRound, tone: "primary" },
  animal: { label: "Animal study", icon: PawPrint, tone: "primary" },
  cellular_in_vitro: { label: "Cellular / in vitro", icon: Microscope, tone: "primary" },
  computational: { label: "Computational", icon: Atom, tone: "primary" },
  preprint: { label: "Preprint", icon: FlaskRound, tone: "warning" },
  expert_opinion: { label: "Expert opinion", icon: CircleUserRound, tone: "warning" },
  community_experience: { label: "Community experience", icon: UsersRound, tone: "warning" },
  ai_generated_hypothesis: { label: "AI hypothesis", icon: Sparkles, tone: "danger" },
  speculation: { label: "Speculation", icon: CircleHelp, tone: "danger" },
};

const evidenceToneClasses = {
  success: "border-success/25 bg-success-muted text-success",
  primary: "border-primary/20 bg-secondary text-secondary-foreground",
  warning: "border-warning/30 bg-warning-muted text-warning-foreground",
  danger: "border-danger/25 bg-danger-muted text-danger",
};

function EvidenceBadge({
  evidenceClass,
  className,
}: {
  evidenceClass: EvidenceClass;
  className?: string;
}) {
  const { label, icon: Icon, tone } = evidenceBadgeConfig[evidenceClass];
  return (
    <Badge
      variant="outline"
      className={cn("gap-1.5 border px-2.5 py-1", evidenceToneClasses[tone], className)}
    >
      <Icon aria-hidden="true" />
      {label}
    </Badge>
  );
}

function VerificationBadge({ state, className }: { state: VerificationState; className?: string }) {
  const verified = state === "verified";
  return (
    <Badge
      variant="outline"
      className={cn(
        "gap-1.5 border px-2.5 py-1",
        verified
          ? "border-success/25 bg-success-muted text-success"
          : "border-warning/30 bg-warning-muted text-warning-foreground",
        className,
      )}
    >
      {verified ? <ShieldCheck aria-hidden="true" /> : <CircleHelp aria-hidden="true" />}
      {verified ? "Verified" : "Unverified"}
    </Badge>
  );
}

function ProfileAvatar({ initials, className }: { initials: string; className?: string }) {
  return (
    <Avatar className={cn("ring-2 ring-background shadow-sm", className)}>
      <AvatarFallback>{initials}</AvatarFallback>
    </Avatar>
  );
}

function FoundationLabel({ children }: { children: ReactNode }) {
  return (
    <span className="inline-flex items-center gap-2 text-xs text-muted-foreground">
      <Activity aria-hidden="true" className="size-3.5 text-primary" />
      {children}
    </span>
  );
}

export {
  EmptyState,
  EvidenceBadge,
  FeatureCard,
  FoundationLabel,
  PageShell,
  PortalSwitcher,
  ProfileAvatar,
  SectionHeading,
  Separator,
  SiteFooter,
  SiteHeader,
  VerificationBadge,
};

export type { PortalLink };
