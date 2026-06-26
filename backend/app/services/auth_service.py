"""Authentication business logic."""

from uuid import UUID

from fastapi import HTTPException, status

from app.middleware.auth_middleware import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.schemas.user import (
    ChangePasswordRequest,
    LanguageSettingsUpdate,
    NotificationSettingsUpdate,
    ProfileUpdate,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
    UserSettingsResponse,
)
from app.services.supabase_service import SupabaseService


class AuthService:
    """User registration, login, and profile management."""

    def __init__(self) -> None:
        self.db = SupabaseService()

    async def register(self, payload: UserRegister) -> TokenResponse:
        """Register a new user and return a JWT."""
        existing = await self.db.select_one("users", {"email": payload.email})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Email already registered",
            )

        user_data = {
            "name": payload.name,
            "email": payload.email,
            "password_hash": hash_password(payload.password),
        }
        user = await self.db.insert("users", user_data)

        await self.db.insert(
            "user_settings",
            {
                "user_id": user["id"],
                "default_source_language": "English",
                "default_target_languages": ["Tamil", "Hindi"],
                "email_notifications": True,
                "localization_complete": True,
                "weekly_digest": False,
            },
        )

        token = create_access_token(user["id"])
        return TokenResponse(access_token=token)

    async def login(self, payload: UserLogin) -> TokenResponse:
        """Authenticate user and return a JWT."""
        user = await self.db.select_one("users", {"email": payload.email})
        if not user or not verify_password(payload.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        token = create_access_token(user["id"])
        return TokenResponse(access_token=token)

    async def get_profile(self, user: UserResponse) -> UserResponse:
        """Return the current user profile."""
        return user

    async def update_profile(self, user_id: UUID, payload: ProfileUpdate) -> UserResponse:
        """Update user name and avatar."""
        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No fields to update",
            )

        updated = await self.db.update("users", {"id": str(user_id)}, update_data)
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return UserResponse(
            id=updated["id"],
            name=updated["name"],
            email=updated["email"],
            avatar_url=updated.get("avatar_url"),
            created_at=updated["created_at"],
        )

    async def change_password(self, user_id: UUID, payload: ChangePasswordRequest) -> dict[str, str]:
        """Change the user's password after verifying the old one."""
        user = await self.db.select_one("users", {"id": str(user_id)})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if not verify_password(payload.old_password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect",
            )

        await self.db.update(
            "users",
            {"id": str(user_id)},
            {"password_hash": hash_password(payload.new_password)},
        )
        return {"message": "Password updated successfully"}

    async def get_settings(self, user_id: UUID) -> UserSettingsResponse:
        """Return user preferences."""
        settings = await self.db.select_one("user_settings", {"user_id": str(user_id)})
        if not settings:
            return UserSettingsResponse()
        return UserSettingsResponse(
            default_source_language=settings.get("default_source_language", "English"),
            default_target_languages=settings.get("default_target_languages", ["Tamil", "Hindi"]),
            email_notifications=settings.get("email_notifications", True),
            localization_complete=settings.get("localization_complete", True),
            weekly_digest=settings.get("weekly_digest", False),
        )

    async def update_language_settings(
        self, user_id: UUID, payload: LanguageSettingsUpdate
    ) -> UserSettingsResponse:
        """Update default source and target languages."""
        await self.db.update(
            "user_settings",
            {"user_id": str(user_id)},
            {
                "default_source_language": payload.default_source_language,
                "default_target_languages": payload.default_target_languages,
            },
        )
        return await self.get_settings(user_id)

    async def update_notification_settings(
        self, user_id: UUID, payload: NotificationSettingsUpdate
    ) -> UserSettingsResponse:
        """Update email notification preferences."""
        await self.db.update(
            "user_settings",
            {"user_id": str(user_id)},
            payload.model_dump(),
        )
        return await self.get_settings(user_id)
