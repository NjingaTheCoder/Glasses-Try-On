from datetime import datetime, timezone
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.upload import Upload
from app.schemas.upload import UploadCreate, UploadRead

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/face", response_model=UploadRead, status_code=status.HTTP_201_CREATED)
async def record_face_upload(
    data: UploadCreate,
    db: AsyncSession = Depends(get_db),
) -> UploadRead:
    """
    Record that a face photo was saved to Firebase Storage.
    The actual upload happens client-side; this just persists metadata.
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


@router.post("/glasses", status_code=status.HTTP_200_OK)
async def glasses_upload_url() -> dict:
    """
    Glasses PNGs are uploaded directly to Firebase Storage client-side.
    This endpoint is a placeholder for any future server-side processing.
    """
    return {"message": "Upload glasses PNG directly to Firebase Storage from the admin client."}
