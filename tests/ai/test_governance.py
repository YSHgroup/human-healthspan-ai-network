import pytest

from healthspan_ai.governance.permissions import AccessDeniedError, ensure_environment_allowed


def test_general_environment_is_available_without_researcher_permissions() -> None:
    assert ensure_environment_allowed(" GENERAL ") == "general"


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({}, "disabled"),
        ({"scientist_enabled": True}, "Verified email"),
        (
            {"scientist_enabled": True, "email_verified": True},
            "Approved researcher",
        ),
    ],
)
def test_scientist_environment_requires_each_permission(
    kwargs: dict[str, bool],
    message: str,
) -> None:
    with pytest.raises(AccessDeniedError, match=message):
        ensure_environment_allowed("scientist", **kwargs)


def test_scientist_environment_allows_verified_approved_researchers() -> None:
    assert (
        ensure_environment_allowed(
            "scientist",
            scientist_enabled=True,
            email_verified=True,
            researcher_approved=True,
        )
        == "scientist"
    )


def test_unknown_ai_environment_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported AI environment"):
        ensure_environment_allowed("organization")
