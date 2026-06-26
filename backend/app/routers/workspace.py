"""Workspace editing and export routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.middleware.auth_middleware import get_current_user
from app.schemas.localization import (
    BlockUpdateRequest,
    ExportRequest,
    TranslatedBlockResponse,
    WorkspaceResponse,
)
from app.schemas.user import UserResponse
from app.services.localization_service import LocalizationService

router = APIRouter(prefix="/workspace", tags=["Workspace"])


@router.get("/{course_id}", response_model=WorkspaceResponse, summary="Get workspace view")
async def get_workspace(
    course_id: UUID,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> WorkspaceResponse:
    """Return source and translated content blocks side by side."""
    return await LocalizationService().get_workspace(current_user.id, course_id)


@router.put(
    "/block/{block_id}",
    response_model=TranslatedBlockResponse,
    summary="Update translated block",
)
async def update_block(
    block_id: UUID,
    payload: BlockUpdateRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> TranslatedBlockResponse:
    """Manually edit a translated content block."""
    return await LocalizationService().update_block(current_user.id, block_id, payload)


@router.post(
    "/{localization_id}/approve",
    summary="Approve localization",
)
async def approve_localization(
    localization_id: UUID,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> dict[str, str]:
    """Approve all translated blocks and mark the localization complete."""
    return await LocalizationService().approve_localization(current_user.id, localization_id)


@router.post(
    "/{localization_id}/export",
    summary="Export localized content",
)
async def export_localization(
    localization_id: UUID,
    payload: ExportRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> Response:
    """Export localized content as a PDF or plain text file."""
    content, filename, media_type = await LocalizationService().export_localization(
        current_user.id, localization_id, payload.format
    )
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
