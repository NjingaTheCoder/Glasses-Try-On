from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@127.0.0.1:5434/glasses_tryon"
    firebase_service_account_base64: str = ""
    cors_origins: list[str] = ["http://localhost:5173"]
    openai_api_key: str = ""
    openai_image_model: str = "gpt-image-1"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
