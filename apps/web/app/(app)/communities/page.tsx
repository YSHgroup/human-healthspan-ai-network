import { getCommunities } from "../../../lib/data";

export default async function CommunitiesPage() {
  const allCommunities = await getCommunities();

  return (
    <>
      <header className="page-heading">
        <p className="page-eyebrow">Find your people</p>
        <h1>Communities</h1>
        <p>Starter communities are sample data while the communities API is being built.</p>
      </header>
      <section className="community-grid" aria-label="Starter communities">
        {allCommunities.map((community) => (
          <article className="community-card" key={community.id}>
            <span className="topic-tag">{community.topic}</span>
            <h2>{community.name}</h2>
            <p>{community.description}</p>
            <span className="community-members">{community.members.toLocaleString()} sample members</span>
          </article>
        ))}
      </section>
    </>
  );
}
