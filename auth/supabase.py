import os
import atexit
from typing import Optional
from supabase import Client, create_client

_client: Optional[Client] = None
_client_anon: Optional[Client] = None


def get_client(use_anon_key: bool = False) -> Client:
    """Get Supabase client with optional anonymous access."""
    global _client, _client_anon

    if use_anon_key:
        # Anonymous client - limited permissions
        if _client_anon is None:
            url = os.environ.get("SUPABASE_URL")
            key = os.environ.get("SUPABASE_SERVICE_KEY")  # Renamed for clarity
            print(key)
            if not url or not key:
                raise ValueError("Supabase URL and anonymous key required")
            _client_anon = create_client(supabase_url=url, supabase_key=key)
            atexit.register(_cleanup_clients)
        return _client_anon
    else:
        # Authenticated client - full permissions
        if _client is None:
            url = os.environ.get("SUPABASE_URL")
            key = os.environ.get("SUPABASE_ANON_KEY")  # Renamed for clarity
            print(key)
            if not url or not key:
                raise ValueError("Supabase URL and service key required")
            _client = create_client(supabase_url=url, supabase_key=key)
            atexit.register(_cleanup_clients)
        return _client


def _cleanup_clients():
    """Clean up both clients."""
    global _client, _client_anon
    if _client:
        _client.close()
        _client = None
    if _client_anon:
        _client_anon.close()
        _client_anon = None


def close_clients():
    """Explicitly close all clients."""
    _cleanup_clients()


# Dependency functions for frameworks like FastAPI
def get_supabase_auth() -> Client:
    """Dependency for authenticated (service role) client."""
    return get_client(use_anon_key=False)


def get_supabase_anon() -> Client:
    """Dependency for anonymous client."""
    return get_client(use_anon_key=True)
