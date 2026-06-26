"""Supabase client initialization and async helpers."""

import asyncio
from functools import partial
from typing import Any, Callable, TypeVar

from supabase import Client, create_client

from app.config import get_settings

T = TypeVar("T")

_client: Client | None = None


def get_supabase_client() -> Client:
    """Return a singleton Supabase client instance."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = create_client(settings.supabase_url, settings.effective_supabase_key)
    return _client


async def run_sync(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """Execute a blocking Supabase call in a thread pool."""
    return await asyncio.to_thread(partial(func, *args, **kwargs))
