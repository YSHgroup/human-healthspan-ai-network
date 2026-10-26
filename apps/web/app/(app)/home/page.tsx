import PostComposer from "../../components/PostComposer";
import { getFeed } from "../../../lib/data";

export default async function HomePage() {
  const posts = await getFeed();

  return (
    <>
      <header className="page-heading">
        <p className="page-eyebrow">Your network</p>
        <h1>Home</h1>
        <p>Questions, ideas, and conversations from across the healthspan community.</p>
      </header>
      <PostComposer />
      <section className="feed-list" aria-label="Community feed">
        {posts.map((post) => (
          <article className="feed-card" key={post.id}>
            <div className="feed-author">
              <span className="avatar" aria-hidden="true">{post.author_name.slice(0, 1)}</span>
              <div>
                <strong>{post.author_name}</strong>
                <span>{post.role} · {post.posted_at}</span>
              </div>
            </div>
            <p>{post.body}</p>
            <span className="mock-label">Sample feed post</span>
          </article>
        ))}
      </section>
    </>
  );
}
