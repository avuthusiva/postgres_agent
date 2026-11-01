from sqlalchemy import bindparam, text

from app.config import settings
from app.db import engine


def _require_engine():
    if engine is None:
        raise ValueError("Database is not configured. Set DATABASE_URL in backend/.env.")
    return engine


def get_schema_context() -> str:
    db_engine = _require_engine()
    statement = text(
        """
        SELECT table_schema, table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema IN :schemas
        ORDER BY table_schema, table_name, ordinal_position
        """
    ).bindparams(bindparam("schemas", expanding=True))
    with db_engine.connect() as connection:
        rows = connection.execute(statement, {"schemas": settings.allowed_schemas}).all()

    if not rows:
        raise ValueError(
            "No visible tables were found in ALLOWED_SCHEMAS. Check the schema name and database permissions."
        )

    grouped: dict[str, list[str]] = {}
    for schema, table, column, data_type in rows:
        grouped.setdefault(f"{schema}.{table}", []).append(f"{column} ({data_type})")
    return "\n".join(
        f"{table}: {', '.join(columns)}" for table, columns in grouped.items()
    )


def get_allowed_tables() -> dict[str, set[str]]:
    db_engine = _require_engine()
    statement = text(
        """
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_schema IN :schemas
          AND table_type IN ('BASE TABLE', 'VIEW', 'FOREIGN')
        """
    )
    statement = statement.bindparams(bindparam("schemas", expanding=True))
    with db_engine.connect() as connection:
        rows = connection.execute(statement, {"schemas": settings.allowed_schemas}).all()
    return {
        schema: {table for row_schema, table in rows if row_schema == schema}
        for schema in settings.allowed_schemas
    }
