"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  FlaskConical,
  House,
  Microscope,
  Search,
  Sparkles,
  UsersRound,
} from "lucide-react";
import ApiStatus from "./ApiStatus";
import { buttonVariants } from "@healthspan/ui/button";
import { cn } from "@/lib/utils";
import MemberSessionControls from "./MemberSessionControls";

const navigation = [
  { href: "/home", label: "Home", icon: House },
  { href: "/discover", label: "Discover", icon: Search },
  { href: "/communities", label: "Communities", icon: UsersRound },
  { href: "/science", label: "Science", icon: Microscope },
  { href: "/research", label: "Research", icon: FlaskConical },
  { href: "/ai", label: "AI", icon: Sparkles },
];

export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-[radial-gradient(ellipse_at_55%_-20%,rgba(191,232,215,.27),transparent_48%),#f5f8f6]">
      <aside className="fixed inset-y-0 left-0 z-30 flex w-64 flex-col border-r border-[#e5ece8] bg-[#fbfdfc]/95 px-4 py-6 shadow-[8px_0_30px_rgba(27,65,57,.025)] backdrop-blur-xl max-[820px]:sticky max-[820px]:top-0 max-[820px]:h-auto max-[820px]:w-full max-[820px]:border-r-0 max-[820px]:border-b max-[820px]:px-4 max-[820px]:py-2.5">
        <Link href="/home" className="mb-7 flex items-center justify-start px-2 max-[820px]:mb-2" aria-label="Healthspan Network home">
          <Image
            src="/brand/logo.png"
            alt="Healthspan Network"
            width={1112}
            height={385}
            priority
            className="h-9 w-auto object-contain"
          />
        </Link>
        <p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-[.17em] text-[#9ba9a3] max-[820px]:hidden">Workspace</p>
        <nav className="flex flex-col gap-1 max-[820px]:flex-row max-[820px]:overflow-x-auto" aria-label="App navigation">
          {navigation.map((item) => (
            <Link
              aria-current={pathname === item.href || pathname.startsWith(`${item.href}/`) ? "page" : undefined}
              className={cn(
                buttonVariants({ variant: "ghost", size: "lg" }),
                "h-11 justify-start gap-3 rounded-xl px-3 text-[#71817a] transition-all hover:bg-[#eff6f2] hover:text-[#176b59] max-[820px]:h-10 max-[820px]:w-auto max-[820px]:shrink-0",
                (pathname === item.href || pathname.startsWith(`${item.href}/`)) && "bg-[#eaf5ef] font-semibold text-[#176b59] shadow-[inset_0_0_0_1px_rgba(22,107,89,.06)] hover:bg-[#eaf5ef] hover:text-[#176b59]"
              )}
              href={item.href}
              key={item.href}
            >
              <item.icon aria-hidden="true" className={cn("size-[17px]", (pathname === item.href || pathname.startsWith(`${item.href}/`)) ? "text-[#16866e]" : "text-[#81928b]")} />
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="mt-auto space-y-4 max-[820px]:hidden">
          <div className="rounded-2xl border border-[#dcece4] bg-gradient-to-br from-[#eef8f3] to-[#f8fbf8] p-4">
            <span className="mb-3 flex size-8 items-center justify-center rounded-xl bg-white text-[#16866e] shadow-sm">
              <Microscope aria-hidden="true" className="size-4" />
            </span>
            <p className="text-sm font-semibold text-[#33534a]">Curiosity meets evidence.</p>
            <p className="mt-1 text-xs leading-5 text-[#82918b]">A community for people moving health research forward.</p>
          </div>
          <div className="border-t border-[#e5ece8] px-2 pt-4">
            <ApiStatus />
            <p className="mt-2 text-[11px] text-[#9aa7a1]">Early access · MVP</p>
          </div>
        </div>
      </aside>
      <main className="ml-64 min-h-screen max-[820px]:ml-0">
        <div className="sticky top-0 z-20 flex min-h-[4.25rem] items-center justify-between gap-4 border-b border-[#e5ece8]/80 bg-[#f8fbf9]/85 px-5 text-sm text-[#84928c] backdrop-blur-xl sm:px-8 lg:px-10">
          <div className="flex min-w-0 items-center gap-2">
            <span className="truncate font-medium text-[#52655e]">Human Healthspan Network</span>
            <span aria-hidden="true" className="text-[#c0cbc5]">/</span>
            <span className="hidden shrink-0 text-[#9aa7a1] sm:inline">Member space</span>
          </div>
          <div className="flex min-w-0 items-center gap-3 sm:gap-5">
            <Link className="hidden shrink-0 rounded-lg px-2 py-1 font-medium text-[#63766e] transition-colors hover:bg-white hover:text-[#176b59] sm:inline-flex" href="/">About the network</Link>
            <MemberSessionControls />
          </div>
        </div>
        <div className="mx-auto w-full max-w-[88rem] p-4 sm:p-7 lg:p-9 2xl:px-12">{children}</div>
      </main>
    </div>
  );
}
