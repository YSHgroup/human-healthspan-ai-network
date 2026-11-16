import { Dialog as DialogPrimitive } from "@base-ui/react/dialog";
import { X } from "lucide-react";
import type { ComponentProps } from "react";

import { cn } from "./utils";

function Sheet(props: ComponentProps<typeof DialogPrimitive.Root>) {
  return <DialogPrimitive.Root {...props} />;
}

function SheetTrigger(props: ComponentProps<typeof DialogPrimitive.Trigger>) {
  return <DialogPrimitive.Trigger data-slot="sheet-trigger" {...props} />;
}

function SheetContent({
  className,
  children,
  side = "right",
  showCloseButton = true,
  ...props
}: ComponentProps<typeof DialogPrimitive.Popup> & {
  side?: "left" | "right" | "top" | "bottom";
  showCloseButton?: boolean;
}) {
  const placement = {
    left: "inset-y-0 left-0 h-full w-[min(22rem,calc(100%-2rem))] border-r data-[starting-style]:-translate-x-4 data-[ending-style]:-translate-x-4",
    right:
      "inset-y-0 right-0 h-full w-[min(22rem,calc(100%-2rem))] border-l data-[starting-style]:translate-x-4 data-[ending-style]:translate-x-4",
    top: "inset-x-0 top-0 max-h-[85dvh] w-full border-b data-[starting-style]:-translate-y-4 data-[ending-style]:-translate-y-4",
    bottom:
      "inset-x-0 bottom-0 max-h-[85dvh] w-full border-t data-[starting-style]:translate-y-4 data-[ending-style]:translate-y-4",
  }[side];

  return (
    <DialogPrimitive.Portal>
      <DialogPrimitive.Backdrop className="fixed inset-0 z-50 bg-foreground/30 backdrop-blur-[3px] transition-opacity data-[starting-style]:opacity-0 data-[ending-style]:opacity-0" />
      <DialogPrimitive.Popup
        data-slot="sheet-content"
        className={cn(
          "fixed z-50 flex flex-col gap-5 overflow-y-auto border-border bg-popover p-6 text-popover-foreground shadow-lg outline-none transition-[opacity,transform] data-[starting-style]:opacity-0 data-[ending-style]:opacity-0 sm:p-7",
          placement,
          className,
        )}
        {...props}
      >
        {children}
        {showCloseButton && (
          <DialogPrimitive.Close
            aria-label="Close panel"
            className="absolute top-4 right-4 inline-flex size-10 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/25"
          >
            <X aria-hidden="true" className="size-4" />
          </DialogPrimitive.Close>
        )}
      </DialogPrimitive.Popup>
    </DialogPrimitive.Portal>
  );
}

function SheetHeader({ className, ...props }: ComponentProps<"div">) {
  return <div className={cn("grid gap-2 text-left", className)} {...props} />;
}

function SheetTitle({ className, ...props }: ComponentProps<typeof DialogPrimitive.Title>) {
  return (
    <DialogPrimitive.Title
      className={cn("font-display text-xl leading-tight tracking-tight", className)}
      {...props}
    />
  );
}

function SheetDescription({
  className,
  ...props
}: ComponentProps<typeof DialogPrimitive.Description>) {
  return (
    <DialogPrimitive.Description
      className={cn("text-sm leading-relaxed text-muted-foreground", className)}
      {...props}
    />
  );
}

export { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger };
