"use client";

import { MessageCircle, Send, Sparkles, X } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

import { cn } from "@healthspan/ui/utils";

import { previewSummary } from "../../lib/preview-data";
import { usePortalState } from "./portal-state";

type Tab = "people" | "ai";

/**
 * Quick chat dock (design specification, section 7). It never sends messages itself: the Chat
 * page owns conversations and permission checks. It stays quiet when Do Not Disturb is on.
 */
export function QuickChatDock() {
  const { status } = usePortalState();
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const [tab, setTab] = useState<Tab>("people");
  const unread = previewSummary.chatUnread;

  if (pathname.startsWith("/messages") || status === "Do Not Disturb") return null;

  return (
    <div className="fixed right-4 bottom-4 z-30 hidden sm:block">
      {open ? (
        <section
          aria-label="Quick chat"
          className="glass-strong flex h-96 w-80 flex-col overflow-hidden rounded-3xl"
        >
          <div className="flex items-center justify-between border-b border-border px-4 py-3">
            <div role="tablist" aria-label="Chat type" className="flex gap-1">
              {(["people", "ai"] as const).map((id) => (
                <button
                  key={id}
                  role="tab"
                  type="button"
                  aria-selected={tab === id}
                  onClick={() => setTab(id)}
                  className={cn(
                    "min-h-9 rounded-full px-3 text-xs font-semibold outline-none focus-visible:ring-[3px] focus-visible:ring-ring/30",
                    tab === id ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-accent",
                  )}
                >
                  {id === "people" ? "People" : "AI"}
                </button>
              ))}
            </div>
            <button
              type="button"
              aria-label="Close quick chat"
              onClick={() => setOpen(false)}
              className="grid size-9 place-items-center rounded-full text-muted-foreground outline-none hover:bg-accent focus-visible:ring-[3px] focus-visible:ring-ring/30"
            >
              <X aria-hidden="true" className="size-4" />
            </button>
          </div>
          <div role="tabpanel" className="flex flex-1 flex-col items-center justify-center gap-2 px-6 text-center">
            <span className="grid size-12 place-items-center rounded-2xl bg-accent text-accent-foreground">
              {tab === "people" ? <MessageCircle aria-hidden="true" /> : <Sparkles aria-hidden="true" />}
            </span>
            <p className="text-sm font-semibold">
              {tab === "people" ? "No recent conversations" : "Ask Healthspan AI"}
            </p>
            <p className="text-xs leading-relaxed text-muted-foreground">
              {tab === "people"
                ? "Recent chats with people will appear here."
                : "Open the full chat to talk with the AI assistant."}
            </p>
          </div>
          <div className="flex items-center gap-2 border-t border-border p-3">
            <Link
              href="/messages"
              className="inline-flex min-h-11 flex-1 items-center justify-center gap-2 rounded-full bg-primary px-4 text-sm font-medium text-primary-foreground outline-none focus-visible:ring-[3px] focus-visible:ring-ring/40"
            >
              <Send aria-hidden="true" className="size-4" />
              Open full chat
            </Link>
          </div>
        </section>
      ) : (
        <button
          type="button"
          onClick={() => setOpen(true)}
          aria-label={unread > 0 ? `Open quick chat, ${unread} unread` : "Open quick chat"}
          className="relative inline-flex min-h-12 items-center gap-2 rounded-full bg-primary px-5 text-sm font-semibold text-primary-foreground shadow-lg outline-none transition-transform hover:-translate-y-0.5 focus-visible:ring-[3px] focus-visible:ring-ring/40 motion-reduce:transform-none"
        >
          <MessageCircle aria-hidden="true" className="size-5" />
          Chat
          {unread > 0 && (
            <span className="absolute -top-1 -right-1 grid min-w-5 place-items-center rounded-full bg-danger px-1 text-[0.65rem] font-bold text-danger-foreground">
              {unread}
            </span>
          )}
        </button>
      )}
    </div>
  );
}
