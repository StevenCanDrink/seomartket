from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/auth", tags=["auth"])


class UserModel(BaseModel):
    username: str
    password: str
    captcha_token: Optional[str]


@router.post("/register")
async def user_register(i: UserModel) -> JSONResponse:

    return JSONResponse(status_code=200, content={})


@router.post("/login")
async def user_register(i: UserModel) -> JSONResponse:

    return JSONResponse(status_code=200, content={})
