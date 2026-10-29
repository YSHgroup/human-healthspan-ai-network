import PostComposer from "../../components/PostComposer";
import PageHeader from "../../components/PageHeader";
import { getFeed } from "../../../lib/data";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@healthspan/ui/badge";
import { Card, CardContent } from "@/components/ui/card";

export default async function HomePage() {
  const posts = await getFeed();

  return (
    <>
      <PageHeader
        eyebrow="Your network"
        title="Home"
        description="Questions, ideas, and conversations from across the healthspan community."
      />
      <PostComposer />
      <section className="grid gap-4" aria-label="Community feed">
        {posts.map((post) => (
          <Card className="gap-0 rounded-2xl border-border py-0 shadow-sm" key={post.id}>
            <CardContent className="space-y-4 p-5 sm:p-6">
              <div className="flex items-center gap-3">
                <Avatar className="size-10 rounded-full">
                  <AvatarFallback className="rounded-full bg-secondary font-semibold text-primary">
                    {post.author_name.slice(0, 1)}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <p className="text-sm font-semibold text-foreground">{post.author_name}</p>
                  <p className="text-xs text-muted-foreground">{post.role} · {post.posted_at}</p>
                </div>
              </div>
              <p className="whitespace-pre-wrap text-sm leading-6 text-foreground/90">{post.body}</p>
              <Badge className="text-[10px] uppercase tracking-wide" variant="secondary">Sample feed post</Badge>
            </CardContent>
          </Card>
        ))}
      </section>
    </>
  );
}
