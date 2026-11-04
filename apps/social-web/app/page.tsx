import Image from "next/image";
import Link from "next/link";
import {
  ArrowDown,
  ArrowRight,
  ArrowUpRight,
  Atom,
  Brain,
  Dna,
  Dumbbell,
  FlaskConical,
  HeartPulse,
  Microscope,
  Moon,
  Network,
  ShieldCheck,
  Sparkles,
  UsersRound,
  type LucideIcon,
} from "lucide-react";

import { Badge } from "@healthspan/ui/badge";
import { Button, buttonVariants } from "@healthspan/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@healthspan/ui/card";
import { cn } from "@healthspan/ui/utils";

const audiences: { name: string; roles: string; icon: LucideIcon; tone: string }[] = [
  { name: "People", roles: "Connect · Share · Learn", icon: UsersRound, tone: "mint" },
  { name: "Researchers", roles: "Collaborate · Innovate", icon: Microscope, tone: "blue" },
  {
    name: "Health professionals",
    roles: "Share · Advise · Improve",
    icon: HeartPulse,
    tone: "rose",
  },
  {
    name: "Scientists",
    roles: "Discover · Validate · Publish",
    icon: FlaskConical,
    tone: "violet",
  },
  { name: "Engineers", roles: "Build · Advance · Create", icon: Atom, tone: "amber" },
  { name: "Institutions", roles: "Support · Enable · Scale", icon: Network, tone: "sky" },
];

const focusAreas: { name: string; icon: LucideIcon }[] = [
  { name: "Health & aging", icon: HeartPulse },
  { name: "Strength", icon: Dumbbell },
  { name: "Nutrition", icon: Sparkles },
  { name: "Sleep", icon: Moon },
  { name: "Brain & cognition", icon: Brain },
  { name: "Research", icon: Microscope },
];

const journey = [
  "Questions",
  "Discussion",
  "Evidence",
  "Knowledge",
  "Collaboration",
  "Research",
  "Validation",
];

const pillars: {
  key: string;
  icon: LucideIcon;
  title: string;
  tagline: string;
  items: string[];
}[] = [
  {
    key: "human",
    icon: UsersRound,
    title: "Human & health",
    tagline: "Real people. Better questions. Healthier lives.",
    items: ["Community and conversation", "Health and performance learning", "Experts and peers"],
  },
  {
    key: "science",
    icon: Microscope,
    title: "Science & research",
    tagline: "Trusted evidence. Shared effort. Greater impact.",
    items: ["Research communities", "Projects and collaboration", "Sources and provenance"],
  },
  {
    key: "ai",
    icon: Sparkles,
    title: "Responsible AI",
    tagline: "Grounded in evidence. Designed for discovery.",
    items: ["Source-aware assistance", "Permission-aware research", "Uncertainty and oversight"],
  },
];

const personalPortalUrl = process.env.PERSONAL_APP_URL ?? "http://localhost:3001";
const researcherPortalUrl = process.env.RESEARCHER_APP_URL ?? "http://localhost:3002";

export default function Home() {
  return (
    <div className="landing-page" id="top">
      <header className="site-header">
        <div className="landing-container header-inner">
          <Link className="brand" href="#top" aria-label="Healthspan Network home">
            <Image
              src="/brand/logo.png"
              alt="Healthspan Network — Better People. Better Science. A Healthier Future."
              width={1112}
              height={385}
              priority
            />
          </Link>
          <nav className="main-nav" aria-label="Primary">
            <Link href="#network">Network</Link>
            <Link href="#journey">Journey</Link>
            <Link href="#platform">Platform</Link>
            <Link href="#principles">Principles</Link>
          </nav>
          <Button
            render={<Link href="#network" />}
            variant="outline"
            size="sm"
            className="header-cta"
          >
            Explore the network <ArrowUpRight aria-hidden="true" />
          </Button>
        </div>
      </header>

      <main>
        <section className="landing-hero">
          <div className="landing-container hero-grid">
            <div className="hero-copy">
              <Badge className="hero-kicker" variant="outline">
                <span className="live-dot" aria-hidden="true" />
                People · Science · Possibility
              </Badge>
              <p className="hero-eyebrow">The human healthspan network</p>
              <h1>
                Better healthspan.
                <span>Built together.</span>
              </h1>
              <p className="hero-lead">
                A living network where people, researchers, clinicians, and technology come together
                to turn better questions into better science.
              </p>
              <div className="hero-actions">
                <Button
                  render={<Link href="#network" />}
                  className="hero-button hero-button-primary"
                  size="lg"
                >
                  Discover the network <ArrowRight aria-hidden="true" />
                </Button>
                <Link
                  className={cn(
                    buttonVariants({ variant: "outline", size: "lg" }),
                    "hero-button hero-button-secondary",
                  )}
                  href="#journey"
                >
                  See how it works <ArrowDown aria-hidden="true" />
                </Link>
              </div>
              <div className="hero-trust-line">
                <span>
                  <ShieldCheck aria-hidden="true" /> Open by design
                </span>
                <i aria-hidden="true" />
                <span>Privacy-aware</span>
                <i aria-hidden="true" />
                <span>Evidence-led</span>
              </div>
            </div>

            <div className="hero-visual" role="img" aria-label="People and science connected">
              <div className="visual-glow" aria-hidden="true" />
              <div className="visual-grid" aria-hidden="true" />
              <div className="visual-orbit orbit-outer" aria-hidden="true" />
              <div className="visual-orbit orbit-middle" aria-hidden="true" />
              <div className="visual-orbit orbit-inner" aria-hidden="true" />
              <div className="orbit-node node-people" aria-hidden="true">
                <UsersRound />
              </div>
              <div className="orbit-node node-science" aria-hidden="true">
                <Microscope />
              </div>
              <div className="orbit-node node-ai" aria-hidden="true">
                <Sparkles />
              </div>
              <div className="orbit-node node-health" aria-hidden="true">
                <HeartPulse />
              </div>
              <div className="visual-center">
                <span className="center-halo" />
                <Image src="/brand/mark.png" alt="" width={371} height={371} priority />
              </div>
              <div className="visual-label label-top">
                <span className="visual-label-icon">
                  <Dna aria-hidden="true" />
                </span>
                <span>
                  <strong>Human potential</strong>
                  <small>Explore what’s possible</small>
                </span>
              </div>
              <div className="visual-label label-bottom">
                <span className="visual-signal" />
                <span>
                  <strong>Curiosity in motion</strong>
                  <small>Questions grow into discovery</small>
                </span>
                <ArrowUpRight aria-hidden="true" />
              </div>
              <span className="visual-spark spark-one" aria-hidden="true">
                ✦
              </span>
              <span className="visual-spark spark-two" aria-hidden="true">
                ✧
              </span>
            </div>
          </div>
          <div className="landing-container hero-bottom-line">
            <span>One connected space for a healthier future</span>
            <span className="hero-bottom-rule" />
            <a href="#network">
              Scroll to explore <ArrowDown aria-hidden="true" />
            </a>
          </div>
        </section>

        <section className="network-intro section-light" id="network">
          <div className="landing-container">
            <div className="section-heading">
              <span className="section-eyebrow">A network with room for everyone</span>
              <h2>
                Many perspectives.
                <span>One shared direction.</span>
              </h2>
              <p>
                Healthspan is too important for any one discipline to solve alone. We bring diverse
                contributors into the same conversation.
              </p>
            </div>
            <div className="audience-grid">
              {audiences.map(({ name, roles, icon: Icon, tone }, index) => (
                <Card className={`audience-card audience-${tone}`} key={name}>
                  <CardHeader className="audience-header">
                    <span className="audience-icon">
                      <Icon aria-hidden="true" />
                    </span>
                    <span className="audience-index">0{index + 1}</span>
                    <CardTitle>{name}</CardTitle>
                    <CardDescription>{roles}</CardDescription>
                  </CardHeader>
                </Card>
              ))}
            </div>
            <div className="focus-panel">
              <p>Explore what matters to you</p>
              <div className="focus-chips">
                {focusAreas.map(({ name, icon: Icon }) => (
                  <Badge className="focus-chip" key={name} variant="outline">
                    <Icon aria-hidden="true" />
                    {name}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="journey-section" id="journey">
          <div className="journey-decoration" aria-hidden="true" />
          <div className="landing-container">
            <div className="section-heading section-heading-dark">
              <span className="section-eyebrow">From spark to science</span>
              <h2>
                Good questions can
                <span>change what comes next.</span>
              </h2>
              <p>
                Make the journey from curiosity to validated knowledge more connected, transparent,
                and collaborative.
              </p>
            </div>
            <ol className="journey-track">
              {journey.map((step, index) => (
                <li key={step}>
                  <span className="journey-node">{String(index + 1).padStart(2, "0")}</span>
                  <span className="journey-step">{step}</span>
                </li>
              ))}
            </ol>
            <p className="journey-note">
              <Sparkles aria-hidden="true" />
              <span>
                <strong>AI alongside the journey</strong> — designed to help people ask better
                questions and explore evidence responsibly.
              </span>
            </p>
          </div>
        </section>

        <section className="platform-section section-light" id="platform">
          <div className="landing-container">
            <div className="section-heading">
              <span className="section-eyebrow">A connected foundation</span>
              <h2>
                Three layers.
                <span>Working as one.</span>
              </h2>
              <p>
                People-first community, protected research, and an accountable intelligence layer—
                designed to strengthen each other.
              </p>
            </div>
            <div className="pillar-grid">
              {pillars.map(({ key, title, tagline, items, icon: Icon }, index) => (
                <Card className={`pillar-card pillar-${key}`} key={key}>
                  <CardHeader className="pillar-header">
                    <div className="pillar-topline">
                      <span>0{index + 1} / 03</span>
                      <Icon aria-hidden="true" />
                    </div>
                    <CardTitle>{title}</CardTitle>
                    <CardDescription className="pillar-tagline">{tagline}</CardDescription>
                  </CardHeader>
                  <CardContent className="pillar-content">
                    <ul>
                      {items.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </CardContent>
                  <span className="pillar-watermark">
                    <Icon aria-hidden="true" />
                  </span>
                </Card>
              ))}
            </div>
            <div className="portal-choices">
              <div>
                <span className="section-eyebrow">Find your place</span>
                <h3>One network, distinct experiences.</h3>
              </div>
              <div className="portal-links">
                <Link href={personalPortalUrl}>
                  Personal portal <ArrowUpRight aria-hidden="true" />
                </Link>
                <Link href={researcherPortalUrl}>
                  Researcher portal <ArrowUpRight aria-hidden="true" />
                </Link>
              </div>
            </div>
          </div>
        </section>

        <section className="principles-section" id="principles">
          <div className="landing-container principles-inner">
            <div className="principles-copy">
              <Badge className="principles-badge" variant="outline">
                Built on trust
              </Badge>
              <h2>Progress only matters when it’s responsible.</h2>
              <p>
                Better healthspan needs more than good intentions. It needs evidence, clear
                permissions, and respect for the people behind the data.
              </p>
              <Link className="principles-link" href="#top">
                Our guiding principles <ArrowUpRight aria-hidden="true" />
              </Link>
            </div>
            <div className="principles-list">
              <div>
                <span>01</span>
                <p>Popularity and scientific evidence are not the same thing.</p>
              </div>
              <div>
                <span>02</span>
                <p>Personal health information stays private by default.</p>
              </div>
              <div>
                <span>03</span>
                <p>Research and AI respect explicit permissions and provenance.</p>
              </div>
              <div>
                <span>04</span>
                <p>AI hypotheses are proposals, not validated findings.</p>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="site-footer">
        <div className="landing-container footer-inner">
          <Link className="footer-brand" href="#top" aria-label="Back to Healthspan Network home">
            <Image src="/brand/logo.png" alt="Healthspan Network" width={1112} height={385} />
          </Link>
          <p>Better people. Better science. A healthier future.</p>
          <Link className="back-to-top" href="#top">
            Back to top <ArrowUpRight aria-hidden="true" />
          </Link>
        </div>
      </footer>
    </div>
  );
}
