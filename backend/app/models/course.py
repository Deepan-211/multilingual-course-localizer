"""Course domain models."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class ContentType(str, Enum):
    """Supported course content types."""

    PDF = "pdf"
    VIDEO = "video"


class Course(BaseModel):
    """Course record stored in Supabase."""

    id: UUID
    user_id: UUID
    title: str
    source_language: str
    content_type: ContentType
    file_url: str | None = None
    file_name: str | None = None
    file_size: int | None = None
    created_at: datetime
