"""
Supabase client singleton for database operations.
Uses service role key to bypass RLS for backend writes.
"""

import os
from typing import Optional

from supabase import create_client, Client

from config import settings

# Global client instance - initialized lazily
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Get or create Supabase client using service role key."""
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    # Try settings first, fall back to direct env var read
    supabase_url = settings.supabase_url or os.environ.get("SUPABASE_URL", "")
    supabase_key = settings.supabase_service_key or os.environ.get("SUPABASE_SERVICE_KEY", "")

    if not supabase_url:
        raise ValueError("SUPABASE_URL is not configured")
    if not supabase_key:
        raise ValueError("SUPABASE_SERVICE_KEY is not configured")

    _supabase_client = create_client(supabase_url, supabase_key)
    return _supabase_client


def is_supabase_configured() -> bool:
    """Check if Supabase environment variables are set."""
    supabase_url = settings.supabase_url or os.environ.get("SUPABASE_URL", "")
    supabase_key = settings.supabase_service_key or os.environ.get("SUPABASE_SERVICE_KEY", "")
    return bool(supabase_url and supabase_key)
