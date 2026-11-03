import { cn } from "cn";

/** Shared verification indicator: green = verified by an authorized party, yellow = self-declared (Architecture 3.3.2). */
export function VerificationBadge({ status, className }: { status: "verified" | "unverified"; className?: string }) {
  const verified = status === "verified";
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-xs font-medium",
        verified ? "border-green-300 bg-green-50 text-green-800" : "border-amber-300 bg-amber-50 text-amber-800",
        className,
      )}
      title={verified ? "Verified by an authorized organization or the platform" : "Self-declared and not yet verified"}
    >
      <span aria-hidden="true" className={cn("size-1.5 rounded-full", verified ? "bg-green-600" : "bg-amber-500")} />
      {verified ? "Verified" : "Unverified"}
    </span>
  );
}
