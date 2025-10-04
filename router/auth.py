from fastapi import APIRouter, Depends, Request, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from auth.supabase import get_supabase_auth, Client, get_supabase_anon
from supabase import AsyncClient, create_client, create_async_client
from middlewares.decorator import supa_handle_exceptions
from middlewares.auth import get_current_user, get_token

import os

router = APIRouter(prefix="/auth", tags=["auth"])


from contextlib import contextmanager


@contextmanager
def create_supabase_client(token: str = None):
    """Context manager for creating temporary clients"""
    client = create_client(
        os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_ANON_KEY")
    )

    if token:
        client.auth.set_session(token)

    try:
        yield client
    finally:
        # Clean up if needed
        pass


class UserModel(BaseModel):
    phone: Optional[str] = None
    password: str
    captcha_token: Optional[str] = None


@router.post("/register")
@supa_handle_exceptions
async def user_register(
    i: UserModel,
    background_tasks: BackgroundTasks,
    supabase: AsyncClient = Depends(get_supabase_auth),
) -> JSONResponse:
    response = supabase.auth.sign_up(
        {
            "email": i.phone,
            "password": i.password,
        }
    )

    user_id = response.user.id

    current_user = supabase.rpc("get_client_info").execute()
    profile_data = {
        "user_id": user_id,
        "avatar_url": "",
        "created_at": "now()",
        "ip": "0.0.0.0",
    }
    background_tasks.add_task(
        insert_profile_helper,
        supabase,
        profile_data,  # Use a proper function, not lambda
    )
    return JSONResponse(status_code=200, content=response.json())


@router.post("/login")
@supa_handle_exceptions
async def user_register(
    i: UserModel,
    background_tasks: BackgroundTasks,
    request: Request,
    supabase: AsyncClient = Depends(get_supabase_auth),
) -> JSONResponse:
    response = supabase.auth.sign_in_with_password(
        {
            "email": i.phone,
            "password": i.password,
        }
    )
    user_id = response.user.id
    client_ip = request.client.host
    # response = supabase.rpc("get_client_info").execute()
    background_tasks.add_task(
        update_profile_helper,
        supabase,
        user_id,
        client_ip,  # Use a proper function, not lambda
    )
    # Only insert if profile doesn't exist

    return JSONResponse(status_code=200, content=response.json())


@router.put("/profile")
@supa_handle_exceptions
async def update_profile(
    data: dict,
    token: str = Depends(get_token),
    supabase: Client = Depends(get_supabase_auth),
):
    authenticated_client = create_client(
        supabase_url=os.environ.get("SUPABASE_URL"),
        supabase_key=os.environ.get("SUPABASE_ANON_KEY"),  # Use anon key as base
    )
    print(token)
    authenticated_client.auth.get_user(token)

    response = authenticated_client.rpc("get_client_info").execute()
    # if "ip" in data:
    #     raise HTTPException(status_code=403, detail="Cannot update IP field")
    response = (
        supabase.table("profiles")
        .update(data)
        .eq("user_id", "00f8ac67-f955-45f9-a90f-8380316e8343")
        .execute()
    )
    print(response)
    return JSONResponse(status_code=200, content=response.data)


def insert_profile_helper(supabase: Client, profile_data: dict):
    try:
        supabase.table("profiles").insert(profile_data).execute()
    except Exception as e:
        print(f"Background profile insertion failed: {e}")


def update_profile_helper(supabase: Client, user_id: str, ip: str):
    try:
        # Correct method name and syntax
        result = (
            supabase.table("profiles")
            .update({"ip": ip})
            .eq("user_id", user_id)
            .execute()
        )

        print(f"Profile updated successfully: {result}")
        return result

    except Exception as e:
        print(f"Background profile update failed: {e}")
        return None


def check_current_role_helper(supabase):
    try:
        # Execute a query that returns current role
        result = supabase.rpc("get_current_role").execute()
        print("Current role from RPC:", result.data)
    except:
        # Alternative: query a system function
        result = supabase.from_("").select("current_user").execute()
        print("Current user:", result.data)
