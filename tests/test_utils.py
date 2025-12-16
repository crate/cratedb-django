from django.db import connection

from cratedb_django.fields import TextField
from cratedb_django.models import CrateModel
from tests.utils import captured_queries
from tests.utils import get_sql_of


def test_captured_queries():
    with captured_queries(connection) as ctx:
        connection.cursor().execute("select 1")
        connection.cursor().execute("select 2")
        connection.cursor().execute("select 3")

        assert ctx.first_query.stmt == "select 1"
        assert ctx.query_at(1).stmt == "select 2"
        assert ctx.latest_query.stmt == "select 3"


def test_get_sql_of():
    class SomeModel(CrateModel):
        f = TextField()

        class Meta:
            app_label = "_crate_test"

    # We cannot ensure that get_sql_of SQL is correct, but at least that
    # it returns some kind of SQL looking string.
    sql, params = get_sql_of(SomeModel).table()
    assert isinstance(sql, str)
    assert isinstance(params, list)
    assert "CREATE TABLE" in sql

    sql, params = get_sql_of(SomeModel).field("f")
    assert isinstance(sql, str)
    assert isinstance(params, list)
    assert "text" in sql
