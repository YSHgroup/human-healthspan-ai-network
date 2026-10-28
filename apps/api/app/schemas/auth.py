from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    display_name: str = Field(min_length=1, max_length=120)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=120)
    bio: str | None = Field(default=None, max_length=1000)
    timezone: str | None = Field(default=None, max_length=100)
    interests: list[str] | None = Field(default=None, max_length=30)
    expertise: list[str] | None = Field(default=None, max_length=30)
    is_public: bool | None = None

    @field_validator("display_name", "bio", "timezone")
    @classmethod
    def optional_strings_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("This value cannot be blank.")
        return value.strip() if value is not None else None


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    display_name: str
    bio: str | None
    timezone: str | None
    interests: list[str]
    expertise: list[str]
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


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class VerificationRequest(BaseModel):
    token: str = Field(min_length=20, max_length=200)


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str = Field(min_length=20, max_length=200)
    new_password: str = Field(min_length=12, max_length=128)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RegistrationOut(BaseModel):
    user: UserOut
    tokens: TokenPair | None = None
    verification_required: bool = True
    verification_token: str | None = None
