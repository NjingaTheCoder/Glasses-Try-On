from __future__ import annotations

import base64
from io import BytesIO

from openai import AsyncOpenAI, OpenAIError
from PIL import Image

from app.core.config import settings

_MAX_INPUT_PX = 1024


def _resize_to_fit(data: bytes, content_type: str) -> tuple[bytes, str]:
    """Shrink image so its longest side is ≤ _MAX_INPUT_PX. Returns (bytes, mime)."""
    img = Image.open(BytesIO(data))
    if max(img.size) > _MAX_INPUT_PX:
        img.thumbnail((_MAX_INPUT_PX, _MAX_INPUT_PX), Image.LANCZOS)
    buf = BytesIO()
    fmt = "PNG" if "png" in content_type else "JPEG"
    img.save(buf, format=fmt)
    return buf.getvalue(), f"image/{fmt.lower()}"

_PROMPT = (
    "You are given two images.\n"
    "Image 1: a portrait photograph of a person — this is the base image to edit.\n"
    "Image 2: a PNG of eyeglasses — these are the glasses to place on the person.\n\n"
    "Edit Image 1 so the person is wearing the eyeglasses from Image 2 naturally and "
    "realistically, as a skilled retoucher would.\n\n"
    "Requirements:\n"
    "- Preserve the person's identity, face shape, skin tone, hairstyle, expression, "
    "clothing, pose, and background exactly — change nothing except adding the glasses.\n"
    "- Replicate the exact frame shape, rim thickness, bridge design, color, and temple "
    "style from Image 2.\n"
    "- Centre the glasses on the eyes, resting naturally on the nose bridge, with correct "
    "perspective and scale for this face.\n"
    "- Add subtle, natural shadows where the frame contacts the nose and temples.\n"
    "- Do not alter the background, lighting, clothing, or any facial features.\n"
    "- Do not add any accessories beyond the eyeglasses."
)


class AIRenderError(Exception):
    """Raised when the OpenAI call fails or returns unusable data."""


async def render_ai(
    face_bytes: bytes,
    glasses_bytes: bytes,
    face_content_type: str = "image/png",
) -> str:
    """Call OpenAI image edit and return a base64 PNG data URL."""
    if not settings.openai_api_key:
        raise AIRenderError("OpenAI API key is not configured on the server.")

    client = AsyncOpenAI(api_key=settings.openai_api_key)

    face_bytes, face_content_type = _resize_to_fit(face_bytes, face_content_type)
    glasses_bytes, _ = _resize_to_fit(glasses_bytes, "image/png")

    image_files: list[tuple[str, BytesIO, str]] = [
        ("face.png", BytesIO(face_bytes), face_content_type),
        ("glasses.png", BytesIO(glasses_bytes), "image/png"),
    ]

    try:
        response = await client.images.edit(
            model=settings.openai_image_model,
            image=image_files,
            prompt=_PROMPT,
            n=1,
            size="1024x1024",
            quality="medium",
        )
    except OpenAIError as exc:
        raise AIRenderError(f"OpenAI request failed: {exc}") from exc

    try:
        b64 = response.data[0].b64_json
        if not b64:
            raise AIRenderError("OpenAI returned an empty image.")
    except (IndexError, AttributeError) as exc:
        raise AIRenderError("Unexpected response shape from OpenAI.") from exc

    try:
        base64.b64decode(b64, validate=True)
    except Exception as exc:
        raise AIRenderError("OpenAI returned invalid base64 data.") from exc

    return f"data:image/png;base64,{b64}"
