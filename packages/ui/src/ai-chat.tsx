"use client";

import { useState, type FormEvent } from "react";
import type { AIAnswer } from "@healthspan/shared-types";
import { Button } from "./button";

interface Turn {
  prompt: string;
  answer?: AIAnswer;
  error?: string;
}

/**
 * Shared chat surface for the General AI, Private AI Scientist and Organization AI.
 * Every answer shows its sources, evidence labels, an uncertainty statement and an AI-generated notice,
 * so the three systems look and behave consistently while staying separate on the backend.
 */
export function AiChat({
  ask,
  title,
  placeholder = "Ask a question…",
  onFeedback,
}: {
  ask: (prompt: string, conversationId?: string) => Promise<AIAnswer>;
  title: string;
  placeholder?: string;
  onFeedback?: (runId: string, rating: "up" | "down") => Promise<void>;
}) {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [prompt, setPrompt] = useState("");
  const [conversationId, setConversationId] = useState<string>();
  const [busy, setBusy] = useState(false);
  const [rated, setRated] = useState<Record<string, "up" | "down">>({});

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const text = prompt.trim();
    if (text.length < 2 || busy) return;
    setBusy(true);
    setPrompt("");
    try {
      const answer = await ask(text, conversationId);
      setConversationId(answer.conversation_id);
      setTurns((current) => [...current, { prompt: text, answer }]);
    } catch (failure) {
      setTurns((current) => [...current, { prompt: text, error: failure instanceof Error ? failure.message : "The assistant is unavailable." }]);
    } finally {
      setBusy(false);
    }
  }

  async function rate(runId: string, rating: "up" | "down") {
    if (!onFeedback || rated[runId]) return;
    try {
      await onFeedback(runId, rating);
      setRated((current) => ({ ...current, [runId]: rating }));
    } catch {
      /* feedback is optional; keep the conversation usable */
    }
  }

  return (
    <section aria-label={title} className="flex flex-col gap-4">
      <div className="space-y-4" aria-live="polite">
        {turns.length === 0 && <p className="text-sm text-muted-foreground">Answers are drawn only from sources this assistant is allowed to use, and every source is listed.</p>}
        {turns.map((turn, index) => (
          <div className="space-y-2" key={index}>
            <p className="ml-auto max-w-[85%] rounded-2xl bg-primary/10 px-4 py-2 text-sm text-foreground">{turn.prompt}</p>
            {turn.error && <p className="rounded-xl border border-destructive/30 bg-destructive/5 px-4 py-2 text-sm text-destructive" role="alert">{turn.error}</p>}
            {turn.answer && (
              <div className="space-y-3 rounded-2xl border border-border bg-card p-4 text-sm shadow-sm">
                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">AI-generated · {turn.answer.provider} · {turn.answer.model_version}</p>
                <p className="whitespace-pre-line leading-6">{turn.answer.answer}</p>
                {turn.answer.sources.length > 0 && (
                  <ol className="space-y-2 border-t border-border pt-3">
                    {turn.answer.sources.map((source) => (
                      <li className="rounded-lg bg-muted/50 px-3 py-2" key={`${source.id}-${source.index}`}>
                        <p className="font-medium">[{source.index}] {source.title}</p>
                        <p className="text-xs text-muted-foreground">{source.evidence_label}{source.source_url ? " · " : ""}{source.source_url && <a className="text-primary underline" href={source.source_url} rel="noreferrer noopener" target="_blank">source</a>}</p>
                      </li>
                    ))}
                  </ol>
                )}
                <p className="text-xs text-muted-foreground"><strong>Uncertainty:</strong> {turn.answer.uncertainty}</p>
                <p className="text-xs text-muted-foreground">{turn.answer.disclaimer}</p>
                {onFeedback && (
                  <div className="flex gap-2">
                    {(["up", "down"] as const).map((rating) => (
                      <Button disabled={Boolean(rated[turn.answer!.run_id])} key={rating} onClick={() => void rate(turn.answer!.run_id, rating)} size="xs" type="button" variant={rated[turn.answer!.run_id] === rating ? "default" : "outline"}>
                        {rating === "up" ? "Helpful" : "Not helpful"}
                      </Button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
      <form className="flex gap-2" onSubmit={submit}>
        <input
          aria-label={title}
          className="h-10 min-w-0 flex-1 rounded-lg border border-border bg-background px-3 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring/50"
          maxLength={4000}
          onChange={(event) => setPrompt(event.target.value)}
          placeholder={placeholder}
          value={prompt}
        />
        <Button disabled={busy || prompt.trim().length < 2} type="submit">{busy ? "Thinking…" : "Ask"}</Button>
      </form>
    </section>
  );
}
