from fastapi import APIRouter, Depends, Request, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from auth.supabase import get_supabase, Client, get_supabase_anon
from supabase import AsyncClient
from middlewares.decorator import supa_handle_exceptions
from middlewares.auth import get_current_user, get_token

router = APIRouter(prefix="/auth", tags=["auth"])


class UserModel(BaseModel):
    phone: Optional[str] = None
    password: str
    captcha_token: Optional[str] = None


@router.post("/register")
@supa_handle_exceptions
async def user_register(
    i: UserModel,
    background_tasks: BackgroundTasks,
    supabase: AsyncClient = Depends(get_supabase),
) -> JSONResponse:
    response = supabase.auth.sign_up(
        {
            "phone": i.phone,
            "password": i.password,
        }
    )

    user_id = response.user.id
    profile_data = {
        "user_id": user_id,
        "avatar_url": i.phone,
        "created_at": "now()",
        "avatar_url": "",
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
    supabase: AsyncClient = Depends(get_supabase),
) -> JSONResponse:
    response = supabase.auth.sign_in_with_password(
        {
            "phone": i.phone,
            "password": i.password,
        }
    )
    user_id = response.user.id
    client_ip = request.client.host

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
    supabase: Client = Depends(get_supabase_anon),
):
    """
    User can update their own profile fields (except 'ip').
    """

    print(token)
    print(supabase)
    supabase.postgrest.auth(token)
    # if "ip" in data:
    #     raise HTTPException(status_code=403, detail="Cannot update IP field")

    response = supabase.table("profiles").update(data).execute()

    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)

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
