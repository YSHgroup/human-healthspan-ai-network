"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import PageHeader from "@/app/components/PageHeader";
import FeedPostCard from "@/app/components/FeedPostCard";
import PostComposer from "@/app/components/PostComposer";
import { Badge } from "@healthspan/ui/badge";
import { Button } from "@healthspan/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  getCommunity,
  getCommunityFeed,
  joinCommunity,
  leaveCommunity,
  type Community,
  type FeedPost,
} from "@/lib/api";
import { useSession } from "@/lib/session";

export default function CommunityDetailPage() {
  const { communityId } = useParams<{ communityId: string }>();
  const { user, status } = useSession();
  const [community, setCommunity] = useState<Community | null>(null);
  const [posts, setPosts] = useState<FeedPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const loadPage = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [nextCommunity, nextPosts] = await Promise.all([
        getCommunity(communityId),
        getCommunityFeed(communityId),
      ]);
      setCommunity(nextCommunity);
      setPosts(nextPosts);
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : "Unable to load this community.");
    } finally {
      setLoading(false);
    }
  }, [communityId]);

  useEffect(() => {
    void loadPage();
  }, [loadPage]);

  async function toggleMembership() {
    if (!community) return;
    setBusy(true);
    setError("");
    try {
      if (community.is_member) await leaveCommunity(community.id);
      else await joinCommunity(community.id);
      setCommunity(await getCommunity(community.id));
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : "Unable to update community membership.");
    } finally {
      setBusy(false);
    }
  }

  if (loading && !community) return <p className="text-sm text-muted-foreground">Loading community…</p>;
  if (!community) {
    return (
      <div className="space-y-3">
        <p className="text-sm text-destructive" role="alert">{error || "This community is unavailable."}</p>
        <Button disabled={loading} onClick={() => void loadPage()} type="button" variant="outline">Retry</Button>
        <p><Link className="text-sm text-primary hover:underline" href="/communities">Back to communities</Link></p>
      </div>
    );
  }

  return (
    <>
      <PageHeader eyebrow="Community" title={community.name} description={community.description} />
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Badge variant="secondary">{community.topic}</Badge>
          <span className="text-sm text-muted-foreground">{community.member_count.toLocaleString()} members</span>
        </div>
        {user && (
          <Button disabled={busy} onClick={() => void toggleMembership()} type="button" variant={community.is_member ? "outline" : "default"}>
            {busy ? "Updating…" : community.is_member ? "Leave community" : "Join community"}
          </Button>
        )}
      </div>
      {error && <p className="mb-4 text-sm text-destructive" role="alert">{error}</p>}
      {user && community.is_member ? (
        <PostComposer communityId={community.id} onPostCreated={() => void loadPage()} />
      ) : user ? (
        <Card className="mb-6">
          <CardContent className="p-5 text-sm text-muted-foreground">Join this community to start a discussion or question.</CardContent>
        </Card>
      ) : status === "unauthenticated" ? (
        <Card className="mb-6">
          <CardContent className="p-5 text-sm text-muted-foreground">Sign in and join this community to participate.</CardContent>
        </Card>
      ) : null}
      <section className="grid gap-4" aria-label={`${community.name} posts`}>
        {posts.map((post) => <FeedPostCard key={post.id} post={post} />)}
        {!loading && posts.length === 0 && <p className="text-sm text-muted-foreground">No posts in this community yet.</p>}
        {loading && posts.length === 0 && <p className="text-sm text-muted-foreground">Loading community posts…</p>}
      </section>
    </>
  );
}
