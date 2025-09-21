from pydantic import BaseModel


class StreamBunnyObject(BaseModel):
    guid: str
    videoUrl: str
    thumbnailUrl: str
    preview: str


class UploadVideoResponse(BaseModel):
    status: str
    message: str  # Public URL of the uploaded avatar
    tast_id: str  # Stored filename
    guid: str  # Stored filename


class UploadFileResponse(BaseModel):
    status: int
    url: str


class UploadStatusResponse(BaseModel):
    status: str
    message: str
    data: StreamBunnyObject


class GetListVideoResponse(BaseModel):
    totalItems: int
    currentPage: int
    itemsPerPage: int
    items: StreamBunnyObject
