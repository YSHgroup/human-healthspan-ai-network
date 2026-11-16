"""AI environment permission checks for the M4 launch slice."""

from __future__ import annotations


class AccessDeniedError(PermissionError):
    """Raised when a caller is not allowed to use a restricted AI environment."""


def ensure_environment_allowed(
    environment: str,
    *,
    scientist_enabled: bool = False,
    email_verified: bool = False,
    researcher_approved: bool = False,
) -> str:
    """Validate environment access before the request reaches the model gateway.

    The public General Platform AI is open to all authenticated members; the Private AI
    Scientist route is a narrower, permission-gated environment and must not be reached by
    unverified or unapproved researchers.
    """
    env_name = (environment or "").strip().lower()
    if env_name not in {"general", "scientist"}:
        raise ValueError(f"Unsupported AI environment: {environment}")

    if env_name == "general":
        return env_name

    if not scientist_enabled:
        raise AccessDeniedError("The Private AI Scientist prototype is disabled")
    if not email_verified:
        raise AccessDeniedError("Verified email required for Private AI Scientist access")
    if not researcher_approved:
        raise AccessDeniedError("Approved researcher access required")
    return env_name


__all__ = ["AccessDeniedError", "ensure_environment_allowed"]
