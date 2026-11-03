"use client";

import { FormEvent, useState } from "react";
import { Bookmark, Flag, MessageCircle, ThumbsUp } from "lucide-react";
import { Button } from "@healthspan/ui/button";
import { Badge } from "@healthspan/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import {
  bookmarkPost,
  createComment,
  getComments,
  removePostReaction,
  reportPost,
  reactToPost,
  unbookmarkPost,
  type Comment,
  type FeedPost,
} from "@/lib/api";
import { useSession } from "@/lib/session";

function humanize(value: string): string {
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export default function FeedPostCard({ post }: { post: FeedPost }) {
  const { user } = useSession();
  const [isReacted, setIsReacted] = useState(post.is_reacted);
  const [reactionCount, setReactionCount] = useState(post.reaction_count);
  const [isBookmarked, setIsBookmarked] = useState(post.is_bookmarked);
  const [comments, setComments] = useState<Comment[]>([]);
  const [commentsOpen, setCommentsOpen] = useState(false);
  const [commentBody, setCommentBody] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function toggleReaction() {
    setBusy(true);
    setError("");
    try {
      if (isReacted) {
        await removePostReaction(post.id);
        setIsReacted(false);
        setReactionCount((count) => Math.max(0, count - 1));
      } else {
        await reactToPost(post.id);
        setIsReacted(true);
        setReactionCount((count) => count + 1);
      }
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : "Unable to update your reaction.");
    } finally {
      setBusy(false);
    }
  }

  async function toggleBookmark() {
    setBusy(true);
    setError("");
    try {
      if (isBookmarked) {
        await unbookmarkPost(post.id);
        setIsBookmarked(false);
      } else {
        await bookmarkPost(post.id);
        setIsBookmarked(true);
      }
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : "Unable to update your bookmark.");
    } finally {
      setBusy(false);
    }
  }

  async function toggleComments() {
    if (commentsOpen) {
      setCommentsOpen(false);
      return;
    }
    setBusy(true);
    setError("");
    try {
      setComments(await getComments(post.id));
      setCommentsOpen(true);
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : "Unable to load comments.");
    } finally {
      setBusy(false);
    }
  }

  async function submitComment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await createComment(post.id, commentBody);
      setCommentBody("");
      setComments(await getComments(post.id));
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : "Unable to post your comment.");
    } finally {
      setBusy(false);
    }
  }

  async function submitReport() {
    const reason = window.prompt("Why are you reporting this post? (for example: spam, harassment, misinformation)");
    if (!reason?.trim()) return;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await reportPost(post.id, reason.trim());
      setNotice("Report submitted for moderator review.");
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : "Unable to submit your report.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <Card className="gap-0 rounded-2xl border-border py-0 shadow-sm" id={`post-${post.id}`}>
      <CardContent className="space-y-4 p-5 sm:p-6">
        <div className="flex items-center justify-between gap-3">
          <div className="flex min-w-0 items-center gap-3">
            <span className="flex size-10 shrink-0 items-center justify-center rounded-full bg-secondary font-semibold text-primary">
              {post.author_display_name.slice(0, 1).toUpperCase()}
            </span>
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-foreground">{post.author_display_name}</p>
              <p className="text-xs text-muted-foreground">{humanize(post.author_role)} · {formatDate(post.created_at)}</p>
            </div>
          </div>
          <Badge className="shrink-0 text-[10px] uppercase tracking-wide" variant="secondary">
            {humanize(post.content_type)} · {humanize(post.classification)}
          </Badge>
        </div>
        <p className="whitespace-pre-wrap text-sm leading-6 text-foreground/90">{post.body}</p>
        <div className="flex flex-wrap items-center gap-2 border-t pt-3">
          {user ? (
            <>
              <Button aria-pressed={isReacted} disabled={busy} onClick={() => void toggleReaction()} size="sm" type="button" variant={isReacted ? "secondary" : "outline"}>
                <ThumbsUp aria-hidden="true" /> {isReacted ? "Helpful" : "Mark helpful"} ({reactionCount})
              </Button>
              <Button aria-pressed={isBookmarked} disabled={busy} onClick={() => void toggleBookmark()} size="sm" type="button" variant={isBookmarked ? "secondary" : "outline"}>
                <Bookmark aria-hidden="true" /> {isBookmarked ? "Saved" : "Save"}
              </Button>
              <Button disabled={busy} onClick={() => void submitReport()} size="sm" type="button" variant="ghost">
                <Flag aria-hidden="true" /> Report
              </Button>
            </>
          ) : null}
          <Button aria-expanded={commentsOpen} disabled={busy} onClick={() => void toggleComments()} size="sm" type="button" variant="ghost">
            <MessageCircle aria-hidden="true" /> Comments ({post.comment_count})
          </Button>
        </div>
        {notice && <p className="text-sm text-green-700" role="status">{notice}</p>}
        {error && <p className="text-sm text-destructive" role="alert">{error}</p>}
        {commentsOpen && (
          <div className="space-y-4 border-t pt-4">
            {comments.map((comment) => (
              <article className="rounded-lg bg-muted/50 p-3" key={comment.id}>
                <div className="flex justify-between gap-3 text-xs">
                  <span className="font-semibold">{comment.author_display_name}</span>
                  <time className="text-muted-foreground" dateTime={comment.created_at}>{formatDate(comment.created_at)}</time>
                </div>
                <p className="mt-2 whitespace-pre-wrap text-sm">{comment.body}</p>
              </article>
            ))}
            {comments.length === 0 && <p className="text-sm text-muted-foreground">No comments yet.</p>}
            {user && (
              <form className="space-y-2" onSubmit={submitComment}>
                <label className="sr-only" htmlFor={`comment-${post.id}`}>Write a comment</label>
                <Textarea id={`comment-${post.id}`} maxLength={5000} onChange={(event) => setCommentBody(event.target.value)} placeholder="Write a thoughtful comment…" required value={commentBody} />
                <Button disabled={busy || !commentBody.trim()} size="sm" type="submit">{busy ? "Posting…" : "Comment"}</Button>
              </form>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
