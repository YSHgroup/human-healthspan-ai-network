from fastapi.testclient import TestClient

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
    }


def test_responses_carry_request_id_and_security_headers() -> None:
    response = client.get("/healthz", headers={"X-Request-ID": "req-123"})

    assert response.headers["X-Request-ID"] == "req-123"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"


def test_request_id_is_generated_when_missing() -> None:
    assert client.get("/healthz").headers["X-Request-ID"]


def test_cors_allows_trusted_portal_origin_with_credentials() -> None:
    response = client.get("/healthz", headers={"Origin": "http://localhost:3001"})

    assert response.headers["access-control-allow-origin"] == "http://localhost:3001"
    assert response.headers["access-control-allow-credentials"] == "true"


def test_cors_does_not_allow_unknown_origins() -> None:
    response = client.get("/healthz", headers={"Origin": "https://untrusted.example"})

    assert "access-control-allow-origin" not in response.headers
