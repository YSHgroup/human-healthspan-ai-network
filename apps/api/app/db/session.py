from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base import Base

engine = create_engine(
    settings.database_url,
    echo=settings.sql_echo,
    pool_pre_ping=True,
    poolclass=StaticPool if settings.database_url.endswith(":memory:") else None,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


if settings.database_url.startswith("sqlite"):
    @event.listens_for(Engine, "connect")
    def enable_sqlite_foreign_keys(dbapi_connection: object, _: object) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


def initialize_database() -> None:
    from app.models import domain  # noqa: F401

    Base.metadata.create_all(bind=engine)
    seed_communities()


def seed_communities() -> None:
    from app.models.domain import Community

    starter_communities = (
        ("healthy-aging", "Healthy Aging", "Research and practical discussion about healthy aging.", "Healthy Aging"),
        ("fitness-strength", "Fitness & Strength", "Movement, fitness, and strength across the lifespan.", "Fitness"),
        ("nutrition", "Nutrition", "Nutrition science, food, and health.", "Nutrition"),
        ("skin-appearance", "Skin & Appearance", "Evidence-informed discussion of skin and appearance.", "Skin & Appearance"),
        ("brain-cognition", "Brain & Cognition", "Brain health, cognition, and neurological research.", "Brain & Cognition"),
        ("biomedical-research", "Biomedical Research", "Discuss biomedical research and scientific methods.", "Research"),
    )
    with SessionLocal.begin() as session:
        for slug, name, description, topic in starter_communities:
            existing = session.query(Community).filter_by(slug=slug).first()
            if existing is None:
                session.add(Community(slug=slug, name=name, description=description, topic=topic))
