import type { ReactNode } from "react";

export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: ReactNode;
}) {
  return (
    <header className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div className="min-w-0">
        {eyebrow && (
          <p className="mb-2 text-xs font-semibold tracking-[0.16em] text-primary uppercase">{eyebrow}</p>
        )}
        <h1 className="font-display text-3xl leading-tight tracking-tight sm:text-4xl">{title}</h1>
        {description && (
          <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground sm:text-base">
            {description}
          </p>
        )}
      </div>
      {actions}
    </header>
  );
}

export function GlassSection({
  title,
  action,
  children,
  className,
  label,
}: {
  title?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
  label?: string;
}) {
  return (
    <section aria-label={label ?? title} className={`glass rounded-3xl p-5 ${className ?? ""}`}>
      {(title || action) && (
        <div className="mb-4 flex items-center justify-between gap-3">
          {title && <h2 className="font-display text-xl">{title}</h2>}
          {action}
        </div>
      )}
      {children}
    </section>
  );
}
