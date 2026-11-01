from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from app.config import settings

engine: Engine | None = (
    create_engine(settings.database_url, pool_pre_ping=True)
    if settings.database_url
    else None
)
