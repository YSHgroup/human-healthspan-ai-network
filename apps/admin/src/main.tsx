import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const plannedModules = ["Users and organizations", "Community moderation", "Audit and security"];
const socialPortalUrl = import.meta.env.VITE_SOCIAL_APP_URL ?? "http://localhost:3000";

function AdminApp() {
  return (
    <main className="admin-shell">
      <aside className="admin-sidebar">
        <a className="admin-brand" href={socialPortalUrl}>
          <img className="admin-mark" src="/brand/mark.png" alt="" />
          <span>
            <strong>HEALTHSPAN</strong>
            <small>ADMINISTRATION</small>
          </span>
        </a>
        <div className="sidebar-status">
          <span />
          FOUNDATION
        </div>
        <p className="sidebar-note">
          Administrative access and permissions will be enforced by the API, not this interface.
        </p>
      </aside>
      <section className="admin-main">
        <header className="admin-topbar">
          <span>Platform administration</span>
          <span className="admin-environment">LOCAL FOUNDATION</span>
        </header>
        <div className="admin-content">
          <p className="admin-eyebrow">OPERATIONS &amp; GOVERNANCE</p>
          <h1>A responsible network starts with trust.</h1>
          <p className="admin-intro">
            This separate Admin application is the starting point for platform oversight,
            moderation, and auditable operations.
          </p>
          <div className="admin-notice">
            <span aria-hidden="true">ⓘ</span>
            <p>
              No administrative actions are available. Authentication, role checks, audit logging,
              and API integration must be implemented before this interface can manage platform
              data.
            </p>
          </div>
          <div className="module-grid">
            {plannedModules.map((module, index) => (
              <article className="module-card" key={module}>
                <span>0{index + 1}</span>
                <h2>{module}</h2>
                <p>Planned foundation · Not connected to live platform data</p>
              </article>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <AdminApp />
  </StrictMode>,
);
