from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
import httpx

from app.services.openai_service import AIRenderError, render_ai

router = APIRouter(prefix="/try-on", tags=["try-on"])

_MAX_FILE_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("/render-ai")
async def render_ai_endpoint(
    face_image: UploadFile = File(...),
    glasses_url: str = Form(...),
) -> dict[str, str]:
    # --- validate face image ---
    face_content_type = face_image.content_type or ""
    if not face_content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="face_image must be an image file.",
        )

    face_bytes = await face_image.read()
    if len(face_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="face_image is empty.",
        )
    if len(face_bytes) > _MAX_FILE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="face_image exceeds the 10 MB limit.",
        )

    # --- fetch glasses image ---
    if not glasses_url.startswith("https://"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="glasses_url must be a valid HTTPS URL.",
        )

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(glasses_url)
            resp.raise_for_status()
            glasses_bytes = resp.content
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not fetch glasses image: HTTP {exc.response.status_code}.",
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not reach glasses image URL: {exc}.",
        ) from exc

    if len(glasses_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fetched glasses image is empty.",
        )

    # --- call OpenAI ---
    try:
        image_url = await render_ai(face_bytes, glasses_bytes, face_content_type)
    except AIRenderError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return {"image_url": image_url}
