"use client";

import {
  Bookmark,
  CheckCircle2,
  CircleUserRound,
  Heart,
  House,
  LockKeyhole,
  Settings2,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { useMemo, useState } from "react";

import { Alert, AlertDescription } from "@healthspan/ui/alert";
import { Badge } from "@healthspan/ui/badge";
import { Button } from "@healthspan/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@healthspan/ui/card";
import { Input } from "@healthspan/ui/input";
import { Label } from "@healthspan/ui/label";
import { Textarea } from "@healthspan/ui/textarea";
import {
  PageShell,
  ProfileAvatar,
  SectionHeading,
  Separator,
  SiteFooter,
  SiteHeader,
} from "@healthspan/ui/composites";
import { ThemeToggle } from "@healthspan/ui/theme-toggle";

const socialPortalUrl = process.env.PUBLIC_APP_URL ?? "http://localhost:3000";

const sections = [
  { label: "Overview", href: "#overview", icon: House },
  { label: "Your profile", href: "#profile", icon: CircleUserRound },
  { label: "Saved knowledge", href: "#saved", icon: Bookmark },
  { label: "Privacy settings", href: "#privacy", icon: Settings2 },
];

const initialProfile = {
  name: "Harper Stone",
  title: "Health & longevity enthusiast",
  location: "Seattle, WA",
  bio: "I am exploring sleep, mobility, and evidence-based healthy aging with a focus on sustainable routines.",
};

const initialSaved = [
  { title: "Sleep quality checklist", meta: "10 min read · Wellbeing", tag: "Personal" },
  { title: "Evidence summary: recovery trends", meta: "Research note · 2 attachments", tag: "Research" },
  { title: "Morning routine template", meta: "Saved from community · 1 review", tag: "Routine" },
];

const initialPrivacy = {
  profileVisible: true,
  communityActivityVisible: true,
  researchFollowupsAllowed: false,
  shareHealthPreferences: false,
  consentForDataReview: false,
};

export default function PersonalHome() {
  const [profile, setProfile] = useState(initialProfile);
  const [savedItems] = useState(initialSaved);
  const [privacy, setPrivacy] = useState(initialPrivacy);
  const [savedMessage, setSavedMessage] = useState("Profile changes are only stored in this browser session.");

  const consentCount = useMemo(
    () => Object.values(privacy).filter(Boolean).length,
    [privacy],
  );

  const togglePrivacy = (key: keyof typeof privacy) => {
    setPrivacy((current) => ({ ...current, [key]: !current[key] }));
  };

  const handleSaveProfile = () => {
    setSavedMessage("Profile saved locally for this session. Consent and data-sharing settings remain private by default.");
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <SiteHeader
        title="Your personal space"
        eyebrow="Personal Portal · Foundation"
        homeHref="#overview"
        links={sections}
        themeToggle={<ThemeToggle />}
        actions={
          <div className="flex items-center gap-2">
            <a
              href="/messages"
              className="inline-flex min-h-11 items-center rounded-full border border-border bg-card px-3 text-sm font-medium text-foreground transition-colors hover:bg-accent focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/30"
            >
              Messages
            </a>
            <a
              href={socialPortalUrl}
              className="hidden min-h-11 items-center gap-2 rounded-full border border-border bg-card px-4 text-sm font-medium text-foreground transition-colors hover:bg-accent focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/30 sm:inline-flex"
            >
              Community <Sparkles aria-hidden="true" className="size-4" />
            </a>
          </div>
        }
      />
      <main id="overview">
        <PageShell wide className="grid gap-8 xl:grid-cols-[15rem_minmax(0,1fr)]">
          <aside className="hidden xl:block">
            <nav
              aria-label="Personal portal sections"
              className="sticky top-24 grid gap-1 rounded-xl border border-border/70 bg-card/70 p-2 shadow-xs"
            >
              <p className="px-3 py-2 text-xs font-semibold tracking-[0.14em] text-muted-foreground uppercase">
                Your space
              </p>
              {sections.map(({ label, href, icon: Icon }, index) => (
                <a
                  key={label}
                  href={href}
                  aria-current={index === 0 ? "page" : undefined}
                  className={`flex min-h-11 items-center gap-3 rounded-lg px-3 text-sm transition-colors focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/30 ${
                    index === 0
                      ? "bg-accent text-accent-foreground"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  }`}
                >
                  <Icon aria-hidden="true" className="size-4" />
                  {label}
                </a>
              ))}
              <Separator className="my-2" />
              <p className="px-3 pb-2 text-xs leading-relaxed text-muted-foreground">
                Personal health information stays private by default.
              </p>
            </nav>
          </aside>

          <div className="min-w-0">
            <nav
              aria-label="Personal portal sections"
              className="mb-7 flex gap-2 overflow-x-auto pb-2 xl:hidden"
            >
              {sections.map(({ label, href, icon: Icon }) => (
                <a
                  key={label}
                  href={href}
                  className="inline-flex min-h-11 shrink-0 items-center gap-2 rounded-full border border-border bg-card px-4 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/30"
                >
                  <Icon aria-hidden="true" className="size-4" />
                  {label}
                </a>
              ))}
            </nav>

            <section aria-labelledby="welcome-heading" className="mb-7">
              <Badge variant="outline" className="mb-4 gap-1.5 bg-accent/70">
                <Heart aria-hidden="true" />A calmer space for your health journey
              </Badge>
              <h1
                id="welcome-heading"
                className="max-w-3xl font-display text-4xl leading-tight tracking-tight sm:text-5xl"
              >
                Your health story, on your terms.
              </h1>
              <p className="mt-3 max-w-2xl text-base leading-relaxed text-muted-foreground">
                This personal portal keeps the foundation for profile details, saved knowledge, and
                privacy controls ahead of full health-data integration.
              </p>
            </section>

            <Alert className="mb-7 flex items-start gap-3 border-success/25 bg-success-muted/60">
              <LockKeyhole aria-hidden="true" className="mt-0.5 size-5 shrink-0 text-success" />
              <AlertDescription className="pl-0 text-foreground">
                <strong className="font-semibold">Private by default.</strong> Consent settings and
                profile details are handled only inside the session until backend storage is enabled.
              </AlertDescription>
            </Alert>

            <section className="mb-8 grid gap-4 md:grid-cols-3">
              <Card className="border-primary/10 bg-gradient-to-br from-card to-accent/30">
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Profile priority</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-display">82%</p>
                  <p className="mt-2 text-sm text-muted-foreground">Personal completeness</p>
                </CardContent>
              </Card>
              <Card className="border-success/15 bg-success-muted/30">
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Privacy</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-display">{consentCount}/5</p>
                  <p className="mt-2 text-sm text-muted-foreground">Enabled consent checks</p>
                </CardContent>
              </Card>
              <Card className="border-secondary/20 bg-secondary/25">
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Saved items</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-display">{savedItems.length}</p>
                  <p className="mt-2 text-sm text-muted-foreground">Curated resources</p>
                </CardContent>
              </Card>
            </section>

            <section id="profile" aria-labelledby="profile-heading" className="mb-8 scroll-mt-24">
              <Card className="overflow-hidden border-primary/10 bg-gradient-to-br from-card to-accent/35 shadow-sm">
                <CardContent className="flex flex-col gap-5 py-5 sm:flex-row sm:items-center sm:justify-between sm:py-6">
                  <div className="flex items-center gap-4">
                    <ProfileAvatar initials="HS" className="size-14 text-base" />
                    <div className="min-w-0">
                      <div className="mb-1 flex flex-wrap items-center gap-2">
                        <h2 id="profile-heading" className="font-display text-xl">
                          Your profile
                        </h2>
                        <Badge variant="outline">Ready for review</Badge>
                      </div>
                      <p className="max-w-xl text-sm leading-relaxed text-muted-foreground">
                        {profile.title} · {profile.location}
                      </p>
                    </div>
                  </div>
                  <Button variant="outline" onClick={handleSaveProfile} className="shrink-0">
                    <Settings2 aria-hidden="true" />
                    Save profile
                  </Button>
                </CardContent>
                <CardContent className="space-y-5 border-t border-border/60 pt-5">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="grid gap-2">
                      <Label htmlFor="profile-name">Name</Label>
                      <Input
                        id="profile-name"
                        value={profile.name}
                        onChange={(event) => setProfile((current) => ({ ...current, name: event.target.value }))}
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="profile-title">Headline</Label>
                      <Input
                        id="profile-title"
                        value={profile.title}
                        onChange={(event) =>
                          setProfile((current) => ({ ...current, title: event.target.value }))
                        }
                      />
                    </div>
                    <div className="grid gap-2 md:col-span-2">
                      <Label htmlFor="profile-location">Location</Label>
                      <Input
                        id="profile-location"
                        value={profile.location}
                        onChange={(event) =>
                          setProfile((current) => ({ ...current, location: event.target.value }))
                        }
                      />
                    </div>
                    <div className="grid gap-2 md:col-span-2">
                      <Label htmlFor="profile-bio">Bio</Label>
                      <Textarea
                        id="profile-bio"
                        value={profile.bio}
                        onChange={(event) =>
                          setProfile((current) => ({ ...current, bio: event.target.value }))
                        }
                        className="min-h-24"
                      />
                    </div>
                  </div>
                  <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
                    <CheckCircle2 aria-hidden="true" className="size-4 text-success" />
                    {savedMessage}
                  </div>
                </CardContent>
              </Card>
            </section>

            <section id="saved" aria-labelledby="saved-heading" className="mb-8 scroll-mt-24">
              <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
                <SectionHeading
                  eyebrow="Your library"
                  title="Saved knowledge"
                  description="Curated resources and community notes that are ready for later review."
                />
                <Badge variant="outline">Local preview</Badge>
              </div>
              <div className="grid gap-4 md:grid-cols-3">
                {savedItems.map((item) => (
                  <Card key={item.title} className="h-full">
                    <CardHeader>
                      <div className="flex items-center justify-between gap-3">
                        <Badge variant="outline">{item.tag}</Badge>
                        <Bookmark aria-hidden="true" className="size-4 text-primary" />
                      </div>
                      <CardTitle className="pt-2 text-lg leading-snug">{item.title}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <CardDescription className="leading-relaxed">{item.meta}</CardDescription>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </section>

            <section
              id="privacy"
              aria-labelledby="privacy-heading"
              className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]"
            >
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between gap-3">
                    <span className="grid size-10 place-items-center rounded-xl bg-accent text-accent-foreground">
                      <LockKeyhole aria-hidden="true" className="size-5" />
                    </span>
                    <Badge variant="outline">Consent controls</Badge>
                  </div>
                  <CardTitle id="privacy-heading" className="pt-2 font-display text-xl">
                    Privacy settings
                  </CardTitle>
                  <CardDescription className="leading-relaxed">
                    Privacy and consent controls are foundation-level in this M2 milestone. They are
                    not yet connected to stored health records.
                  </CardDescription>
                </CardHeader>
                <CardContent className="grid gap-3">
                  {Object.entries({
                    profileVisible: "Make profile visible to trusted community members",
                    communityActivityVisible: "Share community activity in my profile",
                    researchFollowupsAllowed: "Allow follow-up invitations from verified researchers",
                    shareHealthPreferences: "Share health goals and interests with the network",
                    consentForDataReview: "Consent to a limited review of my data preferences",
                  }).map(([key, label]) => {
                    const enabled = privacy[key as keyof typeof privacy];
                    return (
                      <button
                        key={key}
                        type="button"
                        onClick={() => togglePrivacy(key as keyof typeof privacy)}
                        aria-pressed={enabled}
                        className={`flex w-full items-center justify-between gap-3 rounded-xl border p-3 text-left transition-colors ${
                          enabled
                            ? "border-success/35 bg-success-muted/45 text-foreground"
                            : "border-border bg-card text-muted-foreground hover:bg-accent/30"
                        }`}
                      >
                        <span className="flex-1 text-sm font-medium">{label}</span>
                        <span
                          className={`inline-flex min-w-20 items-center justify-center rounded-full px-2 py-1 text-xs font-semibold ${
                            enabled ? "bg-success text-success-foreground" : "bg-muted text-muted-foreground"
                          }`}
                        >
                          {enabled ? "Enabled" : "Disabled"}
                        </span>
                      </button>
                    );
                  })}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between gap-3">
                    <span className="grid size-10 place-items-center rounded-xl bg-secondary text-secondary-foreground">
                      <ShieldCheck aria-hidden="true" className="size-5" />
                    </span>
                    <Badge variant="outline">Audit summary</Badge>
                  </div>
                  <CardTitle className="pt-2 font-display text-xl">Privacy review</CardTitle>
                  <CardDescription className="leading-relaxed">
                    Access is still governed by explicit consent and no personal health records are
                    connected yet.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3 text-sm text-muted-foreground">
                  <div className="rounded-xl border border-border bg-surface-raised/50 p-3">
                    <p className="font-medium text-foreground">Consent checks active</p>
                    <p className="mt-1">{consentCount} of 5 active controls</p>
                  </div>
                  <div className="rounded-xl border border-border bg-surface-raised/50 p-3">
                    <p className="font-medium text-foreground">Storage mode</p>
                    <p className="mt-1">Session-local only until secure backend persistence is enabled</p>
                  </div>
                  <div className="rounded-xl border border-border bg-surface-raised/50 p-3">
                    <p className="font-medium text-foreground">Access boundary</p>
                    <p className="mt-1">Health data remains private by default, even if profile metadata is visible</p>
                  </div>
                </CardContent>
              </Card>
            </section>
          </div>
        </PageShell>
      </main>
      <SiteFooter note="Private by default · Consent-managed profile and privacy foundations for M2." />
    </div>
  );
}
