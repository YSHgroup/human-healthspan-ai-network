"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  ArrowUpRight,
  Building2,
  FlaskConical,
  House,
  Microscope,
  Sparkles,
} from "lucide-react";
import { PORTALS, portalUrl } from "@healthspan/shared-config/portals";
import ApiStatus from "./ApiStatus";
import { buttonVariants } from "@healthspan/ui/button";
import { cn } from "@/lib/utils";
import MemberSessionControls from "./MemberSessionControls";

const navigation = [
  { href: "/research", label: "Projects", icon: FlaskConical },
  { href: "/science", label: "Science", icon: Microscope }
];

export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const active = (href: string) => pathname === href || pathname.startsWith(`${href}/`);

  return (
    <div className="min-h-screen bg-[radial-gradient(ellipse_at_55%_-20%,rgba(181,218,247,.3),transparent_48%),#f5f9fd]">
      <aside className="fixed inset-y-0 left-0 z-30 flex w-64 flex-col border-r border-[#e3ebf2] bg-[#fbfdff]/95 px-4 py-6 backdrop-blur-xl max-[820px]:sticky max-[820px]:top-0 max-[820px]:h-auto max-[820px]:w-full max-[820px]:border-r-0 max-[820px]:border-b max-[820px]:px-4 max-[820px]:py-2.5">
        <Link href="/home" className="app-shell-brand mb-7 flex items-center justify-start px-2 max-[820px]:mb-2" aria-label="Healthspan Network home">
          <Image src="/brand/logo.png" alt="Healthspan Network" width={1112} height={385} priority className="h-9 w-auto object-contain" />
        </Link>
        <p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-[.17em] text-[#91a4b3] max-[820px]:hidden">Researcher Workspace</p>
        <nav className="flex flex-col gap-1 max-[820px]:flex-row max-[820px]:overflow-x-auto" aria-label="Researcher Workspace navigation">
          {navigation.map((item) => (
            <Link
              aria-current={active(item.href) ? "page" : undefined}
              className={cn(
                buttonVariants({ variant: "ghost", size: "lg" }),
                "h-11 justify-start gap-3 rounded-xl px-3 text-[#708597] transition-all hover:bg-[#edf6fd] hover:text-[#1c6da8] max-[820px]:h-10 max-[820px]:w-auto max-[820px]:shrink-0",
                active(item.href) && "bg-[#e9f4fc] font-semibold text-[#1c6da8] hover:bg-[#e9f4fc] hover:text-[#1c6da8]"
              )}
              href={item.href}
              key={item.href}
            >
              <item.icon aria-hidden="true" className={cn("size-[17px]", active(item.href) ? "text-[#287fba]" : "text-[#8194a3]")} />
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="mt-auto space-y-4 max-[820px]:hidden">
          <div className="rounded-2xl border border-[#dce8f2] bg-gradient-to-br from-[#edf6fd] to-[#f8fbfe] p-3">
            <p className="mb-1 px-3 text-[10px] font-semibold uppercase tracking-[.17em] text-[#91a4b3]">Switch space</p>
            <a className="flex items-center justify-between rounded-lg px-3 py-2 text-sm text-[#637a8b] hover:bg-white hover:text-[#1c6da8]" href={portalUrl("social", "/home")}>{PORTALS.social.name}<ArrowUpRight aria-hidden="true" className="size-3.5" /></a>
            <a className="flex items-center justify-between rounded-lg px-3 py-2 text-sm text-[#637a8b] hover:bg-white hover:text-[#1c6da8]" href={portalUrl("personal", "/home")}>{PORTALS.personal.name}<ArrowUpRight aria-hidden="true" className="size-3.5" /></a>
          </div>
          <div className="border-t border-[#e3ebf2] px-2 pt-4">
            <ApiStatus />
            <p className="mt-2 text-[11px] text-[#94a5b2]">Early access · MVP</p>
          </div>
        </div>
      </aside>
      <main className="ml-64 min-h-screen max-[820px]:ml-0">
        <div className="sticky top-0 z-20 flex min-h-[4.25rem] items-center justify-between gap-4 border-b border-[#e3ebf2]/80 bg-[#f8fbfe]/85 px-5 text-sm text-[#8495a2] backdrop-blur-xl sm:px-8 lg:px-10">
          <div className="flex min-w-0 items-center gap-2">
            <span className="truncate font-medium text-[#526a7c]">Human Healthspan Network</span>
            <span aria-hidden="true" className="text-[#c0cdd7]">/</span>
            <span className="hidden shrink-0 text-[#94a5b2] sm:inline">{PORTALS.researcher.name}</span>
          </div>
          <MemberSessionControls />
        </div>
        <div className="mx-auto w-full max-w-[88rem] p-4 sm:p-7 lg:p-9 2xl:px-12">{children}</div>
      </main>
    </div>
  );
}
