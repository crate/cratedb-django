import dataclasses

from django.test.utils import CaptureQueriesContext
from django.db import connection

from cratedb_django.models import CrateModel


@dataclasses.dataclass
class CapturedQuery:
    """Represents a query that was captured before arriving to the database."""

    _original_query: dict = dataclasses.field(repr=False)
    stmt: str = dataclasses.field(init=False)
    params: tuple = dataclasses.field(init=False)
    time: str = dataclasses.field(init=False)

    def __post_init__(self):
        _parts = self._original_query["sql"].split("-")
        self.stmt = _parts[0].split("=")[1].strip().replace("'", "")
        self.params = _parts[1].split("=")[1].strip()
        self.time = self._original_query["time"]

    def is_insert(self):
        return "insert" in self.stmt.lower()


class captured_queries(CaptureQueriesContext):
    @property
    def latest_query(self) -> CapturedQuery:
        """Returns the most recently captured query.

        Returns:
            CapturedQuery: The latest captured query.
        """
        return CapturedQuery(self.captured_queries[-1])

    @property
    def first_query(self) -> CapturedQuery:
        """Returns the first captured query."""
        return CapturedQuery(self.captured_queries[0])

    def query_at(self, index: int) -> CapturedQuery:
        """Returns the captured query at the given index.

        Args:
            index: Zero-based index into the captured queries list.

        Returns:
            CapturedQuery: The captured query at the given index.

        Raises:
            IndexError: If the index is out of range.
        """
        return CapturedQuery(self.captured_queries[index])


class SqlExtractor:
    def __init__(self, model):
        self.model = model

    def field(self, field_name: str) -> tuple[str, tuple]:
        """
        Generate the DDL fragment for a single model field.

        Parameters
        ----------
        field_name : str
            The name of the model field whose DDL should be generated.

        Returns
        -------
        tuple[str, tuple]
            A pair containing:
            - The SQL string for the column definition.
            - The parameters associated with that SQL string.
        """
        with connection.schema_editor() as schema_editor:
            sql, params = schema_editor.column_sql(
                self.model, self.model._meta.get_field(field_name)
            )
            return sql, params

    def table(self) -> tuple[str, tuple]:
        """
        Generate the full CREATE TABLE DDL for the model.

        Returns
        -------
        tuple[str, tuple]
            A pair containing:
            - The SQL statement for creating the table.
            - The parameters associated with that SQL statement.
        """
        with connection.schema_editor() as schema_editor:
            sql, params = schema_editor.table_sql(self.model)
            return sql, params


def get_sql_of(model: CrateModel) -> "SqlExtractor":
    """
    Create an SQL extractor for the given model.

    Parameters
    ----------
    model : CrateModel
        The model class whose generated DDL should be inspected.

    Examples
    --------
    >>> sql, params = get_sql_of(MyModel).table()
    >>> sql
    'CREATE TABLE "app_mymodel" (...);'

    >>> sql, params = get_sql_of(MyModel).field("id")
    >>> sql
    '"id" integer NOT NULL PRIMARY KEY'

    Returns
    -------
    SqlExtractor
        An instance exposing `field(name)` and `table()` for retrieving
        Django-generated DDL SQL and parameters.
    """
    if not isinstance(model, type) and isinstance(model, CrateModel):
        raise ValueError(
            "You passed an instance of a model, a class is expected instead. Fix: "
            'try removing "()", e.g. get_sql_of(MyModel()) -> get_sql_of(MyModel)'
        )
    return SqlExtractor(model)
