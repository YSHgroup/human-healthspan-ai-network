"use client";

import { CheckCircle2, Settings2 } from "lucide-react";

import { Button } from "@healthspan/ui/button";
import { Input } from "@healthspan/ui/input";
import { Label } from "@healthspan/ui/label";
import { Textarea } from "@healthspan/ui/textarea";
import { ProfileAvatar } from "@healthspan/ui/composites";

import { GlassSection, PageHeader } from "./page-header";
import { profileInitials, usePortalState, type Profile } from "./portal-state";
import { PersonBadge } from "./tier-chip";

const fields: { key: keyof Profile; id: string; label: string; wide?: boolean }[] = [
  { key: "name", id: "profile-name", label: "Name" },
  { key: "title", id: "profile-title", label: "Headline" },
  { key: "location", id: "profile-location", label: "Location", wide: true },
];

export function ProfilePage() {
  const { profile, setProfileField, savedMessage, saveProfile } = usePortalState();

  return (
    <>
      <PageHeader
        eyebrow="Me"
        title="Your profile"
        description="Details other members can see, depending on your privacy settings. Health information is never part of your profile."
      />
      <GlassSection label="Profile">
        <div className="-m-5 mb-5 h-28 rounded-t-3xl bg-gradient-to-br from-[color-mix(in_oklch,var(--primary)_50%,white)] via-[color-mix(in_oklch,var(--ring)_40%,white)] to-[color-mix(in_oklch,var(--secondary)_90%,white)]" aria-hidden="true" />
        <div className="-mt-14 mb-5 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div className="flex items-end gap-4">
            <ProfileAvatar initials={profileInitials(profile.name)} className="size-20 text-xl" />
            <div className="min-w-0 pb-1">
              <p className="font-display text-2xl leading-tight">{profile.name}</p>
              <p className="text-sm text-muted-foreground">
                {profile.title} · {profile.location}
              </p>
              <div className="mt-2">
                <PersonBadge>Ready for review</PersonBadge>
              </div>
            </div>
          </div>
          <Button variant="outline" onClick={saveProfile} className="shrink-0 rounded-full">
            <Settings2 aria-hidden="true" />
            Save profile
          </Button>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          {fields.map((field) => (
            <div key={field.id} className={`grid gap-2 ${field.wide ? "md:col-span-2" : ""}`}>
              <Label htmlFor={field.id}>{field.label}</Label>
              <Input
                id={field.id}
                value={profile[field.key]}
                onChange={(event) => setProfileField(field.key, event.target.value)}
              />
            </div>
          ))}
          <div className="grid gap-2 md:col-span-2">
            <Label htmlFor="profile-bio">Bio</Label>
            <Textarea
              id="profile-bio"
              value={profile.bio}
              onChange={(event) => setProfileField("bio", event.target.value)}
              className="min-h-24"
            />
          </div>
        </div>
        <p className="mt-5 flex items-center gap-2 text-sm text-muted-foreground" aria-live="polite">
          <CheckCircle2 aria-hidden="true" className="size-4 text-success" />
          {savedMessage}
        </p>
      </GlassSection>
    </>
  );
}
