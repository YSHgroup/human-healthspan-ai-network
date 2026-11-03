const workspaceFoundations = [
  ["Community access", "Membership and application workflows are planned."],
  ["Research projects", "Project roles and resource-level permissions come first."],
  ["Evidence practice", "Sources, provenance, and uncertainty belong in every workflow."],
];

export default function ResearcherHome() {
  return (
    <main className="research-page">
      <header className="research-header">
        <a className="research-brand" href="http://localhost:3000">
          <span className="research-mark" aria-hidden="true">
            ⌬
          </span>
          <span>
            <strong>HEALTHSPAN</strong>
            <small>RESEARCHER PORTAL</small>
          </span>
        </a>
        <span className="research-access">A protected research environment</span>
      </header>
      <section className="research-content">
        <p className="research-eyebrow">RESEARCH, WITH THE RIGHT FOUNDATIONS</p>
        <h1>Good science is a team effort.</h1>
        <p className="research-lead">
          A future workspace for approved researchers to turn important questions into transparent,
          collaborative research.
        </p>
        <div className="research-boundary">
          <span className="boundary-icon" aria-hidden="true">
            ◈
          </span>
          <p>
            Access to a portal will never grant access to restricted research. Membership,
            organization, and project permissions must be explicitly verified by the backend.
          </p>
        </div>
        <div className="research-foundations">
          {workspaceFoundations.map(([title, description], index) => (
            <article key={title}>
              <span>0{index + 1}</span>
              <h2>{title}</h2>
              <p>{description}</p>
            </article>
          ))}
        </div>
        <p className="research-status">
          Foundation only · No research data, files, or AI tools are available yet.
        </p>
      </section>
    </main>
  );
}
