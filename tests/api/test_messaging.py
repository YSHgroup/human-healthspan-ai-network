from fastapi.testclient import TestClient


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
    assert response.status_code == 201
    return client.cookies.get("healthspan_session")


def test_authenticated_users_can_exchange_text_messages(api_client: TestClient) -> None:
    first_session = register(api_client, "first@example.test", "First")
    second_session = register(api_client, "second@example.test", "Second")
    api_client.cookies.set("healthspan_session", first_session)

    conversation = api_client.post(
        "/api/v1/user/social/messages/conversations",
        headers={"Origin": "http://localhost:3000"},
        json={"participant_emails": ["second@example.test"]},
    )

    assert conversation.status_code == 201, conversation.text
    conversation_id = conversation.json()["id"]
    sent = api_client.post(
        f"/api/v1/user/social/messages/conversations/{conversation_id}/messages",
        headers={"Origin": "http://localhost:3000"},
        json={"body": "Hello from localhost."},
    )
    assert sent.status_code == 201
    assert sent.json()["body"] == "Hello from localhost."

    api_client.cookies.set("healthspan_session", second_session)
    received = api_client.get(
        f"/api/v1/user/social/messages/conversations/{conversation_id}/messages"
    )
    assert received.status_code == 200
    assert [message["body"] for message in received.json()] == ["Hello from localhost."]


def test_conversation_messages_are_hidden_from_nonparticipants(api_client: TestClient) -> None:
    first_session = register(api_client, "first@example.test", "First")
    register(api_client, "second@example.test", "Second")
    outsider_session = register(api_client, "outsider@example.test", "Outsider")
    api_client.cookies.set("healthspan_session", first_session)
    conversation = api_client.post(
        "/api/v1/user/social/messages/conversations",
        headers={"Origin": "http://localhost:3000"},
        json={"participant_emails": ["second@example.test"]},
    ).json()

    api_client.cookies.set("healthspan_session", outsider_session)
    response = api_client.get(
        f"/api/v1/user/social/messages/conversations/{conversation['id']}/messages"
    )

    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_messaging_is_authenticated_and_text_only(api_client: TestClient) -> None:
    unauthenticated = api_client.get("/api/v1/user/social/messages/conversations")
    assert unauthenticated.status_code == 401

    first_session = register(api_client, "first@example.test", "First")
    register(api_client, "second@example.test", "Second")
    api_client.cookies.set("healthspan_session", first_session)
    api_client.post(
        "/api/v1/user/social/messages/conversations",
        headers={"Origin": "http://localhost:3000"},
        json={"participant_emails": ["second@example.test"]},
    )
    conversation = api_client.get("/api/v1/user/social/messages/conversations").json()[0]
    invalid_message = api_client.post(
        f"/api/v1/user/social/messages/conversations/{conversation['id']}/messages",
        headers={"Origin": "http://localhost:3000"},
        json={"body": " ", "attachment": "must-not-be-accepted"},
    )
    assert invalid_message.status_code == 422
