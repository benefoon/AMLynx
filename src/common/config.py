from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # App
    APP_NAME: str = "AMLynx"
    ENV: str = "dev"

    # DB
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "amlynx"
    DB_USER: str = "amlynx"
    DB_PASSWORD: str = "amlynx"

    # ML
    MODEL_DIR: str = "models"
    CONTAMINATION: float = 0.01
    IFOREST_TREES: int = 300
    RANDOM_STATE: int = 42

    # Rules
    RULES_PATH: str = "rules.yaml"
    RULES_WEIGHT: float = 0.6
    ANOMALY_WEIGHT: float = 0.4
    ALERT_THRESHOLD: float = 0.85

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def db_url(self) -> str:
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

@lru_cache
def get_settings() -> Settings:
    return Settings()
