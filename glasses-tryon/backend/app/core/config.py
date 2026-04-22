import json
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@127.0.0.1:5434/glasses_tryon"
    firebase_service_account_base64: str = ""
    cors_origins: list[str] = [
        "http://localhost:5173",
        "https://believable-insight-production-092d.up.railway.app",
    ]
    openai_api_key: str = ""
    openai_image_model: str = "gpt-image-1"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: object) -> object:
        if not isinstance(v, str):
            return v
        v = v.strip()
        if not v:
            return []
        if v.startswith("["):
            return json.loads(v)
        return [origin.strip() for origin in v.split(",") if origin.strip()]


settings = Settings()
