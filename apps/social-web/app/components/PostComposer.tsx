"use client";

import { FormEvent, useState } from "react";
import { createPost, type PostClassification } from "@/lib/api";
import { Button } from "@healthspan/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import Link from "next/link";
import { useSession } from "@/lib/session";
import { Select } from "@healthspan/ui/select";

export default function PostComposer({
  communityId,
  onPostCreated,
}: {
  communityId?: string;
  onPostCreated: () => void;
}) {
  const { user, status, error: sessionError } = useSession();
  const [body, setBody] = useState("");
  const [contentType, setContentType] = useState<"post" | "question">("post");
  const [classification, setClassification] = useState<PostClassification>("personal_experience");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const post = await createPost({
        body,
        content_type: contentType,
        classification,
        ...(communityId ? { community_id: communityId } : {}),
      });
      setBody("");
      setContentType("post");
      setClassification("personal_experience");
      onPostCreated();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to submit your post.");
    } finally {
      setIsSubmitting(false);
    }
  }

  if (status === "loading") {
    return <p className="mb-6 text-sm text-muted-foreground">Checking your account…</p>;
  }
  if (status === "unavailable") {
    return <p className="mb-6 text-sm text-destructive" role="alert">{sessionError ?? "The account service is unavailable."}</p>;
  }
  if (!user) {
    return (
      <Card className="mb-6 rounded-2xl shadow-sm">
        <CardContent className="space-y-2 p-5 sm:p-6">
          <p className="font-medium">Sign in to join the conversation.</p>
          <Link className="text-sm text-primary hover:underline" href="/login">Sign in</Link>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="mb-6 gap-0 rounded-2xl border-border py-0 shadow-sm">
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-4 p-5 sm:p-6">
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="block space-y-2 text-sm font-medium text-foreground" htmlFor="post-type">
              Share a post or question
              <Select id="post-type" onChange={(event) => setContentType(event.target.value as "post" | "question")} value={contentType}>
                <option value="post">Post</option>
                <option value="question">Question</option>
              </Select>
            </label>
            <label className="block space-y-2 text-sm font-medium text-foreground" htmlFor="post-classification">
              Content classification
              <Select id="post-classification" onChange={(event) => setClassification(event.target.value as PostClassification)} value={classification}>
                <option value="personal_experience">Personal experience</option>
                <option value="opinion">Opinion</option>
                <option value="scientific_evidence">Scientific evidence</option>
                <option value="expert_interpretation">Expert interpretation</option>
                <option value="research_hypothesis">Research hypothesis</option>
                <option value="speculation">Speculation</option>
              </Select>
            </label>
          </div>
          <Textarea
            id="post-body"
            className="min-h-28 resize-y"
            maxLength={10000}
            minLength={1}
            onChange={(event) => setBody(event.target.value)}
            placeholder="What are you thinking about?"
            required
            rows={3}
            value={body}
          />
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <small className="text-xs text-muted-foreground">Posting as {user.profile?.display_name ?? user.email}</small>
            <Button className="shrink-0" disabled={isSubmitting || !body.trim()} type="submit">
              {isSubmitting ? "Posting…" : "Post"}
            </Button>
          </div>
          {error && <p className="text-sm text-destructive" role="alert">{error}</p>}
        </CardContent>
      </form>
    </Card>
  );
}
