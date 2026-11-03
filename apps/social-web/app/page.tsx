import Image from "next/image";
import Link from "next/link";
import {
  ArrowDown,
  ArrowRight,
  ArrowUpRight,
  Atom,
  Brain,
  BriefcaseMedical,
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
import { Card } from "@/components/ui/card";
import { buttonVariants } from "@healthspan/ui/button";
import { cn } from "@/lib/utils";

const audiences: { name: string; verbs: string; icon: LucideIcon; tone: string }[] = [
  { name: "People", verbs: "Connect · Share · Learn", icon: UsersRound, tone: "mint" },
  { name: "Researchers", verbs: "Collaborate · Innovate", icon: Microscope, tone: "blue" },
  { name: "Healthcare professionals", verbs: "Share · Advise · Improve", icon: BriefcaseMedical, tone: "rose" },
  { name: "Scientists", verbs: "Discover · Validate · Publish", icon: FlaskConical, tone: "violet" },
  { name: "Engineers", verbs: "Build · Advance · Create", icon: Atom, tone: "amber" },
  { name: "AI systems", verbs: "Analyze · Augment · Accelerate", icon: Sparkles, tone: "sky" },
  { name: "Institutions", verbs: "Support · Enable · Scale", icon: Network, tone: "mint" },
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
  "Question",
  "Discussion",
  "Evidence",
  "Knowledge",
  "Hypothesis",
  "Collaboration",
  "Research",
  "Validation",
];

const pillars = [
  {
    key: "human",
    icon: UsersRound,
    title: "Human & health",
    tagline: "Real people. Real conversations. Better health and capability.",
    items: ["Social feed & communities", "Health & performance content", "Experts and researchers", "Personal progress & goals"],
  },
  {
    key: "science",
    icon: Microscope,
    title: "Science & research",
    tagline: "Trusted evidence. Deeper knowledge. Greater impact.",
    items: ["Papers, evidence & citations", "Research projects & collaboration", "Literature & datasets", "Research workspace"],
  },
  {
    key: "ai",
    icon: Sparkles,
    title: "Responsible AI",
    tagline: "Grounded in evidence. Built for discovery. Always accountable.",
    items: ["RAG + verified sources", "Citations & provenance", "Workspace-aware AI", "Responsible & explainable"],
  },
];

const stack = [
  { name: "Next.js", detail: "Member experience" },
  { name: "FastAPI", detail: "Application services" },
  { name: "PostgreSQL", detail: "Data foundation" },
  { name: "Redis", detail: "Cache & queue" },
  { name: "OpenSearch", detail: "Discovery" },
  { name: "S3", detail: "Object storage" },
];

const values = ["Open", "Privacy-first", "Collaborative", "Impactful"];

export default function Home() {
  return (
    <div className="landing-page">
      <header className="site-header">
        <div className="landing-container header-inner">
          <Link className="brand" href="#top" aria-label="Healthspan Network home">
            <Image src="/brand/logo.png" alt="Healthspan Network" width={1112} height={385} priority />
          </Link>
          <nav className="nav" aria-label="Primary">
            <Link href="#network">Network</Link>
            <Link href="#journey">Journey</Link>
            <Link href="#platform">Platform</Link>
            <Link href="#community">Community</Link>
          </nav>
          <Link className="landing-header-cta" href="/home">
            Enter the network <ArrowUpRight aria-hidden="true" />
          </Link>
        </div>
      </header>

      <main id="top">
        <section className="landing-hero">
          <div className="landing-container landing-hero-grid">
            <div className="landing-hero-copy">
              <Badge className="landing-kicker">
                <span aria-hidden="true" className="landing-live-dot" />
                People · Science · Possibility
              </Badge>
              <p className="eyebrow">The human healthspan network</p>
              <h1>
                Better healthspan.
                <span>Built together.</span>
              </h1>
              <p className="landing-lead">
                A living network where people, researchers, clinicians, and technology come together
                to turn better questions into better science.
              </p>
              <div className="landing-actions">
                <Link className="landing-button landing-button-primary" href="/home">
                  Discover the network <ArrowRight aria-hidden="true" />
                </Link>
                <Link className="landing-button landing-button-secondary" href="#network">
                  See how it works <ArrowDown aria-hidden="true" />
                </Link>
              </div>
              <div className="landing-trust-line">
                <span><ShieldCheck aria-hidden="true" /> Open by design</span>
                <i aria-hidden="true" />
                <span>Privacy-first</span>
                <i aria-hidden="true" />
                <span>Evidence-led</span>
              </div>
            </div>

            <div className="landing-visual" aria-label="A connected network for people and science">
              <div aria-hidden="true" className="visual-glow" />
              <div aria-hidden="true" className="visual-grid" />
              <div className="orbit orbit-outer" aria-hidden="true" />
              <div className="orbit orbit-middle" aria-hidden="true" />
              <div className="orbit orbit-inner" aria-hidden="true" />
              <div className="orbit-node node-people"><UsersRound aria-hidden="true" /></div>
              <div className="orbit-node node-science"><Microscope aria-hidden="true" /></div>
              <div className="orbit-node node-ai"><Sparkles aria-hidden="true" /></div>
              <div className="orbit-node node-health"><HeartPulse aria-hidden="true" /></div>
              <div className="visual-center">
                <Image src="/brand/mark.png" alt="" width={371} height={371} priority />
              </div>
              <div className="visual-label label-top">
                <span className="visual-label-icon"><Dna aria-hidden="true" /></span>
                <span><strong>Human potential</strong><small>Explore what’s possible</small></span>
              </div>
              <div className="visual-label label-bottom">
                <span className="visual-signal" />
                <span><strong>Curiosity in motion</strong><small>Questions grow into discovery</small></span>
                <ArrowUpRight aria-hidden="true" />
              </div>
              <span className="visual-spark spark-one" aria-hidden="true">✦</span>
              <span className="visual-spark spark-two" aria-hidden="true">✧</span>
            </div>
          </div>
          <div className="landing-container hero-bottom-line">
            <span>One connected space for a healthier future</span>
            <span className="hero-bottom-rule" />
            <span>Scroll to explore <ArrowDown aria-hidden="true" /></span>
          </div>
        </section>

        <section className="landing-intro" id="network">
          <div className="landing-container">
            <div className="section-head landing-section-head">
              <span className="section-eyebrow">A network with room for everyone</span>
              <h2>Many perspectives.<br /><span>One shared direction.</span></h2>
              <p>Healthspan is too important for any one discipline to solve alone. We bring diverse contributors into the same conversation.</p>
            </div>
            <div className="audience-grid">
              {audiences.map(({ name, verbs, icon: Icon, tone }, index) => (
                <Card className={`audience-card audience-${tone}`} key={name}>
                  <span className="audience-icon"><Icon aria-hidden="true" /></span>
                  <span className="audience-index">0{index + 1}</span>
                  <h3>{name}</h3>
                  <p>{verbs}</p>
                </Card>
              ))}
            </div>
            <div className="focus-panel">
              <p>Explore what matters to you</p>
              <div className="focus-chips">
                {focusAreas.map(({ name, icon: Icon }) => (
                  <Badge className="focus-chip" key={name} variant="outline"><Icon aria-hidden="true" />{name}</Badge>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="journey-section" id="journey">
          <div aria-hidden="true" className="journey-decoration" />
          <div className="landing-container">
            <div className="section-head landing-section-head">
              <span className="section-eyebrow section-eyebrow-light">From spark to science</span>
              <h2>Good questions can<br /><span>change what comes next.</span></h2>
              <p>Make the journey from curiosity to validated knowledge more connected, transparent, and collaborative.</p>
            </div>
            <ol className="journey-track">
              {journey.map((step, index) => (
                <li key={step}>
                  <span className="journey-node">{String(index + 1).padStart(2, "0")}</span>
                  <span className="journey-step">{step}</span>
                </li>
              ))}
            </ol>
            <p className="journey-note"><Sparkles aria-hidden="true" /><span><strong>AI alongside the journey</strong> — designed to help people ask better questions and explore evidence responsibly.</span></p>
          </div>
        </section>

        <section className="platform-section" id="platform">
          <div className="landing-container">
            <div className="section-head landing-section-head">
              <span className="section-eyebrow">A connected foundation</span>
              <h2>Three layers.<br /><span>Working as one.</span></h2>
              <p>People-first community, research workflows, and an accountable intelligence layer—designed to reinforce each other.</p>
            </div>
            <div className="pillar-grid">
              {pillars.map(({ key, title, tagline, items, icon: Icon }, index) => (
                <Card className={`pillar-card pillar-${key}`} key={key}>
                  <div className="pillar-topline"><span>0{index + 1} / 03</span><Icon aria-hidden="true" /></div>
                  <h3>{title}</h3>
                  <p className="pillar-tagline">{tagline}</p>
                  <ul>{items.map((item) => <li key={item}>{item}</li>)}</ul>
                  <span className="pillar-watermark"><Icon aria-hidden="true" /></span>
                </Card>
              ))}
            </div>

            <div className="technology-block">
              <div className="technology-heading">
                <div><span className="section-eyebrow">Built to evolve</span><h3>Modern technology foundation</h3></div>
                <p>Modular by design · Ready to grow</p>
              </div>
              <div className="technology-grid">
                {stack.map((item, index) => (
                  <div className="technology-item" key={item.name}>
                    <span className="technology-index">0{index + 1}</span>
                    <strong>{item.name}</strong>
                    <span>{item.detail}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="overview-section" id="overview">
          <div className="landing-container overview-grid">
            <div className="overview-art">
              <div className="overview-art-frame">
                <Image
                  src="/brand/one-pager.png"
                  alt="Human Healthspan AI Scientific Network one-page overview"
                  width={1024}
                  height={1536}
                  sizes="(max-width: 820px) 90vw, 480px"
                />
              </div>
              <span className="overview-art-caption"><span /> THE NETWORK AT A GLANCE</span>
            </div>
            <div className="overview-copy">
              <span className="section-eyebrow">The big picture</span>
              <h2>Make the complex<br /><span>feel connected.</span></h2>
              <p>A single visual summary of who takes part, how questions become validated knowledge, and the technology underneath.</p>
              <p className="overview-emphasis">Better questions. Better science. A healthier future.</p>
              <a className="landing-button landing-button-dark" href="/brand/one-pager.png" target="_blank" rel="noopener noreferrer">
                View the one-page overview <ArrowUpRight aria-hidden="true" />
              </a>
            </div>
          </div>
        </section>

        <section className="community-section" id="community">
          <div className="landing-container">
            <div className="community-card">
              <div className="community-copy">
                <span className="section-eyebrow section-eyebrow-light">Built by a community</span>
                <h2>Better futures are<br /><span>a team effort.</span></h2>
                <p>YSH IT Nexus brings people, scientists, clinicians, and technologists together to create open, privacy-first infrastructure for health and research.</p>
                <div className="community-values">{values.map((value) => <span key={value}><span />{value}</span>)}</div>
                <Link className="community-link" href="/home">Meet the network <ArrowRight aria-hidden="true" /></Link>
              </div>
              <div className="community-banner">
                <Image
                  src="/brand/ysh-nexus-banner.png"
                  alt="YSH IT Nexus, a community for better health and better research"
                  width={2172}
                  height={724}
                  sizes="(max-width: 1200px) 100vw, 1160px"
                />
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="landing-footer">
        <div className="landing-container footer-inner">
          <Link href="#top" className="footer-brand" aria-label="Back to top">
            <Image src="/brand/logo.png" alt="Healthspan Network" width={1112} height={385} />
          </Link>
          <p>Better People. Better Science. A Healthier Future.</p>
          <Link className="footer-top-link" href="#top">Back to top <ArrowUpRight aria-hidden="true" /></Link>
        </div>
      </footer>
    </div>
  );
}
