"""
Supabase client singleton for database operations.
Uses service role key to bypass RLS for backend writes.
"""

from functools import lru_cache

from supabase import create_client, Client

from config import settings


@lru_cache
def get_supabase_client() -> Client:
    """Get cached Supabase client using service role key."""
    return create_client(
        settings.supabase_url,
        settings.supabase_service_key,
    )
