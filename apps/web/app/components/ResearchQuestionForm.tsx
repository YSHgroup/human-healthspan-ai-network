"use client";

import { FormEvent, useState } from "react";
import { createResearchQuestion } from "../../lib/api";
import type { ResearchProject } from "../../lib/mock/data";

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
    <form className="composer-card question-form" onSubmit={handleSubmit}>
      <h2>Ask a research question</h2>
      <p>Questions are sent to the API. The current backend returns a demo response and does not save them.</p>
      <label htmlFor="question-project">Project</label>
      <select
        id="question-project"
        onChange={(event) => setProjectId(event.target.value)}
        required
        value={projectId}
      >
        {projects.map((project) => (
          <option key={project.id} value={project.id}>{project.title}</option>
        ))}
      </select>
      <label htmlFor="question-title">Question title</label>
      <input
        id="question-title"
        maxLength={500}
        minLength={3}
        onChange={(event) => setTitle(event.target.value)}
        required
        value={title}
      />
      <label htmlFor="question-description">Description</label>
      <textarea
        id="question-description"
        maxLength={10000}
        onChange={(event) => setDescription(event.target.value)}
        required
        rows={4}
        value={description}
      />
      <div className="composer-footer">
        <span />
        <button className="app-button" disabled={isSubmitting || !projectId} type="submit">
          {isSubmitting ? "Submitting…" : "Submit question"}
        </button>
      </div>
      {message && <p className="form-feedback" role="status">{message}</p>}
      {error && <p className="form-error" role="alert">{error}</p>}
    </form>
  );
}
