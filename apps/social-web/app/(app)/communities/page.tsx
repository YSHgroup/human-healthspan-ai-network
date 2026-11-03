"use client";

import { useCallback, useEffect, useState } from "react";
import PageHeader from "../../components/PageHeader";
import { Badge } from "@healthspan/ui/badge";
import { Button } from "@healthspan/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";
import { getCommunities, joinCommunity, leaveCommunity, type Community } from "@/lib/api";
import { useSession } from "@/lib/session";

export default function CommunitiesPage() {
  const { user, status } = useSession();
  const [communities, setCommunities] = useState<Community[]>([]);
  const [loading, setLoading] = useState(true);
  const [busyCommunity, setBusyCommunity] = useState<string | null>(null);
  const [error, setError] = useState("");

  const loadCommunities = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setCommunities(await getCommunities());
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : "Unable to load communities.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadCommunities();
  }, [loadCommunities]);

  async function toggleMembership(community: Community) {
    setBusyCommunity(community.id);
    setError("");
    try {
      if (community.is_member) await leaveCommunity(community.id);
      else await joinCommunity(community.id);
      await loadCommunities();
      setBusyCommunity(null);
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : "Unable to update community membership.");
      setBusyCommunity(null);
    }
  }

  return (
    <>
      <PageHeader
        eyebrow="Find your people"
        title="Communities"
        description="Join communities to connect with people exploring healthspan, science, and research."
      />
      {error && <p className="mb-4 text-sm text-destructive" role="alert">{error}</p>}
      {loading && communities.length === 0 && <p className="text-sm text-muted-foreground">Loading communities…</p>}
      {!loading && communities.length === 0 && !error && <p className="text-sm text-muted-foreground">No communities are available yet.</p>}
      <section className="grid gap-4 md:grid-cols-2" aria-label="Communities">
        {communities.map((community) => (
          <Card className="gap-0 rounded-2xl border-border py-0 shadow-sm" id={`community-${community.id}`} key={community.id}>
            <CardHeader className="gap-3 px-5 pt-5 sm:px-6 sm:pt-6">
              <Badge className="w-fit font-medium" variant="secondary">{community.topic}</Badge>
              <CardTitle className="text-lg text-primary">{community.name}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 p-5 pt-3 sm:px-6 sm:pb-6">
              <p className="text-sm leading-6 text-muted-foreground">{community.description}</p>
              <div className="flex items-center justify-between gap-3">
                <p className="text-xs text-muted-foreground">{community.member_count.toLocaleString()} members</p>
                <div className="flex items-center gap-2">
                  <Link href={`/communities/${community.id}`}>
                    <Button size="sm" type="button" variant="outline">Open</Button>
                  </Link>
                  {user && (
                  <Button
                    disabled={busyCommunity === community.id}
                    onClick={() => void toggleMembership(community)}
                    size="sm"
                    type="button"
                    variant={community.is_member ? "outline" : "default"}
                  >
                    {busyCommunity === community.id ? "Updating…" : community.is_member ? "Leave" : "Join"}
                  </Button>
                  )}
                </div>
              </div>
              {!user && status === "unauthenticated" && <p className="text-xs text-muted-foreground">Sign in to join this community.</p>}
            </CardContent>
          </Card>
        ))}
      </section>
    </>
  );
}
