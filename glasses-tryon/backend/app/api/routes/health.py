import logging

from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import engine

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health() -> dict:
    """Always returns 200 — includes DB status for observability."""
    db_status = "ok"
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = f"error: {type(exc).__name__}"
        logger.warning("Health check DB ping failed: %s", exc)

    return {"status": "ok", "database": db_status}
