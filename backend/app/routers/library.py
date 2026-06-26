"""Localization library routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from app.middleware.auth_middleware import get_current_user
from app.schemas.localization import LibrarySearchResponse
from app.schemas.user import UserResponse
from app.services.localization_service import LocalizationService

router = APIRouter(prefix="/library", tags=["Library"])


@router.get("", response_model=LibrarySearchResponse, summary="List completed localizations")
async def get_library(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> LibrarySearchResponse:
    """Return all completed localizations with course info."""
    return await LocalizationService().get_library(current_user.id)


@router.get("/search", response_model=LibrarySearchResponse, summary="Search library")
async def search_library(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    q: str | None = Query(None, description="Search query for course title"),
    language: str | None = Query(None, description="Filter by target language"),
    status: str | None = Query(None, description="Filter by status"),
) -> LibrarySearchResponse:
    """Search localizations by query, language, and status."""
    return await LocalizationService().search_library(
        current_user.id, query=q, language=language, status_filter=status
    )


@router.get(
    "/{localization_id}/download",
    summary="Download localized content",
)
async def download_localization(
    localization_id: UUID,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> Response:
    """Download localized content as a text file."""
    content, filename, media_type = await LocalizationService().download_localization(
        current_user.id, localization_id
    )
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
