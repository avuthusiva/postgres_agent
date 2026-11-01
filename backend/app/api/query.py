import logging
import time

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.db import engine
from app.models import QueryRequest, QueryResponse
from app.services.schema import get_schema_context, get_allowed_tables
from app.services.sql_generator import generate_sql
from app.services.sql_guard import validate_sql

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def run_query(request: QueryRequest) -> QueryResponse:
    if engine is None:
        raise HTTPException(status_code=503, detail="Database is not configured.")

    try:
        schema = get_schema_context()
        sql = generate_sql(request.question, schema)
        validate_sql(sql, get_allowed_tables())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    started = time.perf_counter()
    try:
        with engine.begin() as connection:
            connection.exec_driver_sql("SET TRANSACTION READ ONLY")
            connection.exec_driver_sql("SET LOCAL statement_timeout = '5000ms'")
            result = connection.exec_driver_sql(sql)
            columns = list(result.keys())
            rows = [list(row) for row in result.fetchmany(501)]
    except SQLAlchemyError as exc:
        logger.exception("Database query failed")
        raise HTTPException(
            status_code=400,
            detail="The database could not run the generated query.",
        ) from exc

    truncated = len(rows) > 500
    rows = rows[:500]
    return QueryResponse(
        sql=sql,
        columns=columns,
        rows=[[str(value) if value is not None else None for value in row] for row in rows],
        execution_time_ms=round((time.perf_counter() - started) * 1000),
        truncated=truncated,
    )
