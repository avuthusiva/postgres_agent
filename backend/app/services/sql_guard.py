import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError


def validate_sql(sql: str, allowed_tables: dict[str, set[str]]) -> None:
    try:
        statements = sqlglot.parse(sql, read="postgres")
    except ParseError as exc:
        raise ValueError("The generated SQL could not be parsed.") from exc

    if len(statements) != 1 or not isinstance(statements[0], exp.Select):
        raise ValueError("Only one SELECT query is allowed.")

    query = statements[0]
    if query.find(exp.Into) or query.find(exp.Lock):
        raise ValueError("SELECT INTO and locking queries are not allowed.")

    cte_names = {
        cte.alias_or_name.lower()
        for cte in query.find_all(exp.CTE)
    }
    known_tables = {
        (schema.lower(), table.lower())
        for schema, tables in allowed_tables.items()
        for table in tables
    }

    for table in query.find_all(exp.Table):
        name = table.name.lower()
        schema = table.db.lower()
        if not schema and name in cte_names:
            continue
        if schema:
            permitted = (schema, name) in known_tables
        else:
            matches = [item for item in known_tables if item[1] == name]
            permitted = len(matches) == 1
        if not permitted:
            raise ValueError(f"Table '{table.sql()}' is not in the allowed database schema.")
