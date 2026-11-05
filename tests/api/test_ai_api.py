from dataclasses import replace

from fastapi.testclient import TestClient

import app.api.v1.user.ai_chat as ai_routes


def test_private_scientist_is_gated_to_approved_researchers(
    api_client: TestClient,
    monkeypatch,
) -> None:
    registration = api_client.post(
        "/api/v1/user/auth/register",
        headers={"Origin": "http://localhost:3000"},
        json={
            "email": "member@example.test",
            "display_name": "Member",
            "password": "a-secure-test-password",
        },
    )
    assert registration.status_code == 201
    monkeypatch.setattr(ai_routes, "settings", replace(ai_routes.settings, scientist_enabled=True))
    response = api_client.post(
        "/api/v1/user/researcher/ai/chat",
        headers={"Origin": "http://localhost:3002"},
        json={"messages": [{"role": "user", "content": "Summarize this paper"}]},
    )
    assert response.status_code == 403
    assert response.json()["code"] == "forbidden"


def test_general_chat_reports_disabled_provider_without_claiming_answer(
    api_client: TestClient,
    monkeypatch,
) -> None:
    response = api_client.post(
        "/api/v1/user/auth/register",
        headers={"Origin": "http://localhost:3000"},
        json={
            "email": "member@example.test",
            "display_name": "Member",
            "password": "a-secure-test-password",
        },
    )
    assert response.status_code == 201
    import app.services.ai_chat as ai_service

    monkeypatch.setattr(ai_routes, "settings", replace(ai_routes.settings, ai_provider="disabled"))
    monkeypatch.setattr(ai_service, "settings", replace(ai_service.settings, ai_provider="disabled"))
    response = api_client.post(
        "/api/v1/user/social/ai/chat",
        headers={"Origin": "http://localhost:3000"},
        json={"messages": [{"role": "user", "content": "What is healthspan?"}]},
    )
    assert response.status_code == 503
    assert response.json()["code"] == "service_unavailable"
