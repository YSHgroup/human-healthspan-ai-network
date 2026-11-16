"use client";

import { Bell, ChevronDown, Lock, Menu, Search } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useEffect, useRef, type FormEvent } from "react";

import { ThemeToggle } from "@healthspan/ui/theme-toggle";
import { toast } from "@healthspan/ui/sonner";
import { ProfileAvatar } from "@healthspan/ui/composites";
import { cn } from "@healthspan/ui/utils";

import { buildPortalMenus, type PortalUrls } from "../../lib/portal-nav";
import { previewSummary } from "../../lib/preview-data";
import { HoverMenu, menuItemClass } from "./menu";
import { usePortalState, profileInitials } from "./portal-state";
import { TierChip } from "./tier-chip";

const triggerBase =
  "inline-flex min-h-11 items-center gap-1.5 rounded-full px-4 text-sm font-medium outline-none transition-colors focus-visible:ring-[3px] focus-visible:ring-ring/30";

function SoonTag() {
  return (
    <span className="rounded-full bg-muted px-2 py-0.5 text-[0.65rem] font-semibold text-muted-foreground">
      Soon
    </span>
  );
}

export function TopBar({
  urls,
  apiBaseUrl,
  onOpenNav,
}: {
  urls: PortalUrls;
  apiBaseUrl: string;
  onOpenNav: () => void;
}) {
  const { profile, cardState, vipCard } = usePortalState();
  const searchRef = useRef<HTMLInputElement>(null);
  const menus = buildPortalMenus(urls);
  const unread = previewSummary.inboxUnread;

  // Shortcut: slash focuses search, unless the person is already typing somewhere.
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      const typing =
        target && (["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName) || target.isContentEditable);
      if (event.key === "/" && !typing && !event.metaKey && !event.ctrlKey) {
        event.preventDefault();
        searchRef.current?.focus();
      }
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, []);

  const onSearch = (event: FormEvent) => {
    event.preventDefault();
    toast("Search is coming with Milestone 4", {
      description: "It will cover people, communities, posts, events and favorites. Never health data.",
    });
  };

  const logOut = async () => {
    try {
      const response = await fetch(`${apiBaseUrl.replace(/\/$/, "")}/api/v1/user/auth/logout`, {
        method: "POST",
        credentials: "include",
      });
      if (!response.ok && response.status !== 401) throw new Error("Logout failed");
      toast.success("You are signed out.");
    } catch {
      toast.error("Could not sign out. Please try again.");
    }
  };

  const tier = cardState === "active" ? vipCard.tier : "Free";

  return (
    <header className="sticky top-0 z-40 border-b border-border/60 bg-background/80 backdrop-blur-xl">
      <div className="mx-auto flex min-h-[4.25rem] max-w-[100rem] items-center gap-2 px-3 sm:gap-3 sm:px-5">
        <button
          type="button"
          aria-label="Open navigation"
          onClick={onOpenNav}
          className="grid size-11 shrink-0 place-items-center rounded-full text-foreground outline-none hover:bg-accent focus-visible:ring-[3px] focus-visible:ring-ring/30 xl:hidden"
        >
          <Menu aria-hidden="true" className="size-5" />
        </button>

        <Link
          href="/"
          aria-label="Healthspan Network, personal portal home"
          className="flex min-h-11 shrink-0 items-center rounded-lg outline-none focus-visible:ring-[3px] focus-visible:ring-ring/30 xl:w-[17rem]"
        >
          <Image
            src="/brand/logo.png"
            alt=""
            width={1112}
            height={385}
            priority
            className="hidden h-10 w-auto sm:block"
          />
          <Image
            src="/brand/logo-symbol.png"
            alt=""
            width={274}
            height={338}
            priority
            className="h-9 w-auto sm:hidden"
          />
        </Link>

        <nav aria-label="Portals" className="hidden items-center gap-1 lg:flex">
          {menus.map((menu) => {
            const current = menu.id === "personal";
            return (
              <HoverMenu
                key={menu.id}
                label={`${menu.label} portal menu`}
                triggerClassName={cn(
                  triggerBase,
                  current
                    ? "bg-card text-foreground shadow-xs ring-1 ring-primary/25"
                    : "text-muted-foreground hover:bg-accent hover:text-foreground",
                )}
                trigger={
                  <>
                    {menu.label}
                    {menu.locked && <Lock aria-hidden="true" className="size-3.5" />}
                    <ChevronDown aria-hidden="true" className="size-3.5" />
                  </>
                }
                panelClassName="w-64"
              >
                {(close) => (
                  <>
                    {menu.locked && (
                      <p className="mb-1 flex items-start gap-2 rounded-xl bg-warning-muted/70 px-3 py-2 text-xs leading-relaxed text-warning-foreground">
                        <Lock aria-hidden="true" className="mt-0.5 size-3.5 shrink-0" />
                        Researcher access needs approval. Apply for access from the Overview page.
                      </p>
                    )}
                    {menu.links.map((link) =>
                      link.href && !link.soon ? (
                        link.external ? (
                          <a key={link.label} href={link.href} className={menuItemClass} onClick={close}>
                            {link.label}
                          </a>
                        ) : (
                          <Link key={link.label} href={link.href} className={menuItemClass} onClick={close}>
                            {link.label}
                          </Link>
                        )
                      ) : (
                        <span
                          key={link.label}
                          aria-disabled="true"
                          className={cn(menuItemClass, "cursor-default text-muted-foreground hover:bg-transparent")}
                        >
                          {link.label}
                          <SoonTag />
                        </span>
                      ),
                    )}
                  </>
                )}
              </HoverMenu>
            );
          })}
        </nav>

        <form role="search" onSubmit={onSearch} className="relative mx-auto hidden min-w-0 max-w-xl flex-1 md:block">
          <Search
            aria-hidden="true"
            className="pointer-events-none absolute top-1/2 left-4 size-4 -translate-y-1/2 text-muted-foreground"
          />
          <input
            ref={searchRef}
            type="search"
            aria-label="Search people, communities, posts, events and favorites"
            placeholder="Search people, communities, topics…  ( / )"
            className="glass min-h-11 w-full rounded-full pr-4 pl-11 text-sm text-foreground outline-none placeholder:text-muted-foreground focus-visible:ring-[3px] focus-visible:ring-ring/30"
          />
        </form>

        <div className="ml-auto flex items-center gap-1.5 sm:gap-2 md:ml-0">
          <button
            type="button"
            aria-label="Search"
            onClick={() => searchRef.current?.focus()}
            className="grid size-11 place-items-center rounded-full outline-none hover:bg-accent focus-visible:ring-[3px] focus-visible:ring-ring/30 md:hidden"
          >
            <Search aria-hidden="true" className="size-5" />
          </button>
          <ThemeToggle />
          <HoverMenu
            hover={false}
            align="right"
            label={unread > 0 ? `Inbox, ${unread} unread` : "Inbox, no unread items"}
            triggerClassName="relative grid size-11 place-items-center rounded-full border border-border bg-card shadow-xs outline-none hover:bg-accent focus-visible:ring-[3px] focus-visible:ring-ring/30"
            trigger={
              <>
                <Bell aria-hidden="true" className="size-5" />
                {unread > 0 && (
                  <span className="absolute -top-1 -right-1 grid min-w-5 place-items-center rounded-full bg-danger px-1 text-[0.65rem] font-bold text-danger-foreground">
                    {unread}
                  </span>
                )}
              </>
            }
            panelClassName="w-72"
          >
            {() => (
              <div className="px-3 py-4 text-sm">
                <p className="font-semibold">You are all caught up</p>
                <p className="mt-1 text-muted-foreground">
                  Notifications and requests will appear here. The full Inbox page is on its way.
                </p>
              </div>
            )}
          </HoverMenu>
          <HoverMenu
            hover={false}
            align="right"
            label="Account menu"
            triggerClassName="flex min-h-11 items-center gap-1 rounded-full outline-none focus-visible:ring-[3px] focus-visible:ring-ring/30"
            trigger={
              <>
                <ProfileAvatar initials={profileInitials(profile.name)} className="size-10" />
                <ChevronDown aria-hidden="true" className="hidden size-3.5 text-muted-foreground sm:block" />
              </>
            }
            panelClassName="w-64"
          >
            {(close) => (
              <>
                <div className="flex items-center gap-3 px-3 py-2">
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold">{profile.name}</p>
                    <TierChip tier={tier} className="mt-1" />
                  </div>
                </div>
                <div className="my-1 h-px bg-border" />
                <Link href="/profile" className={menuItemClass} onClick={close}>
                  Profile
                </Link>
                {["Events", "Groups"].map((label) => (
                  <span key={label} aria-disabled="true" className={cn(menuItemClass, "cursor-default text-muted-foreground hover:bg-transparent")}>
                    {label}
                    <SoonTag />
                  </span>
                ))}
                <Link href="/favorites" className={menuItemClass} onClick={close}>
                  Favorites
                </Link>
                {["VIP Club", "Settings"].map((label) => (
                  <span key={label} aria-disabled="true" className={cn(menuItemClass, "cursor-default text-muted-foreground hover:bg-transparent")}>
                    {label}
                    <SoonTag />
                  </span>
                ))}
                <span className={cn(menuItemClass, "cursor-default justify-between")}>
                  Language
                  <span className="text-xs text-muted-foreground">English</span>
                </span>
                <div className="my-1 h-px bg-border" />
                <button
                  type="button"
                  className={menuItemClass}
                  onClick={() => {
                    close();
                    void logOut();
                  }}
                >
                  Log out
                </button>
              </>
            )}
          </HoverMenu>
        </div>
      </div>
    </header>
  );
}
