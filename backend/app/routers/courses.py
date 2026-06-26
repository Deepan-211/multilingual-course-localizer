"""Course management routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.middleware.auth_middleware import get_current_user
from app.schemas.course import CourseCreateResponse, CourseListResponse, CourseResponse
from app.schemas.user import UserResponse
from app.services.course_service import CourseService

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.post("/upload", response_model=CourseCreateResponse, summary="Upload a course")
async def upload_course(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    title: Annotated[str, Form(...)],
    source_language: Annotated[str, Form(...)],
    content_type: Annotated[str, Form(...)],
    file: Annotated[UploadFile, File(...)],
) -> CourseCreateResponse:
    """Upload a PDF or video course file with metadata."""
    return await CourseService().upload_course(
        user_id=current_user.id,
        title=title,
        source_language=source_language,
        content_type=content_type,
        file=file,
    )


@router.get("/", response_model=CourseListResponse, summary="List all courses")
async def list_courses(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> CourseListResponse:
    """Return all courses belonging to the current user."""
    courses = await CourseService().list_courses(current_user.id)
    return CourseListResponse(courses=courses, total=len(courses))


@router.get("/{course_id}", response_model=CourseResponse, summary="Get course details")
async def get_course(
    course_id: UUID,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> CourseResponse:
    """Return details for a single course."""
    return await CourseService().get_course(current_user.id, course_id)


@router.delete("/{course_id}", summary="Delete a course")
async def delete_course(
    course_id: UUID,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> dict[str, str]:
    """Delete a course and all related localizations."""
    return await CourseService().delete_course(current_user.id, course_id)
