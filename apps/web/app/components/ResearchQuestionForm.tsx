"use client";

import { FormEvent, useState } from "react";
import { createResearchQuestion } from "../../lib/api";
import type { ResearchProject } from "../../lib/mock/data";
import { Button } from "@healthspan/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@healthspan/ui/input";
import { Select } from "@healthspan/ui/select";
import { Textarea } from "@/components/ui/textarea";

export default function ResearchQuestionForm({ projects }: { projects: ResearchProject[] }) {
  const [projectId, setProjectId] = useState(projects[0]?.id ?? "");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("");
    setError("");
    setIsSubmitting(true);

    try {
      const question = await createResearchQuestion({ project_id: projectId, title, description });
      setTitle("");
      setDescription("");
      setMessage(`Question submitted (ID: ${question.id}; status: ${question.evidence_status}).`);
    } catch (submitError) {
      setError(
        submitError instanceof Error ? submitError.message : "Unable to submit your research question.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Card className="mt-7 gap-0 rounded-2xl border-border py-0 shadow-sm">
      <CardHeader className="px-5 pt-5 sm:px-6 sm:pt-6">
        <CardTitle className="text-xl">Ask a research question</CardTitle>
        <p className="text-sm text-muted-foreground">
          Questions are sent to the API. The current backend returns a demo response and does not save them.
        </p>
      </CardHeader>
      <CardContent className="p-5 pt-4 sm:px-6 sm:pb-6">
        <form className="space-y-4" onSubmit={handleSubmit}>
          <div className="space-y-2">
            <label className="text-sm font-medium" htmlFor="question-project">Project</label>
            <Select
              id="question-project"
              onChange={(event) => setProjectId(event.target.value)}
              required
              value={projectId}
            >
              {projects.map((project) => (
                <option key={project.id} value={project.id}>{project.title}</option>
              ))}
            </Select>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium" htmlFor="question-title">Question title</label>
            <Input
              id="question-title"
              maxLength={500}
              minLength={3}
              onChange={(event) => setTitle(event.target.value)}
              required
              value={title}
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium" htmlFor="question-description">Description</label>
            <Textarea
              id="question-description"
              maxLength={10000}
              onChange={(event) => setDescription(event.target.value)}
              required
              rows={4}
              value={description}
            />
          </div>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="space-y-2">
              {message && <p className="text-sm text-green-700" role="status">{message}</p>}
              {error && <p className="text-sm text-destructive" role="alert">{error}</p>}
            </div>
            <Button disabled={isSubmitting || !projectId} type="submit">
              {isSubmitting ? "Submitting…" : "Submit question"}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
