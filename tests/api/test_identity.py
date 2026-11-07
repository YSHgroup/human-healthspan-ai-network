from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models import AIConsent, AIInteraction, User, UserSession


def register(client: TestClient, email: str, display_name: str = "Member") -> str:
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


def test_registration_creates_shared_http_only_session(api_client: TestClient) -> None:
    response = api_client.post(
        "/api/v1/user/auth/register",
        headers={"Origin": "http://localhost:3000"},
        json={
            "email": "Person@Example.test",
            "display_name": "A member",
            "password": "a-secure-test-password",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "person@example.test"
    assert response.json()["researcher_approved"] is False
    cookie = response.headers["set-cookie"]
    assert "HttpOnly" in cookie
    assert "SameSite=lax" in cookie
    assert "Domain=" not in cookie
    assert api_client.get("/api/v1/user/auth/me").json()["id"] == response.json()["id"]

    with api_client.app.state.test_session_factory() as db:
        user = db.scalar(select(User).where(User.email == "person@example.test"))
        user_session = db.scalar(select(UserSession).where(UserSession.user_id == user.id))
        assert user.password_hash != "a-secure-test-password"
        assert user_session.token_hash != api_client.cookies.get("healthspan_session")


def test_duplicate_registration_and_invalid_login_are_rejected(api_client: TestClient) -> None:
    register(api_client, "person@example.test", "Member")
    headers = {"Origin": "http://localhost:3000"}

    duplicate = api_client.post(
        "/api/v1/user/auth/register",
        headers=headers,
        json={
            "email": "PERSON@example.test",
            "display_name": "Another",
            "password": "a-secure-test-password",
        },
    )
    invalid_login = api_client.post(
        "/api/v1/user/auth/login",
        headers=headers,
        json={"email": "person@example.test", "password": "not-the-password"},
    )

    assert duplicate.status_code == 409
    assert duplicate.json()["code"] == "conflict"
    assert invalid_login.status_code == 401
    assert invalid_login.json()["code"] == "unauthorized"


def test_logout_revokes_the_session(api_client: TestClient) -> None:
    register(api_client, "person@example.test", "Member")
    logout_response = api_client.post(
        "/api/v1/user/auth/logout",
        headers={"Origin": "http://localhost:3000"},
    )

    assert logout_response.status_code == 204
    assert api_client.get("/api/v1/user/auth/me").status_code == 401


def test_browser_mutations_reject_untrusted_origins(api_client: TestClient) -> None:
    response = api_client.post(
        "/api/v1/user/auth/register",
        headers={"Origin": "https://untrusted.example"},
        json={
            "email": "person@example.test",
            "display_name": "Member",
            "password": "a-secure-test-password",
        },
    )

    assert response.status_code == 403
    assert response.json()["code"] == "forbidden"


def test_browser_mutations_reject_missing_origins(api_client: TestClient) -> None:
    registration = api_client.post(
        "/api/v1/user/auth/register",
        json={
            "email": "person@example.test",
            "display_name": "Member",
            "password": "a-secure-test-password",
        },
    )
    assert registration.status_code == 403

    register(api_client, "person@example.test", "Member")
    consent = api_client.put(
        "/api/v1/user/auth/ai-learning-consent",
        json={"allowed": True},
    )
    assert consent.status_code == 403
    assert api_client.get("/api/v1/user/auth/me").json()["ai_learning_consent"] is False


def test_ai_learning_consent_is_opt_in_and_revocable(api_client: TestClient) -> None:
    user_id = register(api_client, "person@example.test", "Member")
    assert api_client.get("/api/v1/user/auth/me").json()["ai_learning_consent"] is False
    enabled = api_client.put(
        "/api/v1/user/auth/ai-learning-consent",
        headers={"Origin": "http://localhost:3000"},
        json={"allowed": True},
    )
    assert enabled.json()["ai_learning_consent"] is True

    with api_client.app.state.test_session_factory() as db:
        consent_records = db.scalars(select(AIConsent).where(AIConsent.user_id == user_id)).all()
        assert len(consent_records) == 1
        assert consent_records[0].allowed is True
        db.add(
            AIInteraction(
                user_id=user_id,
                consent_id=consent_records[0].id,
                environment="general",
                provider="test",
                prompt_content="consented prompt",
                response_content="consented answer",
                input_characters=16,
                output_characters=16,
                latency_ms=1,
                succeeded=True,
                training_eligible=False,
            )
        )
        db.commit()

    revoked = api_client.put(
        "/api/v1/user/auth/ai-learning-consent",
        headers={"Origin": "http://localhost:3000"},
        json={"allowed": False},
    )
    assert revoked.json()["ai_learning_consent"] is False
    with api_client.app.state.test_session_factory() as db:
        interaction = db.scalar(select(AIInteraction).where(AIInteraction.user_id == user_id))
        assert interaction.prompt_content is None
        assert interaction.response_content is None
        assert interaction.training_eligible is False
