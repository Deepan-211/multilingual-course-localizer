"""Dashboard routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.middleware.auth_middleware import get_current_user
from app.schemas.course import RecentCourseResponse
from app.schemas.localization import DashboardActivityResponse, DashboardStatsResponse
from app.schemas.user import UserResponse
from app.services.course_service import CourseService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse, summary="Dashboard statistics")
async def get_stats(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> DashboardStatsResponse:
    """Return total courses, languages processed, completions, and queue size."""
    return await CourseService().get_dashboard_stats(current_user.id)


@router.get("/activity", response_model=DashboardActivityResponse, summary="Activity chart data")
async def get_activity(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> DashboardActivityResponse:
    """Return localization counts per day for the last 7 days."""
    activity = await CourseService().get_activity(current_user.id)
    return DashboardActivityResponse(activity=activity)


@router.get("/recent", response_model=list[RecentCourseResponse], summary="Recent courses")
async def get_recent(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> list[RecentCourseResponse]:
    """Return the 5 most recently created courses with status."""
    return await CourseService().get_recent_courses(current_user.id)
