export default function PageHeader({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string;
  title: string;
  description: string;
}) {
  return (
    <header className="mb-7 space-y-2">
      <p className="text-xs font-bold tracking-[0.11em] text-teal-700 uppercase">
        {eyebrow}
      </p>
      <h1 className="text-4xl leading-tight font-semibold tracking-tight text-foreground sm:text-5xl">
        {title}
      </h1>
      <p className="max-w-2xl text-sm leading-6 text-muted-foreground sm:text-base">
        {description}
      </p>
    </header>
  );
}
