import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Alert, AlertDescription } from "@healthspan/ui/alert";
import { Badge } from "@healthspan/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@healthspan/ui/card";
import { Info } from "lucide-react";
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
        <Badge className="sidebar-status" variant="outline">
          <span className="sidebar-status-dot" aria-hidden="true" />
          FOUNDATION
        </Badge>
        <p className="sidebar-note">
          Administrative access and permissions will be enforced by the API, not this interface.
        </p>
      </aside>
      <section className="admin-main">
        <header className="admin-topbar">
          <span>Platform administration</span>
          <Badge className="admin-environment" variant="outline">
            LOCAL FOUNDATION
          </Badge>
        </header>
        <div className="admin-content">
          <p className="admin-eyebrow">OPERATIONS &amp; GOVERNANCE</p>
          <h1>A responsible network starts with trust.</h1>
          <p className="admin-intro">
            This separate Admin application is the starting point for platform oversight,
            moderation, and auditable operations.
          </p>
          <Alert className="admin-notice">
            <Info aria-hidden="true" />
            <AlertDescription>
              No administrative actions are available. Authentication, role checks, audit logging,
              and API integration must be implemented before this interface can manage platform
              data.
            </AlertDescription>
          </Alert>
          <div className="module-grid">
            {plannedModules.map((module, index) => (
              <Card className="module-card" key={module}>
                <CardHeader className="module-card-header">
                  <Badge variant="outline">0{index + 1}</Badge>
                  <CardTitle>{module}</CardTitle>
                </CardHeader>
                <CardContent className="module-card-content">
                  <p>Planned foundation · Not connected to live platform data</p>
                </CardContent>
              </Card>
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
