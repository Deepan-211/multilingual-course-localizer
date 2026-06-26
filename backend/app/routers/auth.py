"""Authentication routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.middleware.auth_middleware import get_current_user
from app.schemas.user import (
    ChangePasswordRequest,
    ProfileUpdate,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, summary="Register a new user")
async def register(payload: UserRegister) -> TokenResponse:
    """Register with name, email, and password; returns a JWT token."""
    return await AuthService().register(payload)


@router.post("/login", response_model=TokenResponse, summary="Login")
async def login(payload: UserLogin) -> TokenResponse:
    """Authenticate with email and password; returns a JWT token."""
    return await AuthService().login(payload)


@router.get("/me", response_model=UserResponse, summary="Get current user profile")
async def get_me(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> UserResponse:
    """Return the authenticated user's profile."""
    return current_user


@router.put("/profile", response_model=UserResponse, summary="Update profile")
async def update_profile(
    payload: ProfileUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> UserResponse:
    """Update the current user's name and avatar."""
    return await AuthService().update_profile(current_user.id, payload)


@router.post("/change-password", summary="Change password")
async def change_password(
    payload: ChangePasswordRequest,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> dict[str, str]:
    """Change password after verifying the current password."""
    return await AuthService().change_password(current_user.id, payload)
