from datetime import date

from pydantic import BaseModel


class DailyActivityOut(BaseModel):
    day: date
    post_count: int


class DashboardSummaryOut(BaseModel):
    active_members: int
    active_communities: int
    your_communities: int
    accessible_projects: int
    posts_last_7_days: int
    activity: list[DailyActivityOut]
