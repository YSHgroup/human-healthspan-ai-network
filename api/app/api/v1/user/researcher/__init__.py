"""Researcher Portal routes (planned, M3): research, evidence, literature, projects, tasks, reports, organizations, workspace, organization-ai."""

from fastapi import APIRouter

router = APIRouter(prefix="/researcher", tags=["user-researcher"])
