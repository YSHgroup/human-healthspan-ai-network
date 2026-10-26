"use client";

import { useEffect, useState } from "react";
import { getHealth } from "../../lib/api";

type Status = "checking" | "online" | "offline";

export default function ApiStatus() {
  const [status, setStatus] = useState<Status>("checking");

  useEffect(() => {
    let active = true;

    async function checkHealth() {
      try {
        const health = await getHealth();
        if (active) setStatus(health.status === "ok" ? "online" : "offline");
      } catch {
        if (active) setStatus("offline");
      }
    }

    void checkHealth();
    const intervalId = window.setInterval(() => void checkHealth(), 30_000);

    return () => {
      active = false;
      window.clearInterval(intervalId);
    };
  }, []);

  const label = status === "checking" ? "Checking API" : status === "online" ? "API online" : "API offline";

  return (
    <div className={`api-status api-status-${status}`} role="status" aria-live="polite">
      <span className="api-status-dot" aria-hidden="true" />
      {label}
    </div>
  );
}
