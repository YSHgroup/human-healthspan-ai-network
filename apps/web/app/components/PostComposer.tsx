"use client";

import { FormEvent, useState } from "react";
import { createPost } from "../../lib/api";
import { Button } from "@healthspan/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";

const TEMPORARY_AUTHOR_ID = "demo-user";

export default function PostComposer() {
  const [body, setBody] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    setError("");
    setIsSubmitting(true);

    try {
      const post = await createPost({ author_id: TEMPORARY_AUTHOR_ID, body });
      setBody("");
      setMessage(`Demo API response received (ID: ${post.id}). Posts are not saved yet.`);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to submit your post.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Card className="mb-6 gap-0 rounded-2xl border-border py-0 shadow-sm">
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-4 p-5 sm:p-6">
          <label className="block text-sm font-medium text-foreground" htmlFor="post-body">
            Share a question or reflection
          </label>
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
            <small className="text-xs text-muted-foreground">
              Temporary demo author ID: {TEMPORARY_AUTHOR_ID} · authentication is not available and posts are not saved yet.
            </small>
            <Button className="shrink-0" disabled={isSubmitting || !body.trim()} type="submit">
              {isSubmitting ? "Posting…" : "Post"}
            </Button>
          </div>
          {message && <p className="text-sm text-green-700" role="status">{message}</p>}
          {error && <p className="text-sm text-destructive" role="alert">{error}</p>}
        </CardContent>
      </form>
    </Card>
  );
}
