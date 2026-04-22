from fastapi import Header, HTTPException, status
from app.core.firebase_admin import verify_token


async def require_admin(authorization: str = Header(default="")) -> str:
    """Dependency that validates Firebase Bearer token and returns UID."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Bearer token")
    token = authorization.removeprefix("Bearer ")
    try:
        uid = await verify_token(token)
        return uid
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
