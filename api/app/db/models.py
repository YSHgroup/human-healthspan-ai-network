from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(200))

class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int]
    body: Mapped[str] = mapped_column(Text)
    evidence_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
