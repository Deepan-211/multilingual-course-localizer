"""User settings routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.middleware.auth_middleware import get_current_user
from app.schemas.user import (
    LanguageSettingsUpdate,
    NotificationSettingsUpdate,
    UserResponse,
    UserSettingsResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("", response_model=UserSettingsResponse, summary="Get user settings")
async def get_settings(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> UserSettingsResponse:
    """Return the current user's preferences."""
    return await AuthService().get_settings(current_user.id)


@router.put("/language", response_model=UserSettingsResponse, summary="Update language settings")
async def update_language_settings(
    payload: LanguageSettingsUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> UserSettingsResponse:
    """Update default source and target languages."""
    return await AuthService().update_language_settings(current_user.id, payload)


@router.put(
    "/notifications",
    response_model=UserSettingsResponse,
    summary="Update notification settings",
)
async def update_notification_settings(
    payload: NotificationSettingsUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> UserSettingsResponse:
    """Update email notification preferences."""
    return await AuthService().update_notification_settings(current_user.id, payload)
