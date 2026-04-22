from datetime import datetime
from pydantic import BaseModel


class UploadCreate(BaseModel):
    user_session_id: str
    firebase_url: str


class UploadRead(BaseModel):
    id: str
    user_session_id: str
    firebase_url: str
    created_at: datetime

    model_config = {"from_attributes": True}


class StorageUploadRead(BaseModel):
    """Returned by server-side upload endpoints."""
    bucket: str
    path: str
    filename: str
    content_type: str
    size: int
    public_url: str
