"use client";

import { Toaster as Sonner } from "sonner";
import type { ComponentProps } from "react";

function Toaster(props: ComponentProps<typeof Sonner>) {
  return (
    <Sonner
      data-slot="toaster"
      theme="system"
      position="bottom-right"
      richColors
      closeButton
      toastOptions={{
        classNames: {
          toast: "border border-border bg-card text-card-foreground shadow-md",
          description: "text-muted-foreground",
          actionButton: "bg-primary text-primary-foreground",
          cancelButton: "bg-muted text-muted-foreground",
        },
      }}
      {...props}
    />
  );
}

export { Toaster };
export { toast } from "sonner";
