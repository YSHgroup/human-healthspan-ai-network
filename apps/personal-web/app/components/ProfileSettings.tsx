"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@healthspan/ui/button";
import { Input } from "@healthspan/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import PageHeader from "@/app/components/PageHeader";
import { useSession, type MemberProfile, type MemberUser } from "@/lib/session";

function listText(values: string[] | undefined): string {
  return values?.join(", ") ?? "";
}

function parseList(value: string): string[] {
  return [...new Set(value.split(",").map((item) => item.trim()).filter(Boolean))];
}

function detailsFrom(payload: unknown): string {
  return typeof payload === "object" && payload !== null && "detail" in payload
    ? String(payload.detail)
    : "Unable to save profile changes.";
}

export default function ProfileSettings() {
  const router = useRouter();
  const { user, status, error, setUser } = useSession();
  const profile = user?.profile;
  const [displayName, setDisplayName] = useState("");
  const [bio, setBio] = useState("");
  const [location, setLocation] = useState("");
  const [timezone, setTimezone] = useState("");
  const [interests, setInterests] = useState("");
  const [topics, setTopics] = useState("");
  const [expertise, setExpertise] = useState("");
  const [researcherIdentifier, setResearcherIdentifier] = useState("");
  const [organization, setOrganization] = useState("");
  const [isPublic, setIsPublic] = useState(true);
  const [notice, setNotice] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [changingPassword, setChangingPassword] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!profile) return;
    setDisplayName(profile.display_name);
    setBio(profile.bio ?? "");
    setLocation(profile.location ?? "");
    setTimezone(profile.timezone ?? "");
    setInterests(listText(profile.interests));
    setTopics(listText(profile.topics));
    setExpertise(listText(profile.expertise));
    setResearcherIdentifier(profile.researcher_identifier ?? "");
    setOrganization(profile.organization_affiliation ?? "");
    setIsPublic(profile.is_public);
  }, [profile]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setNotice(null);
    setSaveError(null);
    const updatedProfile: Partial<MemberProfile> = {
      display_name: displayName,
      bio: bio || null,
      location: location || null,
      timezone: timezone || null,
      interests: parseList(interests),
      topics: parseList(topics),
      expertise: parseList(expertise),
      researcher_identifier: researcherIdentifier || null,
      organization_affiliation: organization || null,
      is_public: isPublic,
    };
    try {
      const response = await fetch("/api/backend/api/v1/me", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updatedProfile),
      });
      const payload: unknown = await response.json();
      if (!response.ok) throw new Error(detailsFrom(payload));
      setUser(payload as MemberUser);
      setNotice("Your profile has been saved.");
    } catch (saveFailure) {
      setSaveError(saveFailure instanceof Error ? saveFailure.message : "Unable to save profile changes.");
    } finally {
      setBusy(false);
    }
  }

  async function handlePasswordChange(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setChangingPassword(true);
    setPasswordError(null);
    try {
      const response = await fetch("/api/auth/password-change", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
        }),
      });
      const payload: unknown = await response.json();
      if (!response.ok) throw new Error(detailsFrom(payload));
      router.replace("/login?passwordChanged=1");
    } catch (failure) {
      setPasswordError(failure instanceof Error ? failure.message : "Unable to change your password.");
    } finally {
      setChangingPassword(false);
    }
  }

  if (status === "loading") return <p className="text-sm text-muted-foreground">Loading your account…</p>;
  if (status === "unavailable") return <p className="text-sm text-destructive" role="alert">{error ?? "Account service unavailable."}</p>;
  if (!user) {
    return (
      <Card>
        <CardContent className="space-y-3 p-6">
          <p>Sign in to manage your member profile.</p>
          <Link className="text-primary hover:underline" href="/login">Sign in</Link>
        </CardContent>
      </Card>
    );
  }
  if (!profile) return <p className="text-sm text-destructive" role="alert">Your account does not have a profile. Contact support.</p>;

  return (
    <>
      <PageHeader eyebrow="Account" title="Your profile" description="Manage the information associated with your Healthspan Network account." />
      <Card className="rounded-2xl shadow-sm">
        <CardHeader><CardTitle>Member profile</CardTitle></CardHeader>
        <CardContent>
          <form className="space-y-5" onSubmit={handleSubmit}>
            <label className="block space-y-2 text-sm font-medium" htmlFor="profile-display-name">
              Display name
              <Input id="profile-display-name" maxLength={120} onChange={(event) => setDisplayName(event.target.value)} required value={displayName} />
            </label>
            <label className="block space-y-2 text-sm font-medium" htmlFor="profile-bio">
              Biography
              <Textarea id="profile-bio" maxLength={1000} onChange={(event) => setBio(event.target.value)} rows={4} value={bio} />
            </label>
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="block space-y-2 text-sm font-medium" htmlFor="profile-location">
                Location
                <Input id="profile-location" maxLength={160} onChange={(event) => setLocation(event.target.value)} value={location} />
              </label>
              <label className="block space-y-2 text-sm font-medium" htmlFor="profile-timezone">
                Time zone
                <Input id="profile-timezone" maxLength={100} onChange={(event) => setTimezone(event.target.value)} placeholder="e.g. Europe/London" value={timezone} />
              </label>
            </div>
            <label className="block space-y-2 text-sm font-medium" htmlFor="profile-interests">
              Interests <span className="font-normal text-muted-foreground">(comma-separated)</span>
              <Input id="profile-interests" onChange={(event) => setInterests(event.target.value)} value={interests} />
            </label>
            <label className="block space-y-2 text-sm font-medium" htmlFor="profile-topics">
              Topics <span className="font-normal text-muted-foreground">(comma-separated)</span>
              <Input id="profile-topics" onChange={(event) => setTopics(event.target.value)} value={topics} />
            </label>
            <label className="block space-y-2 text-sm font-medium" htmlFor="profile-expertise">
              Expertise <span className="font-normal text-muted-foreground">(comma-separated)</span>
              <Input id="profile-expertise" onChange={(event) => setExpertise(event.target.value)} value={expertise} />
            </label>
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="block space-y-2 text-sm font-medium" htmlFor="profile-researcher-id">
                Researcher identifier
                <Input id="profile-researcher-id" maxLength={100} onChange={(event) => setResearcherIdentifier(event.target.value)} placeholder="e.g. ORCID" value={researcherIdentifier} />
              </label>
              <label className="block space-y-2 text-sm font-medium" htmlFor="profile-organization">
                Organization affiliation
                <Input id="profile-organization" maxLength={200} onChange={(event) => setOrganization(event.target.value)} value={organization} />
              </label>
            </div>
            <label className="flex items-start gap-3 text-sm">
              <input checked={isPublic} className="mt-1 size-4 accent-primary" onChange={(event) => setIsPublic(event.target.checked)} type="checkbox" />
              <span><span className="font-medium">Public profile</span><span className="mt-1 block text-muted-foreground">When enabled, your profile details can be shown to other members. Turn this off to keep your profile private.</span></span>
            </label>
            {notice && <p className="text-sm text-green-700" role="status">{notice}</p>}
            {saveError && <p className="text-sm text-destructive" role="alert">{saveError}</p>}
            <Button disabled={busy} type="submit">{busy ? "Saving…" : "Save profile"}</Button>
          </form>
        </CardContent>
      </Card>
      <Card className="mt-6 rounded-2xl shadow-sm">
        <CardHeader><CardTitle>Change password</CardTitle></CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={handlePasswordChange}>
            <label className="block space-y-2 text-sm font-medium" htmlFor="current-password">
              Current password
              <Input autoComplete="current-password" id="current-password" onChange={(event) => setCurrentPassword(event.target.value)} required type="password" value={currentPassword} />
            </label>
            <label className="block space-y-2 text-sm font-medium" htmlFor="new-password">
              New password
              <Input autoComplete="new-password" id="new-password" minLength={12} onChange={(event) => setNewPassword(event.target.value)} required type="password" value={newPassword} />
              <span className="block text-xs font-normal text-muted-foreground">Use at least 12 characters. Changing your password signs out all active sessions.</span>
            </label>
            {passwordError && <p className="text-sm text-destructive" role="alert">{passwordError}</p>}
            <Button disabled={changingPassword} type="submit">{changingPassword ? "Changing…" : "Change password"}</Button>
          </form>
        </CardContent>
      </Card>
    </>
  );
}
