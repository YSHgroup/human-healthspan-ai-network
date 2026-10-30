"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  ArrowRight,
  ArrowUpRight,
  BookOpenCheck,
  FlaskConical,
  RefreshCw,
  Sparkles,
  UsersRound,
} from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
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
  if (!value) return "Syncing your network";
  return `Updated ${value.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}`;
}

function ActivityChart({ data }: { data: DashboardSummary["activity"] }) {
  const chartData = data.map((item) => ({ ...item, dayLabel: formatDay(item.day) }));

  return (
    <div
      aria-label={`Daily post activity for the last seven days: ${data.map((item) => `${formatDay(item.day)} ${item.post_count}`).join(", ")}`}
      className="h-[205px] w-full"
      role="img"
    >
      <ResponsiveContainer height="100%" width="100%">
        <AreaChart data={chartData} margin={{ top: 8, right: 4, bottom: 0, left: -24 }}>
          <defs>
            <linearGradient id="activity-fill" x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stopColor="#58a9e3" stopOpacity={0.28} />
              <stop offset="95%" stopColor="#58a9e3" stopOpacity={0.015} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#e8eef2" strokeDasharray="3 5" vertical={false} />
          <XAxis
            axisLine={false}
            dataKey="dayLabel"
            tick={{ fill: "#82909b", fontSize: 11 }}
            tickLine={false}
            tickMargin={10}
          />
          <YAxis allowDecimals={false} axisLine={false} tick={{ fill: "#a1adb5", fontSize: 10 }} tickLine={false} width={30} />
          <Tooltip
            contentStyle={{
              background: "rgba(255,255,255,.96)",
              border: "1px solid #e3ebe9",
              borderRadius: 12,
              boxShadow: "0 12px 30px rgba(20,54,49,.12)",
              fontSize: 12,
            }}
            formatter={(value) => [`${value} posts`, "Community activity"]}
            labelStyle={{ color: "#4b5c62", fontWeight: 600, marginBottom: 4 }}
          />
          <Area
            activeDot={{ fill: "#287fba", r: 5, stroke: "#fff", strokeWidth: 3 }}
            dataKey="post_count"
            fill="url(#activity-fill)"
            isAnimationActive
            stroke="#287fba"
            strokeLinecap="round"
            strokeWidth={3}
            type="monotone"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

function StatCard({
  icon: Icon,
  label,
  value,
  detail,
  tone,
}: {
  icon: typeof UsersRound;
  label: string;
  value: number | string;
  detail: string;
  tone: "mint" | "blue" | "amber" | "violet";
}) {
  const tones = {
    mint: "bg-[#e7f3fc] text-[#287fba] ring-[#287fba]/10",
    blue: "bg-[#eaf2ff] text-[#4779ca] ring-[#4779ca]/10",
    amber: "bg-[#fff4df] text-[#c88932] ring-[#c88932]/10",
    violet: "bg-[#f1edff] text-[#8066c7] ring-[#8066c7]/10",
  };

  return (
    <Card className="group relative overflow-hidden rounded-[1.35rem] border-[#e6edeb] bg-white shadow-[0_8px_24px_rgba(27,65,57,.035)] transition-all duration-300 hover:-translate-y-1 hover:border-[#cbded8] hover:shadow-[0_16px_34px_rgba(27,65,57,.09)]">
      <CardContent className="relative p-4 sm:p-5">
        <div className="flex items-start justify-between gap-2">
          <span className="pt-1 text-[11px] font-semibold uppercase tracking-[.09em] text-[#7b898d] sm:text-xs">{label}</span>
          <span className={`flex size-9 items-center justify-center rounded-xl ring-1 transition-transform duration-300 group-hover:scale-105 ${tones[tone]}`}>
            <Icon aria-hidden="true" className="size-[17px]" />
          </span>
        </div>
        <p className="mt-4 text-3xl font-semibold tracking-[-.045em] text-[#18332f] sm:text-[2rem]">{value}</p>
        <p className="mt-1.5 truncate text-xs text-[#8a9798]">{detail}</p>
      </CardContent>
    </Card>
  );
}

function LoadingCard() {
  return (
    <Card aria-hidden="true" className="animate-pulse rounded-2xl border-[#e6edeb]">
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
    <div className="dashboard-page space-y-7 sm:space-y-9">
      <section className="dashboard-hero relative isolate overflow-hidden rounded-[1.8rem] px-6 py-7 text-white sm:rounded-[2rem] sm:px-9 sm:py-9 lg:px-11 lg:py-10">
        <div aria-hidden="true" className="dashboard-orb dashboard-orb-one" />
        <div aria-hidden="true" className="dashboard-orb dashboard-orb-two" />
        <div className="relative grid items-center gap-8 lg:grid-cols-[minmax(0,1.3fr)_minmax(15rem,.7fr)]">
          <div className="max-w-2xl">
            <div className="mb-6 flex flex-wrap items-center gap-2.5">
              <Badge className="gap-1.5 rounded-full border-white/15 bg-white/10 px-3 py-1 text-[11px] font-medium text-white backdrop-blur-md hover:bg-white/10" variant="outline">
                <span aria-hidden="true" className="relative flex size-2">
                  <span className="absolute inline-flex size-full animate-ping rounded-full bg-emerald-300 opacity-60" />
                  <span className="relative inline-flex size-2 rounded-full bg-emerald-300" />
                </span>
                Network pulse
              </Badge>
              <span className="text-xs text-white/60">{formatRefreshTime(updatedAt)}</span>
            </div>
            <p className="text-sm font-medium tracking-wide text-[#b8f1dc]">{greeting()}, {firstName(displayName)}</p>
            <h1 className="mt-2 max-w-xl text-[2rem] font-semibold leading-[1.08] tracking-[-.04em] sm:text-5xl">
              Better healthspan, <span className="text-[#a5ead4]">built together.</span>
            </h1>
            <p className="mt-4 max-w-lg text-sm leading-6 text-[#e2f2ed]/75 sm:text-[15px]">
              Connect with curious minds, exchange ideas, and help move health research forward.
            </p>
            <div className="mt-7 flex flex-wrap items-center gap-3">
              <Link href="/discover">
                <Button className="h-11 rounded-xl bg-[#c4f1df] px-4 font-semibold text-[#123e36] shadow-[0_8px_24px_rgba(4,20,19,.18)] transition-transform hover:-translate-y-0.5 hover:bg-white">
                  Explore the network <ArrowRight aria-hidden="true" />
                </Button>
              </Link>
              <Button
                className="h-11 rounded-xl border-white/20 bg-white/[.07] px-4 text-white backdrop-blur hover:bg-white/[.14] hover:text-white"
                onClick={() => document.getElementById("post-body")?.focus()}
                type="button"
                variant="outline"
              >
                <Sparkles aria-hidden="true" /> Share an idea
              </Button>
            </div>
          </div>

          <div aria-label="Healthspan Network connects people, science, and ideas" className="dashboard-orbit-card relative mx-auto hidden w-full max-w-[19rem] rounded-[1.65rem] border border-white/15 bg-white/[.07] p-5 shadow-[0_24px_70px_rgba(3,25,24,.2)] backdrop-blur-xl lg:block">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-[.19em] text-white/55">The network effect</p>
                <p className="mt-1 text-sm font-medium text-white">One connected community</p>
              </div>
              <span className="flex size-9 items-center justify-center rounded-xl bg-[#c4f1df]/15 text-[#c4f1df]">
                <Activity aria-hidden="true" className="size-[18px]" />
              </span>
            </div>
            <div className="network-ripple relative mt-5 flex h-[8.5rem] items-center justify-center">
              <span className="absolute size-[7.5rem] rounded-full border border-white/10" />
              <span className="absolute size-[5.5rem] rounded-full border border-white/15" />
              <span className="absolute size-[3.55rem] rounded-full bg-[#a5ead4]/15 shadow-[0_0_34px_rgba(165,234,212,.22)]" />
              <span className="relative flex size-12 items-center justify-center rounded-2xl bg-gradient-to-br from-[#d6fff0] to-[#80d9bf] text-[#155447] shadow-lg">
                <Sparkles aria-hidden="true" className="size-5" />
              </span>
              <span className="absolute left-[22%] top-[21%] size-2 rounded-full bg-[#e6c998] shadow-[0_0_12px_#e6c998]" />
              <span className="absolute right-[21%] top-[31%] size-2.5 rounded-full bg-[#b0c9ff] shadow-[0_0_12px_#b0c9ff]" />
              <span className="absolute bottom-[17%] left-[35%] size-1.5 rounded-full bg-[#d6fff0]" />
              <span className="absolute bottom-[20%] right-[27%] size-2 rounded-full bg-[#f0c6a9]" />
            </div>
            <div className="grid grid-cols-3 gap-2 border-t border-white/10 pt-4 text-center">
              <div><p className="text-xs font-semibold text-white">People</p><p className="mt-0.5 text-[10px] text-white/50">Connect</p></div>
              <div><p className="text-xs font-semibold text-white">Science</p><p className="mt-0.5 text-[10px] text-white/50">Explore</p></div>
              <div><p className="text-xs font-semibold text-white">Ideas</p><p className="mt-0.5 text-[10px] text-white/50">Advance</p></div>
            </div>
          </div>
        </div>
      </section>

      <section aria-label="Network overview" className="grid grid-cols-2 gap-3 sm:gap-4 xl:grid-cols-4">
        <StatCard detail="Shared across the network" icon={Sparkles} label="Posts this week" tone="mint" value={summary?.posts_last_7_days ?? "—"} />
        <StatCard detail="Growing through discovery" icon={UsersRound} label="Active members" tone="blue" value={summary?.active_members ?? "—"} />
        <StatCard detail={summary ? `You’ve joined ${summary.your_communities}` : "Across the network"} icon={UsersRound} label="Communities" tone="amber" value={summary ? summary.active_communities : communities.length || "—"} />
        <StatCard detail="Projects you can access" icon={FlaskConical} label="Research projects" tone="violet" value={summary?.accessible_projects ?? "—"} />
      </section>

      {error && (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-destructive/20 bg-destructive/[.045] px-4 py-3.5" role="alert">
          <p className="text-sm text-destructive">{error}</p>
          <Button className="rounded-xl" disabled={refreshing} onClick={() => void loadDashboard(true)} size="sm" type="button" variant="outline">
            Retry
          </Button>
        </div>
      )}

      <div className="grid items-start gap-6 xl:grid-cols-[minmax(0,1fr)_20rem] xl:gap-7">
        <section aria-label="Your community feed" className="min-w-0 space-y-5">
          <section aria-label="Share with your network" className="dashboard-composer" id="share-a-thought">
            <PostComposer onPostCreated={() => void loadDashboard(true)} />
          </section>
          <div className="flex items-end justify-between gap-3 pb-1">
            <div>
              <div className="mb-1.5 flex items-center gap-2">
                <span className="size-1.5 rounded-full bg-[#36a98d]" />
                <span className="text-[10px] font-semibold uppercase tracking-[.17em] text-[#78918a]">From your network</span>
              </div>
              <h2 className="text-2xl font-semibold tracking-[-.035em] text-[#1b3430]">Community feed</h2>
              <p className="mt-1 text-sm text-[#7b8987]">Fresh perspectives and thoughtful conversations.</p>
            </div>
            <Button
              aria-label="Refresh community feed"
              className="size-10 rounded-xl border-[#e0e9e5] bg-white text-[#526c65] shadow-sm hover:bg-[#eff7f3]"
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
            <Card className="rounded-[1.5rem] border-dashed border-[#d9e7e1] bg-white/70">
              <CardContent className="flex flex-col items-center px-6 py-11 text-center">
                <span className="mb-4 flex size-14 items-center justify-center rounded-[1.2rem] bg-[#e7f3fc] text-[#287fba]">
                  <BookOpenCheck aria-hidden="true" className="size-6" />
                </span>
                <h3 className="font-semibold text-[#24423a]">Start a thoughtful conversation</h3>
                <p className="mt-1 max-w-sm text-sm text-[#7b8987]">Share a question or join a community to get the discussion started.</p>
                <Link className="mt-4 text-sm font-semibold text-[#287fba] hover:underline" href="/communities">Browse communities</Link>
              </CardContent>
            </Card>
          )}
          <section className="grid gap-4" aria-label="Latest network posts">
            {posts.map((post) => <FeedPostCard key={post.id} post={post} />)}
          </section>
          {posts.length > 0 && (
            <div className="flex justify-center pt-1">
              <Link href="/discover">
                <Button className="rounded-xl text-[#54756b] hover:bg-[#eaf4ef] hover:text-[#176b59]" variant="ghost">
                  Discover more conversations <ArrowRight aria-hidden="true" />
                </Button>
              </Link>
            </div>
          )}
        </section>

        <aside aria-label="Your network snapshot" className="space-y-5">
          <Card className="overflow-hidden rounded-[1.5rem] border-[#e4ece8] bg-white shadow-[0_8px_24px_rgba(27,65,57,.035)]">
            <CardHeader className="flex flex-row items-start justify-between space-y-0 px-5 pb-0 pt-5">
              <div>
                <div className="mb-1.5 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-[.15em] text-[#78918a]">
                  <Activity aria-hidden="true" className="size-3.5 text-[#287fba]" /> This week
                </div>
                <CardTitle className="text-base font-semibold tracking-tight text-[#233c36]">Network activity</CardTitle>
                <p className="mt-1 text-xs text-[#87938f]">Community posts over the last 7 days</p>
              </div>
              <span aria-hidden="true" className="mt-1 flex size-2.5 rounded-full bg-[#36a98d] shadow-[0_0_0_4px_rgba(54,169,141,.12)]" />
            </CardHeader>
            <CardContent className="px-4 pb-4 pt-3 sm:px-5">
              {summary ? (
                <>
                  <div className="flex items-baseline gap-2 px-1">
                    <span className="text-[2rem] font-semibold tracking-[-.055em] text-[#183b32]">{summary.posts_last_7_days}</span>
                    <span className="text-xs font-medium text-[#899590]">posts this week</span>
                  </div>
                  <ActivityChart data={summary.activity} />
                </>
              ) : (
                <div className="flex h-[205px] items-center justify-center rounded-xl bg-[#f5f8f6] px-4 text-center text-sm text-[#899590]">
                  {user ? "Activity data is not available right now." : "Sign in to see your network activity."}
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="rounded-[1.5rem] border-[#e4ece8] bg-white shadow-[0_8px_24px_rgba(27,65,57,.035)]">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 px-5 pb-2 pt-5">
              <div>
                <div className="mb-1.5 text-[10px] font-semibold uppercase tracking-[.15em] text-[#78918a]">Find your people</div>
                <CardTitle className="text-base font-semibold tracking-tight text-[#233c36]">Communities</CardTitle>
              </div>
              <Link aria-label="Browse all communities" className="flex size-8 items-center justify-center rounded-lg bg-[#eaf4fc] text-[#287fba] transition-colors hover:bg-[#dceefa]" href="/communities">
                <ArrowUpRight aria-hidden="true" className="size-4" />
              </Link>
            </CardHeader>
            <CardContent className="space-y-1 px-3 pb-4">
              {(user ? activeCommunities : communities).slice(0, 4).map((community, index) => (
                <Link
                  className="group flex items-center justify-between gap-2 rounded-xl px-2.5 py-2.5 transition-colors hover:bg-[#f4f8f5]"
                  href={`/communities/${community.id}`}
                  key={community.id}
                >
                  <span className="flex min-w-0 items-center gap-3">
                    <span className={`flex size-9 shrink-0 items-center justify-center rounded-xl text-[11px] font-semibold ${["bg-[#e7f5ee] text-[#398c70]", "bg-[#edf1fc] text-[#667dc0]", "bg-[#fbf0df] text-[#b08243]", "bg-[#f2ebf8] text-[#8d68a9]"][index % 4]}`}>
                      {community.name.slice(0, 1).toUpperCase()}
                    </span>
                    <span className="min-w-0">
                      <span className="block truncate text-sm font-medium text-[#314841]">{community.name}</span>
                      <span className="block text-[11px] text-[#8a9691]">{community.member_count.toLocaleString()} members</span>
                    </span>
                  </span>
                  <ArrowRight aria-hidden="true" className="size-4 shrink-0 text-[#9ba9a3] transition-transform group-hover:translate-x-0.5 group-hover:text-[#287fba]" />
                </Link>
              ))}
              {loading && communities.length === 0 && <p className="px-3 py-3 text-sm text-[#87938f]">Loading communities…</p>}
              {!loading && communities.length === 0 && <p className="px-3 py-3 text-sm text-[#87938f]">Communities aren’t available right now.</p>}
              {user && activeCommunities.length === 0 && communities.length > 0 && <p className="px-3 pt-2 text-xs text-[#87938f]">Join your first community to make it yours.</p>}
              {user && activeCommunities.length === 0 && communities.length > 0 && (
                <Link className="mt-2 inline-flex items-center gap-1 px-3 text-sm font-semibold text-[#287fba] hover:underline" href="/communities">
                  Find a community <ArrowRight aria-hidden="true" className="size-3.5" />
                </Link>
              )}
              {!user && communities.length > 0 && (
                <Link className="mt-2 inline-flex items-center gap-1 px-3 text-sm font-semibold text-[#287fba] hover:underline" href="/communities">
                  Explore communities <ArrowRight aria-hidden="true" className="size-3.5" />
                </Link>
              )}
            </CardContent>
          </Card>

          <Card className="research-spotlight overflow-hidden rounded-[1.5rem] border-0 shadow-[0_12px_32px_rgba(16,87,72,.12)]">
            <CardContent className="relative p-5">
              <div aria-hidden="true" className="absolute -right-8 -top-10 size-32 rounded-full border border-white/10" />
              <div aria-hidden="true" className="absolute -right-1 -top-3 size-20 rounded-full border border-white/10" />
              <span className="relative mb-4 flex size-10 items-center justify-center rounded-xl bg-white/15 text-[#c8f3df] ring-1 ring-white/10">
                <FlaskConical aria-hidden="true" className="size-[18px]" />
              </span>
              <div className="relative">
                <p className="text-[10px] font-semibold uppercase tracking-[.16em] text-[#c5eadc]/70">From curiosity to evidence</p>
                <h3 className="mt-1.5 text-lg font-semibold leading-snug tracking-tight text-white">Good questions move science forward.</h3>
                <p className="mt-2 text-sm leading-5 text-[#e2f4ed]/70">Explore research projects and collaborate around the evidence.</p>
                <Link className="mt-4 inline-flex items-center gap-1.5 text-sm font-semibold text-[#c8f3df] transition-colors hover:text-white" href="/research">
                  {user ? `${projects.length} projects you can access` : "Explore research"}
                  <ArrowRight aria-hidden="true" className="size-3.5" />
                </Link>
              </div>
            </CardContent>
          </Card>

          <p className="px-1 text-[11px] leading-5 text-[#8a9691]">
            Health and research conversations are for learning and collaboration, not a substitute for professional medical advice.
          </p>
        </aside>
      </div>
    </div>
  );
}
