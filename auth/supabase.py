from supabase import create_client, Client
import atexit, os

_client = None
_client_anon = None


def get_client() -> Client:
    global _client
    if _client is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        _client = create_client(supabase_url=url, supabase_key=key)
        # Register a cleanup function
        atexit.register(lambda: (_client.close() if _client else None))

    return _client


def get_client_anon() -> Client:
    global _client_anon
    if _client_anon is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_ANON")
        _client_anon = create_client(supabase_url=url, supabase_key=key)
        # Register a cleanup function
        atexit.register(lambda: (_client_anon.close() if _client_anon else None))
    return _client_anon


def close_client():
    global _client
    if _client:
        _client.close()
        _client = None
    if _client_anon:
        _client_anon.close()
        _client_anon = None


def get_supabase() -> Client:
    """Dependency to inject the Supabase client into routes."""
    return get_client()


def get_supabase_anon() -> Client:
    """Dependency to inject the Supabase client into routes."""
    return get_client_anon()
