import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.core.firebase_admin import init_firebase
from app.api.routes import health, products, uploads, tryon

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Firebase ────────────────────────────────────────────────────────────
    try:
        init_firebase()
    except Exception as exc:
        logger.error("Firebase init failed at startup: %s", exc)

    # ── Database connectivity check ─────────────────────────────────────────
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection OK")
    except Exception as exc:
        # Log clearly but don't crash — individual requests will surface the error
        logger.error("Database connection FAILED at startup: %s", exc)

    yield

    await engine.dispose()


app = FastAPI(title="Glasses Try-On API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(uploads.router, prefix="/api")
app.include_router(tryon.router, prefix="/api")
