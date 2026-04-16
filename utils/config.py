from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(
        default="postgresql+psycopg2://postgres:postgres@localhost:5432/healthcare_db",
        alias="DATABASE_URL",
    )
    raw_table_name: str = Field(default="healthcare_raw", alias="RAW_TABLE_NAME")
    processed_table_name: str = Field(default="healthcare_processed", alias="PROCESSED_TABLE_NAME")
    model_dir: Path = Field(default=Path("artifacts"), alias="MODEL_DIR")
    model_file_name: str = Field(default="best_model.joblib", alias="MODEL_FILE_NAME")
    random_state: int = Field(default=42, alias="RANDOM_STATE")


@lru_cache
def get_settings() -> Settings:
    return Settings()
