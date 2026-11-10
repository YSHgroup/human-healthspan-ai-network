from fastapi.testclient import TestClient

from app.api import middleware
from app.main import app

client = TestClient(app)


def test_only_operational_endpoints_are_exposed() -> None:
    """Only implemented and documented workflows appear in OpenAPI."""
    assert set(app.openapi()["paths"]) == {
        "/healthz",
        "/readyz",
        "/api/v1/user/auth/register",
        "/api/v1/user/auth/login",
        "/api/v1/user/auth/logout",
        "/api/v1/user/auth/me",
        "/api/v1/user/auth/ai-learning-consent",
        "/api/v1/user/social/feed",
        "/api/v1/user/social/posts",
        "/api/v1/user/social/posts/{post_id}/reports",
        "/api/v1/user/social/communities",
        "/api/v1/user/social/communities/requests",
        "/api/v1/user/social/communities/{community_id}/join",
        "/api/v1/user/social/communities/{community_id}/memberships/pending",
        "/api/v1/user/social/communities/{community_id}/memberships/{membership_id}/decision",
        "/api/v1/user/social/communities/{community_id}/posts",
        "/api/v1/user/social/posts/{post_id}/comments",
        "/api/v1/user/social/posts/{post_id}/reactions",
        "/api/v1/user/social/comments/{comment_id}/reports",
        "/api/v1/user/social/communities/{community_id}/moderation/reports",
        "/api/v1/user/social/communities/{community_id}/moderation/reports/{report_id}/actions",
        "/api/v1/user/social/me/moderation/actions",
        "/api/v1/user/social/me/moderation/actions/{action_id}/appeals",
        "/api/v1/user/social/communities/{community_id}/moderation/appeals/{appeal_id}/decision",
        "/api/v1/user/social/communities/{community_id}/moderation/appeals",
        "/api/v1/user/social/messages/conversations",
        "/api/v1/user/social/messages/conversations/{conversation_id}/messages",
        "/api/v1/user/social/ai/chat",
        "/api/v1/user/researcher/ai/chat",
        "/api/v1/user/researcher/me",
        "/api/v1/user/researcher/applications",
        "/api/v1/user/researcher/profile",
        "/api/v1/user/researcher/profiles",
        "/api/v1/user/researcher/organizations/requests",
        "/api/v1/user/researcher/organizations/requests/me",
        "/api/v1/user/researcher/organizations",
        "/api/v1/user/researcher/organizations/invitations",
        "/api/v1/user/researcher/organizations/invitations/{invitation_id}/accept",
        "/api/v1/user/researcher/organizations/invitations/{invitation_id}/decline",
        "/api/v1/user/researcher/organizations/{organization_id}/invitations",
        "/api/v1/user/researcher/organizations/{organization_id}/members",
        "/api/v1/user/researcher/projects",
        "/api/v1/user/researcher/projects/{project_id}",
        "/api/v1/user/researcher/projects/{project_id}/members",
        "/api/v1/user/researcher/projects/{project_id}/tasks",
        "/api/v1/user/researcher/projects/{project_id}/tasks/{task_id}",
        "/api/v1/user/researcher/projects/{project_id}/documents",
        "/api/v1/user/researcher/projects/{project_id}/documents/upload",
        "/api/v1/user/researcher/projects/{project_id}/documents/{document_id}/download",
        "/api/v1/user/researcher/projects/{project_id}/activity",
        "/api/v1/user/researcher/events",
        "/api/v1/user/researcher/events/{event_id}/registration",
        "/api/v1/admin/communities/requests",
        "/api/v1/admin/communities/requests/{request_id}/decision",
        "/api/v1/admin/moderation/reports",
        "/api/v1/admin/moderation/reports/{report_id}/actions",
        "/api/v1/admin/moderation/appeals",
        "/api/v1/admin/moderation/appeals/{appeal_id}/decision",
        "/api/v1/admin/ai/usage",
        "/api/v1/admin/users",
        "/api/v1/admin/users/{user_id}/verification",
        "/api/v1/admin/researcher/applications",
        "/api/v1/admin/researcher/applications/{application_id}/decision",
        "/api/v1/admin/organizations/requests",
        "/api/v1/admin/organizations/requests/{request_id}/decision",
        "/api/v1/admin/organizations",
        "/api/v1/admin/users/{user_id}/entitlements",
        "/api/v1/admin/entitlements/{entitlement_id}/revoke",
        "/api/v1/admin/events",
        "/api/v1/admin/events/{event_id}/decision",
        "/api/v1/admin/audit/events",
    }


def test_responses_carry_request_id_and_security_headers() -> None:
    response = client.get("/healthz", headers={"X-Request-ID": "req-123"})

    assert response.headers["X-Request-ID"] == "req-123"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"


def test_chunked_research_upload_body_is_bounded(monkeypatch) -> None:
    monkeypatch.setattr(middleware, "MAX_RESEARCH_UPLOAD_BODY_SIZE", 32)
    response = client.post(
        "/api/v1/user/researcher/projects/project-id/documents/upload",
        headers={"Content-Type": "multipart/form-data; boundary=upload"},
        content=iter([b"x" * 24, b"y" * 24]),
    )
    assert response.status_code == 413
    assert response.json()["code"] == "request_too_large"


def test_request_id_is_generated_when_missing() -> None:
    assert client.get("/healthz").headers["X-Request-ID"]


def test_cors_allows_trusted_portal_origin_with_credentials() -> None:
    response = client.get("/healthz", headers={"Origin": "http://localhost:3001"})

    assert response.headers["access-control-allow-origin"] == "http://localhost:3001"
    assert response.headers["access-control-allow-credentials"] == "true"


def test_cors_does_not_allow_unknown_origins() -> None:
    response = client.get("/healthz", headers={"Origin": "https://untrusted.example"})

    assert "access-control-allow-origin" not in response.headers
