import json
from typing import Any, Tuple, Type

from pydantic_settings import BaseSettings, EnvSettingsSource, PydanticBaseSettingsSource


class _SafeEnvSource(EnvSettingsSource):
    """
    Patches EnvSettingsSource so that list[str] fields (e.g. cors_origins)
    accept empty strings and comma-separated values without crashing.

    pydantic-settings calls json.loads() on complex-typed env vars *before*
    any pydantic field_validator runs, so the only safe interception point is
    here, in the source layer.
    """

    _LIST_FIELDS = {"cors_origins"}

    def prepare_field_value(
        self, field_name: str, field: Any, value: Any, value_is_complex: bool
    ) -> Any:
        if field_name in self._LIST_FIELDS and isinstance(value, str):
            v = value.strip()
            if not v:
                return "[]"                                  # empty → empty list
            if v.startswith("["):
                return v                                     # already JSON array
            # comma-separated → JSON array
            items = [o.strip() for o in v.split(",") if o.strip()]
            return json.dumps(items)
        return super().prepare_field_value(field_name, field, value, value_is_complex)


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
            _SafeEnvSource(settings_cls),   # replaces stock env_settings
            dotenv_settings,
            file_secret_settings,
        )


settings = Settings()
