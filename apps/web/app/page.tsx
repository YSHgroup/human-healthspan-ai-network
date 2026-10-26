import Image from "next/image";

const audiences = [
  { name: "People", verbs: "Connect · Share · Learn" },
  { name: "Researchers", verbs: "Collaborate · Innovate" },
  { name: "Healthcare Professionals", verbs: "Share · Advise · Improve" },
  { name: "Scientists", verbs: "Discover · Validate · Publish" },
  { name: "Engineers", verbs: "Build · Advance · Create" },
  { name: "AI Systems", verbs: "Analyze · Augment · Accelerate" },
  { name: "Institutions", verbs: "Support · Enable · Scale" },
];

const focusAreas = [
  "Health & Aging",
  "Fitness & Strength",
  "Nutrition",
  "Sleep & Recovery",
  "Skincare & Appearance",
  "Brain & Cognition",
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
    title: "Human & Health Network",
    tagline: "Real people. Real conversations. Better health and capability.",
    items: [
      "Social feed & communities",
      "Health & performance content",
      "Experts and researchers",
      "Personal progress & goals",
    ],
  },
  {
    key: "science",
    title: "Scientific & Research Network",
    tagline: "Trusted evidence. Deeper knowledge. Greater impact.",
    items: [
      "Papers, evidence & citations",
      "Research projects & collaboration",
      "Literature & datasets",
      "Research workspace",
    ],
  },
  {
    key: "ai",
    title: "AI Intelligence Layer",
    tagline: "Grounded in evidence. Built for discovery. Always accountable.",
    items: [
      "RAG + verified sources",
      "Citations & provenance",
      "Workspace-aware AI",
      "Responsible & explainable",
    ],
  },
];

const stack = [
  { name: "Next.js", detail: "React" },
  { name: "FastAPI", detail: "Python" },
  { name: "PostgreSQL", detail: "pgvector" },
  { name: "Redis", detail: "Cache / Queue" },
  { name: "OpenSearch", detail: "Search" },
  { name: "S3", detail: "Storage" },
];

const values = ["Open", "Privacy-First", "Collaborative", "Impactful"];

export default function Home() {
  return (
    <>
      <header className="site-header">
        <div className="container">
          <a className="brand" href="#top" aria-label="Healthspan Network home">
            <Image src="/brand/logo.png" alt="Healthspan Network" width={1112} height={385} priority />
          </a>
          <nav className="nav" aria-label="Primary">
            <a href="#network">Network</a>
            <a href="#journey">Journey</a>
            <a href="#platform">Platform</a>
            <a href="#overview">Overview</a>
            <a href="#community">Community</a>
          </nav>
        </div>
      </header>

      <main id="top">
        <section className="hero">
          <div className="container">
            <div>
              <span className="eyebrow">Healthspan Network</span>
              <h1>
                Human Healthspan <span className="accent">AI Scientific Network</span>
              </h1>
              <p className="lead">
                A global network for better human health, capability and longevity, where people,
                researchers and AI move from better questions to better science.
              </p>
              <div className="cta-row">
                <a className="btn btn-primary" href="/home">
                  Open the app
                </a>
                <a className="btn btn-ghost" href="#network">
                  Explore the network
                </a>
                <a className="btn btn-ghost" href="#overview">
                  See the one-pager
                </a>
              </div>
            </div>
            <div className="hero-mark">
              <div className="glow">
                <Image src="/brand/mark.png" alt="Healthspan Network mark" width={371} height={371} priority />
              </div>
            </div>
          </div>
        </section>

        <section className="section" id="network">
          <div className="container">
            <div className="section-head">
              <h2>One network, many contributors</h2>
              <p>
                People, scientists, clinicians, engineers, institutions and AI systems working in
                the same space, each with a clear role.
              </p>
            </div>
            <div className="grid cols-4">
              {audiences.map((a) => (
                <article className="card" key={a.name}>
                  <h3>{a.name}</h3>
                  <p className="verbs">{a.verbs}</p>
                </article>
              ))}
            </div>
            <div className="chips" aria-label="Focus areas">
              {focusAreas.map((f) => (
                <span className="chip" key={f}>
                  {f}
                </span>
              ))}
            </div>
          </div>
        </section>

        <section className="section soft" id="journey">
          <div className="container">
            <div className="section-head">
              <h2>From Questions to Breakthroughs</h2>
              <p>Every discussion can be traced from a question to validated knowledge.</p>
            </div>
            <ol className="journey">
              {journey.map((step) => (
                <li key={step}>{step}</li>
              ))}
            </ol>
            <p className="journey-note">
              <strong>AI</strong> sits alongside every step, helping the community ask better
              questions.
            </p>
          </div>
        </section>

        <section className="section" id="platform">
          <div className="container">
            <div className="section-head">
              <h2>Three layers, one platform</h2>
              <p>Social, scientific and AI capabilities designed to work together.</p>
            </div>
            <div className="grid cols-3">
              {pillars.map((p) => (
                <article className={`card pillar ${p.key}`} key={p.key}>
                  <h3>{p.title}</h3>
                  <p className="tagline">{p.tagline}</p>
                  <ul>
                    {p.items.map((i) => (
                      <li key={i}>{i}</li>
                    ))}
                  </ul>
                </article>
              ))}
            </div>
            <div className="section-head" style={{ marginTop: 56, marginBottom: 24 }}>
              <h2 style={{ fontSize: "1.4rem" }}>Modern technology foundation</h2>
              <p>Scalable · Secure · Future-ready</p>
            </div>
            <div className="stack">
              {stack.map((s) => (
                <div key={s.name}>
                  <strong>{s.name}</strong>
                  <span>{s.detail}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="section soft" id="overview">
          <div className="container overview">
            <div className="frame">
              <Image
                src="/brand/one-pager.png"
                alt="Human Healthspan AI Scientific Network one-page overview"
                width={1024}
                height={1536}
                sizes="(max-width: 820px) 90vw, 420px"
              />
            </div>
            <div>
              <h2>The idea on one page</h2>
              <p>
                A single visual summary of the network: who takes part, how a question becomes a
                validated result, and the technology underneath. Better questions, better
                science, a healthier future.
              </p>
              <a className="btn btn-outline" href="/brand/one-pager.png" target="_blank" rel="noopener noreferrer">
                Open full size
              </a>
            </div>
          </div>
        </section>

        <section className="section" id="community">
          <div className="container">
            <div className="section-head">
              <h2>Built by a community</h2>
              <p>
                YSH IT Nexus brings people, scientists, clinicians and technologists together to
                create open, privacy-first infrastructure for health and research.
              </p>
            </div>
            <div className="banner">
              <Image
                src="/brand/ysh-nexus-banner.png"
                alt="YSH IT Nexus, a community for better health and better research"
                width={2172}
                height={724}
                sizes="(max-width: 1200px) 100vw, 1160px"
              />
            </div>
            <ul className="values">
              {values.map((v) => (
                <li key={v}>{v}</li>
              ))}
            </ul>
          </div>
        </section>
      </main>

      <footer className="site-footer">
        <div className="container">
          <div className="footer-logo">
            <Image src="/brand/logo.png" alt="Healthspan Network" width={1112} height={385} />
          </div>
          <p>Better People. Better Science. A Healthier Future.</p>
        </div>
      </footer>
    </>
  );
}
