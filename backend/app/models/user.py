"""User domain models."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    """User record stored in Supabase."""

    id: UUID
    name: str
    email: EmailStr
    password_hash: str
    avatar_url: str | None = None
    created_at: datetime
