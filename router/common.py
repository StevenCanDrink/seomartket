from fastapi import APIRouter, Body, HTTPException, responses
from dotenv import load_dotenv
from pydantic import BaseModel
from src.bunny_cdn import BunnyCdn
import os


class DeleteRequest(BaseModel):
    url: str


bunny = BunnyCdn()
router = APIRouter(prefix="/common", tags=["common"])


@router.delete("/file")
async def bunny_delete_file(request: DeleteRequest):
    try:
        rs = await bunny.delete_file(request.url)
        return rs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error delete file: {str(e)}")


@router.get("/check-health")
async def check_health():
    return responses.JSONResponse(status_code=200, content="FUCKKK AWS")
