from datetime import timedelta
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.base import utc_now
from app.db.session import get_db
from app.domains.common import as_utc
from app.domains.notifications.service import notify
from app.domains.research.access import (
    has_research_access,
    project_or_404,
    require_project_read,
    require_project_write,
)
from app.models.domain import Evidence, ResearchMember, ResearchProject, User
from app.models.platform import (
    OrganizationMember,
    ProjectOrganization,
    ResearchMembership,
    ResearchTask,
    WorkHistoryEntry,
)
from app.schemas.platform import (
    ResearchMembershipApply,
    ResearchMembershipOut,
    TaskCreate,
    TaskOut,
    TaskUpdate,
)
from app.services.audit import record_audit_event
from app.services.authorization import AuthorizationService

router = APIRouter(tags=["researcher"])


@router.get("/membership")
def my_research_membership(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    record = db.scalar(select(ResearchMembership).where(ResearchMembership.user_id == user.id))
    return {
        "has_research_access": has_research_access(db, user),
        "status": record.status if record else ("staff" if has_research_access(db, user) else "none"),
        "application": ResearchMembershipOut.model_validate(record) if record else None,
    }


@router.post("/membership/apply", response_model=ResearchMembershipOut, status_code=status.HTTP_201_CREATED)
def apply_for_research_membership(
    payload: ResearchMembershipApply,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResearchMembership:
    record = db.scalar(select(ResearchMembership).where(ResearchMembership.user_id == user.id))
    if record is not None and record.status in {"pending", "approved"}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Your application is already {record.status}.")
    if record is not None and record.status == "revoked":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Researcher access was revoked; contact an administrator.")
    if record is None:
        record = ResearchMembership(user_id=user.id, status="pending", statement=payload.statement)
        db.add(record)
    else:  # previously rejected: allow a fresh application
        record.status, record.statement = "pending", payload.statement
        record.reviewed_by = record.reviewed_at = record.review_note = None
    db.flush()
    record_audit_event(db, user.id, "research_membership.applied", "research_membership", record.id)
    db.commit()
    db.refresh(record)
    return record


def _task_project(db: Session, task_id: UUID) -> tuple[ResearchTask, ResearchProject]:
    task = db.get(ResearchTask, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    return task, project_or_404(db, task.project_id)


def _valid_assignee(db: Session, project: ResearchProject, assignee_id: UUID) -> None:
    if assignee_id == project.owner_id:
        return
    is_member = db.scalar(
        select(ResearchMember.id).where(ResearchMember.project_id == project.id, ResearchMember.user_id == assignee_id)
    )
    if is_member is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Assignees must be project members.")


@router.post("/projects/{project_id}/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    project_id: UUID,
    payload: TaskCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResearchTask:
    project = project_or_404(db, project_id)
    require_project_write(db, user, project)
    if payload.assignee_id is not None:
        _valid_assignee(db, project, payload.assignee_id)
    task = ResearchTask(project_id=project_id, created_by=user.id, **payload.model_dump())
    db.add(task)
    db.flush()
    if task.assignee_id:
        notify(db, task.assignee_id, "task.assigned", "A research task was assigned to you", task.title, "research_task", task.id, user.id)
    record_audit_event(db, user.id, "research_task.created", "research_task", task.id)
    db.commit()
    db.refresh(task)
    return task


@router.get("/projects/{project_id}/tasks", response_model=list[TaskOut])
def list_tasks(
    project_id: UUID,
    status_filter: Annotated[Literal["todo", "in_progress", "done"] | None, Query(alias="status")] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ResearchTask]:
    project = project_or_404(db, project_id)
    require_project_read(db, user, project)
    query = select(ResearchTask).where(ResearchTask.project_id == project_id)
    if status_filter:
        query = query.where(ResearchTask.status == status_filter)
    return list(db.scalars(query.order_by(ResearchTask.created_at.desc())))


@router.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(
    task_id: UUID,
    payload: TaskUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResearchTask:
    task, project = _task_project(db, task_id)
    require_project_read(db, user, project)
    require_project_write(db, user, project)
    changes = payload.model_dump(exclude_unset=True)
    if changes.get("assignee_id") is not None:
        _valid_assignee(db, project, changes["assignee_id"])
    previous_status = task.status
    for field, value in changes.items():
        if field == "status" and value is None:
            continue
        setattr(task, field, value)
    if task.status == "done" and previous_status != "done":
        task.completed_at = utc_now()
        contributor = task.assignee_id or user.id
        organization_id = db.scalar(
            select(ProjectOrganization.organization_id).where(ProjectOrganization.project_id == project.id)
        )
        # Contribution is recorded only for real organization members when the project is organizational.
        if organization_id is not None and db.scalar(
            select(OrganizationMember.id).where(
                OrganizationMember.organization_id == organization_id, OrganizationMember.user_id == contributor
            )
        ) is None:
            organization_id = None
        db.add(
            WorkHistoryEntry(
                user_id=contributor,
                organization_id=organization_id,
                project_id=project.id,
                task_id=task.id,
                kind="task_completed",
                summary=f"Completed task: {task.title}"[:1000],
                created_at=utc_now(),
            )
        )
    elif task.status != "done":
        task.completed_at = None
    record_audit_event(db, user.id, "research_task.updated", "research_task", task.id, {"status": task.status})
    db.commit()
    db.refresh(task)
    return task


@router.get("/projects/{project_id}/progress")
def project_progress(
    project_id: UUID,
    period: Literal["day", "week", "month"] = "week",
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    project = project_or_404(db, project_id)
    require_project_read(db, user, project)
    days = {"day": 1, "week": 7, "month": 30}[period]
    since = utc_now() - timedelta(days=days)
    tasks = list(db.scalars(select(ResearchTask).where(ResearchTask.project_id == project_id)))
    by_status = {"todo": 0, "in_progress": 0, "done": 0}
    completed_in_period = 0
    for task in tasks:
        by_status[task.status] = by_status.get(task.status, 0) + 1
        completed = as_utc(task.completed_at)
        if completed is not None and completed >= since:
            completed_in_period += 1
    total = len(tasks)
    return {
        "project_id": str(project_id),
        "period": period,
        "total_tasks": total,
        "by_status": by_status,
        "completed_in_period": completed_in_period,
        "completion_rate": round(by_status["done"] / total, 4) if total else 0.0,
    }


@router.get("/workspace/summary")
def workspace_summary(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    readable = AuthorizationService(db).readable_project_ids(user)
    my_projects = db.scalar(select(func.count()).select_from(ResearchProject).where(
        ResearchProject.owner_id == user.id)) or 0
    accessible = db.scalar(select(func.count()).select_from(readable.subquery())) or 0
    assigned = dict(
        db.execute(
            select(ResearchTask.status, func.count())
            .where(ResearchTask.assignee_id == user.id)
            .group_by(ResearchTask.status)
        ).all()
    )
    recent_evidence = db.scalars(
        select(Evidence).where(Evidence.project_id.in_(readable)).order_by(Evidence.created_at.desc()).limit(5)
    )
    return {
        "has_research_access": has_research_access(db, user),
        "owned_projects": my_projects,
        "accessible_projects": accessible,
        "assigned_tasks": {"todo": assigned.get("todo", 0), "in_progress": assigned.get("in_progress", 0), "done": assigned.get("done", 0)},
        "recent_evidence": [
            {"id": str(item.id), "project_id": str(item.project_id), "label": item.label, "summary": item.summary[:200], "review_status": item.review_status}
            for item in recent_evidence
        ],
    }
