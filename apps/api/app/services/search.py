from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.domain import Community, Post, ResearchProject, User


class SearchService:
    def __init__(self, db: Session):
        self.db = db

    def search(self, query: str, limit: int = 20) -> dict[str, list[dict[str, str]]]:
        pattern = f"%{query.strip()}%"
        posts = self.db.execute(
            select(Post, User)
            .join(User, User.id == Post.author_id)
            .where(Post.deleted_at.is_(None), User.is_active.is_(True), Post.body.ilike(pattern))
            .limit(limit)
        )
        projects = self.db.scalars(
            select(ResearchProject)
            .where(
                ResearchProject.visibility == "public",
                or_(ResearchProject.title.ilike(pattern), ResearchProject.description.ilike(pattern)),
            )
            .limit(limit)
        )
        communities = self.db.scalars(
            select(Community)
            .where(
                Community.is_active.is_(True),
                or_(Community.name.ilike(pattern), Community.description.ilike(pattern)),
            )
            .limit(limit)
        )
        return {
            "posts": [
                {"id": str(post.id), "body": post.body, "classification": post.classification}
                for post, _ in posts
            ],
            "projects": [
                {"id": str(project.id), "title": project.title, "description": project.description}
                for project in projects
            ],
            "communities": [
                {"id": str(community.id), "name": community.name, "topic": community.topic}
                for community in communities
            ],
        }
