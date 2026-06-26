"""Localization job routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.middleware.auth_middleware import get_current_user
from app.schemas.localization import (
    LocalizationStartRequest,
    LocalizationStartResponse,
    LocalizationStatusResponse,
)
from app.schemas.user import UserResponse
from app.services.localization_service import LocalizationService

router = APIRouter(prefix="/localize", tags=["Localization"])


@router.post("/start", response_model=LocalizationStartResponse, summary="Start localization")
async def start_localization(
    payload: LocalizationStartRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> LocalizationStartResponse:
    """Extract content, translate via Claude, and save results."""
    return await LocalizationService().start_localization(current_user.id, payload)


@router.get(
    "/{localization_id}/status",
    response_model=LocalizationStatusResponse,
    summary="Get localization status",
)
async def get_localization_status(
    localization_id: UUID,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> LocalizationStatusResponse:
    """Return processing status, progress percentage, and estimated time."""
    return await LocalizationService().get_status(current_user.id, localization_id)
