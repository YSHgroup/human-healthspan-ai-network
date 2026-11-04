from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_only_operational_endpoints_are_exposed() -> None:
    """Planned product routes must not exist until they are implemented and documented."""
    assert set(app.openapi()["paths"]) == {"/healthz"}


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
