from typing import Dict, Any, Optional
from pathlib import Path
from src.helper import generate_presigned_signature, upload_tasks
from middlewares.decorator import handle_http_errors
from pydantic import BaseModel, Field
from fastapi import responses
from pattern.index import SingletonMeta
import tus
import requests
import json
import os
import time
import shutil
import tempfile

# def save_file_sync(temp_video_path, content: bytes):
#     # Create temporary file first
#     with tempfile.NamedTemporaryFile(delete=False, mode="wb") as temp_file:
#         temp_file.write(content)
#         temp_path = temp_file.name

#     try:
#         # Use shutil to copy the temp file to final destination
#         shutil.copy2(temp_path, temp_video_path)
#     finally:
#         # Clean up temp file
#         if os.path.exists(temp_path):
#             os.unlink(temp_path)


class GetListVideoQueryParam(BaseModel):
    page: int
    limit: int
    search: Optional[str] = Field(default="title || guid || null")
    orderBy: Optional[str] = Field(default="date || null")


class BunnyCdn(metaclass=SingletonMeta):
    def __init__(self, host=None, zone=None, key=None, cdn=None, stream_key=None):
        if getattr(self, "_initialized", False):
            return
        if not all([host, zone, key, cdn, stream_key]):
            raise ValueError("Must provide all arguments on first init")
        self.host = host
        self.zone = zone
        self.key = key
        self.cdn = cdn
        self.stream_key = stream_key
        self.tus_url = "https://video.bunnycdn.com/tusupload"
        self.stream_collection = "026db7af-aab4-4937-9887-a1e8039b3732"
        self.stream_library = "482552"
        self.stream_cdn = "https://vz-fdf68231-082.b-cdn.net"
        self.upload = None
        self._initialized = True

    async def upload_file(self, file_data, path_filename):
        response = requests.put(
            self.get_url(path_filename), headers=self.get_headers(), data=file_data
        )
        return {
            "status": response.status_code,
            "message": response.text,
            "url": f"{self.cdn}/{path_filename}",
        }

    async def delete_file(self, url: str):
        path_filename = url.replace(self.cdn + "/", "")
        response = requests.delete(
            self.get_url(path_filename),
            headers=self.get_headers(),
        )
        return {"status": response.status_code, "message": response.text}

    def get_url(self, path_filename):
        return f"https://{self.host}/{self.zone}/{path_filename}"

    def get_headers(self):
        return {
            "AccessKey": self.key,
            "Content-Type": "application/octet-stream",
            "accept": "application/json",
        }

    @handle_http_errors
    async def create_video(
        self,
        title,
    ):
        url = f"https://video.bunnycdn.com/library/{self.stream_library}/videos"

        payload = {
            "title": title,
            "collectionId": self.stream_collection,
            "thumbnailTime": 5000,
        }

        response = requests.post(url, json=payload, headers=self.get_stream_headers())
        # print("debug + ", response.text)
        return response

    def setup_upload(self, parsed_video_json, title, uri, ext, task_id):
        try:
            # parsed_create_video = json.loads(create_video_json)
            videoId = parsed_video_json["guid"]
            presigned = self.generate_presigned_video(videoId)

            headers = {
                "AuthorizationSignature": presigned["signature"],
                "AuthorizationExpire": str(presigned["expire"]),
                "VideoId": videoId,
                "LibraryId": self.stream_library,
            }

            metadata = {
                "filetype": ext,
                "title": title,
                "collection": self.stream_collection,
            }

            # Open file and upload
            with open(uri, "rb") as f:
                self.upload = tus.upload(
                    tus_endpoint=self.tus_url,
                    chunk_size=1024 * 1024 * 5,
                    headers=headers,
                    metadata=metadata,
                    file_obj=f,
                )

            # Get video info
            videoUrl, thumbnailUrl, previewUrl = self.get_video_info(videoId)

            # Update task status
            upload_tasks[task_id]["data"] = {
                "guid": videoId,
                "videoUrl": videoUrl,
                "thumbnailUrl": thumbnailUrl,
                "preview": previewUrl,
            }
            upload_tasks[task_id]["status"] = "completed"
            upload_tasks[task_id]["completed_at"] = round(time.time())

            return responses.JSONResponse(
                status_code=200, content=upload_tasks[task_id]
            )

        finally:
            # Always remove the temporary file
            if os.path.exists(uri):
                os.remove(uri)

    @handle_http_errors
    async def delete_video(self, videoId) -> Dict[str, any]:
        reponse = requests.delete(
            self.get_stream_url() + f"/{videoId}", headers=self.get_stream_headers()
        )
        return reponse

    @handle_http_errors
    async def get_list_videos(self, i: GetListVideoQueryParam) -> Dict[str, Any]:
        query = {
            "page": i.page,
            "itemsPerPage": i.limit,
            "search": i.search,
            "orderBy": i.orderBy,
        }

        response = requests.get(
            url=self.get_stream_url(),
            params=query,
            headers=self.get_stream_headers(),  # <-- must use 'params', not 'query:'
        )
        return response

    def get_stream_url(self):
        return f"https://video.bunnycdn.com/library/{self.stream_library}/videos"

    def get_video_info(self, guid):
        return (
            f"{self.stream_cdn}/{guid}/playlist.m3u8",
            f"{self.stream_cdn}/{guid}/thumbnail.jpg",
            f"{self.stream_cdn}/{guid}/preview.webp",
        )

    def generate_presigned_video(self, videoId):
        return generate_presigned_signature(
            self.stream_library, self.stream_key, videoId
        )

    def get_stream_headers(self):
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "AccessKey": self.stream_key,
        }
        return headers
