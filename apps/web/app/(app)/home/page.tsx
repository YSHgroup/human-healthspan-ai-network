"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import {
  ArrowRight,
  BookOpenCheck,
  FlaskConical,
  RefreshCw,
  Sparkles,
  UsersRound,
} from "lucide-react";
import FeedPostCard from "../../components/FeedPostCard";
import PostComposer from "../../components/PostComposer";
import { Badge } from "@healthspan/ui/badge";
import { Button } from "@healthspan/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  getCommunities,
  getDashboardSummary,
  getFeed,
  getResearchProjects,
  type Community,
  type DashboardSummary,
  type FeedPost,
  type ResearchProject,
} from "@/lib/api";
import { useSession } from "@/lib/session";

function firstName(displayName?: string): string {
  return displayName?.trim().split(/\s+/)[0] || "there";
}

function greeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 18) return "Good afternoon";
  return "Good evening";
}

function formatDay(value: string): string {
  return new Intl.DateTimeFormat(undefined, { weekday: "short" }).format(new Date(`${value}T12:00:00Z`));
}

function formatRefreshTime(value: Date | null): string {
  if (!value) return "Connecting to your network";
  return `Updated ${value.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}`;
}

function ActivityChart({ data }: { data: DashboardSummary["activity"] }) {
  const maxCount = Math.max(1, ...data.map((item) => item.post_count));

  return (
    <div
      aria-label={`Daily post activity for the last seven days: ${data.map((item) => `${formatDay(item.day)} ${item.post_count}`).join(", ")}`}
      className="flex h-36 items-end gap-2"
      role="img"
    >
      {data.map((item) => {
        const height = Math.max(10, (item.post_count / maxCount) * 100);
        return (
          <div className="flex h-full flex-1 flex-col items-center justify-end gap-2" key={item.day}>
            <span className="text-[10px] font-medium text-muted-foreground">{item.post_count || ""}</span>
            <div className="flex h-24 w-full items-end overflow-hidden rounded-md bg-muted/70">
              <div
                className="w-full rounded-md bg-gradient-to-t from-primary to-teal-500 transition-[height] duration-700 ease-out"
                style={{ height: `${height}%` }}
                title={`${item.post_count} posts on ${item.day}`}
              />
            </div>
            <span className="text-[10px] text-muted-foreground">{formatDay(item.day)}</span>
          </div>
        );
      })}
    </div>
  );
}

function StatCard({
  icon: Icon,
  label,
  value,
  detail,
}: {
  icon: typeof UsersRound;
  label: string;
  value: number | string;
  detail: string;
}) {
  return (
    <Card className="group relative overflow-hidden rounded-2xl border-border/80 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md">
      <CardContent className="p-4 sm:p-5">
        <div className="flex items-start justify-between gap-2">
          <span className="text-xs font-medium text-muted-foreground sm:text-sm">{label}</span>
          <span className="flex size-8 items-center justify-center rounded-xl bg-primary/5 text-primary transition-colors group-hover:bg-primary/10">
            <Icon aria-hidden="true" className="size-4" />
          </span>
        </div>
        <p className="mt-4 text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">{value}</p>
        <p className="mt-1 text-[11px] leading-4 text-muted-foreground sm:text-xs">{detail}</p>
      </CardContent>
    </Card>
  );
}

function LoadingCard() {
  return (
    <Card aria-hidden="true" className="animate-pulse rounded-2xl">
      <CardContent className="space-y-4 p-5">
        <div className="h-4 w-2/5 rounded bg-muted" />
        <div className="h-3 w-full rounded bg-muted" />
        <div className="h-3 w-4/5 rounded bg-muted" />
      </CardContent>
    </Card>
  );
}

export default function HomePage() {
  const { user, status: sessionStatus } = useSession();
  const [posts, setPosts] = useState<FeedPost[]>([]);
  const [communities, setCommunities] = useState<Community[]>([]);
  const [projects, setProjects] = useState<ResearchProject[]>([]);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [updatedAt, setUpdatedAt] = useState<Date | null>(null);

  const loadDashboard = useCallback(async (background = false) => {
    if (background) setRefreshing(true);
    else setLoading(true);
    setError("");

    const [feedResult, communityResult, summaryResult, projectResult] = await Promise.allSettled([
      getFeed(8),
      getCommunities(),
      user ? getDashboardSummary() : Promise.resolve(null),
      user ? getResearchProjects() : Promise.resolve([]),
    ]);

    const failures: string[] = [];
    if (feedResult.status === "fulfilled") setPosts(feedResult.value);
    else failures.push("Could not load the community feed.");
    if (communityResult.status === "fulfilled") setCommunities(communityResult.value);
    else failures.push("Could not load communities.");
    if (summaryResult.status === "fulfilled") setSummary(summaryResult.value);
    else failures.push("Could not load your network summary.");
    if (projectResult.status === "fulfilled") setProjects(projectResult.value);
    else failures.push("Could not load your research projects.");

    setError(failures.join(" "));
    setUpdatedAt(new Date());
    setLoading(false);
    setRefreshing(false);
  }, [user]);

  useEffect(() => {
    if (sessionStatus === "loading") return;
    void loadDashboard();
    const intervalId = window.setInterval(() => void loadDashboard(true), 60_000);
    return () => window.clearInterval(intervalId);
  }, [sessionStatus, loadDashboard]);

  const activeCommunities = communities.filter((community) => community.is_member);
  const displayName = user?.profile?.display_name;

  return (
    <div className="space-y-7">
      <section className="relative isolate overflow-hidden rounded-[1.75rem] bg-gradient-to-br from-[#08264f] via-[#0d3d69] to-[#0d6b69] px-6 py-7 text-white shadow-lg shadow-primary/10 sm:px-9 sm:py-9">
        <div aria-hidden="true" className="pointer-events-none absolute -right-10 -top-20 -z-10 size-64 rounded-full bg-teal-300/15 blur-3xl" />
        <div aria-hidden="true" className="pointer-events-none absolute -bottom-28 left-1/3 -z-10 size-56 rounded-full bg-sky-300/15 blur-3xl" />
        <div className="flex flex-col gap-7 md:flex-row md:items-end md:justify-between">
          <div className="max-w-2xl">
            <div className="mb-4 flex flex-wrap items-center gap-2">
              <Badge className="border-white/20 bg-white/10 text-white hover:bg-white/10" variant="outline">
                <span aria-hidden="true" className="mr-1.5 size-1.5 animate-pulse rounded-full bg-emerald-300" />
                Your network, live
              </Badge>
              <span className="text-xs text-white/65">{formatRefreshTime(updatedAt)}</span>
            </div>
            <p className="text-sm font-medium text-teal-100">{greeting()}, {firstName(displayName)}</p>
            <h1 className="mt-1 text-3xl font-semibold tracking-tight sm:text-4xl">A healthier future starts together.</h1>
            <p className="mt-3 max-w-xl text-sm leading-6 text-sky-50/80 sm:text-base">
              Discover thoughtful conversations, connect with your communities, and turn great questions into research.
            </p>
          </div>
          <div className="flex shrink-0 flex-wrap gap-3">
            <Link href="/discover">
              <Button className="border-white/20 bg-white/10 text-white hover:bg-white/20" variant="outline">
                Explore network <ArrowRight aria-hidden="true" />
              </Button>
            </Link>
            <Button
              className="bg-white text-primary hover:bg-white/90"
              onClick={() => document.getElementById("post-body")?.focus()}
              type="button"
            >
              Share a thought
            </Button>
          </div>
        </div>
      </section>

      <section aria-label="Network overview" className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard
          detail="In the last seven days"
          icon={Sparkles}
          label="Network posts"
          value={summary?.posts_last_7_days ?? "—"}
        />
        <StatCard
          detail="Across the network"
          icon={UsersRound}
          label="Active members"
          value={summary?.active_members ?? "—"}
        />
        <StatCard
          detail={summary ? `You’ve joined ${summary.your_communities}` : "Sign in to track your groups"}
          icon={UsersRound}
          label="Active communities"
          value={summary ? summary.active_communities : communities.length || "—"}
        />
        <StatCard
          detail="You can access"
          icon={FlaskConical}
          label="Research projects"
          value={summary?.accessible_projects ?? "—"}
        />
      </section>

      {error && (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-destructive/20 bg-destructive/5 px-4 py-3" role="alert">
          <p className="text-sm text-destructive">{error}</p>
          <Button disabled={refreshing} onClick={() => void loadDashboard(true)} size="sm" type="button" variant="outline">
            Retry
          </Button>
        </div>
      )}

      <div className="grid items-start gap-6 xl:grid-cols-[minmax(0,1fr)_19rem]">
        <section aria-label="Your community feed" className="min-w-0 space-y-5">
          <section aria-label="Share with your network" id="share-a-thought">
            <PostComposer onPostCreated={() => void loadDashboard(true)} />
          </section>
          <div className="flex items-center justify-between gap-3">
            <div>
              <h2 className="text-xl font-semibold tracking-tight">Community feed</h2>
              <p className="text-sm text-muted-foreground">Fresh ideas and questions from across the network.</p>
            </div>
            <Button
              aria-label="Refresh community feed"
              disabled={refreshing}
              onClick={() => void loadDashboard(true)}
              size="icon"
              type="button"
              variant="outline"
            >
              <RefreshCw aria-hidden="true" className={refreshing ? "animate-spin" : ""} />
            </Button>
          </div>
          {loading && posts.length === 0 && <><LoadingCard /><LoadingCard /></>}
          {!loading && posts.length === 0 && !error && (
            <Card className="rounded-2xl border-dashed">
              <CardContent className="flex flex-col items-center px-6 py-10 text-center">
                <span className="mb-3 flex size-12 items-center justify-center rounded-2xl bg-primary/5 text-primary">
                  <BookOpenCheck aria-hidden="true" className="size-6" />
                </span>
                <h3 className="font-semibold">Your feed is ready for its first conversation</h3>
                <p className="mt-1 max-w-sm text-sm text-muted-foreground">Share a thoughtful question or join a community to get the discussion started.</p>
                <Link className="mt-4 text-sm font-medium text-primary hover:underline" href="/communities">Browse communities</Link>
              </CardContent>
            </Card>
          )}
          <section className="grid gap-4" aria-label="Latest network posts">
            {posts.map((post) => <FeedPostCard key={post.id} post={post} />)}
          </section>
          {posts.length > 0 && (
            <div className="flex justify-center">
              <Link href="/discover">
                <Button variant="ghost">Discover more conversations <ArrowRight aria-hidden="true" /></Button>
              </Link>
            </div>
          )}
        </section>

        <aside aria-label="Your network snapshot" className="space-y-5">
          <Card className="rounded-2xl shadow-sm">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div>
                <CardTitle className="text-base">Network activity</CardTitle>
                <p className="mt-1 text-xs text-muted-foreground">Posts created · last 7 days</p>
              </div>
              <span aria-hidden="true" className="size-2 animate-pulse rounded-full bg-emerald-500" />
            </CardHeader>
            <CardContent>
              {summary ? (
                <>
                  <div className="mb-2 flex items-baseline gap-2">
                    <span className="text-2xl font-semibold tracking-tight">{summary.posts_last_7_days}</span>
                    <span className="text-xs text-muted-foreground">posts this week</span>
                  </div>
                  <ActivityChart data={summary.activity} />
                </>
              ) : (
                <div className="flex h-36 items-center justify-center rounded-xl bg-muted/40 px-4 text-center text-sm text-muted-foreground">
                  {user ? "Activity data is not available right now." : "Sign in to see your network activity."}
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="rounded-2xl shadow-sm">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div>
                <CardTitle className="text-base">Your communities</CardTitle>
                <p className="mt-1 text-xs text-muted-foreground">A place for good questions</p>
              </div>
              <Link aria-label="Browse all communities" className="text-primary hover:text-primary/80" href="/communities">
                <ArrowRight aria-hidden="true" className="size-4" />
              </Link>
            </CardHeader>
            <CardContent className="space-y-1">
              {(user ? activeCommunities : communities).slice(0, 4).map((community) => (
                <Link
                  className="flex items-center justify-between gap-2 rounded-xl px-2 py-2.5 transition-colors hover:bg-muted/70"
                  href={`/communities/${community.id}`}
                  key={community.id}
                >
                  <span className="min-w-0">
                    <span className="block truncate text-sm font-medium">{community.name}</span>
                    <span className="block text-xs text-muted-foreground">{community.member_count.toLocaleString()} members</span>
                  </span>
                  <ArrowRight aria-hidden="true" className="size-4 shrink-0 text-muted-foreground" />
                </Link>
              ))}
              {loading && communities.length === 0 && <p className="px-2 py-3 text-sm text-muted-foreground">Loading communities…</p>}
              {!loading && communities.length === 0 && <p className="px-2 py-3 text-sm text-muted-foreground">Communities aren’t available right now.</p>}
              {user && activeCommunities.length === 0 && communities.length > 0 && (
                <p className="px-2 py-3 text-sm text-muted-foreground">Join your first community to make it yours.</p>
              )}
              {user && activeCommunities.length === 0 && communities.length > 0 && (
                <Link className="mt-1 inline-flex items-center gap-1 px-2 text-sm font-medium text-primary hover:underline" href="/communities">
                  Find a community <ArrowRight aria-hidden="true" className="size-3.5" />
                </Link>
              )}
              {!user && communities.length > 0 && (
                <Link className="mt-1 inline-flex items-center gap-1 px-2 text-sm font-medium text-primary hover:underline" href="/communities">
                  Explore communities <ArrowRight aria-hidden="true" className="size-3.5" />
                </Link>
              )}
            </CardContent>
          </Card>

          <Card className="overflow-hidden rounded-2xl border-primary/10 bg-gradient-to-br from-primary/[0.04] via-background to-teal-500/[0.06] shadow-sm">
            <CardContent className="p-5">
              <span className="mb-3 flex size-9 items-center justify-center rounded-xl bg-primary/10 text-primary">
                <FlaskConical aria-hidden="true" className="size-4" />
              </span>
              <h3 className="font-semibold">Questions become research</h3>
              <p className="mt-1 text-sm leading-5 text-muted-foreground">Create a project, collect literature, and invite collaborators to explore the evidence.</p>
              <Link className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-primary hover:underline" href="/research">
                {user ? `${projects.length} projects you can access` : "Explore research"}
                <ArrowRight aria-hidden="true" className="size-3.5" />
              </Link>
            </CardContent>
          </Card>

          <p className="px-1 text-[11px] leading-5 text-muted-foreground">
            Health and research conversations are for learning and collaboration, not a substitute for professional medical advice.
          </p>
        </aside>
      </div>
    </div>
  );
}
