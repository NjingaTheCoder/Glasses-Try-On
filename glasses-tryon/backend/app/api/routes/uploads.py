import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.upload import Upload
from app.schemas.upload import StorageUploadRead, UploadCreate, UploadRead
from app.services.firebase_service import StorageUploadError, upload_to_storage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/face", response_model=UploadRead, status_code=status.HTTP_201_CREATED)
async def record_face_upload(
    data: UploadCreate,
    db: AsyncSession = Depends(get_db),
) -> UploadRead:
    """
    Record a face photo that was uploaded client-side to Firebase Storage.
    The client handles the actual upload; this persists the resulting URL.
    """
    upload = Upload(
        id=str(uuid.uuid4()),
        user_session_id=data.user_session_id,
        firebase_url=data.firebase_url,
        created_at=datetime.now(timezone.utc),
    )
    db.add(upload)
    await db.commit()
    await db.refresh(upload)
    return upload


@router.post(
    "/face/server",
    response_model=StorageUploadRead,
    status_code=status.HTTP_201_CREATED,
)
async def server_upload_face(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> StorageUploadRead:
    """
    Server-side face photo upload.
    Accepts a multipart file, uploads it to Firebase Storage,
    persists the record, and returns full storage metadata.
    """
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are accepted.",
        )

    session_id = uuid.uuid4().hex

    try:
        result = await upload_to_storage(file, folder="faces", session_id=session_id)
    except StorageUploadError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    upload = Upload(
        id=str(uuid.uuid4()),
        user_session_id=session_id,
        firebase_url=result["public_url"],
        created_at=datetime.now(timezone.utc),
    )
    db.add(upload)
    await db.commit()

    return StorageUploadRead(**result)


@router.post(
    "/glasses/server",
    response_model=StorageUploadRead,
    status_code=status.HTTP_201_CREATED,
)
async def server_upload_glasses(
    file: UploadFile = File(...),
) -> StorageUploadRead:
    """
    Server-side glasses image upload (admin use).
    Accepts a PNG, uploads to Firebase Storage, returns storage metadata.
    The returned public_url can be stored as the product's image_url.
    """
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are accepted.",
        )

    try:
        result = await upload_to_storage(file, folder="glasses")
    except StorageUploadError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return StorageUploadRead(**result)
