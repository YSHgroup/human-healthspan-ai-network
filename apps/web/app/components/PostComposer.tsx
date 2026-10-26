"use client";

import { FormEvent, useState } from "react";
import { createPost } from "../../lib/api";

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
    <form className="composer-card" onSubmit={handleSubmit}>
      <label htmlFor="post-body">Share a question or reflection</label>
      <textarea
        id="post-body"
        maxLength={10000}
        minLength={1}
        onChange={(event) => setBody(event.target.value)}
        placeholder="What are you thinking about?"
        required
        rows={3}
        value={body}
      />
      <div className="composer-footer">
        <small>
          Temporary demo author ID: {TEMPORARY_AUTHOR_ID} · authentication is not available and posts are not saved yet.
        </small>
        <button className="app-button" disabled={isSubmitting || !body.trim()} type="submit">
          {isSubmitting ? "Posting…" : "Post"}
        </button>
      </div>
      {message && <p className="form-feedback" role="status">{message}</p>}
      {error && <p className="form-error" role="alert">{error}</p>}
    </form>
  );
}
