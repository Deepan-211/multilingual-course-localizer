"""Supabase storage and database operations."""

import os
import uuid
from pathlib import Path
from typing import Any
from uuid import UUID

from app.config import get_settings
from app.database import get_supabase_client, run_sync


class SupabaseService:
    """Wrapper for Supabase database and storage operations."""

    def __init__(self) -> None:
        self.client = get_supabase_client()
        self.settings = get_settings()
        Path(self.settings.upload_dir).mkdir(parents=True, exist_ok=True)

    async def upload_file(self, file_bytes: bytes, file_name: str, user_id: UUID) -> tuple[str, str]:
        """Upload a file to local storage and return path and public URL."""
        ext = Path(file_name).suffix
        unique_name = f"{user_id}/{uuid.uuid4()}{ext}"
        local_path = Path(self.settings.upload_dir) / unique_name
        local_path.parent.mkdir(parents=True, exist_ok=True)

        def _write() -> None:
            with open(local_path, "wb") as f:
                f.write(file_bytes)

        await run_sync(_write)

        bucket_path = f"courses/{unique_name}"

        def _upload_storage() -> str:
            try:
                self.client.storage.from_("course-files").upload(
                    bucket_path,
                    file_bytes,
                    {"content-type": "application/octet-stream", "upsert": "true"},
                )
                return self.client.storage.from_("course-files").get_public_url(bucket_path)
            except Exception:
                return str(local_path)

        public_url = await run_sync(_upload_storage)
        return str(local_path), public_url

    async def insert(self, table: str, data: dict[str, Any]) -> dict[str, Any]:
        """Insert a row and return the created record."""

        def _insert() -> dict[str, Any]:
            response = self.client.table(table).insert(data).execute()
            return response.data[0]

        return await run_sync(_insert)

    async def select(
        self,
        table: str,
        filters: dict[str, Any] | None = None,
        columns: str = "*",
        order_by: str | None = None,
        ascending: bool = True,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Select rows from a table with optional filters."""

        def _select() -> list[dict[str, Any]]:
            query = self.client.table(table).select(columns)
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            if order_by:
                query = query.order(order_by, desc=not ascending)
            if limit:
                query = query.limit(limit)
            response = query.execute()
            return response.data or []

        return await run_sync(_select)

    async def select_one(self, table: str, filters: dict[str, Any], columns: str = "*") -> dict[str, Any] | None:
        """Select a single row or return None."""

        def _select() -> dict[str, Any] | None:
            query = self.client.table(table).select(columns)
            for key, value in filters.items():
                query = query.eq(key, value)
            response = query.limit(1).execute()
            return response.data[0] if response.data else None

        return await run_sync(_select)

    async def update(self, table: str, filters: dict[str, Any], data: dict[str, Any]) -> dict[str, Any] | None:
        """Update rows matching filters."""

        def _update() -> dict[str, Any] | None:
            query = self.client.table(table).update(data)
            for key, value in filters.items():
                query = query.eq(key, value)
            response = query.execute()
            return response.data[0] if response.data else None

        return await run_sync(_update)

    async def delete(self, table: str, filters: dict[str, Any]) -> None:
        """Delete rows matching filters."""

        def _delete() -> None:
            query = self.client.table(table).delete()
            for key, value in filters.items():
                query = query.eq(key, value)
            query.execute()

        await run_sync(_delete)

    async def count(self, table: str, filters: dict[str, Any] | None = None) -> int:
        """Count rows in a table."""

        def _count() -> int:
            query = self.client.table(table).select("id", count="exact")
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            response = query.execute()
            return response.count or 0

        return await run_sync(_count)

    async def delete_local_file(self, file_path: str) -> None:
        """Remove a local file if it exists."""
        if os.path.isfile(file_path):

            def _remove() -> None:
                os.remove(file_path)

            await run_sync(_remove)
