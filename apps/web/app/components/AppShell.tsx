import Image from "next/image";
import Link from "next/link";
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

const navigation = [
  { href: "/home", label: "Home", icon: House },
  { href: "/discover", label: "Discover", icon: Search },
  { href: "/communities", label: "Communities", icon: UsersRound },
  { href: "/science", label: "Science", icon: Microscope },
  { href: "/research", label: "Research", icon: FlaskConical },
  { href: "/ai", label: "AI", icon: Sparkles },
];

export default function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-muted/40">
      <aside className="fixed inset-y-0 left-0 z-10 flex w-60 flex-col border-r bg-background px-4 py-6 max-[820px]:static max-[820px]:h-auto max-[820px]:w-full max-[820px]:border-r-0 max-[820px]:border-b max-[820px]:py-3">
        <Link href="/home" className="mb-6 flex justify-center px-2" aria-label="Healthspan Network home">
          <Image
            src="/brand/logo.png"
            alt="Healthspan Network"
            width={1112}
            height={385}
            priority
            className="h-10 w-auto object-contain"
          />
        </Link>
        <nav className="flex flex-col gap-1 max-[820px]:flex-row max-[820px]:overflow-x-auto" aria-label="App navigation">
          {navigation.map((item) => (
            <Link
              className={cn(
                buttonVariants({ variant: "ghost", size: "lg" }),
                "h-11 justify-start gap-3 px-3 text-muted-foreground hover:text-primary max-[820px]:w-auto max-[820px]:shrink-0"
              )}
              href={item.href}
              key={item.href}
            >
              <item.icon aria-hidden="true" className="size-4 text-primary" />
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="mt-auto space-y-3 border-t px-2 pt-4 max-[820px]:hidden">
          <ApiStatus />
          <p className="text-xs text-muted-foreground">Early access · MVP</p>
        </div>
      </aside>
      <main className="ml-60 min-h-screen max-[820px]:ml-0">
        <div className="flex min-h-16 items-center justify-between gap-4 border-b bg-background/90 px-6 text-sm text-muted-foreground backdrop-blur sm:px-10">
          <span className="truncate">Human Healthspan AI Scientific Network</span>
          <Link className="shrink-0 font-medium text-primary hover:underline" href="/">About the network</Link>
        </div>
        <div className="mx-auto w-full max-w-5xl p-4 sm:p-8 lg:p-10">{children}</div>
      </main>
    </div>
  );
}
