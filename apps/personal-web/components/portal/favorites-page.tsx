"use client";

import { Bookmark } from "lucide-react";

import { Badge } from "@healthspan/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@healthspan/ui/card";

import { PageHeader } from "./page-header";
import { usePortalState } from "./portal-state";

export function FavoritesPage() {
  const { savedItems } = usePortalState();

  return (
    <>
      <PageHeader
        eyebrow="Your library"
        title="Saved knowledge"
        description="Curated resources and community notes that are ready for later review."
        actions={<Badge variant="outline">Local preview</Badge>}
      />
      <div className="grid gap-4 md:grid-cols-2 2xl:grid-cols-3">
        {savedItems.map((item) => (
          <Card key={item.title} className="glass h-full rounded-3xl border-0">
            <CardHeader>
              <div className="flex items-center justify-between gap-3">
                <Badge variant="outline">{item.tag}</Badge>
                <Bookmark aria-hidden="true" className="size-4 text-primary" />
              </div>
              <CardTitle className="pt-2 text-lg leading-snug">{item.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="leading-relaxed">{item.meta}</CardDescription>
            </CardContent>
          </Card>
        ))}
      </div>
    </>
  );
}
