from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    embedding_model: str = "all-MiniLM-L6-v2"

    database_path: str = "data/inbox.db"

    chunk_size_chars: int = 800
    chunk_overlap_chars: int = 120

    top_k_default: int = 4

    cors_origins: str = "http://localhost:5173"

    url_fetch_timeout_seconds: float = 10.0
    max_note_chars: int = 50_000
    max_fetched_page_chars: int = 200_000

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
