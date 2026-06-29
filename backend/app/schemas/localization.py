"""Localization request/response schemas."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class LocalizationStartRequest(BaseModel):
    """Start localization job."""

    course_id: UUID
    target_languages: list[str] = Field(..., min_length=1)
    ai_model: str = "claude-sonnet-4-6"


class LocalizationStartResponse(BaseModel):
    """Response after starting localization."""

    localization_ids: list[UUID]
    message: str = "Localization started"


class LocalizationStatusResponse(BaseModel):
    """Localization job status."""

    localization_id: UUID
    status: str
    progress_percentage: int
    estimated_time_seconds: int | None = None
    target_language: str


class ContentBlockResponse(BaseModel):
    """Source content block."""

    id: UUID
    block_number: int
    original_text: str


class TranslatedBlockResponse(BaseModel):
    """Translated content block."""

    id: UUID
    block_id: UUID
    translated_text: str
    confidence_score: str
    is_approved: bool


class WorkspaceBlockPair(BaseModel):
    """Side-by-side source and translation."""

    block_number: int
    source: ContentBlockResponse
    translation: TranslatedBlockResponse | None = None


class WorkspaceResponse(BaseModel):
    """Workspace view for a course."""

    course_id: UUID
    course_title: str
    source_language: str
    localization_id: UUID | None = None
    blocks: list[WorkspaceBlockPair]


class BlockUpdateRequest(BaseModel):
    """Manual translation edit."""

    translated_text: str = Field(..., min_length=1)


class ExportFormat(str, Enum):
    """Export file formats."""

    PDF = "pdf"
    TEXT = "text"


class ExportRequest(BaseModel):
    """Export localized content."""

    format: ExportFormat = ExportFormat.PDF


class LibraryItemResponse(BaseModel):
    """Completed localization library entry."""

    localization_id: UUID
    course_id: UUID
    course_title: str
    target_language: str
    status: str
    completed_at: datetime | None
    created_at: datetime


class LibrarySearchResponse(BaseModel):
    """Library search results."""

    items: list[LibraryItemResponse]
    total: int


class ProgressItemResponse(BaseModel):
    """Active localization progress."""

    localization_id: UUID
    course_id: UUID
    course_title: str
    target_language: str
    status: str
    progress_percentage: int
    created_at: datetime


class AIStatusResponse(BaseModel):
    """Claude API health and load."""

    status: str
    avg_response_time_ms: float
    current_load: int
    model: str = "claude-sonnet-4-6"


class DashboardStatsResponse(BaseModel):
    """Dashboard summary statistics."""

    total_courses: int
    languages_processed: int
    localizations_completed: int
    processing_in_queue: int


class ActivityDayResponse(BaseModel):
    """Daily localization activity."""

    date: str
    count: int


class DashboardActivityResponse(BaseModel):
    """Last 7 days activity chart data."""

    activity: list[ActivityDayResponse]
