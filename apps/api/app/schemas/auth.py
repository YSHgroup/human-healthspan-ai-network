from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class IdentityInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RegisterRequest(IdentityInput):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    display_name: str = Field(min_length=1, max_length=120)

    @field_validator("display_name")
    @classmethod
    def display_name_must_not_be_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Display name cannot be blank.")
        return normalized


class LoginRequest(IdentityInput):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserProfileUpdate(IdentityInput):
    display_name: str | None = Field(default=None, min_length=1, max_length=120)
    bio: str | None = Field(default=None, max_length=1000)
    location: str | None = Field(default=None, max_length=160)
    timezone: str | None = Field(default=None, max_length=100)
    interests: list[str] | None = Field(default=None, max_length=30)
    topics: list[str] | None = Field(default=None, max_length=30)
    expertise: list[str] | None = Field(default=None, max_length=30)
    researcher_identifier: str | None = Field(default=None, max_length=100)
    organization_affiliation: str | None = Field(default=None, max_length=200)
    is_public: bool | None = None

    @field_validator("display_name", "bio", "location", "timezone", "researcher_identifier", "organization_affiliation")
    @classmethod
    def optional_strings_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("This value cannot be blank.")
        return value.strip() if value is not None else None

    @field_validator("interests", "topics", "expertise")
    @classmethod
    def normalize_profile_lists(cls, values: list[str] | None) -> list[str] | None:
        if values is None:
            return None
        normalized: list[str] = []
        seen: set[str] = set()
        for value in values:
            item = value.strip()
            if not item:
                raise ValueError("Profile list items cannot be blank.")
            if len(item) > 80:
                raise ValueError("Profile list items must be 80 characters or fewer.")
            key = item.casefold()
            if key not in seen:
                normalized.append(item)
                seen.add(key)
        return normalized


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    display_name: str
    bio: str | None
    location: str | None
    timezone: str | None
    interests: list[str]
    topics: list[str]
    expertise: list[str]
    researcher_identifier: str | None
    organization_affiliation: str | None
    is_public: bool


class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    role: str
    is_verified: bool
    profile: ProfileOut | None = None


class PublicUserOut(BaseModel):
    id: UUID
    role: str
    profile: ProfileOut


class AdminUserOut(UserOut):
    is_active: bool
    created_at: datetime


class RefreshRequest(IdentityInput):
    refresh_token: str = Field(min_length=1)


class VerificationRequest(IdentityInput):
    token: str = Field(min_length=20, max_length=200)


class PasswordResetRequest(IdentityInput):
    email: EmailStr


class PasswordResetConfirm(IdentityInput):
    token: str = Field(min_length=20, max_length=200)
    new_password: str = Field(min_length=12, max_length=128)


class PasswordChangeRequest(IdentityInput):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=12, max_length=128)

    @model_validator(mode="after")
    def new_password_must_differ(self) -> "PasswordChangeRequest":
        if self.current_password == self.new_password:
            raise ValueError("New password must differ from the current password.")
        return self


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_expires_in: int


class RegistrationOut(BaseModel):
    user: UserOut
    tokens: TokenPair | None = None
    verification_required: bool = True
    verification_token: str | None = None
