import os
import sys
from pathlib import Path
from uuid import UUID

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("APP_ENV", "test")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "api"))

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import Settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.main import app
from app.models import domain  # noqa: F401
from app.models.domain import User
from app.services.email import send_action_email
from app.services.retrieval import RetrievalService


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
    result = response.json()
    assert result["verification_required"] is True
    assert client.post(
        "/api/v1/auth/verify-email",
        json={"token": result["verification_token"]},
    ).status_code == 200
    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Strong-test-password-2026"},
    )
    assert login.status_code == 200
    result["tokens"] = login.json()
    return result


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_production_settings_reject_development_secrets() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="production", postgres_password="prod-db-password")
    with pytest.raises(ValidationError):
        Settings(
            app_env="production",
            jwt_secret="a-production-secret-with-at-least-32-characters",
            postgres_password="a-strong-production-database-password",
            public_app_url="http://healthspan.example.org",
        )
    with pytest.raises(ValidationError):
        Settings(app_env="test", public_app_url="javascript:alert(1)")


def test_email_action_uses_public_application_url(monkeypatch: pytest.MonkeyPatch) -> None:
    sent_messages = []

    class SmtpStub:
        def __init__(self, host: str, port: int, timeout: int) -> None:
            assert host == "mail.example.org"
            assert port == 587
            assert timeout == 10

        def __enter__(self) -> "SmtpStub":
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def starttls(self) -> None:
            return None

        def send_message(self, message) -> None:
            sent_messages.append(message)

    from app.core.config import settings
    import app.services.email as email_service

    monkeypatch.setattr(email_service.smtplib, "SMTP", SmtpStub)
    monkeypatch.setattr(settings, "smtp_host", "mail.example.org")
    monkeypatch.setattr(settings, "email_from", "noreply@example.org")
    monkeypatch.setattr(settings, "public_app_url", "https://members.example.org/")
    send_action_email("member@example.org", "verify-email", "one-time-token")

    assert "https://members.example.org/verify-email?token=one-time-token" in sent_messages[0].get_content()


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


def test_member_profile_fields_are_validated_and_cannot_change_role(client: TestClient) -> None:
    registration = register(client, "profile-member@example.org")
    headers = auth_header(registration["tokens"]["access_token"])

    updated = client.patch(
        "/api/v1/me",
        headers=headers,
        json={
            "location": "Cambridge",
            "topics": ["Healthy aging", "healthy aging", "Biomarkers"],
            "researcher_identifier": "0000-0002-1825-0097",
            "organization_affiliation": "Healthspan Institute",
        },
    )
    assert updated.status_code == 200
    profile = updated.json()["profile"]
    assert profile["location"] == "Cambridge"
    assert profile["topics"] == ["Healthy aging", "Biomarkers"]
    assert profile["researcher_identifier"] == "0000-0002-1825-0097"
    assert profile["organization_affiliation"] == "Healthspan Institute"

    role_change = client.patch("/api/v1/me", headers=headers, json={"role": "admin"})
    assert role_change.status_code == 422
    assert client.get("/api/v1/me", headers=headers).json()["role"] == registration["user"]["role"]


def test_authenticated_password_change_revokes_existing_sessions(client: TestClient) -> None:
    registration = register(client, "password-change@example.org")
    headers = auth_header(registration["tokens"]["access_token"])

    incorrect = client.post(
        "/api/v1/auth/password-change",
        headers=headers,
        json={"current_password": "not-the-current-password", "new_password": "A-different-long-password"},
    )
    assert incorrect.status_code == 400
    same_password = client.post(
        "/api/v1/auth/password-change",
        headers=headers,
        json={
            "current_password": "Strong-test-password-2026",
            "new_password": "Strong-test-password-2026",
        },
    )
    assert same_password.status_code == 422

    changed = client.post(
        "/api/v1/auth/password-change",
        headers=headers,
        json={"current_password": "Strong-test-password-2026", "new_password": "A-different-long-password"},
    )
    assert changed.status_code == 200
    assert client.get("/api/v1/me", headers=headers).status_code == 401
    assert client.post(
        "/api/v1/auth/login",
        json={"email": "password-change@example.org", "password": "Strong-test-password-2026"},
    ).status_code == 401
    assert client.post(
        "/api/v1/auth/login",
        json={"email": "password-change@example.org", "password": "A-different-long-password"},
    ).status_code == 200


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


def test_feed_exposes_safe_author_and_interaction_summaries(client: TestClient) -> None:
    member = register(client, "private-feed@example.org")
    headers = auth_header(member["tokens"]["access_token"])
    assert client.patch(
        "/api/v1/me",
        headers=headers,
        json={"display_name": "Private Name", "is_public": False},
    ).status_code == 200
    post = client.post("/api/v1/posts", headers=headers, json={"body": "A private-profile post"})
    assert post.status_code == 201
    post_id = post.json()["id"]
    assert client.post(
        f"/api/v1/posts/{post_id}/comments",
        headers=headers,
        json={"body": "A useful comment"},
    ).status_code == 201
    assert client.post(
        f"/api/v1/posts/{post_id}/reactions",
        headers=headers,
        json={"kind": "insightful"},
    ).status_code == 201
    comments = client.get(f"/api/v1/posts/{post_id}/comments")
    assert comments.status_code == 200
    assert comments.json()[0]["author_display_name"] == "Member"

    anonymous_feed = client.get("/api/v1/feed")
    assert anonymous_feed.status_code == 200
    item = next(post for post in anonymous_feed.json() if post["id"] == post_id)
    assert item["author_display_name"] == "Member"
    assert item["comment_count"] == 1
    assert item["reaction_count"] == 1
    assert item["is_reacted"] is False
    assert item["is_bookmarked"] is False

    member_feed = client.get("/api/v1/feed", headers=headers)
    member_item = next(post for post in member_feed.json() if post["id"] == post_id)
    assert member_item["author_display_name"] == "Member"
    assert member_item["is_reacted"] is True


def test_community_list_includes_member_count_and_current_membership(client: TestClient) -> None:
    member = register(client, "community-member@example.org")
    headers = auth_header(member["tokens"]["access_token"])
    communities = client.get("/api/v1/communities")
    assert communities.status_code == 200
    community = communities.json()[0]
    assert community["member_count"] == 0
    assert community["is_member"] is False

    joined = client.post(f"/api/v1/communities/{community['id']}/join", headers=headers)
    assert joined.status_code == 204
    detail = client.get(f"/api/v1/communities/{community['id']}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["is_member"] is True
    assert detail.json()["member_count"] == 1
    community_post = client.post(
        "/api/v1/posts",
        headers=headers,
        json={"community_id": community["id"], "body": "A community discussion"},
    )
    assert community_post.status_code == 201
    feed = client.get(f"/api/v1/communities/{community['id']}/feed")
    assert feed.status_code == 200
    assert feed.json()[0]["id"] == community_post.json()["id"]
    updated = client.get("/api/v1/communities", headers=headers)
    joined_community = next(item for item in updated.json() if item["id"] == community["id"])
    assert joined_community["member_count"] == 1
    assert joined_community["is_member"] is True


def test_dashboard_summary_reports_real_counts_and_seven_daily_buckets(client: TestClient) -> None:
    member = register(client, "dashboard@example.org")
    headers = auth_header(member["tokens"]["access_token"])
    communities = client.get("/api/v1/communities").json()
    assert client.post(
        f"/api/v1/communities/{communities[0]['id']}/join",
        headers=headers,
    ).status_code == 204
    assert client.post(
        "/api/v1/research/projects",
        headers=headers,
        json={"title": "Member project", "description": "An MVP dashboard test project"},
    ).status_code == 201
    assert client.post(
        "/api/v1/posts",
        headers=headers,
        json={"body": "A recent dashboard post"},
    ).status_code == 201

    summary = client.get("/api/v1/dashboard/summary", headers=headers)
    assert summary.status_code == 200
    data = summary.json()
    assert data["active_members"] == 1
    assert data["active_communities"] == len(communities)
    assert data["your_communities"] == 1
    assert data["accessible_projects"] == 1
    assert data["posts_last_7_days"] == 1
    assert len(data["activity"]) == 7
    assert sum(day["post_count"] for day in data["activity"]) == 1
    assert client.get("/api/v1/dashboard/summary").status_code == 401


def test_search_and_public_profiles_respect_privacy_and_follow_state(client: TestClient) -> None:
    public = register(client, "public-expert@example.org")
    private = register(client, "private-expert@example.org")
    visitor = register(client, "visitor@example.org")
    private_headers = auth_header(private["tokens"]["access_token"])
    visitor_headers = auth_header(visitor["tokens"]["access_token"])

    assert client.patch(
        "/api/v1/me",
        headers=auth_header(public["tokens"]["access_token"]),
        json={"display_name": "Visible Expert", "is_public": True},
    ).status_code == 200
    assert client.patch(
        "/api/v1/me",
        headers=private_headers,
        json={"display_name": "Hidden Expert", "is_public": False},
    ).status_code == 200

    search = client.get("/api/v1/search", params={"q": "Expert"})
    assert search.status_code == 200
    assert [person["display_name"] for person in search.json()["people"]] == ["Visible Expert"]

    private_profile = client.get(f"/api/v1/users/{private['user']['id']}")
    assert private_profile.status_code == 404
    public_profile = client.get(f"/api/v1/users/{public['user']['id']}", headers=visitor_headers)
    assert public_profile.status_code == 200
    assert public_profile.json()["is_following"] is False
    assert client.post(f"/api/v1/users/{public['user']['id']}/follow", headers=visitor_headers).status_code == 204
    followed_profile = client.get(f"/api/v1/users/{public['user']['id']}", headers=visitor_headers)
    assert followed_profile.json()["is_following"] is True
    assert client.get(
        f"/api/v1/users/{private['user']['id']}",
        headers=private_headers,
    ).status_code == 404


def test_admin_can_deactivate_community_with_audited_reason(client: TestClient) -> None:
    admin = register(client, "community-admin@example.org")
    member = register(client, "community-user@example.org")
    with SessionLocal.begin() as db:
        db.get(User, UUID(admin["user"]["id"])).role = "admin"

    admin_headers = auth_header(admin["tokens"]["access_token"])
    member_headers = auth_header(member["tokens"]["access_token"])
    communities = client.get("/api/v1/admin/communities", headers=admin_headers)
    assert communities.status_code == 200
    community = communities.json()[0]
    forbidden = client.get("/api/v1/admin/communities", headers=member_headers)
    assert forbidden.status_code == 403

    updated = client.patch(
        f"/api/v1/admin/communities/{community['id']}",
        headers=admin_headers,
        json={"is_active": False, "reason": "Temporarily paused for review"},
    )
    assert updated.status_code == 200
    assert updated.json()["is_active"] is False
    assert all(item["id"] != community["id"] for item in client.get("/api/v1/communities").json())
    logs = client.get("/api/v1/admin/audit-logs", headers=admin_headers)
    assert any(event["action"] == "admin.community.updated" for event in logs.json())


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
    hypothesis = client.post(
        f"/api/v1/research/questions/{question.json()['id']}/hypotheses",
        headers=member_headers,
        json={"title": "Potential mechanism", "description": "A testable proposal"},
    )
    assert hypothesis.status_code == 201
    assert hypothesis.json()["origin"] == "human"
    members = client.get(
        f"/api/v1/research/projects/{project_id}/members",
        headers=member_headers,
    )
    assert members.status_code == 200
    assert members.json()[0]["user_id"] == member["user"]["id"]


def test_admin_does_not_bypass_private_research_project_permissions(client: TestClient) -> None:
    owner = register(client, "private-owner@example.org")
    admin = register(client, "research-admin@example.org")
    project = client.post(
        "/api/v1/research/projects",
        headers=auth_header(owner["tokens"]["access_token"]),
        json={"title": "Restricted project", "description": "Private research", "visibility": "private"},
    ).json()
    with SessionLocal.begin() as db:
        db.get(User, UUID(admin["user"]["id"])).role = "admin"

    headers = auth_header(admin["tokens"]["access_token"])
    assert client.get(f"/api/v1/research/projects/{project['id']}", headers=headers).status_code == 404
    with SessionLocal() as db:
        results = RetrievalService(db).retrieve(
            "restricted",
            {"principal_id": admin["user"]["id"], "limit": 10},
        )
    assert results == []


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
    assert refresh.json()["refresh_expires_in"] > 0
    replay = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": registration["tokens"]["refresh_token"]},
    )
    assert replay.status_code == 401
    me = client.get("/api/v1/auth/me", headers=auth_header(refresh.json()["access_token"]))
    assert me.status_code == 200


def test_email_verification_and_password_reset_tokens_are_single_use(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "new@example.org",
            "password": "Strong-test-password-2026",
            "display_name": "New User",
        },
    )
    assert response.status_code == 201
    unverified = client.post(
        "/api/v1/auth/login",
        json={"email": "new@example.org", "password": "Strong-test-password-2026"},
    )
    assert unverified.status_code == 401

    verification_token = response.json()["verification_token"]
    assert client.post("/api/v1/auth/verify-email", json={"token": verification_token}).status_code == 200
    assert client.post("/api/v1/auth/verify-email", json={"token": verification_token}).status_code == 400

    reset = client.post("/api/v1/auth/password-reset", json={"email": "new@example.org"})
    assert reset.status_code == 202
    reset_token = reset.json()["reset_token"]
    changed = client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": reset_token, "new_password": "New-strong-password-2026"},
    )
    assert changed.status_code == 200
    assert client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": reset_token, "new_password": "Other-strong-password-2026"},
    ).status_code == 400
    assert client.post(
        "/api/v1/auth/login",
        json={"email": "new@example.org", "password": "New-strong-password-2026"},
    ).status_code == 200
    old_token = client.post(
        "/api/v1/auth/login",
        json={"email": "new@example.org", "password": "New-strong-password-2026"},
    ).json()["access_token"]
    reset_again = client.post("/api/v1/auth/password-reset", json={"email": "new@example.org"}).json()
    assert client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": reset_again["reset_token"], "new_password": "Latest-strong-password-2026"},
    ).status_code == 200
    assert client.get("/api/v1/me", headers=auth_header(old_token)).status_code == 401


def test_reports_are_audited_and_moderator_actions_soft_delete_posts(client: TestClient) -> None:
    author = register(client, "author@example.org")
    reporter = register(client, "reporter@example.org")
    moderator = register(client, "moderator@example.org")
    with SessionLocal.begin() as db:
        db.get(User, UUID(moderator["user"]["id"])).role = "moderator"

    post = client.post(
        "/api/v1/posts",
        headers=auth_header(author["tokens"]["access_token"]),
        json={"body": "Reported post"},
    )
    report = client.post(
        "/api/v1/reports",
        headers=auth_header(reporter["tokens"]["access_token"]),
        json={"target_type": "post", "target_id": post.json()["id"], "reason": "spam"},
    )
    assert report.status_code == 201
    queue = client.get("/api/v1/moderation/queue", headers=auth_header(moderator["tokens"]["access_token"]))
    assert len(queue.json()) == 1
    decision = client.post(
        f"/api/v1/moderation/reports/{report.json()['id']}/decision",
        headers=auth_header(moderator["tokens"]["access_token"]),
        json={"action": "remove", "reason": "Confirmed spam"},
    )
    assert decision.status_code == 200
    assert client.get(f"/api/v1/posts/{post.json()['id']}").status_code == 404


def test_starter_communities_are_seeded_and_join_is_idempotent(client: TestClient) -> None:
    communities = client.get("/api/v1/communities")
    assert communities.status_code == 200
    assert len(communities.json()) == 6

    user = register(client, "community@example.org")
    community_id = communities.json()[0]["id"]
    headers = auth_header(user["tokens"]["access_token"])
    assert client.post(f"/api/v1/communities/{community_id}/join", headers=headers).status_code == 204
    assert client.post(f"/api/v1/communities/{community_id}/join", headers=headers).status_code == 204


def test_community_feed_reactions_and_bookmarks_are_persistent(client: TestClient) -> None:
    user = register(client, "social@example.org")
    headers = auth_header(user["tokens"]["access_token"])
    communities = client.get("/api/v1/communities").json()
    community_id = communities[0]["id"]
    assert client.post(f"/api/v1/communities/{community_id}/join", headers=headers).status_code == 204
    post = client.post(
        "/api/v1/posts",
        headers=headers,
        json={
            "community_id": community_id,
            "content_type": "question",
            "body": "Which evidence should we review?",
        },
    )
    assert post.status_code == 201
    assert post.json()["content_type"] == "question"
    assert client.get(f"/api/v1/communities/{community_id}/feed").json()[0]["id"] == post.json()["id"]

    reaction_url = f"/api/v1/posts/{post.json()['id']}/reactions"
    assert client.post(reaction_url, headers=headers, json={"kind": "insightful"}).status_code == 201
    assert client.post(reaction_url, headers=headers, json={"kind": "like"}).status_code == 201
    assert client.delete(reaction_url, headers=headers).status_code == 204
    bookmark_url = f"/api/v1/posts/{post.json()['id']}/bookmark"
    assert client.post(bookmark_url, headers=headers).status_code == 204
    assert client.post(bookmark_url, headers=headers).status_code == 204
    assert client.delete(bookmark_url, headers=headers).status_code == 204


def test_public_science_search_excludes_private_project_literature(client: TestClient) -> None:
    owner = register(client, "science@example.org")
    headers = auth_header(owner["tokens"]["access_token"])
    for visibility in ("public", "private"):
        project = client.post(
            "/api/v1/research/projects",
            headers=headers,
            json={"title": f"{visibility} project", "description": "Research scope", "visibility": visibility},
        )
        assert project.status_code == 201
        literature = client.post(
            f"/api/v1/research/projects/{project.json()['id']}/literature",
            headers=headers,
            json={"title": f"{visibility} aging paper", "doi": f"10.1000/{visibility}"},
        )
        assert literature.status_code == 201

    results = client.get("/api/v1/science/search", params={"q": "aging"})
    assert results.status_code == 200
    assert [entry["title"] for entry in results.json()] == ["public aging paper"]


def test_retrieval_scopes_project_resources_before_search(client: TestClient) -> None:
    owner = register(client, "private-owner@example.org")
    reader = register(client, "private-reader@example.org")
    owner_headers = auth_header(owner["tokens"]["access_token"])
    project = client.post(
        "/api/v1/research/projects",
        headers=owner_headers,
        json={"title": "Private trial", "description": "Hidden work", "visibility": "private"},
    ).json()
    added = client.post(
        f"/api/v1/research/projects/{project['id']}/literature",
        headers=owner_headers,
        json={"title": "Longevity signal in a private paper"},
    )
    assert added.status_code == 201

    with SessionLocal() as db:
        results = RetrievalService(db).retrieve(
            "longevity",
            {"principal_id": reader["user"]["id"], "limit": 10},
        )
    assert results == []


def test_admin_account_changes_require_reason_and_prevent_self_lockout(client: TestClient) -> None:
    admin = register(client, "admin@example.org")
    member = register(client, "managed@example.org")
    with SessionLocal.begin() as db:
        db.get(User, UUID(admin["user"]["id"])).role = "admin"

    admin_headers = auth_header(admin["tokens"]["access_token"])
    self_lockout = client.patch(
        f"/api/v1/admin/users/{admin['user']['id']}",
        headers=admin_headers,
        json={"role": "user", "reason": "Reduce access"},
    )
    assert self_lockout.status_code == 409

    update = client.patch(
        f"/api/v1/admin/users/{member['user']['id']}",
        headers=admin_headers,
        json={"role": "moderator", "reason": "Assigned moderation duties"},
    )
    assert update.status_code == 200
    assert update.json()["role"] == "moderator"
    assert client.get("/api/v1/admin/users", headers=admin_headers).status_code == 200
    assert client.get("/api/v1/admin/audit-logs", headers=admin_headers).status_code == 200


def test_support_operator_can_manage_account_status_but_not_roles(client: TestClient) -> None:
    operator = register(client, "support@example.org")
    member = register(client, "support-target@example.org")
    admin = register(client, "support-protected-admin@example.org")
    with SessionLocal.begin() as db:
        db.get(User, UUID(operator["user"]["id"])).role = "support_operator"
        db.get(User, UUID(admin["user"]["id"])).role = "admin"
    headers = auth_header(operator["tokens"]["access_token"])

    users = client.get("/api/v1/admin/users", headers=headers)
    assert users.status_code == 200
    target = next(item for item in users.json() if item["id"] == member["user"]["id"])

    denied = client.patch(
        f"/api/v1/admin/users/{target['id']}",
        headers=headers,
        json={"role": "admin", "reason": "Not permitted"},
    )
    assert denied.status_code == 403
    suspended = client.patch(
        f"/api/v1/admin/users/{target['id']}",
        headers=headers,
        json={"is_active": False, "reason": "Abuse report review"},
    )
    assert suspended.status_code == 200
    assert suspended.json()["is_active"] is False
    protected_admin = client.patch(
        f"/api/v1/admin/users/{admin['user']['id']}",
        headers=headers,
        json={"is_active": False, "reason": "Not permitted"},
    )
    assert protected_admin.status_code == 403
