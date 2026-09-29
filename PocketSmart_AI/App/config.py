from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PocketSmart AI"

    secret_key: str = "change-this-in-production"

    database_url: str = "sqlite:///./pocketsmart.db"

    gemini_api_key: str = ""

    gemini_model: str = "gemini-2.5-flash"

    ai_enabled: bool = True

    access_token_expire_minutes: int = 120

    max_upload_mb: int = 5

    allowed_image_types: str = (
        "image/jpeg,image/png,image/webp"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def allowed_image_type_set(self) -> set[str]:
        return {
            item.strip()
            for item in self.allowed_image_types.split(",")
            if item.strip()
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()