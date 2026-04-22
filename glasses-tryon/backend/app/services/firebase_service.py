"""
Server-side Firebase Storage upload service.

Strategy: files are made publicly readable after upload so URLs never expire.
This matches Firebase Storage client SDK behaviour (getDownloadURL returns a
stable media URL).  If you prefer signed URLs that expire, replace make_public()
with blob.generate_signed_url(expiration=timedelta(days=7)) — but note that
signed URLs require the service account to have the `iam.serviceAccounts.signBlob`
permission and won't work with Application Default Credentials.
"""
import logging
import mimetypes
import uuid
from datetime import datetime, timezone
from io import BytesIO

from fastapi import UploadFile

from app.core.firebase_admin import get_bucket

logger = logging.getLogger(__name__)

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB


class StorageUploadError(Exception):
    pass


async def upload_to_storage(
    file: UploadFile,
    folder: str,
    session_id: str | None = None,
) -> dict:
    """
    Upload a FastAPI UploadFile to Firebase Storage.

    Returns:
        dict with keys: bucket, path, filename, content_type, size, public_url
    """
    data = await file.read()
    size = len(data)

    if size == 0:
        raise StorageUploadError("Uploaded file is empty.")
    if size > MAX_UPLOAD_BYTES:
        raise StorageUploadError(
            f"File exceeds the {MAX_UPLOAD_BYTES // (1024 * 1024)} MB limit."
        )

    content_type = (
        file.content_type
        or mimetypes.guess_type(file.filename or "")[0]
        or "application/octet-stream"
    )

    original = file.filename or "upload"
    ext = original.rsplit(".", 1)[-1] if "." in original else ""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    unique_name = f"{ts}_{uuid.uuid4().hex[:8]}"
    if ext:
        unique_name = f"{unique_name}.{ext}"

    path = f"{folder}/{session_id}/{unique_name}" if session_id else f"{folder}/{unique_name}"

    try:
        bucket = get_bucket()
        blob = bucket.blob(path)
        blob.upload_from_file(BytesIO(data), content_type=content_type)
        blob.make_public()
        public_url = blob.public_url
        logger.info("Uploaded %s bytes to gs://%s/%s", size, bucket.name, path)
    except Exception as exc:
        logger.error("Firebase Storage upload failed for path %s: %s", path, exc)
        raise StorageUploadError(f"Storage upload failed: {exc}") from exc

    return {
        "bucket": bucket.name,
        "path": path,
        "filename": unique_name,
        "content_type": content_type,
        "size": size,
        "public_url": public_url,
    }
