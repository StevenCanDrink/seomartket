import uuid
import base64
import secrets

# import cv2
import hashlib
import time
from typing import Dict
from urllib.parse import urlencode
from binascii import hexlify, unhexlify


upload_tasks: Dict[str, dict] = {}


def generate_short_uuid():
    uuid_bytes = uuid.uuid4().bytes
    # Encode to base64 and remove padding, replace URL-unsafe characters
    short_uuid = base64.urlsafe_b64encode(uuid_bytes).rstrip(b"=").decode("ascii")
    return short_uuid


# async def extract_middle_frame_from_file(video_path, output_path=None, quality=80):
#     """
#     Extract middle frame from video file (not memory buffer)
#     """
#     try:
#         # Process video in thread pool
#         loop = asyncio.get_event_loop()
#         webp_data = await loop.run_in_executor(
#             None, _sync_process_video_file, video_path, output_path, quality
#         )
#         return webp_data
#     except Exception as e:
#         raise Exception(f"Failed to extract frame: {str(e)}")


# def _sync_process_video_file(video_path, output_path, quality):
#     """Process video file from disk"""
#     cap = cv2.VideoCapture(video_path)
#     if not cap.isOpened():
#         raise ValueError("Could not open video file")

#     try:
#         total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
#         if total_frames == 0:
#             raise ValueError("Video has no frames")

#         middle_frame_idx = total_frames // 2
#         cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame_idx)

#         ret, frame = cap.read()
#         if not ret:
#             raise ValueError("Could not read middle frame")

#         # Convert and process image
#         frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         pil_image = Image.fromarray(frame_rgb)

#         if output_path:
#             pil_image.save(output_path, "WEBP", quality=quality)
#             return None
#         else:
#             with io.BytesIO() as output:
#                 pil_image.save(output, format="WEBP", quality=quality)
#                 return output.getvalue()

#     finally:
#         cap.release()


def generate_presigned_signature(library_id, api_key, video_id):
    """
    Generate a SHA-256 presigned signature for video access

    Args:
        library_id (str): Your library identifier
        api_key (str): Your API secret key
        expiration_time (int): Unix timestamp when signature expires
        video_id (str): The video identifier

    Returns:
        str: SHA-256 hexadecimal signature
    """

    expiration_time = generate_authorization_expire(30)
    # Create the string to sign
    string_to_sign = f"{library_id}{api_key}{expiration_time}{video_id}"

    # Generate SHA-256 hash
    signature = hashlib.sha256(string_to_sign.encode("utf-8")).hexdigest()

    return {"signature": signature, "expire": expiration_time}


def generate_authorization_expire(minutes_from_now=30):
    return int(time.time()) + (minutes_from_now * 60)


def hash_password(password):
    # Generate a unique random salt for each password (16 bytes = 128 bits)
    salt = secrets.token_bytes(16)

    # Hash the password with the salt using PBKDF2 with SHA256
    hashed_password = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100000,  # 100,000 iterations (OWASP recommendation)
        dklen=32,  # 32 bytes = 256 bits
    )

    # Combine salt and hash for storage: format = salt(hex) + hash(hex)
    salt_hex = hexlify(salt).decode("utf-8")
    hash_hex = hexlify(hashed_password).decode("utf-8")
    stored_password = f"{salt_hex}:{hash_hex}"

    return stored_password


def verify_password(stored_password, provided_password):
    try:
        # Split the stored value into salt and hash components
        salt_hex, hash_hex = stored_password.split(":")
        salt = unhexlify(salt_hex)
        stored_hash = unhexlify(hash_hex)

        # Hash the provided password with the same salt
        provided_hash = hashlib.pbkdf2_hmac(
            "sha256", provided_password.encode("utf-8"), salt, 100000, dklen=32
        )

        # Compare securely using constant-time comparison
        return hashlib.compare_digest(provided_hash, stored_hash)

    except (ValueError, TypeError):
        # Handle invalid stored password format
        return False
