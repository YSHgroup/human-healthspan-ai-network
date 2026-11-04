"""Personal Portal routes (planned, M2/M5): profile, professional, health, records, sharing, activity, messages, devices."""

from fastapi import APIRouter

router = APIRouter(prefix="/personal", tags=["user-personal"])
