export default function Home() {
  return (
    <main style={{maxWidth: 1100, margin: "40px auto", padding: 24, fontFamily: "system-ui"}}>
      <h1>Human Healthspan Network</h1>
      <p>Round 2 foundation: social + research + AI-ready architecture.</p>
      <nav style={{display: "flex", gap: 16, marginTop: 24}}>
        <a href="#feed">Home</a>
        <a href="#science">Science</a>
        <a href="#research">Research</a>
        <a href="#ai">AI</a>
      </nav>
      <section id="feed" style={{marginTop: 50}}>
        <h2>Feed</h2><p>Posts, questions, evidence-aware discussions and communities will live here.</p>
      </section>
      <section id="research" style={{marginTop: 50}}>
        <h2>Research</h2><p>Research projects, questions, hypotheses, literature and evidence.</p>
      </section>
    </main>
  );
}
