"use client";

import { useEffect, useState } from "react";
import { getHealth } from "../../lib/api";
import { Badge } from "@healthspan/ui/badge";
import { cn } from "@/lib/utils";

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
    <Badge
      className="gap-2 border-border px-2.5 py-1 text-xs font-medium"
      variant="outline"
      role="status"
      aria-live="polite"
    >
      <span
        aria-hidden="true"
        className={cn(
          "size-2 rounded-full bg-muted-foreground",
          status === "online" && "bg-green-600",
          status === "offline" && "bg-destructive"
        )}
      />
      {label}
    </Badge>
  );
}
