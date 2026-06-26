"""Localization domain models."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class LocalizationStatus(str, Enum):
    """Localization job lifecycle states."""

    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    APPROVED = "approved"


class ConfidenceScore(str, Enum):
    """AI translation confidence levels."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Localization(BaseModel):
    """Localization job record."""

    id: UUID
    course_id: UUID
    target_language: str
    ai_model: str
    status: LocalizationStatus
    progress_percentage: int = 0
    created_at: datetime
    completed_at: datetime | None = None


class ContentBlock(BaseModel):
    """Extracted source content block."""

    id: UUID
    course_id: UUID
    block_number: int
    original_text: str
    created_at: datetime


class TranslatedBlock(BaseModel):
    """Translated content block for a localization job."""

    id: UUID
    block_id: UUID
    localization_id: UUID
    translated_text: str
    confidence_score: ConfidenceScore
    is_approved: bool = False
    created_at: datetime
