"""
Supabase client singleton for database operations.
Uses service role key to bypass RLS for backend writes.
"""

import os
from functools import lru_cache

from supabase import create_client, Client

from config import settings


@lru_cache
def get_supabase_client() -> Client:
    """Get cached Supabase client using service role key."""
    # Try settings first, fall back to direct env var read
    supabase_url = settings.supabase_url or os.environ.get("SUPABASE_URL", "")
    supabase_key = settings.supabase_service_key or os.environ.get("SUPABASE_SERVICE_KEY", "")

    print(f"DEBUG: settings.supabase_url = '{settings.supabase_url}'")
    print(f"DEBUG: os.environ SUPABASE_URL = '{os.environ.get('SUPABASE_URL', 'NOT SET')}'")
    print(f"DEBUG: Final supabase_url = '{supabase_url}'")

    if not supabase_url:
        raise ValueError("SUPABASE_URL is not configured")
    if not supabase_key:
        raise ValueError("SUPABASE_SERVICE_KEY is not configured")

    return create_client(supabase_url, supabase_key)
