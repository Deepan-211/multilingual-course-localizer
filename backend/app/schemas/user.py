"""User request/response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Registration payload."""

    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserLogin(BaseModel):
    """Login payload."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Public user profile."""

    id: UUID
    name: str
    email: EmailStr
    avatar_url: str | None = None
    created_at: datetime


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"


class ProfileUpdate(BaseModel):
    """Profile update payload."""

    name: str | None = Field(None, min_length=1, max_length=100)
    avatar_url: str | None = None


class ChangePasswordRequest(BaseModel):
    """Change password payload."""

    old_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class UserSettingsResponse(BaseModel):
    """User preferences."""

    default_source_language: str = "English"
    default_target_languages: list[str] = Field(default_factory=lambda: ["Tamil", "Hindi"])
    email_notifications: bool = True
    localization_complete: bool = True
    weekly_digest: bool = False


class LanguageSettingsUpdate(BaseModel):
    """Language preference update."""

    default_source_language: str
    default_target_languages: list[str] = Field(..., min_length=1)


class NotificationSettingsUpdate(BaseModel):
    """Notification preference update."""

    email_notifications: bool = True
    localization_complete: bool = True
    weekly_digest: bool = False
