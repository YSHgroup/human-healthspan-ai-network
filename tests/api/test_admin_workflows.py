from dataclasses import replace
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.api.dependencies import identity
from app.models import (
    Community,
    CommunityMembership,
    CommunityCreationRequest,
    SocialPost,
    SocialPostReport,
    User,
)


ORIGIN = {"Origin": "http://localhost:3003"}
SOCIAL_ORIGIN = {"Origin": "http://localhost:3000"}


def register(client: TestClient, email: str, display_name: str) -> tuple[str, str]:
    response = client.post(
        "/api/v1/user/auth/register",
        headers=SOCIAL_ORIGIN,
        json={
            "email": email,
            "display_name": display_name,
            "password": "a-secure-test-password",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"], client.cookies.get("healthspan_session")


def test_allowlisted_unverified_account_cannot_access_platform_admin(
    api_client: TestClient,
    monkeypatch,
) -> None:
    admin_id, admin_session = register(api_client, "admin@example.test", "Admin")
    monkeypatch.setattr(
        identity,
        "settings",
        replace(identity.settings, platform_admin_emails=("admin@example.test",)),
    )
    api_client.cookies.set("healthspan_session", admin_session)
    assert api_client.get("/api/v1/admin/communities/requests").status_code == 403

    with api_client.app.state.test_session_factory() as db:
        admin = db.get(User, admin_id)
        assert admin is not None
        admin.email_verified_at = datetime.now(timezone.utc)
        db.commit()
    assert api_client.get("/api/v1/admin/communities/requests").status_code == 200


def enable_platform_admin(monkeypatch, client: TestClient, admin_id: str) -> None:
    monkeypatch.setattr(
        identity,
        "settings",
        replace(identity.settings, platform_admin_emails=("admin@example.test",)),
    )
    with client.app.state.test_session_factory() as db:
        admin = db.get(User, admin_id)
        assert admin is not None
        admin.email_verified_at = datetime.now(timezone.utc)
        db.commit()


def test_platform_admin_approves_and_provisions_community_request(
    api_client: TestClient,
    monkeypatch,
) -> None:
    requester_id, requester_session = register(api_client, "requester@example.test", "Requester")
    request = api_client.post(
        "/api/v1/user/social/communities/requests",
        headers=SOCIAL_ORIGIN,
        json={
            "slug": "sleep-research",
            "name": "Sleep Research",
            "description": "A community for discussing sleep and healthy aging.",
            "access_type": "restricted",
        },
    )
    assert request.status_code == 201, request.text
    request_id = request.json()["id"]

    denied = api_client.get("/api/v1/admin/communities/requests")
    assert denied.status_code == 403

    admin_id, admin_session = register(api_client, "admin@example.test", "Admin")
    enable_platform_admin(monkeypatch, api_client, admin_id)
    api_client.cookies.set("healthspan_session", admin_session)
    requests = api_client.get("/api/v1/admin/communities/requests")
    assert requests.status_code == 200
    assert [item["id"] for item in requests.json()] == [request_id]

    decision = api_client.post(
        f"/api/v1/admin/communities/requests/{request_id}/decision",
        headers=ORIGIN,
        json={"decision": "approve"},
    )
    assert decision.status_code == 200, decision.text
    assert decision.json()["status"] == "approved"
    community_id = decision.json()["community_id"]

    with api_client.app.state.test_session_factory() as db:
        creation_request = db.get(CommunityCreationRequest, request_id)
        community = db.get(Community, community_id)
        membership = db.query(CommunityMembership).filter_by(
            community_id=community_id,
            user_id=requester_id,
        ).one()
        assert creation_request.status == "approved"
        assert creation_request.reviewed_by_id == admin_id
        assert creation_request.reviewed_at is not None
        assert community.created_by_id == requester_id
        assert membership.role == "owner"
        assert membership.status == "active"
        assert membership.reviewed_by_id == admin_id

    api_client.cookies.set("healthspan_session", requester_session)
    communities = api_client.get("/api/v1/user/social/communities")
    assert communities.status_code == 200
    assert next(item for item in communities.json() if item["id"] == community_id)[
        "membership_role"
    ] == "owner"


def test_platform_admin_rejects_request_without_provisioning(
    api_client: TestClient,
    monkeypatch,
) -> None:
    register(api_client, "requester@example.test", "Requester")
    request = api_client.post(
        "/api/v1/user/social/communities/requests",
        headers=SOCIAL_ORIGIN,
        json={
            "slug": "sleep-research",
            "name": "Sleep Research",
            "description": "A community for discussing sleep and healthy aging.",
            "access_type": "open",
        },
    )
    admin_id, admin_session = register(api_client, "admin@example.test", "Admin")
    enable_platform_admin(monkeypatch, api_client, admin_id)
    api_client.cookies.set("healthspan_session", admin_session)

    decision = api_client.post(
        f"/api/v1/admin/communities/requests/{request.json()['id']}/decision",
        headers=ORIGIN,
        json={"decision": "reject"},
    )
    assert decision.status_code == 200, decision.text
    assert decision.json()["status"] == "rejected"
    assert decision.json()["community_id"] is None

    with api_client.app.state.test_session_factory() as db:
        creation_request = db.get(CommunityCreationRequest, request.json()["id"])
        assert creation_request.status == "rejected"
        assert creation_request.reviewed_by_id == admin_id
        assert db.query(Community).filter_by(slug="sleep-research").count() == 0


def test_platform_queue_reviews_global_and_escalated_reports_and_appeals(
    api_client: TestClient,
    monkeypatch,
) -> None:
    author_id, author_session = register(api_client, "author@example.test", "Author")
    reporter_id, reporter_session = register(api_client, "reporter@example.test", "Reporter")
    admin_id, admin_session = register(api_client, "admin@example.test", "Admin")
    enable_platform_admin(monkeypatch, api_client, admin_id)

    with api_client.app.state.test_session_factory() as db:
        community = Community(
            slug="community-review",
            name="Community Review",
            description="A community for moderation workflow coverage.",
            rules="Be considerate.",
            access_type="open",
            created_by_id=author_id,
        )
        db.add(community)
        db.flush()
        db.add_all(
            [
                CommunityMembership(
                    community_id=community.id,
                    user_id=author_id,
                    role="member",
                    status="active",
                ),
                CommunityMembership(
                    community_id=community.id,
                    user_id=reporter_id,
                    role="owner",
                    status="active",
                ),
            ]
        )
        db.commit()
        community_id = community.id

    api_client.cookies.set("healthspan_session", author_session)
    global_post = api_client.post(
        "/api/v1/user/social/posts",
        headers=SOCIAL_ORIGIN,
        json={"body": "A global post for platform review."},
    ).json()
    global_comment = api_client.post(
        f"/api/v1/user/social/posts/{global_post['id']}/comments",
        headers=SOCIAL_ORIGIN,
        json={"body": "A global comment for platform review."},
    ).json()
    escalated_post = api_client.post(
        f"/api/v1/user/social/communities/{community_id}/posts",
        headers=SOCIAL_ORIGIN,
        json={"body": "A community post to escalate."},
    ).json()
    local_post = api_client.post(
        f"/api/v1/user/social/communities/{community_id}/posts",
        headers=SOCIAL_ORIGIN,
        json={"body": "A community report that stays local."},
    ).json()

    api_client.cookies.set("healthspan_session", reporter_session)
    global_report = api_client.post(
        f"/api/v1/user/social/posts/{global_post['id']}/reports",
        headers=SOCIAL_ORIGIN,
        json={"reason": "Please review this global post."},
    ).json()
    global_comment_report = api_client.post(
        f"/api/v1/user/social/comments/{global_comment['id']}/reports",
        headers=SOCIAL_ORIGIN,
        json={"reason": "Please review this global comment."},
    ).json()
    escalated_report = api_client.post(
        f"/api/v1/user/social/posts/{escalated_post['id']}/reports",
        headers=SOCIAL_ORIGIN,
        json={"reason": "This community report needs escalation."},
    ).json()
    local_report = api_client.post(
        f"/api/v1/user/social/posts/{local_post['id']}/reports",
        headers=SOCIAL_ORIGIN,
        json={"reason": "This should remain in the community queue."},
    ).json()

    api_client.cookies.set("healthspan_session", reporter_session)
    escalation_action = api_client.post(
        f"/api/v1/user/social/communities/{community_id}/moderation/reports/{escalated_report['id']}/actions",
        headers=SOCIAL_ORIGIN,
        json={"action": "escalate", "reason": "Requires platform review."},
    )
    assert escalation_action.status_code == 201, escalation_action.text

    api_client.cookies.set("healthspan_session", reporter_session)
    forbidden = api_client.get("/api/v1/admin/moderation/reports")
    assert forbidden.status_code == 403
    api_client.cookies.set("healthspan_session", admin_session)
    queue = api_client.get("/api/v1/admin/moderation/reports")
    assert queue.status_code == 200, queue.text
    by_id = {report["id"]: report for report in queue.json()}
    assert set(by_id) == {
        global_report["id"],
        global_comment_report["id"],
        escalated_report["id"],
    }
    assert by_id[global_report["id"]]["status"] == "pending"
    assert by_id[global_report["id"]]["community_id"] is None
    assert by_id[global_comment_report["id"]]["target_kind"] == "comment"
    assert by_id[global_comment_report["id"]]["target_body"] == global_comment["body"]
    assert by_id[escalated_report["id"]]["status"] == "escalated"
    assert by_id[escalated_report["id"]]["community_id"] == community_id

    action = api_client.post(
        f"/api/v1/admin/moderation/reports/{global_report['id']}/actions",
        headers=ORIGIN,
        json={"action": "remove", "reason": "The global post violated network rules."},
    )
    assert action.status_code == 201, action.text
    assert action.json()["community_id"] is None

    api_client.cookies.set("healthspan_session", author_session)
    appeal = api_client.post(
        f"/api/v1/user/social/me/moderation/actions/{action.json()['id']}/appeals",
        headers=SOCIAL_ORIGIN,
        json={"reason": "Please review the removal decision."},
    )
    assert appeal.status_code == 201, appeal.text

    api_client.cookies.set("healthspan_session", admin_session)
    pending_appeals = api_client.get("/api/v1/admin/moderation/appeals")
    assert pending_appeals.status_code == 200, pending_appeals.text
    assert pending_appeals.json()[0]["action"] == "remove"
    overturn = api_client.post(
        f"/api/v1/admin/moderation/appeals/{appeal.json()['id']}/decision",
        headers=ORIGIN,
        json={"decision": "overturned"},
    )
    assert overturn.status_code == 200, overturn.text

    dismiss_comment = api_client.post(
        f"/api/v1/admin/moderation/reports/{global_comment_report['id']}/actions",
        headers=ORIGIN,
        json={"action": "dismiss", "reason": "The global comment was reviewed."},
    )
    assert dismiss_comment.status_code == 201, dismiss_comment.text
    dismiss = api_client.post(
        f"/api/v1/admin/moderation/reports/{escalated_report['id']}/actions",
        headers=ORIGIN,
        json={"action": "dismiss", "reason": "The community escalation was reviewed."},
    )
    assert dismiss.status_code == 201, dismiss.text
    assert api_client.get("/api/v1/admin/moderation/reports").json() == []

    with api_client.app.state.test_session_factory() as db:
        global_post_model = db.get(SocialPost, global_post["id"])
        global_report_model = db.get(SocialPostReport, global_report["id"])
        local_report_model = db.get(SocialPostReport, local_report["id"])
        assert global_post_model.moderation_status == "published"
        assert global_report_model.status == "reviewed"
        assert local_report_model.status == "pending"
