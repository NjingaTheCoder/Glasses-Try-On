import json
import re
from typing import Any, Tuple, Type

from pydantic_settings import BaseSettings, EnvSettingsSource, PydanticBaseSettingsSource

# These origins are always present regardless of what CORS_ORIGINS is set to.
# CORS_ORIGINS env var adds to these — it cannot remove them.
_REQUIRED_ORIGINS: list[str] = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://believable-insight-production-092d.up.railway.app",
]


def _to_async_url(url: str) -> str:
    """Normalize any Postgres URL to postgresql+asyncpg://."""
    url = re.sub(r"^postgres://", "postgresql://", url)
    if re.match(r"^postgresql://", url):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    url = re.sub(r"^postgresql\+(?!asyncpg)[^:]+://", "postgresql+asyncpg://", url)
    return url


def _merge_origins(extra: list[str]) -> list[str]:
    """Merge extra origins with the required set, preserving order, deduplicating."""
    seen: dict[str, None] = {}
    for o in _REQUIRED_ORIGINS + extra:
        seen[o] = None
    return list(seen)


class _SafeEnvSource(EnvSettingsSource):
    """
    Intercepts env var parsing before pydantic-settings calls json.loads().
    For list[str] fields, pydantic-settings tries JSON-parsing the raw string
    before any field_validator runs — this is the only safe interception point.

    For cors_origins: any origins supplied via CORS_ORIGINS are merged with
    _REQUIRED_ORIGINS so the env var can never accidentally remove localhost
    or the production frontend URL.
    """

    def prepare_field_value(
        self, field_name: str, field: Any, value: Any, value_is_complex: bool
    ) -> Any:
        if isinstance(value, str):
            if field_name == "database_url" and value:
                return _to_async_url(value.strip())

            if field_name == "cors_origins":
                v = value.strip()
                if not v:
                    extra: list[str] = []
                elif v.startswith("["):
                    extra = json.loads(v)
                else:
                    extra = [o.strip() for o in v.split(",") if o.strip()]
                return _merge_origins(extra)

        return super().prepare_field_value(field_name, field, value, value_is_complex)


class Settings(BaseSettings):
    # ── Database ────────────────────────────────────────────────────────────
    # On Railway: set DATABASE_URL via reference variable ${{Postgres.DATABASE_URL}}
    # Locally: override via .env
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5434/glasses_tryon"

    # ── CORS ────────────────────────────────────────────────────────────────
    # Default already covers local dev + production.
    # CORS_ORIGINS env var merges with this list — never replaces it.
    cors_origins: list[str] = _REQUIRED_ORIGINS

    # ── Firebase ────────────────────────────────────────────────────────────
    # Railway/production: FIREBASE_SERVICE_ACCOUNT_JSON (raw JSON string)
    # Local dev:          FIREBASE_SERVICE_ACCOUNT_BASE64 (base64-encoded JSON)
    firebase_service_account_json: str = ""
    firebase_service_account_base64: str = ""
    firebase_storage_bucket: str = ""
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
