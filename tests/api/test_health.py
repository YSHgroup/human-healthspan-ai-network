from fastapi.testclient import TestClient

from app.main import asgi_app

client = TestClient(asgi_app)


def test_health_endpoint_reports_liveness() -> None:
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
