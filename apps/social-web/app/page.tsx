import Image from "next/image";
import {
  ArrowDown,
  ArrowRight,
  ArrowUpRight,
  Brain,
  Dna,
  FlaskConical,
  HeartPulse,
  LockKeyhole,
  Microscope,
  Moon,
  Network,
  ShieldCheck,
  Sparkles,
  UsersRound,
  type LucideIcon,
} from "lucide-react";

import { Badge } from "@healthspan/ui/badge";
import { Button } from "@healthspan/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@healthspan/ui/card";
import {
  EmptyState,
  EvidenceBadge,
  FeatureCard,
  PageShell,
  PortalSwitcher,
  SectionHeading,
  SiteFooter,
  SiteHeader,
} from "@healthspan/ui/composites";
import { Reveal, StatCard } from "@healthspan/ui/motion";
import { ThemeToggle } from "@healthspan/ui/theme-toggle";

const socialPortalUrl = process.env.PUBLIC_APP_URL ?? "http://localhost:3000";
const personalPortalUrl = process.env.PERSONAL_APP_URL ?? "http://localhost:3001";
const researcherPortalUrl = process.env.RESEARCHER_APP_URL ?? "http://localhost:3002";

const navigation = [
  { label: "The network", href: "#network" },
  { label: "How it works", href: "#journey" },
  { label: "Principles", href: "#principles" },
];

const audiences: { title: string; description: string; icon: LucideIcon }[] = [
  {
    title: "People",
    description: "Bring questions, experience, and curiosity to a thoughtful community.",
    icon: UsersRound,
  },
  {
    title: "Researchers",
    description: "Find collaborators and make research context easier to follow.",
    icon: Microscope,
  },
  {
    title: "Health professionals",
    description: "Contribute professional perspectives with clear verification boundaries.",
    icon: HeartPulse,
  },
  {
    title: "Scientists and builders",
    description: "Connect disciplines while keeping methods and evidence visible.",
    icon: FlaskConical,
  },
];

const journey = [
  { label: "Ask", detail: "Start with a useful question.", icon: Sparkles },
  { label: "Discuss", detail: "Bring different perspectives together.", icon: UsersRound },
  { label: "Explore", detail: "Look at sources and uncertainty.", icon: Microscope },
  { label: "Collaborate", detail: "Find the right people and context.", icon: Network },
];

const principles = [
  {
    title: "Evidence over popularity",
    description: "Engagement and scientific support are different things.",
    icon: FlaskConical,
  },
  {
    title: "Privacy by default",
    description: "Personal health information stays private unless people choose otherwise.",
    icon: LockKeyhole,
  },
  {
    title: "Clear provenance",
    description: "Sources and evidence classes should be visible in context.",
    icon: Dna,
  },
  {
    title: "Responsible AI",
    description: "AI-generated ideas are hypotheses, not validated findings.",
    icon: ShieldCheck,
  },
];

const focusAreas = [
  { label: "Health & aging", icon: HeartPulse },
  { label: "Sleep", icon: Moon },
  { label: "Brain & cognition", icon: Brain },
  { label: "Research", icon: Microscope },
];

export default function Home() {
  return (
    <div id="top" className="min-h-screen bg-background text-foreground">
      <a
        href="#main-content"
        className="sr-only z-50 rounded-md bg-card px-4 py-3 text-foreground focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus-visible:ring-[3px] focus-visible:ring-ring/40"
      >
        Skip to content
      </a>
      <SiteHeader
        eyebrow="People · Science · Possibility"
        title="Healthspan Network"
        homeHref="#top"
        brand={
          <Image
            src="/brand/logo.png"
            alt="Healthspan Network"
            width={1112}
            height={385}
            priority
            className="h-auto w-36 sm:w-40"
          />
        }
        links={navigation}
        themeToggle={<ThemeToggle />}
        actions={
          <a
            href="#portals"
            className="hidden min-h-11 items-center gap-2 rounded-full bg-primary px-4 text-sm font-medium text-primary-foreground shadow-sm transition hover:-translate-y-0.5 hover:shadow-md focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/40 sm:inline-flex"
          >
            Find your space <ArrowUpRight aria-hidden="true" className="size-4" />
          </a>
        }
      />

      <main id="main-content">
        <section className="hero-surface relative isolate overflow-hidden text-primary-foreground">
          <div className="hero-orb hero-orb-one" aria-hidden="true" />
          <div className="hero-orb hero-orb-two" aria-hidden="true" />
          <PageShell className="relative grid min-h-[min(44rem,calc(100dvh-4.5rem))] items-center gap-10 py-14 sm:py-20 lg:grid-cols-[1.05fr_0.95fr] lg:gap-8 lg:py-24">
            <Reveal className="relative z-10 max-w-2xl">
              <Badge className="mb-6 gap-2 border-primary-foreground/25 bg-primary-foreground/10 text-primary-foreground">
                <span className="size-2 rounded-full bg-success" aria-hidden="true" />A place for
                better questions
              </Badge>
              <h1 className="max-w-3xl font-display text-5xl leading-[1.02] tracking-tight sm:text-6xl lg:text-7xl">
                Human healthspan,
                <span className="mt-1 block text-primary/80">built together.</span>
              </h1>
              <p className="mt-6 max-w-xl text-base leading-relaxed text-primary-foreground/80 sm:text-lg">
                A connected space for people and scientific communities to explore questions,
                perspectives, and evidence with care.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Button
                  render={<a href="#network" />}
                  size="lg"
                  className="bg-card text-foreground hover:bg-card/90"
                >
                  Explore the network <ArrowRight aria-hidden="true" />
                </Button>
                <Button
                  render={<a href="#journey" />}
                  variant="outline"
                  size="lg"
                  className="border-primary-foreground/30 bg-transparent text-primary-foreground hover:bg-primary-foreground/10"
                >
                  How it works <ArrowDown aria-hidden="true" />
                </Button>
              </div>
              <div className="mt-8 flex flex-wrap gap-x-5 gap-y-2 text-sm text-primary-foreground/75">
                <span className="inline-flex items-center gap-2">
                  <ShieldCheck aria-hidden="true" className="size-4 text-success" />
                  Privacy-aware
                </span>
                <span className="inline-flex items-center gap-2">
                  <Microscope aria-hidden="true" className="size-4 text-primary/80" />
                  Evidence-conscious
                </span>
              </div>
            </Reveal>

            <Reveal
              delay={0.08}
              className="relative mx-auto grid w-full max-w-[34rem] place-items-center"
            >
              <div className="hero-art relative grid aspect-square w-full place-items-center rounded-[2rem] border border-primary-foreground/15 bg-primary-foreground/[0.045] shadow-glow">
                <div className="hero-ring hero-ring-one" aria-hidden="true" />
                <div className="hero-ring hero-ring-two" aria-hidden="true" />
                <div className="hero-ring hero-ring-three" aria-hidden="true" />
                <div className="relative z-10 grid size-32 place-items-center rounded-[2rem] border border-primary-foreground/20 bg-primary-foreground/10 p-4 shadow-lg backdrop-blur sm:size-40">
                  <Image
                    src="/brand/mark.png"
                    alt=""
                    width={371}
                    height={371}
                    priority
                    className="size-full object-contain"
                  />
                </div>
                {[
                  { icon: UsersRound, label: "People", position: "art-node-one" },
                  { icon: Microscope, label: "Research", position: "art-node-two" },
                  { icon: Sparkles, label: "Ideas", position: "art-node-three" },
                  { icon: HeartPulse, label: "Health", position: "art-node-four" },
                ].map(({ icon: Icon, label, position }) => (
                  <span key={label} className={`hero-node ${position}`} aria-label={label}>
                    <Icon aria-hidden="true" className="size-5" />
                  </span>
                ))}
                <div className="hero-caption absolute right-3 bottom-4 left-3 mx-auto flex max-w-sm items-center gap-3 rounded-xl border border-primary-foreground/15 bg-background/90 p-3 text-foreground shadow-md backdrop-blur sm:right-6 sm:bottom-6 sm:left-6">
                  <span className="grid size-10 shrink-0 place-items-center rounded-lg bg-accent text-accent-foreground">
                    <Dna aria-hidden="true" className="size-5" />
                  </span>
                  <span>
                    <span className="block text-sm font-semibold">People, ideas, evidence</span>
                    <span className="block text-xs text-muted-foreground">
                      Connected with context
                    </span>
                  </span>
                </div>
              </div>
            </Reveal>
          </PageShell>
          <div className="border-t border-primary-foreground/10">
            <div className="mx-auto flex max-w-screen-2xl flex-col gap-3 px-4 py-4 text-xs text-primary-foreground/70 sm:flex-row sm:items-center sm:px-6 lg:px-8">
              <span>A network for curiosity, collaboration, and careful science.</span>
              <span className="hidden h-px flex-1 bg-primary-foreground/15 sm:block" />
              <a
                href="#network"
                className="inline-flex min-h-11 items-center gap-2 font-medium hover:text-primary-foreground"
              >
                Meet the network <ArrowDown aria-hidden="true" className="size-4" />
              </a>
            </div>
          </div>
        </section>

        <section id="network" className="scroll-mt-24 py-section-sm sm:py-section">
          <PageShell>
            <Reveal>
              <SectionHeading
                eyebrow="A network with room for everyone"
                title="Different perspectives. Shared curiosity."
                description="Questions about healthspan cross disciplines. The network is designed to make it easier to find perspectives and collaborate without blurring the boundaries between community and research."
              />
            </Reveal>
            <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {audiences.map((audience, index) => (
                <Reveal key={audience.title} delay={index * 0.045}>
                  <FeatureCard {...audience} />
                </Reveal>
              ))}
            </div>
            <Card className="mt-7 border-primary/10 bg-surface-raised/60 shadow-none">
              <CardContent className="flex flex-col gap-4 py-5 sm:flex-row sm:items-center sm:justify-between">
                <p className="font-display text-lg">Explore topics that interest you</p>
                <div className="flex flex-wrap gap-2">
                  {focusAreas.map(({ label, icon: Icon }) => (
                    <Badge key={label} variant="outline" className="gap-1.5 bg-card px-3 py-1.5">
                      <Icon aria-hidden="true" />
                      {label}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          </PageShell>
        </section>

        <section
          id="journey"
          className="border-y border-border/70 bg-surface-raised/65 py-section-sm sm:py-section"
        >
          <PageShell>
            <Reveal>
              <SectionHeading
                eyebrow="How it works"
                title="From a question to a clearer conversation."
                description="A thoughtful research journey is iterative. Each step can surface new context, collaborators, and questions."
                centered
              />
            </Reveal>
            <ol className="journey-grid mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {journey.map(({ label, detail, icon: Icon }, index) => (
                <Reveal key={label} delay={index * 0.06}>
                  <li className="h-full">
                    <Card className="h-full bg-card/80 shadow-xs">
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <span className="font-display text-2xl text-primary">0{index + 1}</span>
                          <span className="grid size-11 place-items-center rounded-xl bg-accent text-accent-foreground">
                            <Icon aria-hidden="true" className="size-5" />
                          </span>
                        </div>
                        <CardTitle className="font-display text-xl">{label}</CardTitle>
                        <CardDescription className="leading-relaxed">{detail}</CardDescription>
                      </CardHeader>
                    </Card>
                  </li>
                </Reveal>
              ))}
            </ol>
            <Reveal delay={0.1}>
              <div className="mt-6 flex items-start gap-3 rounded-xl border border-primary/15 bg-card p-4 sm:mx-auto sm:max-w-2xl">
                <Sparkles aria-hidden="true" className="mt-0.5 size-5 shrink-0 text-primary" />
                <p className="text-sm leading-relaxed text-muted-foreground">
                  AI may assist exploration in future workflows. Suggestions remain proposals and
                  require evidence, human judgement, and appropriate permissions.
                </p>
              </div>
            </Reveal>
          </PageShell>
        </section>

        <section className="py-section-sm sm:py-section">
          <PageShell>
            <div className="grid gap-8 lg:grid-cols-[0.8fr_1.2fr] lg:items-start">
              <Reveal>
                <SectionHeading
                  eyebrow="Evidence-aware by design"
                  title="Evidence needs context, not a single score."
                  description="A label describes a source class. It does not replace appraisal, provenance, or uncertainty."
                />
                <p className="mt-5 text-sm leading-relaxed text-muted-foreground">
                  These labels come from the shared model and illustrate how different kinds of
                  sources can be distinguished. They are not endorsements of any finding.
                </p>
              </Reveal>
              <Reveal delay={0.08}>
                <Card className="border-primary/10 bg-gradient-to-br from-card to-surface-raised shadow-sm">
                  <CardHeader>
                    <CardTitle className="font-display text-xl">
                      Evidence classes are visible
                    </CardTitle>
                    <CardDescription>
                      Every class is named explicitly; color is reinforced with an icon and label.
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex flex-wrap gap-2">
                    <EvidenceBadge evidenceClass="peer_reviewed" />
                    <EvidenceBadge evidenceClass="clinical_trial" />
                    <EvidenceBadge evidenceClass="human_observational" />
                    <EvidenceBadge evidenceClass="preprint" />
                    <EvidenceBadge evidenceClass="ai_generated_hypothesis" />
                    <EvidenceBadge evidenceClass="speculation" />
                  </CardContent>
                </Card>
              </Reveal>
            </div>
            <div className="mt-8 grid gap-3 sm:grid-cols-3">
              <StatCard label="Evidence classes" value={11} detail="In the shared type model" />
              <StatCard label="User portals" value={3} detail="Social, Personal, Researcher" />
              <StatCard label="Guiding principles" value={4} detail="Shown below" />
            </div>
          </PageShell>
        </section>

        <section id="principles" className="bg-surface-raised/65 py-section-sm sm:py-section">
          <PageShell>
            <Reveal>
              <SectionHeading
                eyebrow="Built on trust"
                title="Progress only matters when it is responsible."
                description="Our foundations prioritize privacy, evidence, and transparent boundaries."
              />
            </Reveal>
            <div className="mt-8 grid gap-4 sm:grid-cols-2">
              {principles.map(({ title, description, icon: Icon }, index) => (
                <Reveal key={title} delay={index * 0.05}>
                  <FeatureCard
                    title={title}
                    description={description}
                    icon={Icon}
                    className="min-h-44"
                  />
                </Reveal>
              ))}
            </div>
          </PageShell>
        </section>

        <section id="portals" className="py-section-sm sm:py-section">
          <PageShell>
            <Reveal>
              <SectionHeading
                eyebrow="Find your place"
                title="One network, distinct spaces."
                description="Each portal has a different purpose. A portal alone never grants access to restricted resources."
              />
            </Reveal>
            <PortalSwitcher
              className="mt-7"
              portals={[
                {
                  title: "Social Portal",
                  description: "Community and ideas",
                  href: socialPortalUrl,
                  icon: UsersRound,
                },
                {
                  title: "Personal Portal",
                  description: "Your private space",
                  href: personalPortalUrl,
                  icon: LockKeyhole,
                },
                {
                  title: "Researcher Portal",
                  description: "Research workspace",
                  href: researcherPortalUrl,
                  icon: Microscope,
                },
              ]}
            />
            <Reveal delay={0.08} className="mt-7">
              <EmptyState
                icon={Network}
                title="The network is taking shape"
                description="This public page describes the foundation. Member accounts, research tools, and personal records are not available here."
              />
            </Reveal>
          </PageShell>
        </section>

        <section className="border-t border-border/70 bg-primary text-primary-foreground">
          <PageShell className="grid items-center gap-7 py-12 sm:py-16 lg:grid-cols-[1fr_auto]">
            <div>
              <p className="mb-2 text-sm font-medium text-primary-foreground/75">
                Better questions begin with many perspectives
              </p>
              <h2 className="max-w-2xl font-display text-3xl leading-tight sm:text-4xl">
                Explore the network at your own pace.
              </h2>
            </div>
            <Button
              render={<a href="#network" />}
              size="lg"
              className="w-full bg-card text-foreground hover:bg-card/90 sm:w-auto"
            >
              Start exploring <ArrowUpRight aria-hidden="true" />
            </Button>
          </PageShell>
        </section>
      </main>
      <SiteFooter>
        <span className="inline-flex items-center gap-2">
          <ShieldCheck aria-hidden="true" className="size-4 text-success" />
          Evidence-minded · Privacy-aware · Human-led
        </span>
      </SiteFooter>
    </div>
  );
}
