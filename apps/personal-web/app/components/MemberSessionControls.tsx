"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@healthspan/ui/button";
import { useSession } from "@/lib/session";

export default function MemberSessionControls() {
  const router = useRouter();
  const { user, status, error, refresh } = useSession();
  const [logoutError, setLogoutError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function signOut() {
    setBusy(true);
    setLogoutError(null);
    try {
      const response = await fetch("/api/auth/logout", { method: "POST" });
      const payload: unknown = await response.json();
      if (!response.ok) {
        const detail =
          typeof payload === "object" && payload !== null && "detail" in payload
            ? String(payload.detail)
            : "Unable to sign out.";
        throw new Error(detail);
      }
      await refresh();
      router.replace("/login");
      router.refresh();
    } catch (signOutError) {
      setLogoutError(signOutError instanceof Error ? signOutError.message : "Unable to sign out.");
    } finally {
      setBusy(false);
    }
  }

  if (status === "loading") return <span className="text-sm text-muted-foreground">Loading account…</span>;
  if (status === "unavailable") {
    return (
      <div className="flex items-center gap-2 text-sm text-destructive" role="status">
        <span title={error ?? undefined}>Account unavailable</span>
        <Button onClick={() => void refresh()} size="sm" type="button" variant="outline">Retry</Button>
      </div>
    );
  }
  if (!user || !user.id) {
    return (
      <div className="flex items-center gap-3">
        <Link className="text-sm font-medium text-primary hover:underline" href="/login">Sign in</Link>
        <Link className="text-sm font-medium text-primary hover:underline" href="/register">Join</Link>
      </div>
    );
  }

  return (
    <div className="flex flex-wrap items-center justify-end gap-3">
      <span className="max-w-40 truncate text-sm font-medium text-foreground">
        {user.profile?.display_name || user.email}
      </span>
      <Link className="text-sm font-medium text-primary hover:underline" href="/profile">Profile</Link>
      <Button disabled={busy} onClick={signOut} size="sm" type="button" variant="outline">
        {busy ? "Signing out…" : "Sign out"}
      </Button>
      {logoutError && <span className="w-full text-right text-xs text-destructive" role="alert">{logoutError}</span>}
    </div>
  );
}
