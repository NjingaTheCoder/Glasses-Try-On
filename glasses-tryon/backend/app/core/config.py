import json
import re
from typing import Any, Tuple, Type

from pydantic_settings import BaseSettings, EnvSettingsSource, PydanticBaseSettingsSource


def _to_async_url(url: str) -> str:
    """Normalize any Postgres URL to postgresql+asyncpg://."""
    url = re.sub(r"^postgres://", "postgresql://", url)
    if re.match(r"^postgresql://", url):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    url = re.sub(r"^postgresql\+(?!asyncpg)[^:]+://", "postgresql+asyncpg://", url)
    return url


class _SafeEnvSource(EnvSettingsSource):
    """
    Intercepts env var parsing before pydantic-settings calls json.loads().
    For list[str] fields, pydantic-settings tries JSON-parsing the raw string
    before any field_validator runs — this is the only safe interception point.
    """

    def prepare_field_value(
        self, field_name: str, field: Any, value: Any, value_is_complex: bool
    ) -> Any:
        if isinstance(value, str):
            if field_name == "database_url" and value:
                return _to_async_url(value)
            if field_name == "cors_origins":
                v = value.strip()
                if not v:
                    return []
                if v.startswith("["):
                    return json.loads(v)
                return [o.strip() for o in v.split(",") if o.strip()]
        return super().prepare_field_value(field_name, field, value, value_is_complex)


class Settings(BaseSettings):
    # ── Database ────────────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/glasses_tryon"

    # ── CORS ────────────────────────────────────────────────────────────────
    cors_origins: list[str] = [
        "http://localhost:5173",
        "https://believable-insight-production-092d.up.railway.app",
    ]

    # ── Firebase ────────────────────────────────────────────────────────────
    # Railway/production: set FIREBASE_SERVICE_ACCOUNT_JSON (raw JSON string)
    # Local dev legacy: set FIREBASE_SERVICE_ACCOUNT_BASE64 (base64-encoded JSON)
    firebase_service_account_json: str = ""
    firebase_service_account_base64: str = ""
    firebase_storage_bucket: str = ""   # e.g. "wearlen.appspot.com"
    firebase_project_id: str = ""

    # ── OpenAI ──────────────────────────────────────────────────────────────
    openai_api_key: str = ""
    openai_image_model: str = "gpt-image-1"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            _SafeEnvSource(settings_cls),
            dotenv_settings,
            file_secret_settings,
        )


settings = Settings()
