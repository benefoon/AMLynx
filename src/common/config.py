from pydantic import BaseSettings, PostgresDsn
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "AMLynx"
    database_url: PostgresDsn
    env: str = "development"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
