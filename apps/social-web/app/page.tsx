import Image from "next/image";

const pillars = [
  {
    number: "01",
    title: "Open community",
    description:
      "A welcoming place to ask better questions, share perspectives, and find people who care about healthier, longer lives.",
    icon: "community",
  },
  {
    number: "02",
    title: "Protected research",
    description:
      "Approved researchers turn curiosity into collaborative work, with clear membership and resource permissions.",
    icon: "research",
  },
  {
    number: "03",
    title: "Responsible AI",
    description:
      "Purpose-built AI can make knowledge easier to explore while respecting evidence, privacy, and scientific boundaries.",
    icon: "ai",
  },
];

const journey = [
  "Discover",
  "Learn",
  "Connect",
  "Participate",
  "Collaborate",
  "Research",
  "Validate",
  "Share",
];

function ArrowIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 20 20" fill="none">
      <path d="M4.25 10h11.5m-4.75-4.75L15.75 10 11 14.75" />
    </svg>
  );
}

function NetworkIllustration() {
  return (
    <div
      className="network-art"
      role="img"
      aria-label="Community, research, and AI connected in one network"
    >
      <div className="network-orbit orbit-outer" />
      <div className="network-orbit orbit-inner" />
      <span className="orbit-line orbit-line-one" />
      <span className="orbit-line orbit-line-two" />
      <span className="orbit-line orbit-line-three" />
      <span className="orbit-node node-community">
        <span className="node-symbol">◌</span>
        <span>People</span>
      </span>
      <span className="orbit-node node-science">
        <span className="node-symbol">⌬</span>
        <span>Science</span>
      </span>
      <span className="orbit-node node-ai">
        <span className="node-symbol">✳</span>
        <span>AI</span>
      </span>
      <span className="orbit-node node-health">
        <span className="node-symbol">＋</span>
        <span>Health</span>
      </span>
      <div className="network-center">
        <div className="center-glow" />
        <Image
          src="/brand/mark.png"
          alt=""
          width={94}
          height={94}
          priority
          className="center-mark"
        />
        <span>Better, together</span>
      </div>
      <div className="art-caption">
        <span className="caption-dot" />
        One network. Many ways to contribute.
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <>
      <header className="site-header">
        <a className="brand" href="#home" aria-label="Healthspan Network home">
          <Image
            src="/brand/logo.png"
            alt="Healthspan Network — Better People. Better Science. A Healthier Future."
            width={190}
            height={66}
            priority
            className="brand-logo"
          />
        </a>
        <nav className="main-nav" aria-label="Main navigation">
          <a href="#mission">Our mission</a>
          <a href="#network">The network</a>
          <a href="#principles">Our principles</a>
        </nav>
        <a className="header-link" href="#network">
          Explore the network <ArrowIcon />
        </a>
      </header>

      <main id="home">
        <section className="hero page-width">
          <div className="hero-copy">
            <div className="eyebrow">
              <span className="eyebrow-mark" />
              A shared project for humanity
            </div>
            <h1>
              A healthier future is a <em>scientific</em> project.
            </h1>
            <p className="hero-description">
              Bringing people and researchers together to turn the questions we all care about into
              knowledge, collaboration, and better human healthspan.
            </p>
            <div className="hero-actions">
              <a className="button button-primary" href="#mission">
                Discover our mission <ArrowIcon />
              </a>
              <a className="text-link" href="#network">
                See how it connects <span aria-hidden="true">↓</span>
              </a>
            </div>
            <div className="hero-note">
              <span className="note-line" />
              People-first <span>·</span> Science-led <span>·</span> Privacy-aware
            </div>
          </div>
          <NetworkIllustration />
          <div className="hero-footnote">
            <span>01</span> / A connected ecosystem for health and discovery
          </div>
        </section>

        <section className="mission-section" id="mission">
          <div className="page-width mission-grid">
            <div className="section-intro">
              <p className="section-kicker">WHY WE’RE HERE</p>
              <h2>Curiosity deserves a path to discovery.</h2>
            </div>
            <div className="mission-copy">
              <p>
                The most important questions about how we live, age, and feel are asked everywhere.
                The knowledge to answer them is often scattered. We are building a place where
                public curiosity can meet scientific rigor.
              </p>
              <a className="inline-link" href="#principles">
                What guides us <ArrowIcon />
              </a>
            </div>
          </div>
          <div className="journey page-width" aria-label="From curiosity to shared knowledge">
            {journey.map((step, index) => (
              <div className="journey-step" key={step}>
                <span className="journey-number">0{index + 1}</span>
                <span>{step}</span>
                {index < journey.length - 1 && <span className="journey-connector" />}
              </div>
            ))}
          </div>
        </section>

        <section className="network-section page-width" id="network">
          <div className="network-heading">
            <div>
              <p className="section-kicker">ONE NETWORK, THREE LAYERS</p>
              <h2>Different roles. Shared purpose.</h2>
            </div>
            <p>
              An open community creates reach. A protected research environment creates credibility.
              Responsible AI helps knowledge travel further.
            </p>
          </div>
          <div className="pillar-grid">
            {pillars.map((pillar) => (
              <article className={`pillar-card pillar-${pillar.icon}`} key={pillar.number}>
                <div className="pillar-topline">
                  <span>{pillar.number}</span>
                  <span className="pillar-icon" aria-hidden="true">
                    {pillar.icon === "community" ? "◎" : pillar.icon === "research" ? "⌬" : "✳"}
                  </span>
                </div>
                <h3>{pillar.title}</h3>
                <p>{pillar.description}</p>
                <span className="pillar-rule" />
              </article>
            ))}
          </div>
          <div className="portal-links">
            <div>
              <span className="portal-label">A place for every perspective</span>
              <p>Start with what brings you here. Find your way from there.</p>
            </div>
            <div className="portal-list">
              <a href="http://localhost:3000">Social <ArrowIcon /></a>
              <a href="http://localhost:3001">Personal <ArrowIcon /></a>
              <a href="http://localhost:3002">Research <ArrowIcon /></a>
            </div>
          </div>
        </section>

        <section className="principles-section" id="principles">
          <div className="page-width principles-grid">
            <div>
              <p className="section-kicker">A FOUNDATION OF TRUST</p>
              <h2>Progress only matters when it’s responsible.</h2>
            </div>
            <div className="principle-list">
              <div>
                <span>01</span>
                <p>Evidence and personal experience are different—and both deserve context.</p>
              </div>
              <div>
                <span>02</span>
                <p>Personal health information stays private by default and under your control.</p>
              </div>
              <div>
                <span>03</span>
                <p>Research is protected by explicit access, clear provenance, and accountability.</p>
              </div>
              <div>
                <span>04</span>
                <p>AI can support discovery; its hypotheses are not scientific findings.</p>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="site-footer">
        <div className="page-width footer-inner">
          <a className="brand footer-brand" href="#home">
            <Image
              src="/brand/logo.png"
              alt="Healthspan Network"
              width={160}
              height={55}
              className="brand-logo"
            />
          </a>
          <p>Better health. Better research. A healthier future.</p>
          <a className="back-top" href="#home">
            Back to top ↑
          </a>
        </div>
      </footer>
    </>
  );
}
