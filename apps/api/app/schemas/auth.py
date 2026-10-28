from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


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


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RegistrationOut(BaseModel):
    user: UserOut
    tokens: TokenPair
    verification_required: bool = True
