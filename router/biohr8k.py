from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from src.helper import generate_short_uuid
from weasyprint import HTML
from src.bunny_cdn import BunnyCdn
from weasyprint_assets.index import WeasyprintCustom
from router.class_responses import UploadFileResponse
from middlewares.decorator import handle_exceptions
import aiofiles
import os


router = APIRouter(prefix="/biohr8k", tags=["biohr8k"])


weasyprint = WeasyprintCustom()
bunny = BunnyCdn()


@router.get("/")
async def read_root():
    return {"Hello": "World"}


@router.post("/upload-avatar", response_model=UploadFileResponse)
@handle_exceptions
async def upload_image(file: UploadFile = File(...)):
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only image files are allowed (JPEG, PNG, GIF, WEBP)",
        )
    uuid = generate_short_uuid()
    # Validate file size (max 5MB)
    max_size = 5 * 1024 * 1024  # 5MB
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    if file_size > max_size:
        raise HTTPException(
            status_code=400, detail="File size too large. Maximum size is 5MB"
        )
    file_content = await file.read()

    # Generate unique filename
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"hr-bio/avatars/avatar_{uuid}.{file_extension}"
    rs = await bunny.upload_file(file_content, unique_filename)
    return rs


@router.post("/export-pdf", response_model=UploadFileResponse)
async def read_item(html_string: str = Body(..., media_type="text/html")):
    try:
        # Create tmp directory if it doesn't exist
        os.makedirs("tmp", exist_ok=True)

        # Generate unique ID
        uuid = generate_short_uuid()
        file_path = f"tmp/cv-{uuid}.pdf"

        # Convert HTML to PDF
        await weasyprint.create_pdf(html_string, f"cv-{uuid}")

        # Read the generated PDF file and upload
        async with aiofiles.open(file_path, "rb") as file:
            file_content = await file.read()
            unique_filename = f"hr-bio/cvs/cv-{uuid}.pdf"
            response = await bunny.upload_file(file_content, unique_filename)

        # Clean up temporary file
        try:
            if os.path.exists(file_path):
                os.remove(file_path)  # or os.unlink(file_path)
                print(f"✅ File deleted: {file_path}")
        except:
            pass  # Silently fail if file deletion fails

        return response

    except Exception as e:
        # Clean up temporary file in case of error
        try:
            if "file_path" in locals():
                os.remove(file_path)
        except:
            pass

        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")
