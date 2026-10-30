"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useState } from "react";
import ResearchQuestionForm from "../../components/ResearchQuestionForm";
import PageHeader from "../../components/PageHeader";
import { Badge } from "@healthspan/ui/badge";
import { Button } from "@healthspan/ui/button";
import { Input } from "@healthspan/ui/input";
import { Select } from "@healthspan/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  createResearchProject,
  getResearchProjects,
  type ResearchProject,
} from "@/lib/api";
import { useSession } from "@/lib/session";

export default function ResearchPage() {
  const { user, status } = useSession();
  const [projects, setProjects] = useState<ResearchProject[]>([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [visibility, setVisibility] = useState<ResearchProject["visibility"]>("private");
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const loadProjects = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setProjects(await getResearchProjects());
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : "Unable to load research projects.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (status === "authenticated") void loadProjects();
  }, [status, loadProjects]);

  async function submitProject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await createResearchProject({ title, description, visibility });
      setTitle("");
      setDescription("");
      setVisibility("private");
      setNotice("Research project created.");
      await loadProjects();
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : "Unable to create the research project.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <PageHeader
        eyebrow="Collaborate on questions"
        title="Research"
        description="Create projects, explore work you can access, and add questions for collaborators."
      />
      {status === "loading" && <p className="text-sm text-muted-foreground">Checking your account…</p>}
      {status === "unavailable" && <p className="text-sm text-destructive" role="alert">Your account service is unavailable. Try again later.</p>}
      {status === "unauthenticated" && (
        <Card className="mb-6">
          <CardContent className="space-y-2 p-6">
            <p>Sign in to create research projects and view projects you are authorized to access.</p>
            <Link className="text-sm text-primary hover:underline" href="/login">Sign in</Link>
          </CardContent>
        </Card>
      )}
      {user && (
        <>
          <Card className="mb-6 rounded-2xl shadow-sm">
            <CardHeader><CardTitle>Create a research project</CardTitle></CardHeader>
            <CardContent>
              <form className="space-y-4" onSubmit={submitProject}>
                <label className="block space-y-2 text-sm font-medium" htmlFor="project-title">
                  Project title
                  <Input id="project-title" maxLength={200} minLength={3} onChange={(event) => setTitle(event.target.value)} required value={title} />
                </label>
                <label className="block space-y-2 text-sm font-medium" htmlFor="project-description">
                  Project description
                  <textarea className="min-h-28 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" id="project-description" maxLength={10000} onChange={(event) => setDescription(event.target.value)} required value={description} />
                </label>
                <label className="block space-y-2 text-sm font-medium" htmlFor="project-visibility">
                  Visibility
                  <Select id="project-visibility" onChange={(event) => setVisibility(event.target.value as ResearchProject["visibility"])} value={visibility}>
                    <option value="private">Private</option>
                    <option value="team">Team</option>
                    <option value="public">Public</option>
                  </Select>
                </label>
                {notice && <p className="text-sm text-green-700" role="status">{notice}</p>}
                {error && <p className="text-sm text-destructive" role="alert">{error}</p>}
                <Button disabled={busy} type="submit">{busy ? "Creating…" : "Create project"}</Button>
              </form>
            </CardContent>
          </Card>
          <section className="mb-6 grid gap-4 md:grid-cols-2" aria-label="Research projects">
            {projects.map((project) => (
              <Card className="gap-0 rounded-2xl border-border py-0 shadow-sm" id={`research-project-${project.id}`} key={project.id}>
                <CardHeader className="gap-3 px-5 pt-5 sm:px-6 sm:pt-6">
                  <div className="flex items-center justify-between gap-2">
                    <Badge variant="secondary">{project.visibility}</Badge>
                    <span className="text-xs text-muted-foreground">{project.status}</span>
                  </div>
                  <CardTitle className="text-lg text-primary">{project.title}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 p-5 pt-3 sm:px-6 sm:pb-6">
                  <p className="text-sm leading-6 text-muted-foreground">{project.description}</p>
                </CardContent>
              </Card>
            ))}
            {loading && projects.length === 0 && <p className="text-sm text-muted-foreground">Loading your research projects…</p>}
            {!loading && projects.length === 0 && !error && <p className="text-sm text-muted-foreground">No projects are available to your account yet.</p>}
          </section>
          <ResearchQuestionForm projects={projects} />
        </>
      )}
    </>
  );
}
