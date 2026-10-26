import ResearchQuestionForm from "../../components/ResearchQuestionForm";
import { getResearchProjects } from "../../../lib/data";

export default async function ResearchPage() {
  const projects = await getResearchProjects();

  return (
    <>
      <header className="page-heading">
        <p className="page-eyebrow">Collaborate on questions</p>
        <h1>Research</h1>
        <p>Project examples are mock data; new questions use the live API scaffold.</p>
      </header>
      <section className="project-grid" aria-label="Sample research projects">
        {projects.map((project) => (
          <article className="project-card" key={project.id}>
            <div className="project-card-meta">
              <span className="topic-tag">{project.focus}</span>
              <span>{project.status}</span>
            </div>
            <h2>{project.title}</h2>
            <p>{project.description}</p>
            <span className="mock-label">Sample project</span>
          </article>
        ))}
      </section>
      <ResearchQuestionForm projects={projects} />
    </>
  );
}
