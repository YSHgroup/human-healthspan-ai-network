import ResearchQuestionForm from "../../components/ResearchQuestionForm";
import { getResearchProjects } from "../../../lib/data";
import PageHeader from "../../components/PageHeader";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default async function ResearchPage() {
  const projects = await getResearchProjects();

  return (
    <>
      <PageHeader
        eyebrow="Collaborate on questions"
        title="Research"
        description="Project examples are mock data; new questions use the live API scaffold."
      />
      <section className="mb-6 grid gap-4 md:grid-cols-2" aria-label="Sample research projects">
        {projects.map((project) => (
          <Card className="gap-0 rounded-2xl border-border py-0 shadow-sm" key={project.id}>
            <CardHeader className="gap-3 px-5 pt-5 sm:px-6 sm:pt-6">
              <div className="flex items-center justify-between gap-2">
                <Badge variant="secondary">{project.focus}</Badge>
                <span className="text-xs text-muted-foreground">{project.status}</span>
              </div>
              <CardTitle className="text-lg text-primary">{project.title}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 p-5 pt-3 sm:px-6 sm:pb-6">
              <p className="text-sm leading-6 text-muted-foreground">{project.description}</p>
              <Badge className="text-[10px] uppercase tracking-wide" variant="outline">Sample project</Badge>
            </CardContent>
          </Card>
        ))}
      </section>
      <ResearchQuestionForm projects={projects} />
    </>
  );
}
