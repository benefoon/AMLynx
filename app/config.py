from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-ax')

    DATABASE_URL: str = "sqlite:///./amlynx.db"
    LOG_LEVEL: str = "INFO"
    
    # Add other configurations here
    KAFKA_BOOTSTRAP_SERVERS: str | None = None
    KAFKA_TOPIC: str | None = None


@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
