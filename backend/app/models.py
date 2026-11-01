from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class QueryResponse(BaseModel):
    sql: str
    columns: list[str]
    rows: list[list[str | None]]
    execution_time_ms: int
    truncated: bool
