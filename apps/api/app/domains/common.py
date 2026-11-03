from datetime import datetime, timezone

from app.db.base import utc_now


def as_utc(value: datetime | None) -> datetime | None:
    """SQLite returns naive datetimes; treat them as UTC so comparisons are consistent."""
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def is_past(value: datetime | None) -> bool:
    moment = as_utc(value)
    return moment is not None and moment <= utc_now()
