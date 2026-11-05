from collections.abc import Generator

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.main as main
from app.infrastructure.database import get_db


@pytest.fixture
def api_client(tmp_path, monkeypatch) -> Generator[TestClient, None, None]:
    database_url = f"sqlite:///{(tmp_path / 'test.db').as_posix()}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    config = Config("api/alembic.ini")
    config.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(config, "head")

    test_engine = create_engine(database_url, connect_args={"check_same_thread": False})
    test_session = sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)

    def override_get_db():
        with test_session() as db:
            yield db

    main.app.dependency_overrides[get_db] = override_get_db
    main.app.state.test_session_factory = test_session
    monkeypatch.setattr(main, "engine", test_engine)
    with TestClient(main.app) as client:
        yield client
    main.app.dependency_overrides.clear()
    del main.app.state.test_session_factory
    test_engine.dispose()


def register(client: TestClient, email: str, display_name: str) -> str:
    response = client.post(
        "/api/v1/user/auth/register",
        headers={"Origin": "http://localhost:3000"},
        json={
            "email": email,
            "display_name": display_name,
            "password": "a-secure-test-password",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]
