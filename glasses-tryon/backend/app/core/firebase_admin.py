import base64
import json
import logging

import firebase_admin
from firebase_admin import credentials, auth as firebase_auth, storage

from app.core.config import settings

logger = logging.getLogger(__name__)


def _load_service_account() -> dict | None:
    """
    Load the service account dict from whichever env var is set.
    Priority: FIREBASE_SERVICE_ACCOUNT_JSON (raw JSON) > FIREBASE_SERVICE_ACCOUNT_BASE64 (legacy).
    """
    raw_json = settings.firebase_service_account_json.strip()
    if raw_json:
        try:
            return json.loads(raw_json)
        except json.JSONDecodeError as exc:
            logger.error("FIREBASE_SERVICE_ACCOUNT_JSON is not valid JSON: %s", exc)
            raise

    raw_b64 = settings.firebase_service_account_base64.strip()
    if raw_b64:
        try:
            decoded = base64.b64decode(raw_b64)
            return json.loads(decoded)
        except Exception as exc:
            logger.error("FIREBASE_SERVICE_ACCOUNT_BASE64 could not be decoded: %s", exc)
            raise

    return None


def init_firebase() -> None:
    """Initialize Firebase Admin SDK once. Safe to call multiple times."""
    if firebase_admin._apps:
        return

    service_account = _load_service_account()
    if service_account is None:
        logger.warning(
            "No Firebase service account configured "
            "(set FIREBASE_SERVICE_ACCOUNT_JSON or FIREBASE_SERVICE_ACCOUNT_BASE64) — "
            "Firebase auth and storage are disabled."
        )
        return

    bucket = (
        settings.firebase_storage_bucket
        or f"{service_account.get('project_id', '')}.appspot.com"
    )

    try:
        cred = credentials.Certificate(service_account)
        firebase_admin.initialize_app(cred, {"storageBucket": bucket})
        logger.info(
            "Firebase initialized — project=%s bucket=%s",
            service_account.get("project_id"),
            bucket,
        )
    except Exception as exc:
        logger.error("Firebase initialization failed: %s", exc)
        raise


def get_bucket():
    """Return the default Firebase Storage bucket handle."""
    return storage.bucket()


async def verify_token(token: str) -> str:
    """Verify a Firebase ID token and return the UID."""
    try:
        decoded = firebase_auth.verify_id_token(token)
        return decoded["uid"]
    except Exception as exc:
        raise ValueError("Invalid or expired token") from exc
