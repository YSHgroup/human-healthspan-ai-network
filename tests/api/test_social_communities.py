from fastapi.testclient import TestClient

from app.models import Community, CommunityMembership


ORIGIN = {"Origin": "http://localhost:3000"}


def register(client: TestClient, email: str, display_name: str) -> tuple[str, str]:
    response = client.post(
        "/api/v1/user/auth/register",
        headers=ORIGIN,
        json={
            "email": email,
            "display_name": display_name,
            "password": "a-secure-test-password",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"], client.cookies.get("healthspan_session")


def seed_community(
    client: TestClient,
    owner_id: str,
    *,
    slug: str = "healthspan",
    access_type: str = "open",
) -> str:
    with client.app.state.test_session_factory() as db:
        community = Community(
            slug=slug,
            name=f"{slug.title()} Community",
            description="A community for testing social workflows.",
            rules="Be kind and evidence-conscious.",
            access_type=access_type,
            created_by_id=owner_id,
        )
        db.add(community)
        db.flush()
        db.add(
            CommunityMembership(
                community_id=community.id,
                user_id=owner_id,
                role="owner",
                status="active",
            )
        )
        db.commit()
        return community.id


def activate_member(client: TestClient, community_id: str, user_id: str, role: str = "member") -> None:
    with client.app.state.test_session_factory() as db:
        db.add(
            CommunityMembership(
                community_id=community_id,
                user_id=user_id,
                role=role,
                status="active",
            )
        )
        db.commit()


def test_open_community_membership_discussion_comments_and_reactions(
    api_client: TestClient,
) -> None:
    owner_id, owner_session = register(api_client, "owner@example.test", "Owner")
    community_id = seed_community(api_client, owner_id)
    member_id, member_session = register(api_client, "member@example.test", "Member")

    communities = api_client.get("/api/v1/user/social/communities")
    assert communities.status_code == 200
    assert communities.json()[0]["membership_status"] == "none"

    joined = api_client.post(
        f"/api/v1/user/social/communities/{community_id}/join",
        headers=ORIGIN,
        json={"message": "Happy to join."},
    )
    assert joined.status_code == 201, joined.text
    assert joined.json()["status"] == "active"
    assert joined.json()["user_id"] == member_id

    post = api_client.post(
        f"/api/v1/user/social/communities/{community_id}/posts",
        headers=ORIGIN,
        json={"kind": "question", "body": "What does the evidence say?"},
    )
    assert post.status_code == 201, post.text
    assert api_client.get("/api/v1/user/social/feed").json() == []
    assert api_client.get(f"/api/v1/user/social/communities/{community_id}/posts").json()[0]["id"] == post.json()["id"]

    comment = api_client.post(
        f"/api/v1/user/social/posts/{post.json()['id']}/comments",
        headers=ORIGIN,
        json={"body": "Let's compare the available studies."},
    )
    assert comment.status_code == 201, comment.text
    assert api_client.get(f"/api/v1/user/social/posts/{post.json()['id']}/comments").json()[0]["id"] == comment.json()["id"]

    reaction = api_client.put(
        f"/api/v1/user/social/posts/{post.json()['id']}/reactions",
        headers=ORIGIN,
        json={"kind": "curious"},
    )
    assert reaction.status_code == 200
    assert reaction.json() == {
        "post_id": post.json()["id"],
        "count": 1,
        "current_user_reaction": "curious",
    }

    api_client.cookies.set("healthspan_session", owner_session)
    assert api_client.get(f"/api/v1/user/social/posts/{post.json()['id']}/reactions").json()["count"] == 1
    api_client.cookies.set("healthspan_session", member_session)
    removed = api_client.delete(
        f"/api/v1/user/social/posts/{post.json()['id']}/reactions",
        headers=ORIGIN,
    )
    assert removed.status_code == 200
    assert removed.json()["count"] == 0


def test_restricted_community_requires_moderator_approval(api_client: TestClient) -> None:
    owner_id, owner_session = register(api_client, "owner@example.test", "Owner")
    community_id = seed_community(api_client, owner_id, slug="research", access_type="restricted")
    applicant_id, applicant_session = register(api_client, "applicant@example.test", "Applicant")

    joined = api_client.post(
        f"/api/v1/user/social/communities/{community_id}/join",
        headers=ORIGIN,
        json={"message": "I would like to participate."},
    )
    assert joined.status_code == 201
    assert joined.json()["status"] == "pending"
    assert api_client.get(f"/api/v1/user/social/communities/{community_id}/posts").status_code == 403

    api_client.cookies.set("healthspan_session", applicant_session)
    assert api_client.post(
        f"/api/v1/user/social/communities/{community_id}/posts",
        headers=ORIGIN,
        json={"body": "This should be denied."},
    ).status_code == 403

    api_client.cookies.set("healthspan_session", owner_session)
    pending = api_client.get(
        f"/api/v1/user/social/communities/{community_id}/memberships/pending"
    )
    assert pending.status_code == 200
    assert pending.json()[0]["user_id"] == applicant_id

    decision = api_client.post(
        f"/api/v1/user/social/communities/{community_id}/memberships/{joined.json()['id']}/decision",
        headers=ORIGIN,
        json={"decision": "approve"},
    )
    assert decision.status_code == 200
    assert decision.json()["status"] == "active"
    api_client.cookies.set("healthspan_session", applicant_session)
    allowed = api_client.post(
        f"/api/v1/user/social/communities/{community_id}/posts",
        headers=ORIGIN,
        json={"body": "I am an approved member."},
    )
    assert allowed.status_code == 201, allowed.text


def test_non_moderator_cannot_review_membership_or_reports(api_client: TestClient) -> None:
    owner_id, _ = register(api_client, "owner@example.test", "Owner")
    community_id = seed_community(api_client, owner_id, slug="moderated", access_type="restricted")
    register(api_client, "member@example.test", "Member")

    denied = api_client.get(
        f"/api/v1/user/social/communities/{community_id}/memberships/pending"
    )
    denied_reports = api_client.get(
        f"/api/v1/user/social/communities/{community_id}/moderation/reports"
    )
    denied_appeals = api_client.get(
        f"/api/v1/user/social/communities/{community_id}/moderation/appeals"
    )
    assert denied.status_code == 403
    assert denied_reports.status_code == 403
    assert denied_appeals.status_code == 403


def test_moderator_can_remove_content_and_accept_an_appeal(api_client: TestClient) -> None:
    owner_id, owner_session = register(api_client, "owner@example.test", "Owner")
    community_id = seed_community(api_client, owner_id, slug="moderation")
    author_id, author_session = register(api_client, "author@example.test", "Author")
    activate_member(api_client, community_id, author_id)
    reporter_id, reporter_session = register(api_client, "reporter@example.test", "Reporter")
    activate_member(api_client, community_id, reporter_id)

    api_client.cookies.set("healthspan_session", author_session)
    post = api_client.post(
        f"/api/v1/user/social/communities/{community_id}/posts",
        headers=ORIGIN,
        json={"body": "A post moderators will review."},
    ).json()
    comment = api_client.post(
        f"/api/v1/user/social/posts/{post['id']}/comments",
        headers=ORIGIN,
        json={"body": "A comment that can also be reported."},
    ).json()

    api_client.cookies.set("healthspan_session", reporter_session)
    report = api_client.post(
        f"/api/v1/user/social/posts/{post['id']}/reports",
        headers=ORIGIN,
        json={"reason": "Please review this post."},
    )
    comment_report = api_client.post(
        f"/api/v1/user/social/comments/{comment['id']}/reports",
        headers=ORIGIN,
        json={"reason": "Please review this comment."},
    )
    assert report.status_code == 201, report.text
    assert comment_report.status_code == 201, comment_report.text

    api_client.cookies.set("healthspan_session", owner_session)
    queue = api_client.get(
        f"/api/v1/user/social/communities/{community_id}/moderation/reports"
    )
    assert queue.status_code == 200
    assert len(queue.json()) == 2
    action = api_client.post(
        f"/api/v1/user/social/communities/{community_id}/moderation/reports/{report.json()['id']}/actions",
        headers=ORIGIN,
        json={"action": "remove", "reason": "Violates the community rules."},
    )
    assert action.status_code == 201, action.text
    assert api_client.get(f"/api/v1/user/social/communities/{community_id}/posts").json() == []

    api_client.cookies.set("healthspan_session", author_session)
    appeal = api_client.post(
        f"/api/v1/user/social/me/moderation/actions/{action.json()['id']}/appeals",
        headers=ORIGIN,
        json={"reason": "This post does not violate the rules."},
    )
    assert appeal.status_code == 201, appeal.text

    api_client.cookies.set("healthspan_session", author_session)
    member_actions = api_client.get("/api/v1/user/social/me/moderation/actions")
    assert member_actions.status_code == 200
    assert member_actions.json()[0]["id"] == action.json()["id"]

    api_client.cookies.set("healthspan_session", owner_session)
    pending_appeals = api_client.get(
        f"/api/v1/user/social/communities/{community_id}/moderation/appeals"
    )
    assert pending_appeals.status_code == 200
    assert pending_appeals.json()[0]["id"] == appeal.json()["id"]
    decision = api_client.post(
        f"/api/v1/user/social/communities/{community_id}/moderation/appeals/{appeal.json()['id']}/decision",
        headers=ORIGIN,
        json={"decision": "overturned"},
    )
    assert decision.status_code == 200
    assert decision.json()["status"] == "overturned"
    assert len(api_client.get(f"/api/v1/user/social/communities/{community_id}/posts").json()) == 1


def test_temporary_suspension_blocks_posting_and_can_be_appealed(api_client: TestClient) -> None:
    owner_id, owner_session = register(api_client, "owner@example.test", "Owner")
    community_id = seed_community(api_client, owner_id, slug="suspension")
    member_id, member_session = register(api_client, "member@example.test", "Member")
    activate_member(api_client, community_id, member_id)
    reporter_id, reporter_session = register(api_client, "reporter@example.test", "Reporter")
    activate_member(api_client, community_id, reporter_id)

    api_client.cookies.set("healthspan_session", member_session)
    post = api_client.post(
        f"/api/v1/user/social/communities/{community_id}/posts",
        headers=ORIGIN,
        json={"body": "This post will be reported."},
    ).json()
    api_client.cookies.set("healthspan_session", reporter_session)
    report = api_client.post(
        f"/api/v1/user/social/posts/{post['id']}/reports",
        headers=ORIGIN,
        json={"reason": "Needs a moderator review."},
    ).json()
    api_client.cookies.set("healthspan_session", owner_session)
    action = api_client.post(
        f"/api/v1/user/social/communities/{community_id}/moderation/reports/{report['id']}/actions",
        headers=ORIGIN,
        json={
            "action": "suspend",
            "reason": "Temporary posting suspension.",
            "duration_hours": 24,
        },
    )
    assert action.status_code == 201, action.text

    api_client.cookies.set("healthspan_session", member_session)
    blocked = api_client.post(
        f"/api/v1/user/social/communities/{community_id}/posts",
        headers=ORIGIN,
        json={"body": "This should be blocked."},
    )
    assert blocked.status_code == 403
    appeal = api_client.post(
        f"/api/v1/user/social/me/moderation/actions/{action.json()['id']}/appeals",
        headers=ORIGIN,
        json={"reason": "Please reconsider the suspension."},
    )
    assert appeal.status_code == 201

    api_client.cookies.set("healthspan_session", owner_session)
    overturned = api_client.post(
        f"/api/v1/user/social/communities/{community_id}/moderation/appeals/{appeal.json()['id']}/decision",
        headers=ORIGIN,
        json={"decision": "overturned"},
    )
    assert overturned.status_code == 200

    api_client.cookies.set("healthspan_session", member_session)
    allowed = api_client.post(
        f"/api/v1/user/social/communities/{community_id}/posts",
        headers=ORIGIN,
        json={"body": "The appeal restored my posting access."},
    )
    assert allowed.status_code == 201, allowed.text


def test_community_creation_requests_are_free_and_unique(api_client: TestClient) -> None:
    register(api_client, "requester@example.test", "Requester")
    request = api_client.post(
        "/api/v1/user/social/communities/requests",
        headers=ORIGIN,
        json={
            "slug": "sleep-research",
            "name": "Sleep Research",
            "description": "A community for discussing sleep and healthy aging.",
            "access_type": "restricted",
        },
    )
    duplicate = api_client.post(
        "/api/v1/user/social/communities/requests",
        headers=ORIGIN,
        json={
            "slug": "sleep-research",
            "name": "Another Sleep Community",
            "description": "This slug is already pending.",
            "access_type": "open",
        },
    )

    assert request.status_code == 201, request.text
    assert request.json()["status"] == "pending"
    assert duplicate.status_code == 409
