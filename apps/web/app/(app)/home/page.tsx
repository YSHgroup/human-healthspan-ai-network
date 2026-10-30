"use client";

import { useCallback, useEffect, useState } from "react";
import PostComposer from "../../components/PostComposer";
import PageHeader from "../../components/PageHeader";
import FeedPostCard from "../../components/FeedPostCard";
import { Button } from "@healthspan/ui/button";
import { getFeed, type FeedPost } from "@/lib/api";

export default function HomePage() {
  const [posts, setPosts] = useState<FeedPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadFeed = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setPosts(await getFeed());
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : "Unable to load the community feed.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadFeed();
  }, [loadFeed]);

  return (
    <>
      <PageHeader
        eyebrow="Your network"
        title="Home"
        description="Questions, ideas, and conversations from across the healthspan community."
      />
      <PostComposer onPostCreated={() => void loadFeed()} />
      {error && <div className="mb-5 flex flex-wrap items-center justify-between gap-3" role="alert">
        <p className="text-sm text-destructive">{error}</p>
        <Button disabled={loading} onClick={() => void loadFeed()} size="sm" type="button" variant="outline">Retry</Button>
      </div>}
      {loading && posts.length === 0 && <p className="text-sm text-muted-foreground">Loading community posts…</p>}
      {!loading && !error && posts.length === 0 && <p className="text-sm text-muted-foreground">No posts yet. Start the conversation.</p>}
      <section className="grid gap-4" aria-label="Community feed">
        {posts.map((post) => <FeedPostCard key={post.id} post={post} />)}
      </section>
    </>
  );
}
