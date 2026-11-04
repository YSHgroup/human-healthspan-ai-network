import Image from "next/image";
import Link from "next/link";
import { ArrowUpRight, Bookmark, HeartPulse, LockKeyhole, Sparkles } from "lucide-react";

import { Badge } from "@healthspan/ui/badge";
import { Alert, AlertDescription } from "@healthspan/ui/alert";
import { Button } from "@healthspan/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@healthspan/ui/card";

const interests = ["Healthy aging", "Sleep", "Nutrition", "Brain health"];
const socialPortalUrl = process.env.PUBLIC_APP_URL ?? "http://localhost:3000";

export default function PersonalHome() {
  return (
    <main className="personal-shell min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-10 border-b border-border/80 bg-background/90 backdrop-blur">
        <div className="mx-auto flex h-[76px] max-w-6xl items-center justify-between px-5">
          <Link className="block w-[190px]" href={socialPortalUrl} aria-label="Healthspan home">
            <Image
              src="/brand/logo.png"
              alt="Healthspan Network"
              width={1112}
              height={385}
              priority
            />
          </Link>
          <Badge className="hidden sm:inline-flex" variant="outline">
            Personal portal foundation
          </Badge>
          <Button
            render={<Link href={socialPortalUrl} />}
            variant="outline"
            size="sm"
            className="rounded-full"
          >
            Community <ArrowUpRight aria-hidden="true" />
          </Button>
        </div>
      </header>

      <section className="mx-auto grid max-w-6xl gap-8 px-5 py-12 md:grid-cols-[1fr_0.78fr] md:items-center md:py-20">
        <div>
          <Badge className="mb-5 gap-2 bg-emerald-500/10 text-emerald-800" variant="secondary">
            <Sparkles aria-hidden="true" /> Your space in the network
          </Badge>
          <h1 className="max-w-2xl font-serif text-5xl leading-[1.04] tracking-tight text-[#0b2f50] sm:text-6xl">
            A more personal way to explore.
          </h1>
          <p className="mt-5 max-w-xl text-base leading-7 text-muted-foreground">
            Your profile, interests, and saved knowledge will come together here. Personal health
            information stays private by default.
          </p>
          <div className="mt-7 flex flex-wrap gap-3">
            <Button
              render={<Link href={`${socialPortalUrl}#network`} />}
              size="lg"
              className="rounded-full"
            >
              Explore the network <ArrowUpRight aria-hidden="true" />
            </Button>
            <Button variant="outline" size="lg" className="rounded-full" disabled>
              <Bookmark aria-hidden="true" /> Saved knowledge
            </Button>
          </div>
        </div>

        <Card className="relative overflow-hidden border-emerald-900/10 bg-white/90 shadow-xl shadow-emerald-950/5">
          <div
            aria-hidden="true"
            className="pointer-events-none absolute -right-14 -top-20 size-56 rounded-full border border-emerald-700/10 bg-emerald-300/10"
          />
          <CardHeader className="relative">
            <Badge className="w-fit" variant="outline">
              EXAMPLE ONLY
            </Badge>
            <CardTitle className="mt-2 font-serif text-2xl font-medium">
              Start with what you care about.
            </CardTitle>
            <CardDescription>
              These sample interests demonstrate a future personalized experience. Nothing here is
              saved to a profile.
            </CardDescription>
          </CardHeader>
          <CardContent className="relative">
            <div className="flex flex-wrap gap-2">
              {interests.map((interest) => (
                <Badge
                  className="border-emerald-900/10 bg-emerald-50 px-3 py-1.5 text-emerald-900"
                  key={interest}
                  variant="outline"
                >
                  {interest}
                </Badge>
              ))}
            </div>
            <Alert className="mt-7 flex items-start gap-3 rounded-xl border-emerald-900/10 bg-emerald-50/70 p-4">
              <LockKeyhole className="mt-0.5 size-4 shrink-0 text-emerald-800" aria-hidden="true" />
              <AlertDescription className="pl-0 text-xs leading-5 text-emerald-950/75">
                Health records, sharing controls, and AI personalization are not implemented in this
                foundation.
              </AlertDescription>
            </Alert>
            <div className="mt-5 flex items-center gap-2 text-xs text-muted-foreground">
              <HeartPulse className="size-4 text-emerald-700" aria-hidden="true" />
              Private by default. Shared only with your permission.
            </div>
          </CardContent>
        </Card>
      </section>
    </main>
  );
}
