class AuthorizationService:
    """Central policy boundary for user/team/project/document access."""

    def can_read(self, principal_id: str, resource: dict) -> bool:
        return False

    def can_write(self, principal_id: str, resource: dict) -> bool:
        return False
