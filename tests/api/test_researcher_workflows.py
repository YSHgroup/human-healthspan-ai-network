from dataclasses import replace
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.api.dependencies import identity


ADMIN_ORIGIN = {"Origin": "http://localhost:3003"}
RESEARCHER_ORIGIN = {"Origin": "http://localhost:3002"}


def register(client: TestClient, email: str, display_name: str) -> tuple[str, str]:
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
    return response.json()["id"], response.cookies.get("healthspan_session")


def use_session(client: TestClient, session: str) -> None:
    client.cookies.clear()
    client.cookies.set("healthspan_session", session, domain="testserver.local", path="/")


def platform_admin(client: TestClient, monkeypatch) -> tuple[str, str]:
    admin_id, admin_session = register(client, "admin@example.test", "Admin")
    monkeypatch.setattr(
        identity,
        "settings",
        replace(identity.settings, platform_admin_emails=("admin@example.test",)),
    )
    with client.app.state.test_session_factory() as db:
        from app.models import User

        admin = db.get(User, admin_id)
        assert admin is not None
        admin.email_verified_at = datetime.now(timezone.utc)
        db.commit()
    use_session(client, admin_session)
    return admin_id, admin_session


def approve_researcher(
    client: TestClient,
    admin_session: str,
    user_id: str,
    user_session: str,
) -> None:
    use_session(client, admin_session)
    response = client.put(
        f"/api/v1/admin/users/{user_id}/verification",
        headers=ADMIN_ORIGIN,
        json={"verified": True},
    )
    assert response.status_code == 200, response.text
    use_session(client, user_session)
    application = client.post(
        "/api/v1/user/researcher/applications",
        headers=RESEARCHER_ORIGIN,
        json={
            "biography": "Researcher focused on human healthspan and controlled research collaboration.",
            "research_interests": "Healthy aging, longitudinal studies",
            "affiliation": "Independent",
        },
    )
    assert application.status_code == 201, application.text
    use_session(client, admin_session)
    pending = client.get("/api/v1/admin/researcher/applications")
    assert pending.status_code == 200, pending.text
    application_id = next(item["id"] for item in pending.json() if item["user_id"] == user_id)
    decision = client.post(
        f"/api/v1/admin/researcher/applications/{application_id}/decision",
        headers=ADMIN_ORIGIN,
        json={"decision": "approve"},
    )
    assert decision.status_code == 200, decision.text


def test_researcher_organization_project_and_admin_workflows(
    api_client: TestClient,
    monkeypatch,
) -> None:
    admin_id, admin_session = platform_admin(api_client, monkeypatch)
    owner_id, owner_session = register(api_client, "owner@example.test", "Research Lead")
    member_id, member_session = register(api_client, "member@example.test", "Research Member")
    outsider_id, outsider_session = register(api_client, "outsider@example.test", "Outside Researcher")
    approve_researcher(api_client, admin_session, owner_id, owner_session)
    approve_researcher(api_client, admin_session, member_id, member_session)
    approve_researcher(api_client, admin_session, outsider_id, outsider_session)

    use_session(api_client, member_session)
    assert api_client.get("/api/v1/user/researcher/profiles").json() == []
    use_session(api_client, owner_session)
    profile_update = api_client.put(
        "/api/v1/user/researcher/profile",
        headers=RESEARCHER_ORIGIN,
        json={
            "biography": "Researcher focused on human healthspan and controlled research collaboration.",
            "research_interests": "Healthy aging, longitudinal studies",
            "affiliation": "Independent",
            "profile_public": True,
        },
    )
    assert profile_update.status_code == 200, profile_update.text
    use_session(api_client, member_session)
    assert [profile["user_id"] for profile in api_client.get(
        "/api/v1/user/researcher/profiles"
    ).json()] == [owner_id]

    use_session(api_client, owner_session)
    organization_request = api_client.post(
        "/api/v1/user/researcher/organizations/requests",
        headers=RESEARCHER_ORIGIN,
        json={
            "slug": "healthy-aging-lab",
            "name": "Healthy Aging Lab",
            "description": "A collaborative research group studying healthy aging.",
            "website": "https://aging.example.test",
        },
    )
    assert organization_request.status_code == 201, organization_request.text
    request_id = organization_request.json()["id"]

    use_session(api_client, admin_session)
    decision_url = f"/api/v1/admin/organizations/requests/{request_id}/decision"
    no_entitlement = api_client.post(
        decision_url,
        headers=ADMIN_ORIGIN,
        json={"decision": "approve"},
    )
    assert no_entitlement.status_code == 409
    grant = api_client.post(
        f"/api/v1/admin/users/{owner_id}/entitlements",
        headers=ADMIN_ORIGIN,
        json={"key": "organization_create"},
    )
    assert grant.status_code == 201, grant.text
    provisioned = api_client.post(
        decision_url,
        headers=ADMIN_ORIGIN,
        json={"decision": "approve"},
    )
    assert provisioned.status_code == 200, provisioned.text
    organization_id = provisioned.json()["organization_id"]

    use_session(api_client, owner_session)
    invite = api_client.post(
        f"/api/v1/user/researcher/organizations/{organization_id}/invitations",
        headers=RESEARCHER_ORIGIN,
        json={"email": "MEMBER@example.test", "role": "member"},
    )
    assert invite.status_code == 201, invite.text
    use_session(api_client, member_session)
    invitations = api_client.get("/api/v1/user/researcher/organizations/invitations")
    assert invitations.status_code == 200
    assert [item["id"] for item in invitations.json()] == [invite.json()["id"]]
    accepted = api_client.post(
        f"/api/v1/user/researcher/organizations/invitations/{invite.json()['id']}/accept",
        headers=RESEARCHER_ORIGIN,
    )
    assert accepted.status_code == 204, accepted.text

    use_session(api_client, owner_session)
    project = api_client.post(
        "/api/v1/user/researcher/projects",
        headers=RESEARCHER_ORIGIN,
        json={
            "title": "Healthspan cohort study",
            "description": "A project for evaluating longitudinal healthy aging measures.",
            "objectives": "Define a reproducible cohort protocol.",
            "research_questions": "Which measures predict healthspan?",
            "organization_id": organization_id,
            "visibility": "team",
        },
    )
    assert project.status_code == 201, project.text
    project_id = project.json()["id"]
    added = api_client.post(
        f"/api/v1/user/researcher/projects/{project_id}/members",
        headers=RESEARCHER_ORIGIN,
        json={"email": "member@example.test"},
    )
    assert added.status_code == 201, added.text

    task = api_client.post(
        f"/api/v1/user/researcher/projects/{project_id}/tasks",
        headers=RESEARCHER_ORIGIN,
        json={"title": "Review protocol", "assignee_email": "member@example.test"},
    )
    assert task.status_code == 201, task.text
    assert task.json()["assignee_id"] == member_id
    document = api_client.post(
        f"/api/v1/user/researcher/projects/{project_id}/documents",
        headers=RESEARCHER_ORIGIN,
        json={
            "title": "Shared protocol",
            "filename": "protocol.txt",
            "content": "This protocol is shared with authorized project members.",
            "access_scope": "project",
        },
    )
    assert document.status_code == 201, document.text
    private_document = api_client.post(
        f"/api/v1/user/researcher/projects/{project_id}/documents",
        headers=RESEARCHER_ORIGIN,
        json={
            "title": "Private notes",
            "filename": "notes.txt",
            "content": "Visible only to the uploader and project owner.",
        },
    )
    assert private_document.status_code == 201, private_document.text

    use_session(api_client, member_session)
    shared_documents = api_client.get(
        f"/api/v1/user/researcher/projects/{project_id}/documents"
    )
    assert shared_documents.status_code == 200, shared_documents.text
    assert [item["id"] for item in shared_documents.json()] == [document.json()["id"]]
    assert api_client.get(
        f"/api/v1/user/researcher/projects/{project_id}/tasks"
    ).status_code == 200

    use_session(api_client, outsider_session)
    denied_project = api_client.get(
        f"/api/v1/user/researcher/projects/{project_id}"
    )
    assert denied_project.status_code == 403
    assert api_client.get("/api/v1/user/researcher/projects").json() == []

    use_session(api_client, owner_session)
    public_project = api_client.post(
        "/api/v1/user/researcher/projects",
        headers=RESEARCHER_ORIGIN,
        json={
            "title": "Public research summary",
            "description": "A public project overview with protected resources.",
            "visibility": "public",
        },
    )
    assert public_project.status_code == 201, public_project.text
    public_project_id = public_project.json()["id"]
    use_session(api_client, outsider_session)
    assert api_client.get(
        f"/api/v1/user/researcher/projects/{public_project_id}"
    ).status_code == 200
    assert api_client.get(
        f"/api/v1/user/researcher/projects/{public_project_id}/tasks"
    ).status_code == 403
    assert api_client.get(
        f"/api/v1/user/researcher/projects/{public_project_id}/members"
    ).status_code == 403

    use_session(api_client, owner_session)
    starts_at = datetime.now(timezone.utc) + timedelta(days=7)
    event = api_client.post(
        "/api/v1/user/researcher/events",
        headers=RESEARCHER_ORIGIN,
        json={
            "title": "Research methods workshop",
            "description": "A workshop on reproducible healthspan research methods.",
            "organization_id": organization_id,
            "starts_at": starts_at.isoformat(),
            "ends_at": (starts_at + timedelta(hours=2)).isoformat(),
        },
    )
    assert event.status_code == 201, event.text
    use_session(api_client, member_session)
    registration = api_client.post(
        f"/api/v1/user/researcher/events/{event.json()['id']}/registration",
        headers=RESEARCHER_ORIGIN,
    )
    assert registration.status_code == 201, registration.text

    use_session(api_client, admin_session)
    canceled = api_client.post(
        f"/api/v1/admin/events/{event.json()['id']}/decision",
        headers=ADMIN_ORIGIN,
        json={"decision": "cancel"},
    )
    assert canceled.status_code == 200, canceled.text
    assert canceled.json()["status"] == "cancelled"
    audit = api_client.get("/api/v1/admin/audit/events")
    assert audit.status_code == 200
    assert any(item["action"] == "organization_request_decided" for item in audit.json())
    assert any(item["action"] == "research_event_cancelled" for item in audit.json())
    assert admin_id
