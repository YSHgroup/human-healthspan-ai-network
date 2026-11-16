import Image from "next/image";
import type { CSSProperties } from "react";
import {
  ArrowDown,
  ArrowRight,
  ArrowUpRight,
  CalendarDays,
  Globe,
  Handshake,
  LockKeyhole,
  MessageCircle,
  ShieldCheck,
  Sparkles,
  UsersRound,
  FlaskConical,
  BookOpenCheck,
} from "lucide-react";

import { Reveal } from "@healthspan/ui/motion";
import { ThemeToggle } from "@healthspan/ui/theme-toggle";

import { Bubble, Helix, Leaf } from "../components/landing/decor";
import { LandingHeader, type NavGroup } from "../components/landing/landing-header";
import { ParallaxStage } from "../components/landing/parallax-stage";
import "./landing.css";

const personalPortalUrl = process.env.PERSONAL_APP_URL ?? "http://localhost:3001";
const researcherPortalUrl = process.env.RESEARCHER_APP_URL ?? "http://localhost:3002";

const css = (vars: Record<string, string | number>) => vars as CSSProperties;

const navGroups: NavGroup[] = [
  {
    label: "About",
    items: [
      { label: "Our vision", href: "#vision", hint: "Why the network exists" },
      { label: "Responsible AI", href: "#ai", hint: "How we use AI" },
    ],
  },
  {
    label: "Explore",
    items: [
      { label: "Scientific knowledge", href: "#knowledge", hint: "Six areas of science" },
      { label: "Community feed", href: "/feed", hint: "Public questions and discussions" },
    ],
  },
  {
    label: "Communities",
    items: [
      { label: "Find a community", href: "/communities", hint: "Join or apply" },
      { label: "Community feed", href: "/feed", hint: "Browse discussions" },
      { label: "Messages", href: "/messages", hint: "Talk with members" },
    ],
  },
  {
    label: "AI Ecosystem",
    items: [
      { label: "Healthspan AI", href: "/ai", hint: "Ask a question" },
      { label: "Responsible AI", href: "#ai", hint: "Evidence and privacy" },
    ],
  },
  {
    label: "Resources",
    items: [
      { label: "Research and impact", href: "#impact", hint: "Collaboration at work" },
      { label: "Personal portal", href: personalPortalUrl, hint: "Your private space" },
      { label: "Researcher portal", href: researcherPortalUrl, hint: "Approved research" },
    ],
  },
];

const pillars = [
  { label: "Better Health", icon: "icon-health", tone: "green" },
  { label: "Timeless Beauty", icon: "icon-beauty", tone: "pink" },
  { label: "Longer Life", icon: "icon-life", tone: "gold" },
  { label: "Greater Power", icon: "icon-power", tone: "blue" },
  { label: "Unlimited Potential", icon: "icon-potential", tone: "violet" },
];

const topics = [
  { label: "Longevity & Healthspan", image: "leaf", position: "50% 50%" },
  { label: "Genetics & Epigenetics", image: "dna", position: "50% 50%" },
  { label: "Biotechnology", image: "flask", position: "50% 50%" },
  { label: "Brain & Cognition", image: "brain", position: "50% 40%" },
  { label: "Beauty & Wellness", image: "face", position: "62% 35%" },
  { label: "Nutrition & Human Performance", image: "food", position: "50% 50%" },
];

const impact = [
  { label: "Communities", detail: "Open and moderated spaces", icon: UsersRound },
  { label: "Organizations & Labs", detail: "Verified research teams", icon: Handshake },
  { label: "Events & Knowledge", detail: "Learn and share together", icon: CalendarDays },
  { label: "Global Impact", detail: "People and science worldwide", icon: Globe },
];

const trust = [
  { label: "Evidence over popularity", icon: FlaskConical },
  { label: "Private by default", icon: LockKeyhole },
  { label: "Clear sources", icon: BookOpenCheck },
  { label: "Ideas, not findings", icon: ShieldCheck },
];

export default function Home() {
  return (
    <div id="top" className="hs-landing">
      <a href="#main-content" className="hs-skip">
        Skip to content
      </a>
      <LandingHeader
        groups={navGroups}
        joinHref="/communities"
        loginHref="/communities"
        searchHref="/feed"
        themeToggle={<ThemeToggle />}
      />

      <main id="main-content">
        {/* Hero */}
        <section className="hs-hero" aria-labelledby="hero-title">
          <div className="hs-sky" aria-hidden="true">
            <span className="hs-cloud hs-cloud--1" />
            <span className="hs-cloud hs-cloud--2" />
            <span className="hs-cloud hs-cloud--3" />
            <span className="hs-sun" />
          </div>
          <ParallaxStage className="hs-hero-grid">
            <div className="hs-hero-copy">
              <h1 id="hero-title" className="hs-rise" style={css({ "--i": 0 })}>
                Do you want to live long while staying <em className="c-green">youthful</em>,{" "}
                <em className="c-green">healthy</em>, <em className="c-pink">beautiful</em> and{" "}
                <em className="c-gold">powerful</em>?
              </h1>
              <p className="hs-lead hs-rise" style={css({ "--i": 2 })}>
                Who can help you get there?
              </p>
              <p className="hs-script hs-rise" style={css({ "--i": 3 })}>
                Let’s realize it all together, here.
              </p>
              <p className="hs-body hs-rise" style={css({ "--i": 4 })}>
                Healthspan Network connects people, communities and scientific discovery to help
                you live longer, healthier and more fulfilling lives.
              </p>
              <div className="hs-actions hs-rise" style={css({ "--i": 5 })}>
                <a href="/communities" className="hs-btn hs-btn--ocean hs-btn--lg">
                  Join the Network <ArrowRight aria-hidden="true" />
                </a>
                <a href="#vision" className="hs-btn hs-btn--outline hs-btn--lg">
                  Explore Our Vision <ArrowDown aria-hidden="true" />
                </a>
              </div>
            </div>

            <div className="hs-hero-art hs-rise" style={css({ "--i": 2 })}>
              <div className="hs-layer" style={css({ "--depth": 16 })}>
                <Helix className="hs-helix hs-float" />
              </div>
              <div className="hs-layer" style={css({ "--depth": -10 })}>
                <div className="hs-hero-photo">
                  <Image
                    src="/landing/family.jpg"
                    alt="Three generations of a family smiling and looking toward the sky"
                    fill
                    priority
                    sizes="(min-width: 1100px) 700px, 100vw"
                  />
                </div>
              </div>
              <div className="hs-layer hs-leaf-layer" style={css({ "--depth": 24 })}>
                <Leaf className="hs-leaf hs-leaf--a hs-sway" />
                <Leaf className="hs-leaf hs-leaf--b hs-sway" flip />
              </div>
              <div className="hs-layer" style={css({ "--depth": 30 })}>
                <Bubble size={46} className="hs-bubble--h1" />
                <Bubble size={26} className="hs-bubble--h2" delay={1.4} />
                <Bubble size={16} className="hs-bubble--h3" delay={0.6} />
              </div>
            </div>
          </ParallaxStage>
        </section>

        {/* Five promises */}
        <section className="hs-wrap hs-pillars-wrap" aria-label="What the network is for">
          <Reveal>
            <ul className="hs-pillars hs-glass">
              {pillars.map((pillar, index) => (
                <li key={pillar.label} className="hs-pillar" data-tone={pillar.tone}>
                  <span className="hs-pillar-icon" style={css({ "--i": index })}>
                    <Image
                      src={`/landing/${pillar.icon}.png`}
                      alt=""
                      width={94}
                      height={94}
                      sizes="64px"
                    />
                  </span>
                  <span className="hs-pillar-label">{pillar.label}</span>
                </li>
              ))}
            </ul>
          </Reveal>
        </section>

        {/* Vision */}
        <section id="vision" className="hs-section hs-wrap" aria-labelledby="vision-title">
          <div className="hs-vision hs-glass">
            <Reveal className="hs-vision-copy">
              <p className="hs-kicker">Our vision</p>
              <h2 id="vision-title">A healthier, longer, more vibrant life for all.</h2>
              <p className="hs-body">
                Healthspan Network brings people, communities and science together, so you can
                explore, learn, connect and contribute.
              </p>
              <a href="#knowledge" className="hs-btn hs-btn--green hs-btn--lg">
                Explore the science <ArrowRight aria-hidden="true" />
              </a>
            </Reveal>
            <div className="hs-vision-art">
              <Helix className="hs-helix hs-helix--small hs-float" />
              <figure className="hs-blob hs-blob--runner">
                <Image
                  src="/landing/runner.jpg"
                  alt="A runner on a mountain lake road"
                  fill
                  sizes="(min-width: 900px) 260px, 45vw"
                />
              </figure>
              <figure className="hs-blob hs-blob--face">
                <Image
                  src="/landing/face.jpg"
                  alt="A woman with glowing, healthy skin"
                  fill
                  sizes="(min-width: 900px) 300px, 55vw"
                />
              </figure>
              <figure className="hs-blob hs-blob--lab">
                <Image
                  src="/landing/lab.jpg"
                  alt="Researchers working in a bright laboratory"
                  fill
                  sizes="(min-width: 900px) 260px, 45vw"
                />
              </figure>
              <Leaf className="hs-leaf hs-leaf--v hs-sway" />
            </div>
          </div>
        </section>

        {/* Knowledge */}
        <section id="knowledge" className="hs-section hs-wrap" aria-labelledby="knowledge-title">
          <Reveal className="hs-center">
            <h2 id="knowledge-title">Explore Scientific Knowledge</h2>
            <p className="hs-body">Discover breakthroughs across longevity, health, beauty and more.</p>
          </Reveal>
          <ul className="hs-topics">
            {topics.map((topic, index) => (
              <li key={topic.label}>
                <Reveal delay={index * 0.05} className="hs-topic-reveal">
                  <a href="/feed" className="hs-topic" aria-label={`${topic.label}: browse discussions`}>
                    <span className="hs-topic-media">
                      <Image
                        src={`/landing/${topic.image}.jpg`}
                        alt=""
                        fill
                        sizes="(min-width: 1100px) 180px, (min-width: 640px) 30vw, 46vw"
                        style={{ objectPosition: topic.position }}
                      />
                      <span className="hs-topic-arrow">
                        <ArrowUpRight aria-hidden="true" />
                      </span>
                    </span>
                    <span className="hs-topic-label">{topic.label}</span>
                  </a>
                </Reveal>
              </li>
            ))}
          </ul>
        </section>

        {/* Community */}
        <section id="community" className="hs-community" aria-labelledby="community-title">
          <div className="hs-community-bg" aria-hidden="true">
            <Image src="/landing/city.jpg" alt="" fill sizes="100vw" />
          </div>
          <div className="hs-wrap hs-community-grid">
            <Reveal className="hs-community-copy">
              <p className="hs-kicker">Find your community</p>
              <h2 id="community-title">Connect with like‑minded people.</h2>
              <p className="hs-body">
                Share ideas, ask questions, and grow together in our global communities.
              </p>
              <a href="/communities" className="hs-btn hs-btn--green hs-btn--lg">
                Join a Community <ArrowRight aria-hidden="true" />
              </a>
            </Reveal>
            <div className="hs-community-art">
              <span className="hs-chip hs-chip--1" aria-hidden="true">
                <UsersRound />
              </span>
              <span className="hs-chip hs-chip--2" aria-hidden="true">
                <MessageCircle />
              </span>
              <span className="hs-chip hs-chip--3" aria-hidden="true">
                <Globe />
              </span>
              <div className="hs-community-photo">
                <Image
                  src="/landing/friends.jpg"
                  alt="Friends sitting together on the grass in a park, talking and laughing"
                  fill
                  sizes="(min-width: 900px) 640px, 100vw"
                />
              </div>
            </div>
          </div>
        </section>

        {/* AI */}
        <section id="ai" className="hs-wrap hs-ai-wrap" aria-labelledby="ai-title">
          <div className="hs-ai">
            <div className="hs-ai-net" aria-hidden="true">
              <Image src="/landing/network.jpg" alt="" fill sizes="100vw" />
            </div>
            <Reveal className="hs-ai-copy">
              <h2 id="ai-title">
                Human Curiosity. Scientific Intelligence. <span>Responsible AI.</span>
              </h2>
              <p className="hs-body">
                Get trusted answers, explore complex topics, and discover new possibilities with
                Healthspan AI.
              </p>
              <a href="/ai" className="hs-btn hs-btn--green hs-btn--lg">
                Try Healthspan AI <ArrowRight aria-hidden="true" />
              </a>
              <ul className="hs-trust" aria-label="How Healthspan AI is built">
                {trust.map(({ label, icon: Icon }) => (
                  <li key={label}>
                    <Icon aria-hidden="true" />
                    {label}
                  </li>
                ))}
              </ul>
              <p className="hs-fineprint">
                AI responses may be incomplete. Suggestions are hypotheses, not validated findings.
              </p>
            </Reveal>
            <div className="hs-ai-art" aria-hidden="true">
              <Image src="/landing/hologram.jpg" alt="" fill sizes="(min-width: 900px) 560px, 100vw" />
              <span className="hs-scan" />
            </div>
          </div>
        </section>

        {/* Impact */}
        <section id="impact" className="hs-impact" aria-labelledby="impact-title">
          <div className="hs-impact-bg" aria-hidden="true">
            <Image src="/landing/lake.jpg" alt="" fill sizes="100vw" />
          </div>
          <div className="hs-wrap">
            <Reveal className="hs-impact-panel hs-glass">
              <h2 id="impact-title">Research, Collaboration &amp; Impact</h2>
              <p className="hs-body">
                Work together to advance human health and scientific discovery.
              </p>
              <ul className="hs-impact-list">
                {impact.map(({ label, detail, icon: Icon }) => (
                  <li key={label}>
                    <span className="hs-impact-icon">
                      <Icon aria-hidden="true" />
                    </span>
                    <strong>{label}</strong>
                    <small>{detail}</small>
                  </li>
                ))}
              </ul>
            </Reveal>
          </div>
        </section>

        {/* Final call */}
        <section id="join" className="hs-join" aria-labelledby="join-title">
          <div className="hs-join-bg" aria-hidden="true">
            <Image src="/landing/trees.jpg" alt="" fill sizes="100vw" />
          </div>
          <Bubble size={90} className="hs-bubble--j1" />
          <Bubble size={54} className="hs-bubble--j2" delay={1.2} />
          <Bubble size={30} className="hs-bubble--j3" delay={2.1} />
          <Reveal className="hs-wrap hs-join-inner">
            <h2 id="join-title">
              Together, We Advance <br className="hs-br" />
              Human Health and Scientific Discovery.
            </h2>
            <p className="hs-body">
              Be part of a global network that is building a healthier, longer and more capable
              future for all.
            </p>
            <a href="/communities" className="hs-btn hs-btn--gold hs-btn--lg">
              Join the Healthspan Network <ArrowRight aria-hidden="true" />
            </a>
          </Reveal>
        </section>
      </main>

      <footer className="hs-footer">
        <div className="hs-wrap hs-footer-grid">
          <div className="hs-footer-brand">
            <Image src="/brand/logo-symbol.png" alt="" width={274} height={338} className="hs-footer-mark" />
            <div>
              <p className="hs-footer-name">Healthspan Network</p>
              <p className="hs-footer-tag">Better People. Better Science. A Healthier Future.</p>
            </div>
          </div>
          <nav aria-label="Footer" className="hs-footer-nav">
            <a href="#vision">About</a>
            <a href="#knowledge">Explore</a>
            <a href="/communities">Communities</a>
            <a href="/ai">AI Ecosystem</a>
            <a href="#impact">Resources</a>
          </nav>
          <nav aria-label="Portals" className="hs-footer-nav hs-footer-nav--portals">
            <a href="/">Social portal</a>
            <a href={personalPortalUrl}>Personal portal</a>
            <a href={researcherPortalUrl}>Researcher portal</a>
          </nav>
        </div>
        <div className="hs-wrap hs-footer-base">
          <span>© {new Date().getFullYear()} Healthspan Network. All rights reserved.</span>
          <span className="hs-footer-note">
            <Sparkles aria-hidden="true" /> Evidence-minded · Privacy-aware · Human-led
          </span>
        </div>
      </footer>
    </div>
  );
}
