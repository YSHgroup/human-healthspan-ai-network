import Image from "next/image";
import Link from "next/link";
import {
  ArrowUpRight,
  FileSearch,
  FlaskConical,
  LockKeyhole,
  ShieldCheck,
  UsersRound,
} from "lucide-react";

import { Badge } from "@healthspan/ui/badge";
import { Button } from "@healthspan/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@healthspan/ui/card";

const foundations = [
  {
    title: "Community access",
    description: "Membership and application workflows come before restricted resources.",
    icon: UsersRound,
  },
  {
    title: "Research projects",
    description: "Projects need explicit roles, resource permissions, and auditable activity.",
    icon: FlaskConical,
  },
  {
    title: "Evidence practice",
    description: "Sources, provenance, and uncertainty belong in every scientific workflow.",
    icon: FileSearch,
  },
];

const socialPortalUrl = process.env.PUBLIC_APP_URL ?? "http://localhost:3000";

export default function ResearcherHome() {
  return (
    <main className="min-h-screen bg-[#f5f9fb] text-foreground">
      <header className="border-b border-border/80 bg-white">
        <div className="mx-auto flex h-[76px] max-w-6xl items-center justify-between gap-4 px-5">
          <Link className="block w-[190px]" href={socialPortalUrl} aria-label="Healthspan home">
            <Image
              src="/brand/logo.png"
              alt="Healthspan Network"
              width={1112}
              height={385}
              priority
            />
          </Link>
          <div className="flex items-center gap-3">
            <Badge className="hidden sm:inline-flex" variant="outline">
              Protected research environment
            </Badge>
            <Button
              render={<Link href={socialPortalUrl} />}
              size="sm"
              variant="outline"
              className="rounded-full"
            >
              Network <ArrowUpRight aria-hidden="true" />
            </Button>
          </div>
        </div>
      </header>

      <section className="mx-auto max-w-6xl px-5 py-12 md:py-20">
        <div className="max-w-3xl">
          <Badge className="mb-5 gap-2 bg-blue-500/10 text-blue-800" variant="secondary">
            <FlaskConical aria-hidden="true" /> Research, with the right foundations
          </Badge>
          <h1 className="font-serif text-5xl leading-[1.04] tracking-tight text-[#0b2f50] sm:text-6xl">
            Good science is a team effort.
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-muted-foreground">
            A future workspace for approved researchers to turn important questions into
            transparent, collaborative research.
          </p>
        </div>

        <Card className="mt-9 border-emerald-900/10 bg-emerald-50/70 shadow-none">
          <CardContent className="flex items-start gap-4 pt-6">
            <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-white text-emerald-800 shadow-sm">
              <ShieldCheck className="size-5" aria-hidden="true" />
            </span>
            <div>
              <Badge className="mb-2" variant="success">
                Permission boundary
              </Badge>
              <p className="max-w-4xl text-sm leading-6 text-emerald-950/80">
                Access to a portal never grants access to restricted research. Membership,
                organization, and project permissions must be explicitly verified by the backend.
              </p>
            </div>
          </CardContent>
        </Card>

        <div className="mt-10 grid gap-4 md:grid-cols-3">
          {foundations.map(({ title, description, icon: Icon }, index) => (
            <Card className="group min-h-56 border-slate-200 bg-white transition hover:-translate-y-1 hover:shadow-lg hover:shadow-slate-900/5" key={title}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <Badge variant="outline">0{index + 1}</Badge>
                  <Icon
                    className="size-5 text-emerald-700 transition group-hover:scale-110"
                    aria-hidden="true"
                  />
                </div>
                <CardTitle className="pt-4 font-serif text-2xl font-medium text-[#153b59]">
                  {title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm leading-6 text-muted-foreground">{description}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="mt-7 flex flex-wrap items-center justify-between gap-4 border-t border-border pt-5">
          <p className="flex items-center gap-2 text-xs text-muted-foreground">
            <LockKeyhole className="size-4 text-emerald-800" aria-hidden="true" />
            Foundation only. No research data, files, or AI tools are available yet.
          </p>
          <Button
            render={<Link href={`${socialPortalUrl}#principles`} />}
            variant="ghost"
            size="sm"
          >
            Read the network principles <ArrowUpRight aria-hidden="true" />
          </Button>
        </div>
      </section>
    </main>
  );
}
