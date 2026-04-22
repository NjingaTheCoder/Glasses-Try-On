import base64
import json
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from app.core.config import settings


def init_firebase() -> None:
    if firebase_admin._apps:
        return
    if not settings.firebase_service_account_base64:
        return  # Skip in tests / local dev without Firebase
    decoded = base64.b64decode(settings.firebase_service_account_base64)
    service_account = json.loads(decoded)
    cred = credentials.Certificate(service_account)
    firebase_admin.initialize_app(cred)


async def verify_token(token: str) -> str:
    """Return UID of the authenticated admin user or raise."""
    try:
        decoded = firebase_auth.verify_id_token(token)
        return decoded["uid"]
    except Exception as exc:
        raise ValueError("Invalid or expired token") from exc
