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
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_authenticated_member_can_publish_to_public_feed(api_client: TestClient) -> None:
    user_id = register(api_client, "author@example.test", "Author")

    published = api_client.post(
        "/api/v1/user/social/posts",
        headers={"Origin": "http://localhost:3000"},
        json={"kind": "question", "body": "  What supports healthy aging?  "},
    )

    assert published.status_code == 201, published.text
    assert published.json()["author_id"] == user_id
    assert published.json()["author_display_name"] == "Author"
    assert published.json()["body"] == "What supports healthy aging?"
    assert published.json()["kind"] == "question"

    feed = api_client.get("/api/v1/user/social/feed")
    assert feed.status_code == 200
    assert [post["id"] for post in feed.json()] == [published.json()["id"]]


def test_social_post_creation_requires_authentication_and_trusted_origin(
    api_client: TestClient,
) -> None:
    payload = {"kind": "discussion", "body": "A public discussion"}
    unauthenticated = api_client.post(
        "/api/v1/user/social/posts",
        headers={"Origin": "http://localhost:3000"},
        json=payload,
    )
    assert unauthenticated.status_code == 401

    register(api_client, "author@example.test", "Author")
    untrusted = api_client.post(
        "/api/v1/user/social/posts",
        headers={"Origin": "https://untrusted.example"},
        json=payload,
    )
    missing_origin = api_client.post("/api/v1/user/social/posts", json=payload)

    assert untrusted.status_code == 403
    assert missing_origin.status_code == 403
    assert api_client.get("/api/v1/user/social/feed").json() == []


def test_public_feed_is_bounded_and_rejects_blank_posts(api_client: TestClient) -> None:
    register(api_client, "author@example.test", "Author")
    blank = api_client.post(
        "/api/v1/user/social/posts",
        headers={"Origin": "http://localhost:3000"},
        json={"kind": "discussion", "body": "   "},
    )
    invalid_limit = api_client.get("/api/v1/user/social/feed?limit=101")

    assert blank.status_code == 422
    assert invalid_limit.status_code == 422


def test_member_can_report_another_members_post_once(api_client: TestClient) -> None:
    register(api_client, "author@example.test", "Author")
    post = api_client.post(
        "/api/v1/user/social/posts",
        headers={"Origin": "http://localhost:3000"},
        json={"body": "Please review this post"},
    ).json()

    register(api_client, "reporter@example.test", "Reporter")
    headers = {"Origin": "http://localhost:3001"}
    report = api_client.post(
        f"/api/v1/user/social/posts/{post['id']}/reports",
        headers=headers,
        json={"reason": "This appears to violate the community rules."},
    )
    duplicate = api_client.post(
        f"/api/v1/user/social/posts/{post['id']}/reports",
        headers=headers,
        json={"reason": "Duplicate report."},
    )
    own_post = api_client.post(
        "/api/v1/user/social/posts",
        headers=headers,
        json={"body": "My own post"},
    ).json()
    self_report = api_client.post(
        f"/api/v1/user/social/posts/{own_post['id']}/reports",
        headers=headers,
        json={"reason": "This is my own post."},
    )

    assert report.status_code == 201, report.text
    assert report.json()["status"] == "pending"
    assert duplicate.status_code == 409
    assert self_report.status_code == 404


def test_post_reports_require_authentication_and_trusted_origin(api_client: TestClient) -> None:
    register(api_client, "author@example.test", "Author")
    post = api_client.post(
        "/api/v1/user/social/posts",
        headers={"Origin": "http://localhost:3000"},
        json={"body": "A post to report"},
    ).json()

    api_client.cookies.clear()
    unauthenticated = api_client.post(
        f"/api/v1/user/social/posts/{post['id']}/reports",
        headers={"Origin": "http://localhost:3000"},
        json={"reason": "Needs review."},
    )
    register(api_client, "reporter@example.test", "Reporter")
    untrusted = api_client.post(
        f"/api/v1/user/social/posts/{post['id']}/reports",
        headers={"Origin": "https://untrusted.example"},
        json={"reason": "Needs review."},
    )

    assert unauthenticated.status_code == 401
    assert untrusted.status_code == 403
