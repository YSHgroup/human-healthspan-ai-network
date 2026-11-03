const focusAreas = ["Healthy aging", "Sleep", "Nutrition", "Brain health"];

export default function PersonalHome() {
  return (
    <main className="portal-page">
      <header className="portal-header">
        <a className="portal-brand" href="http://localhost:3000">
          <span className="portal-mark" aria-hidden="true">
            H
          </span>
          <span>
            <strong>HEALTHSPAN</strong>
            <small>PERSONAL PORTAL</small>
          </span>
        </a>
        <a className="portal-nav-link" href="http://localhost:3000">
          Visit the community →
        </a>
      </header>
      <section className="portal-content">
        <p className="eyebrow">YOUR SPACE IN THE NETWORK</p>
        <h1>A more personal way to explore.</h1>
        <p className="lead">
          This portal will bring your profile, interests, and saved knowledge together. Your health
          information will remain private by default.
        </p>
        <div className="foundation-card">
          <span className="card-label">FOUNDATION IN PROGRESS</span>
          <h2>Start with what you care about.</h2>
          <p>These example interests show the direction of personalization. They are not saved.</p>
          <div className="interest-list">
            {focusAreas.map((area) => (
              <span key={area}>{area}</span>
            ))}
          </div>
        </div>
        <p className="privacy-note">
          Health records, sharing controls, and AI personalization are not implemented in this
          foundation.
        </p>
      </section>
    </main>
  );
}
