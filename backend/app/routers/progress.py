"""Localization progress and AI status routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.middleware.auth_middleware import get_current_user
from app.schemas.localization import AIStatusResponse, ProgressItemResponse
from app.schemas.user import UserResponse
from app.services.localization_service import LocalizationService

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.get("", response_model=list[ProgressItemResponse], summary="Active localizations")
async def get_progress(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> list[ProgressItemResponse]:
    """Return all active and queued localizations with progress percentage."""
    return await LocalizationService().get_progress(current_user.id)


@router.get("/ai-status", response_model=AIStatusResponse, summary="Claude API status")
async def get_ai_status(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> AIStatusResponse:
    """Return Claude API status, average response time, and current load."""
    return await LocalizationService().get_ai_status()
