import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

def _csv_setting(name: str, default: str) -> list[str]:
    return [value.strip() for value in os.getenv(name, default).split(",") if value.strip()]


@dataclass(frozen=True)
class Settings:
    database_url: str
    openai_api_key: str
    openai_model: str
    allowed_schemas: list[str]
    frontend_origins: list[str]


settings = Settings(
    database_url=os.getenv("DATABASE_URL", ""),
    openai_api_key=os.getenv("OPENAI_API_KEY", ""),
    openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    allowed_schemas=_csv_setting("ALLOWED_SCHEMAS", "public"),
    frontend_origins=_csv_setting("FRONTEND_ORIGINS", "http://localhost:5173"),
)
