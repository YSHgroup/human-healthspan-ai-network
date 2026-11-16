"use client";

import { Menu as MenuIcon } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, type ReactNode } from "react";

import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@healthspan/ui/sheet";
import { cn } from "@healthspan/ui/utils";

import { mobileTabs, type PortalUrls } from "../../lib/portal-nav";
import { LeftSidebar } from "./left-sidebar";
import { PortalStateProvider } from "./portal-state";
import { QuickChatDock } from "./quick-chat-dock";
import { RightSidebar } from "./right-sidebar";
import { TopBar } from "./top-bar";

/**
 * One shell for every personal-portal page (design specification, section 3):
 * top bar, 280 px left sidebar, fluid content, 320 px right sidebar, quick chat dock.
 *
 *  - 1280 px and up: three columns.
 *  - 1024 to 1279 px: left sidebar and content; rewards sit under the content.
 *  - Below 1024 px: content only, the left sidebar is a drawer, the rewards panel a second one.
 *  - Below 640 px: bottom tab bar replaces the chat dock.
 */
export function PortalShell({
  urls,
  apiBaseUrl,
  children,
}: {
  urls: PortalUrls;
  apiBaseUrl: string;
  children: ReactNode;
}) {
  const [navOpen, setNavOpen] = useState(false);
  const [rewardsOpen, setRewardsOpen] = useState(false);
  const pathname = usePathname();

  return (
    <PortalStateProvider>
      <a
        href="#portal-content"
        className="sr-only rounded-full bg-card px-4 py-2 text-sm focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-50"
      >
        Skip to content
      </a>
      <TopBar urls={urls} apiBaseUrl={apiBaseUrl} onOpenNav={() => setNavOpen(true)} />

      <div className="mx-auto grid max-w-[100rem] gap-5 px-3 pt-5 pb-28 sm:px-5 sm:pb-10 xl:grid-cols-[17.5rem_minmax(0,1fr)_20rem]">
        <aside
          aria-label="Profile and navigation"
          className="portal-scroll sticky top-[5.25rem] hidden max-h-[calc(100dvh-6rem)] self-start overflow-y-auto xl:block"
        >
          <LeftSidebar />
        </aside>

        <main id="portal-content" className="min-w-0">
          {children}
          {/* Between 1024 and 1279 px the right sidebar becomes a panel under the content. */}
          <section aria-label="Rewards" className="mt-6 hidden gap-4 lg:grid xl:hidden">
            <h2 className="font-display text-2xl">Rewards</h2>
            <div className="grid gap-4 md:grid-cols-2">
              <RightSidebar socialUrl={urls.social} />
            </div>
          </section>
        </main>

        <aside
          aria-label="Plan, referral and rewards"
          className="portal-scroll sticky top-[5.25rem] hidden max-h-[calc(100dvh-6rem)] self-start overflow-y-auto xl:block"
        >
          <RightSidebar socialUrl={urls.social} />
        </aside>
      </div>

      {/* Floating Rewards button below 1280 px opens the rewards panel as a drawer. */}
      <button
        type="button"
        onClick={() => setRewardsOpen(true)}
        className="glass-strong fixed right-4 bottom-20 z-30 inline-flex min-h-11 items-center gap-2 rounded-full px-4 text-sm font-semibold text-primary outline-none focus-visible:ring-[3px] focus-visible:ring-ring/30 sm:bottom-4 lg:hidden"
      >
        Rewards
      </button>

      <Sheet open={navOpen} onOpenChange={setNavOpen}>
        <SheetContent side="left" className="portal-scroll w-[min(20rem,calc(100%-2rem))] p-4">
          <SheetHeader>
            <SheetTitle>Personal portal</SheetTitle>
          </SheetHeader>
          <LeftSidebar onNavigate={() => setNavOpen(false)} />
        </SheetContent>
      </Sheet>

      <Sheet open={rewardsOpen} onOpenChange={setRewardsOpen}>
        <SheetContent side="right" className="portal-scroll p-4">
          <SheetHeader>
            <SheetTitle>Rewards</SheetTitle>
          </SheetHeader>
          <RightSidebar socialUrl={urls.social} />
        </SheetContent>
      </Sheet>

      <QuickChatDock />

      <nav
        aria-label="Quick pages"
        className="glass-strong fixed inset-x-0 bottom-0 z-30 grid grid-cols-5 rounded-t-3xl px-2 pt-1 pb-[max(0.5rem,env(safe-area-inset-bottom))] sm:hidden"
      >
        {mobileTabs.map(({ label, href, icon: Icon }) => {
          const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <Link
              key={label}
              href={href}
              aria-current={active ? "page" : undefined}
              className={cn(
                "flex min-h-14 flex-col items-center justify-center gap-0.5 rounded-xl text-[0.7rem] outline-none focus-visible:ring-[3px] focus-visible:ring-ring/30",
                active ? "font-semibold text-primary" : "text-muted-foreground",
              )}
            >
              <Icon aria-hidden="true" className="size-5" />
              {label}
            </Link>
          );
        })}
        <button
          type="button"
          onClick={() => setNavOpen(true)}
          className="flex min-h-14 flex-col items-center justify-center gap-0.5 rounded-xl text-[0.7rem] text-muted-foreground outline-none focus-visible:ring-[3px] focus-visible:ring-ring/30"
        >
          <MenuIcon aria-hidden="true" className="size-5" />
          Menu
        </button>
      </nav>
    </PortalStateProvider>
  );
}
