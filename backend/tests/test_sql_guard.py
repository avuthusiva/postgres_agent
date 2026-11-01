import pytest

from app.services.sql_guard import validate_sql


ALLOWED = {"public": {"customers", "orders"}}


def test_accepts_select_from_allowed_table():
    validate_sql("SELECT id FROM public.customers", ALLOWED)


def test_rejects_write_query():
    with pytest.raises(ValueError, match="Only one SELECT"):
        validate_sql("DELETE FROM public.customers", ALLOWED)


def test_rejects_multiple_statements():
    with pytest.raises(ValueError, match="Only one SELECT"):
        validate_sql("SELECT id FROM public.customers; DROP TABLE public.orders", ALLOWED)


def test_rejects_unknown_table():
    with pytest.raises(ValueError, match="not in the allowed"):
        validate_sql("SELECT * FROM public.secrets", ALLOWED)


def test_accepts_cte_using_allowed_table():
    validate_sql(
        "WITH recent AS (SELECT id FROM public.orders) SELECT id FROM recent",
        ALLOWED,
    )
