"use client";

import { LockKeyhole, ShieldCheck } from "lucide-react";

import { Alert, AlertDescription } from "@healthspan/ui/alert";
import { Badge } from "@healthspan/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@healthspan/ui/card";
import { cn } from "@healthspan/ui/utils";

import { PageHeader } from "./page-header";
import { privacyLabels, usePortalState, type PrivacyKey } from "./portal-state";

export function PrivacyPage() {
  const { privacy, togglePrivacy, consentCount } = usePortalState();

  return (
    <>
      <PageHeader
        eyebrow="Account"
        title="Privacy and consent"
        description="You decide what is shared. Health data stays private by default."
      />
      <Alert className="glass mb-5 flex items-start gap-3 rounded-3xl border-success/25 bg-success-muted/60">
        <LockKeyhole aria-hidden="true" className="mt-0.5 size-5 shrink-0 text-success" />
        <AlertDescription className="pl-0 text-foreground">
          <strong className="font-semibold">Private by default.</strong> Consent settings and profile
          details are handled only inside the session until backend storage is enabled.
        </AlertDescription>
      </Alert>

      <div className="grid gap-5 2xl:grid-cols-[1.2fr_0.8fr]">
        <Card className="glass rounded-3xl border-0">
          <CardHeader>
            <div className="flex items-center justify-between gap-3">
              <span className="grid size-10 place-items-center rounded-xl bg-accent text-accent-foreground">
                <LockKeyhole aria-hidden="true" className="size-5" />
              </span>
              <Badge variant="outline">Consent controls</Badge>
            </div>
            <CardTitle className="pt-2 font-display text-xl">Privacy settings</CardTitle>
            <CardDescription className="leading-relaxed">
              Privacy and consent controls are foundation-level in this M2 milestone. They are not yet
              connected to stored health records.
            </CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3">
            {(Object.keys(privacyLabels) as PrivacyKey[]).map((key) => {
              const enabled = privacy[key];
              return (
                <button
                  key={key}
                  type="button"
                  onClick={() => togglePrivacy(key)}
                  aria-pressed={enabled}
                  className={cn(
                    "flex min-h-14 w-full items-center justify-between gap-3 rounded-2xl border p-3 text-left outline-none transition-colors focus-visible:ring-[3px] focus-visible:ring-ring/30",
                    enabled
                      ? "border-success/35 bg-success-muted/45 text-foreground"
                      : "border-border bg-card text-muted-foreground hover:bg-accent/30",
                  )}
                >
                  <span className="flex-1 text-sm font-medium">{privacyLabels[key]}</span>
                  <span
                    className={cn(
                      "inline-flex min-w-20 items-center justify-center rounded-full px-2 py-1 text-xs font-semibold",
                      enabled ? "bg-success text-success-foreground" : "bg-muted text-muted-foreground",
                    )}
                  >
                    {enabled ? "Enabled" : "Disabled"}
                  </span>
                </button>
              );
            })}
          </CardContent>
        </Card>

        <Card className="glass rounded-3xl border-0">
          <CardHeader>
            <div className="flex items-center justify-between gap-3">
              <span className="grid size-10 place-items-center rounded-xl bg-secondary text-secondary-foreground">
                <ShieldCheck aria-hidden="true" className="size-5" />
              </span>
              <Badge variant="outline">Audit summary</Badge>
            </div>
            <CardTitle className="pt-2 font-display text-xl">Privacy review</CardTitle>
            <CardDescription className="leading-relaxed">
              Access is still governed by explicit consent and no personal health records are connected
              yet.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-muted-foreground">
            {[
              ["Consent checks active", `${consentCount} of 5 active controls`],
              ["Storage mode", "Session-local only until secure backend persistence is enabled"],
              ["Access boundary", "Health data remains private by default, even if profile metadata is visible"],
            ].map(([title, body]) => (
              <div key={title} className="rounded-2xl border border-border bg-surface-raised/50 p-3">
                <p className="font-medium text-foreground">{title}</p>
                <p className="mt-1">{body}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </>
  );
}
