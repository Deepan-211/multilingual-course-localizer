"""Course request/response schemas."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class ContentTypeEnum(str, Enum):
    """Supported upload content types."""

    PDF = "pdf"
    VIDEO = "video"


class CourseCreateResponse(BaseModel):
    """Response after course upload."""

    course_id: UUID
    message: str = "Course uploaded successfully"


class CourseResponse(BaseModel):
    """Course details."""

    id: UUID
    title: str
    source_language: str
    content_type: str
    file_url: str | None = None
    file_name: str | None = None
    file_size: int | None = None
    created_at: datetime
    localization_status: str | None = None


class CourseListResponse(BaseModel):
    """List of courses."""

    courses: list[CourseResponse]
    total: int


class RecentCourseResponse(BaseModel):
    """Recent course summary for dashboard."""

    id: UUID
    title: str
    source_language: str
    content_type: str
    status: str
    created_at: datetime
