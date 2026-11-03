"""Contract tests for the Architecture v1.2 platform domains.

Run with: pytest tests -q  (needs the API requirements installed).
"""
import os
import sys
from datetime import timedelta
from pathlib import Path
from uuid import UUID

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("APP_ENV", "test")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "api"))

import pytest
from fastapi.testclient import TestClient

from app.db.base import Base, utc_now
from app.db.session import SessionLocal, engine
from app.main import app
from app.models.domain import User
from app.models.platform import HealthRecord, Notification

from test_api_contract import auth_header, register  # noqa: E402


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


def make_user(client: TestClient, email: str, role: str | None = None) -> tuple[dict, dict]:
    account = register(client, email)
    if role:
        with SessionLocal() as db:
            db.get(User, UUID(account["user"]["id"])).role = role
            db.commit()
    return account, auth_header(account["tokens"]["access_token"])


def grant(client, admin_headers, feature, user_id=None, organization_id=None, quantity=1):
    body = {"feature": feature, "quantity": quantity, "reason": "test grant"}
    if user_id:
        body["user_id"] = user_id
    if organization_id:
        body["organization_id"] = organization_id
    response = client.post("/api/v1/admin/entitlements", headers=admin_headers, json=body)
    assert response.status_code == 201, response.text
    return response.json()


def approved_researcher(client, admin_headers, email):
    account, headers = make_user(client, email)
    applied = client.post(
        "/api/v1/user/researcher/membership/apply",
        headers=headers,
        json={"statement": "Longevity biology researcher with published work."},
    )
    assert applied.status_code == 201, applied.text
    decision = client.post(
        f"/api/v1/admin/research-memberships/{account['user']['id']}/decision",
        headers=admin_headers,
        json={"decision": "approve", "note": "Credentials reviewed"},
    )
    assert decision.status_code == 200, decision.text
    return account, headers


def create_org(client, admin_headers, headers, account, name="Longevity Lab"):
    grant(client, admin_headers, "organization.create", user_id=account["user"]["id"])
    response = client.post("/api/v1/user/researcher/organizations", headers=headers, json={"name": name})
    assert response.status_code == 201, response.text
    return response.json()


# ----------------------------------------------------------------------------- API boundaries
def test_portal_boundaries_alias_existing_mvp_behavior(client):
    _, headers = make_user(client, "alias@example.org")
    post = client.post("/api/v1/user/social/posts", headers=headers, json={"body": "Sleep timing and recovery notes."})
    assert post.status_code == 201
    legacy = client.get("/api/v1/feed")
    portal = client.get("/api/v1/user/social/feed")
    assert legacy.status_code == portal.status_code == 200
    assert [p["id"] for p in legacy.json()] == [p["id"] for p in portal.json()]
    assert client.get("/api/v1/user/personal/profile", headers=headers).status_code == 200
    project = client.post(
        "/api/v1/user/researcher/projects",
        headers=headers,
        json={"title": "Alias project", "description": "Checks alias parity.", "visibility": "private"},
    )
    assert project.status_code == 201


# ----------------------------------------------------------------------------- entitlements and organizations
def test_organization_requires_researcher_access_and_entitlement(client):
    _, admin_headers = make_user(client, "admin1@example.org", "admin")
    account, headers = make_user(client, "member1@example.org")
    denied = client.post("/api/v1/user/researcher/organizations", headers=headers, json={"name": "No Access Org"})
    assert denied.status_code == 403
    researcher, researcher_headers = approved_researcher(client, admin_headers, "res1@example.org")
    no_entitlement = client.post(
        "/api/v1/user/researcher/organizations", headers=researcher_headers, json={"name": "Unpaid Org"}
    )
    assert no_entitlement.status_code == 403 and "premium" in no_entitlement.json()["detail"].lower()
    organization = create_org(client, admin_headers, researcher_headers, researcher)
    assert organization["my_role"] == "founder"
    # one entitlement unit consumed: a second organization is refused
    again = client.post("/api/v1/user/researcher/organizations", headers=researcher_headers, json={"name": "Second Org"})
    assert again.status_code == 403
    badges = client.get(f"/api/v1/user/researcher/organizations/{organization['id']}/badges", headers=researcher_headers)
    assert len(badges.json()) == 2  # two default contributor badges
    extra = client.post(
        f"/api/v1/user/researcher/organizations/{organization['id']}/badges",
        headers=researcher_headers,
        json={"name": "Mentor"},
    )
    assert extra.status_code == 403  # extra badges are paid


def test_purchase_flow_creates_entitlement_only_when_paid(client):
    _, admin_headers = make_user(client, "admin2@example.org", "admin")
    account, headers = make_user(client, "buyer@example.org")
    purchase = client.post("/api/v1/user/personal/purchases", headers=headers, json={"feature": "event.create"})
    assert purchase.status_code == 201 and purchase.json()["status"] == "pending"
    mine = client.get("/api/v1/user/personal/entitlements", headers=headers).json()
    assert mine["entitlements"] == []
    paid = client.post(
        f"/api/v1/admin/payments/{purchase.json()['id']}/decision",
        headers=admin_headers,
        json={"status": "paid", "reason": "Bank transfer confirmed"},
    )
    assert paid.status_code == 200
    mine = client.get("/api/v1/user/personal/entitlements", headers=headers).json()
    assert [item["feature"] for item in mine["entitlements"]] == ["event.create"]
    assert client.post(
        f"/api/v1/admin/payments/{purchase.json()['id']}/decision",
        headers=admin_headers,
        json={"status": "paid", "reason": "duplicate click"},
    ).json()["status"] == "paid"
    assert len(client.get("/api/v1/user/personal/entitlements", headers=headers).json()["entitlements"]) == 1
    assert client.get("/api/v1/admin/payments", headers=headers).status_code == 403


def test_organization_isolation_and_invitation_flow(client):
    _, admin_headers = make_user(client, "admin3@example.org", "admin")
    founder, founder_headers = approved_researcher(client, admin_headers, "founder@example.org")
    organization = create_org(client, admin_headers, founder_headers, founder)
    outsider, outsider_headers = make_user(client, "outsider@example.org")
    base = f"/api/v1/user/researcher/organizations/{organization['id']}"
    assert client.get(f"{base}/members", headers=outsider_headers).status_code == 404
    assert client.get(f"{base}/documents".replace("organizations", "organization-ai"), headers=outsider_headers).status_code == 404
    invite = client.post(f"{base}/invitations", headers=founder_headers, json={"user_id": outsider["user"]["id"], "role": "researcher"})
    assert invite.status_code == 201
    invitations = client.get("/api/v1/user/social/invitations", headers=outsider_headers).json()
    assert len(invitations) == 1 and invitations[0]["organization_name"] == "Longevity Lab"
    assert client.post(f"/api/v1/user/social/invitations/{invitations[0]['id']}/accept", headers=outsider_headers).json() == {"status": "accepted"}
    members = client.get(f"{base}/members", headers=outsider_headers).json()
    assert {m["role"] for m in members} == {"founder", "researcher"}
    # a researcher cannot manage the organization
    assert client.patch(base, headers=outsider_headers, json={"description": "hijack"}).status_code == 403
    with SessionLocal() as db:
        assert db.query(Notification).filter(Notification.kind == "organization.invitation").count() == 1


# ----------------------------------------------------------------------------- professional identity
def test_professional_verification_and_append_only_work_history(client):
    _, admin_headers = make_user(client, "admin4@example.org", "admin")
    lead, lead_headers = approved_researcher(client, admin_headers, "lead@example.org")
    organization = create_org(client, admin_headers, lead_headers, lead)
    worker, worker_headers = approved_researcher(client, admin_headers, "worker@example.org")
    base = f"/api/v1/user/researcher/organizations/{organization['id']}"
    client.post(f"{base}/invitations", headers=lead_headers, json={"user_id": worker["user"]["id"], "role": "researcher"})
    invitation = client.get("/api/v1/user/social/invitations", headers=worker_headers).json()[0]
    client.post(f"/api/v1/user/social/invitations/{invitation['id']}/accept", headers=worker_headers)

    record = client.post(
        "/api/v1/user/personal/professional",
        headers=worker_headers,
        json={"kind": "education", "title": "PhD Molecular Biology", "institution": "Example University", "start_year": 2015, "end_year": 2019},
    )
    assert record.status_code == 201 and record.json()["verification_color"] == "yellow"
    verified = client.post(f"{base}/members/{worker['user']['id']}/professional/{record.json()['id']}/verify", headers=lead_headers)
    assert verified.status_code == 200 and verified.json()["verification_color"] == "green"
    edited = client.patch(f"/api/v1/user/personal/professional/{record.json()['id']}", headers=worker_headers, json={"title": "PhD Biochemistry"})
    assert edited.json()["verification_status"] == "unverified"  # editing invalidates verification
    other = client.post(f"{base}/members/{lead['user']['id']}/professional/{record.json()['id']}/verify", headers=lead_headers)
    assert other.status_code == 404  # record does not belong to that member

    # task completion creates organization work history
    project = client.post(
        "/api/v1/user/researcher/projects",
        headers=lead_headers,
        json={"title": "Org study", "description": "Rapamycin literature review", "visibility": "team"},
    ).json()
    assert client.post(f"{base}/projects", headers=lead_headers, json={"project_id": project["id"]}).status_code == 201
    client.post(f"/api/v1/user/researcher/projects/{project['id']}/members", headers=lead_headers, json={"user_id": worker["user"]["id"], "role": "member"})
    task = client.post(
        f"/api/v1/user/researcher/projects/{project['id']}/tasks",
        headers=lead_headers,
        json={"title": "Screen 20 papers", "assignee_id": worker["user"]["id"]},
    )
    assert task.status_code == 201, task.text
    done = client.patch(f"/api/v1/user/researcher/tasks/{task.json()['id']}", headers=lead_headers, json={"status": "done"})
    assert done.status_code == 200 and done.json()["completed_at"]
    history = client.get("/api/v1/user/personal/professional/work-history/entries", headers=worker_headers).json()
    assert len(history) == 1 and history[0]["organization_id"] == organization["id"]
    entry_id = history[0]["id"]
    assert client.post(f"{base}/work-history/{entry_id}/verify", headers=lead_headers).json()["verification_status"] == "verified"
    amend = client.post(
        f"/api/v1/user/personal/professional/work-history/entries/{entry_id}/amend",
        headers=worker_headers,
        json={"summary": "Screened and extracted 20 papers"},
    )
    assert amend.status_code == 201 and amend.json()["supersedes_id"] == entry_id
    visible = client.get("/api/v1/user/personal/professional/work-history/entries", headers=worker_headers).json()
    assert [e["id"] for e in visible] == [amend.json()["id"]]
    all_entries = client.get(
        "/api/v1/user/personal/professional/work-history/entries?include_superseded=true", headers=worker_headers
    ).json()
    assert len(all_entries) == 2  # original preserved


# ----------------------------------------------------------------------------- health data
def test_health_records_are_private_and_sharing_is_scoped_expiring_and_audited(client):
    owner, owner_headers = make_user(client, "patient@example.org")
    friend, friend_headers = make_user(client, "friend@example.org")
    stranger, stranger_headers = make_user(client, "stranger@example.org")
    base = "/api/v1/user/personal/health"
    created = client.post(
        f"{base}/records",
        headers=owner_headers,
        json={"category": "laboratory", "title": "Fasting glucose", "metric": "glucose", "value_number": 5.1, "unit": "mmol/L"},
    )
    assert created.status_code == 201
    client.post(f"{base}/records", headers=owner_headers, json={"category": "sleep_activity", "title": "Sleep", "metric": "sleep_hours", "value_number": 7.5, "unit": "h"})
    assert client.get(f"{base}/records/{created.json()['id']}", headers=stranger_headers).status_code == 404
    assert client.get(f"{base}/records", headers=stranger_headers).json() == []
    trend = client.get(f"{base}/trends?metric=glucose", headers=owner_headers).json()
    assert trend["count"] == 1 and trend["latest"] == 5.1

    share = client.post(
        "/api/v1/user/personal/sharing",
        headers=owner_headers,
        json={"grantee_user_id": friend["user"]["id"], "categories": ["laboratory"], "expires_in_hours": 24},
    )
    assert share.status_code == 201, share.text
    shared = client.get(f"/api/v1/user/personal/sharing/received/{share.json()['id']}/records", headers=friend_headers)
    assert shared.status_code == 200 and [r["category"] for r in shared.json()] == ["laboratory"]  # sleep not shared
    assert client.get(f"/api/v1/user/personal/sharing/received/{share.json()['id']}/records", headers=stranger_headers).status_code == 404

    link = client.post(
        "/api/v1/user/personal/sharing",
        headers=owner_headers,
        json={"create_link": True, "categories": ["sleep_activity"], "expires_in_hours": 1},
    ).json()
    assert link["link_token"]
    via_link = client.get(f"/api/v1/user/personal/sharing/links/{link['link_token']}/records")
    assert via_link.status_code == 200 and via_link.json()[0]["title"] == "Sleep"
    assert client.get("/api/v1/user/personal/sharing/links/not-a-real-token/records").status_code == 404
    listed = client.get("/api/v1/user/personal/sharing", headers=owner_headers).json()
    assert all("link_token" not in item for item in listed)

    log = client.get(f"{base}/access-log", headers=owner_headers).json()
    assert {entry["action"] for entry in log} == {"health.shared_read", "health.link_read"}

    assert client.delete(f"/api/v1/user/personal/sharing/{share.json()['id']}", headers=owner_headers).status_code == 204
    assert client.get(f"/api/v1/user/personal/sharing/received/{share.json()['id']}/records", headers=friend_headers).status_code == 404

    # expiry is enforced
    with SessionLocal() as db:
        from app.models.platform import HealthShare

        row = db.get(HealthShare, UUID(link["id"]))
        row.expires_at = utc_now() - timedelta(minutes=1)
        db.commit()
    assert client.get(f"/api/v1/user/personal/sharing/links/{link['link_token']}/records").status_code == 404


def test_consent_defaults_to_not_granted(client):
    _, headers = make_user(client, "consent@example.org")
    consents = client.get("/api/v1/user/personal/consents", headers=headers).json()
    assert {c["purpose"] for c in consents} == {"research_use", "ai_training", "interest_personalization"}
    assert all(c["granted"] is False for c in consents)
    assert client.post("/api/v1/user/personal/consents/research_use", headers=headers, json={"granted": True}).json()["granted"] is True
    assert client.post("/api/v1/user/personal/consents/nonsense", headers=headers, json={"granted": True}).status_code == 404


# ----------------------------------------------------------------------------- messaging, events, notifications
def test_direct_messaging_privacy_and_notifications(client):
    a, a_headers = make_user(client, "msg-a@example.org")
    b, b_headers = make_user(client, "msg-b@example.org")
    c, c_headers = make_user(client, "msg-c@example.org")
    sent = client.post("/api/v1/user/personal/messages", headers=a_headers, json={"recipient_id": b["user"]["id"], "body": "Hello"})
    assert sent.status_code == 201
    conversation_id = sent.json()["conversation_id"]
    again = client.post("/api/v1/user/social/messages", headers=b_headers, json={"recipient_id": a["user"]["id"], "body": "Hi back"})
    assert again.json()["conversation_id"] == conversation_id  # one direct thread per pair
    assert client.get(f"/api/v1/user/personal/messages/conversations/{conversation_id}/messages", headers=c_headers).status_code == 404
    assert client.post("/api/v1/user/personal/messages", headers=c_headers, json={"conversation_id": conversation_id, "body": "intrude"}).status_code == 404
    assert client.post("/api/v1/user/personal/messages", headers=a_headers, json={"recipient_id": a["user"]["id"], "body": "me"}).status_code == 400
    listing = client.get("/api/v1/user/personal/messages/conversations", headers=b_headers).json()
    assert listing[0]["unread_count"] == 1
    client.get(f"/api/v1/user/personal/messages/conversations/{conversation_id}/messages", headers=b_headers)
    assert client.get("/api/v1/user/personal/messages/conversations", headers=b_headers).json()[0]["unread_count"] == 0
    assert client.get("/api/v1/user/social/notifications/unread-count", headers=b_headers).json()["unread"] >= 1


def test_events_require_entitlement_and_enforce_visibility_and_capacity(client):
    _, admin_headers = make_user(client, "admin5@example.org", "admin")
    organizer, organizer_headers = make_user(client, "organizer@example.org")
    member, member_headers = make_user(client, "attendee@example.org")
    late, late_headers = make_user(client, "late@example.org")
    payload = {"title": "Longevity meetup", "starts_at": (utc_now() + timedelta(days=3)).isoformat(), "capacity": 1}
    assert client.post("/api/v1/user/social/events", headers=organizer_headers, json=payload).status_code == 403
    grant(client, admin_headers, "event.create", user_id=organizer["user"]["id"])
    event = client.post("/api/v1/user/social/events", headers=organizer_headers, json=payload)
    assert event.status_code == 201, event.text
    assert event.json()["discussion_post_id"]
    event_id = event.json()["id"]
    assert client.post(f"/api/v1/user/social/events/{event_id}/register", headers=member_headers).json()["is_registered"] is True
    assert client.post(f"/api/v1/user/social/events/{event_id}/register", headers=late_headers).status_code == 409  # full
    private = client.post(
        "/api/v1/user/social/events",
        headers=organizer_headers,
        json={**payload, "title": "Invite only", "visibility": "invited", "capacity": None},
    ).json()
    assert client.get(f"/api/v1/user/social/events/{private['id']}", headers=member_headers).status_code == 404
    assert client.post(f"/api/v1/user/social/events/{private['id']}/invitations", headers=organizer_headers, json={"user_id": member["user"]["id"]}).status_code == 204
    assert client.get(f"/api/v1/user/social/events/{private['id']}", headers=member_headers).status_code == 200
    listing = client.get("/api/v1/user/social/events", headers=late_headers).json()
    assert [e["title"] for e in listing] == ["Longevity meetup"]


# ----------------------------------------------------------------------------- AI
def test_general_ai_cites_public_sources_and_never_reads_private_data(client):
    _, headers = make_user(client, "general-ai@example.org")
    owner, owner_headers = make_user(client, "owner-ai@example.org")
    public = client.post(
        "/api/v1/user/researcher/projects",
        headers=owner_headers,
        json={"title": "Public metformin review", "description": "Open review", "visibility": "public"},
    ).json()
    private = client.post(
        "/api/v1/user/researcher/projects",
        headers=owner_headers,
        json={"title": "Private plan", "description": "Secret", "visibility": "private"},
    ).json()
    for project, title in ((public, "Metformin aging trial summary"), (private, "Metformin secret unpublished data")):
        added = client.post(
            f"/api/v1/user/researcher/projects/{project['id']}/literature",
            headers=owner_headers,
            json={"title": title, "authors": "Example et al.", "source_type": "paper"},
        )
        assert added.status_code == 201, added.text
    client.post(
        "/api/v1/user/personal/health/records",
        headers=owner_headers,
        json={"category": "laboratory", "title": "Metformin personal dose log", "value_text": "metformin 500mg private"},
    )
    answer = client.post("/api/v1/user/ai/general/chat", headers=headers, json={"prompt": "What is known about metformin aging?"})
    assert answer.status_code == 200, answer.text
    body = answer.json()
    titles = " ".join(source["title"] for source in body["sources"])
    assert "Metformin aging trial summary" in titles
    assert "secret" not in titles.lower() and "personal dose" not in titles.lower()
    assert body["ai_generated"] is True and body["disclaimer"] and body["uncertainty"]
    nothing = client.post("/api/v1/user/ai/general/chat", headers=headers, json={"prompt": "zzzqqq unrelated xylophone"}).json()
    assert nothing["status"] == "insufficient_evidence" and nothing["sources"] == []


def test_ai_scientist_requires_approval_and_respects_project_permissions(client):
    _, admin_headers = make_user(client, "admin6@example.org", "admin")
    owner, owner_headers = approved_researcher(client, admin_headers, "scientist-owner@example.org")
    other, other_headers = approved_researcher(client, admin_headers, "scientist-other@example.org")
    plain, plain_headers = make_user(client, "plain@example.org")
    project = client.post(
        "/api/v1/user/researcher/projects",
        headers=owner_headers,
        json={"title": "Senolytics", "description": "Private senolytics work", "visibility": "private"},
    ).json()
    client.post(
        f"/api/v1/user/researcher/projects/{project['id']}/literature",
        headers=owner_headers,
        json={"title": "Senolytic dasatinib quercetin outcomes", "authors": "A. Author", "source_type": "paper"},
    )
    client.post(
        f"/api/v1/user/researcher/projects/{project['id']}/hypotheses",
        headers=owner_headers,
        json={"title": "Senolytic timing hypothesis", "description": "Intermittent dosing may reduce senescent burden."},
    )
    url = "/api/v1/user/researcher/ai-scientist/chat"
    assert client.post(url, headers=plain_headers, json={"prompt": "senolytic dasatinib"}).status_code == 403
    mine = client.post(url, headers=owner_headers, json={"prompt": "senolytic dasatinib outcomes"}).json()
    assert mine["status"] == "answered" and mine["system"] == "scientist"
    classes = {source["evidence_class"] for source in mine["sources"]}
    assert "paper" in classes
    theirs = client.post(url, headers=other_headers, json={"prompt": "senolytic dasatinib outcomes"}).json()
    assert theirs["sources"] == []  # no read access to the private project
    legacy = client.post("/api/v1/ai/research", headers=owner_headers, json={"prompt": "senolytic dasatinib"})
    assert legacy.status_code == 200


def test_organization_ai_is_paid_and_strictly_org_scoped(client):
    _, admin_headers = make_user(client, "admin7@example.org", "admin")
    founder_a, a_headers = approved_researcher(client, admin_headers, "org-a@example.org")
    founder_b, b_headers = approved_researcher(client, admin_headers, "org-b@example.org")
    org_a = create_org(client, admin_headers, a_headers, founder_a, "Alpha Labs")
    org_b = create_org(client, admin_headers, b_headers, founder_b, "Beta Labs")
    ai_url = f"/api/v1/user/researcher/organization-ai/{org_a['id']}"
    assert client.post(ai_url, headers=a_headers, json={"name": "Alpha Assistant"}).status_code == 403  # no entitlement
    grant(client, admin_headers, "organization.ai", organization_id=org_a["id"])
    assert client.post(ai_url, headers=a_headers, json={"name": "Alpha Assistant"}).status_code == 201
    grant(client, admin_headers, "organization.ai", organization_id=org_b["id"])
    client.post(f"/api/v1/user/researcher/organization-ai/{org_b['id']}", headers=b_headers, json={"name": "Beta Assistant"})
    client.post(
        f"{ai_url}/documents",
        headers=a_headers,
        json={"title": "Alpha protocol", "content": "Alpha internal protocol: centrifuge samples at 4000 rpm for ten minutes."},
    )
    client.post(
        f"/api/v1/user/researcher/organization-ai/{org_b['id']}/documents",
        headers=b_headers,
        json={"title": "Beta protocol", "content": "Beta internal protocol: centrifuge samples at 9000 rpm confidential."},
    )
    answer = client.post(f"{ai_url}/chat", headers=a_headers, json={"prompt": "centrifuge protocol samples"}).json()
    assert [s["title"] for s in answer["sources"]] == ["Alpha protocol"]
    assert answer["provider"] == "extractive" and answer["system"] == "organization"
    # member of B cannot query A, nor see A's documents
    assert client.post(f"{ai_url}/chat", headers=b_headers, json={"prompt": "centrifuge"}).status_code == 404
    assert client.get(f"{ai_url}/documents", headers=b_headers).status_code == 404


def test_ai_runs_are_monitored_without_prompt_storage(client):
    _, admin_headers = make_user(client, "admin8@example.org", "admin")
    _, headers = make_user(client, "monitored@example.org")
    answered = client.post("/api/v1/user/ai/general/chat", headers=headers, json={"prompt": "secretprompttext qwertyuiop"}).json()
    assert client.post(
        f"/api/v1/user/ai/general/runs/{answered['run_id']}/feedback", headers=headers, json={"rating": "down", "comment": "not helpful"}
    ).status_code == 204
    assert client.post(
        f"/api/v1/user/ai/general/runs/{answered['run_id']}/feedback", headers=headers, json={"rating": "up", "permitted_use": "training"}
    ).status_code == 403  # training needs explicit consent
    stats = client.get("/api/v1/admin/ai-monitoring", headers=admin_headers).json()
    assert stats["total_runs"] == 1 and stats["feedback"]["down"] == 1 and stats["external_provider_runs"] == 0
    audit = client.get("/api/v1/admin/audit?action=ai.run", headers=admin_headers).json()
    assert audit and "secretprompttext" not in str(audit)
    assert client.get("/api/v1/admin/ai-monitoring", headers=headers).status_code == 403


def test_health_data_is_not_reachable_from_any_ai_retriever():
    """Static guard: AI and retrieval code must never import health models or services."""
    root = Path(__file__).resolve().parents[1] / "apps" / "api" / "app"
    forbidden = ("HealthRecord", "HealthShare", "domains.health")
    offenders = [
        str(path.relative_to(root))
        for folder in ("ai", "services")
        for path in (root / folder).glob("*.py")
        if any(token in path.read_text(encoding="utf-8") for token in forbidden)
    ]
    assert offenders == []


# ----------------------------------------------------------------------------- admin
def test_admin_organization_verification_and_researcher_review_are_audited(client):
    _, admin_headers = make_user(client, "admin9@example.org", "admin")
    founder, founder_headers = approved_researcher(client, admin_headers, "founder9@example.org")
    organization = create_org(client, admin_headers, founder_headers, founder, "Verified Org")
    _, member_headers = make_user(client, "member9@example.org")
    assert client.patch(f"/api/v1/admin/organizations/{organization['id']}/verification", headers=member_headers, json={"verification_status": "verified", "reason": "x y z"}).status_code == 403
    done = client.patch(
        f"/api/v1/admin/organizations/{organization['id']}/verification",
        headers=admin_headers,
        json={"verification_status": "verified", "reason": "Documents checked"},
    )
    assert done.status_code == 200 and done.json()["verification_status"] == "verified"
    audit = client.get("/api/v1/admin/audit?action=admin.organization", headers=admin_headers).json()
    assert audit[0]["details"]["reason"] == "Documents checked"
    pending = client.get("/api/v1/admin/research-memberships", headers=admin_headers).json()
    assert pending == []
    overview = client.get("/api/v1/admin/overview", headers=admin_headers).json()
    assert overview["organizations"] == 1
    config = client.get("/api/v1/admin/configuration", headers=admin_headers).json()
    assert "api_key" not in str(config).lower() or config["ai"]["external_provider_ready"] is False
