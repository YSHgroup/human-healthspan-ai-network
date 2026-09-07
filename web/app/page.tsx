const communities = [
  "Healthy Aging", "Fitness & Strength", "Nutrition",
  "Skin & Appearance", "Brain & Cognition", "Biomedical Research"
];

export default function Home() {
  return (
    <main style={{ maxWidth: 1100, margin: "0 auto", padding: 32 }}>
      <h1>Human Healthspan AI Network</h1>
      <p>Connect people, evidence, ideas, researchers and responsible AI.</p>

      <nav style={{ display: "flex", gap: 16, flexWrap: "wrap", margin: "24px 0" }}>
        {["Home", "Discover", "Communities", "Science", "Research", "AI", "Events", "Messages", "Profile"].map(x =>
          <span key={x}>{x}</span>
        )}
      </nav>

      <section>
        <h2>Communities</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
          {communities.map(c => <article key={c} style={{ border: "1px solid #ddd", padding: 16 }}>{c}</article>)}
        </div>
      </section>
    </main>
  );
}
