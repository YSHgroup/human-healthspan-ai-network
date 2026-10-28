import os
import sys
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("APP_ENV", "test")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "api"))

import pytest
from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import engine
from app.main import app
from app.models import domain  # noqa: F401


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


def register(client: TestClient, email: str) -> dict:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Strong-test-password-2026", "display_name": email.split("@")[0]},
    )
    assert response.status_code == 201
    return response.json()


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_registration_login_profile_and_logout(client: TestClient) -> None:
    registration = register(client, "member@example.org")
    access_token = registration["tokens"]["access_token"]

    profile = client.get("/api/v1/me", headers=auth_header(access_token))
    assert profile.status_code == 200
    assert profile.json()["email"] == "member@example.org"

    updated = client.patch(
        "/api/v1/users/me",
        headers=auth_header(access_token),
        json={"bio": "Evidence first", "interests": ["healthy aging"]},
    )
    assert updated.status_code == 200
    assert updated.json()["profile"]["bio"] == "Evidence first"

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "MEMBER@example.org", "password": "Strong-test-password-2026"},
    )
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"

    logout = client.post("/api/v1/auth/logout", headers=auth_header(access_token))
    assert logout.status_code == 204
    assert client.get("/api/v1/me", headers=auth_header(access_token)).status_code == 401


def test_post_identity_comes_from_authenticated_user(client: TestClient) -> None:
    owner = register(client, "owner@example.org")
    outsider = register(client, "outsider@example.org")
    assert client.post("/api/v1/posts", json={"body": "Anonymous write"}).status_code == 401

    response = client.post(
        "/api/v1/posts",
        headers=auth_header(owner["tokens"]["access_token"]),
        json={"author_id": outsider["user"]["id"], "body": "A first post", "classification": "opinion"},
    )
    assert response.status_code == 201
    assert response.json()["author_id"] == owner["user"]["id"]
    assert response.json()["classification"] == "opinion"

    feed = client.get("/api/v1/feed")
    assert feed.status_code == 200
    assert feed.json()[0]["id"] == response.json()["id"]


def test_research_project_visibility_and_team_permissions(client: TestClient) -> None:
    owner = register(client, "researcher@example.org")
    member = register(client, "collaborator@example.org")
    owner_headers = auth_header(owner["tokens"]["access_token"])
    member_headers = auth_header(member["tokens"]["access_token"])

    created = client.post(
        "/api/v1/research/projects",
        headers=owner_headers,
        json={"title": "Private question", "description": "Restricted work", "visibility": "private"},
    )
    assert created.status_code == 201
    project_id = created.json()["id"]
    assert client.get(f"/api/v1/research/projects/{project_id}", headers=member_headers).status_code == 404

    updated = client.patch(
        f"/api/v1/research/projects/{project_id}",
        headers=owner_headers,
        json={"visibility": "team"},
    )
    assert updated.status_code == 200
    assert client.post(
        f"/api/v1/research/projects/{project_id}/members",
        headers=owner_headers,
        json={"user_id": member["user"]["id"], "role": "member"},
    ).status_code == 201

    visible = client.get(f"/api/v1/research/projects/{project_id}", headers=member_headers)
    assert visible.status_code == 200
    question = client.post(
        "/api/v1/research/questions",
        headers=member_headers,
        json={"project_id": project_id, "title": "What changes?", "description": "A scoped question"},
    )
    assert question.status_code == 201
    assert question.json()["author_id"] == member["user"]["id"]


def test_invalid_credentials_and_refresh_token(client: TestClient) -> None:
    registration = register(client, "login@example.org")
    invalid = client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.org", "password": "incorrect-password"},
    )
    assert invalid.status_code == 401

    refresh = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": registration["tokens"]["refresh_token"]},
    )
    assert refresh.status_code == 200
    me = client.get("/api/v1/auth/me", headers=auth_header(refresh.json()["access_token"]))
    assert me.status_code == 200


def test_starter_communities_are_seeded_and_join_is_idempotent(client: TestClient) -> None:
    communities = client.get("/api/v1/communities")
    assert communities.status_code == 200
    assert len(communities.json()) == 6

    user = register(client, "community@example.org")
    community_id = communities.json()[0]["id"]
    headers = auth_header(user["tokens"]["access_token"])
    assert client.post(f"/api/v1/communities/{community_id}/join", headers=headers).status_code == 204
    assert client.post(f"/api/v1/communities/{community_id}/join", headers=headers).status_code == 204
