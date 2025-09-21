from fastapi import (
    APIRouter,
    UploadFile,
    BackgroundTasks,
    File,
    HTTPException,
    responses,
    Body,
)
from src.helper import generate_short_uuid, upload_tasks
from src.bunny_cdn import GetListVideoQueryParam, BunnyCdn
from router.class_responses import (
    UploadVideoResponse,
    UploadStatusResponse,
    GetListVideoResponse,
)
from middlewares.decorator import handle_exceptions
import os, aiofiles
import datetime, time
import json

router = APIRouter(prefix="/charity8k", tags=["charity8k"])
bunny = BunnyCdn()


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


@router.post("/upload-video", response_model=UploadVideoResponse)
async def upload_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    # Extract filename
    try:
        name_without_ext, ext = os.path.splitext(file.filename)
        ext = ext.lstrip(".")
        # Validate file type
        allowed_types = ["video/mp4", "mp4"]
        if file.content_type not in allowed_types or ext not in allowed_types:
            raise HTTPException(status_code=400, detail="Only MP4 videos allowed")
        uid = generate_short_uuid()
        file.file.seek(0)  # Ensure we're at the beginning
        # Ensure temp dir exists
        os.makedirs("tmp", exist_ok=True)
        temp_video_path = f"tmp/{name_without_ext}-{uid}.mp4"

        # Save file quickly
        async with aiofiles.open(temp_video_path, "wb") as f:
            while chunk := await file.read(1024 * 1024 * 5):
                await f.write(chunk)

        upload_tasks[uid] = {
            "status": f"Processing {name_without_ext} from {temp_video_path}",
        }

        create_video_json = await bunny.create_video(name_without_ext)

    except Exception as e:
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
        raise HTTPException(status_code=e.status_code, detail=e.message)

    create_video_parsed = create_video_json
    upload_tasks[uid] = {
        "status": "processing",
        "started_at": round(time.time()),
        "guid": create_video_parsed["guid"],
        "task_id": uid,
        "message": "Upload started in background",
    }

    background_tasks.add_task(
        bunny.setup_upload,
        create_video_parsed,
        name_without_ext,
        temp_video_path,
        ext,
        uid,
    )
    return responses.JSONResponse(status_code=200, content=upload_tasks[uid])


@router.get("/upload-status/{task_id}", response_model=UploadStatusResponse)
async def get_upload_status(task_id: str):
    task = upload_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task["status"] == "completed":
        return responses.JSONResponse(status_code=200, content=task)
    return responses.JSONResponse(status_code=202, content=task)


@router.post("/stream-get-videos", response_model=GetListVideoResponse)
@handle_exceptions
async def get_list_videos(i: GetListVideoQueryParam = Body(...)):
    resp = await bunny.get_list_videos(i)
    result = resp
    items = []

    for item in result["items"]:
        new_item = {}
        videoUrl, thumbnailUrl, previewUrl = bunny.get_video_info(item["guid"])
        new_item["title"] = item["title"]
        new_item["guid"] = item["guid"]
        new_item["videoUrl"] = videoUrl
        new_item["thumbnailUrl"] = thumbnailUrl
        new_item["preview"] = previewUrl
        items.append(new_item)
    result["items"] = items
    return responses.JSONResponse(status_code=200, content=result)


@router.post("/del-video/{videoId}", response_model=GetListVideoResponse)
@handle_exceptions
async def delete_video(videoId: str):
    await bunny.delete_video(videoId)
    return responses.JSONResponse(status_code=200, content="delete success")
