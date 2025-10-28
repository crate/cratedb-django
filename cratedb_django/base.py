import logging
import re
from collections.abc import Mapping
from itertools import tee

from crate.client.converter import DefaultTypeConverter
from crate.client.cursor import Cursor
from crate.client.connection import Connection

from django.core.exceptions import ImproperlyConfigured

from django.db.backends.base.base import BaseDatabaseWrapper
from django.utils.regex_helper import _lazy_re_compile

from .client import DatabaseClient
from .creation import DatabaseCreation
from .features import DatabaseFeatures
from .introspection import DatabaseIntrospection
from .operations import DatabaseOperations
from .schema import DatabaseSchemaEditor


def _get_varchar_column(data):
    if data["max_length"] is None:
        return "varchar"
    return "varchar(%(max_length)s)" % data


class E(Exception):
    pass


class CrateError:
    DataError = E
    OperationalError = E
    IntegrityError = E
    InternalError = E
    ProgrammingError = E
    NotSupportedError = E
    DatabaseError = E
    InterfaceError = E
    Error = E


class DatabaseWrapper(BaseDatabaseWrapper):
    vendor = "Crate.io"
    display_name = "CrateDB"
    Database = CrateError
    client_class = DatabaseClient
    creation_class = DatabaseCreation
    features_class = DatabaseFeatures
    introspection_class = DatabaseIntrospection
    ops_class = DatabaseOperations
    SchemaEditorClass = DatabaseSchemaEditor

    CRATE_SQL_SERIAL = "INTEGER GENERATED ALWAYS AS CAST((random() * 1.0E9) AS integer)"
    data_types = {
        # todo pgdiff - doc
        "AutoField": CRATE_SQL_SERIAL,
        "BigAutoField": CRATE_SQL_SERIAL,
        "SmallAutoField": CRATE_SQL_SERIAL,
        "BinaryField": "bytea",
        "BooleanField": "boolean",
        "CharField": _get_varchar_column,
        "DateField": "timestamp with time zone",
        "DateTimeField": "timestamp with time zone",
        "DecimalField": "numeric(%(max_digits)s, %(decimal_places)s)",
        "DurationField": "interval",
        "FileField": "varchar(%(max_length)s)",
        "FilePathField": "varchar(%(max_length)s)",
        "FloatField": "double precision",
        "IntegerField": "integer",
        "BigIntegerField": "bigint",
        "IPAddressField": "IP",
        "GenericIPAddressField": "inet",
        "JSONField": "object",
        "OneToOneField": "integer",
        "PositiveBigIntegerField": "bigint",
        "PositiveIntegerField": "integer",
        "PositiveSmallIntegerField": "smallint",
        "SlugField": "varchar(%(max_length)s)",
        "SmallIntegerField": "smallint",
        "TextField": "text",
        "TimeField": "time",
        "UUIDField": "text",
        "ObjectField": "OBJECT",
    }

    operators = {
        "exact": "= %s",
        "iexact": "= UPPER(%s)",
        "contains": "LIKE %s",
        "icontains": "LIKE UPPER(%s)",
        "regex": "~ %s",
        "iregex": "~* %s",
        "gt": "> %s",
        "gte": ">= %s",
        "lt": "< %s",
        "lte": "<= %s",
        "startswith": "LIKE %s",
        "endswith": "LIKE %s",
        "istartswith": "LIKE UPPER(%s)",
        "iendswith": "LIKE UPPER(%s)",
    }

    def rollback(self):
        return

    def savepoint(self):
        return

    def commit(self):
        return

    def _set_autocommit(self, autocommit):
        with self.wrap_database_errors:
            self.connection.autocommit = False  # Forcibly set autocommit to False.

    def get_connection_params(self):
        conn_params = dict(servers=self.settings_dict.get("SERVERS"))

        if self.settings_dict["HOST"]:
            conn_params["servers"] = [self.settings_dict["HOST"]]

        if self.settings_dict.get("PORT") or self.settings_dict.get("HOST"):
            raise ImproperlyConfigured(
                "Do not use 'PORT' nor 'HOST' in settings.databases, user 'SERVERS'"
            )
        return conn_params

    def get_new_connection(self, conn_params):
        return Connection(**conn_params)

    def create_cursor(self, name=None):
        return CrateDBCursorWrapper(self.connection, DefaultTypeConverter())


FORMAT_QMARK_REGEX = _lazy_re_compile(r"(?<!%)%s")


def aggressively_refresh():
    """
    Runs a refresh table statement on update statements
    """

    def deco(f):
        def wrapper(*args, **kwargs):
            func = f(*args, **kwargs)

            query = args[1].lower()
            match = re.search(r"update\s+([^\s;]+)", query, re.IGNORECASE)
            if match:
                table_name = match.group(1)
                return args[0].execute(f"refresh table {table_name}", None)
            return func

        return wrapper

    return deco


# Inspired by SQLITE driver
class CrateDBCursorWrapper(Cursor):
    """
    Django uses the "format" and "pyformat" styles, but CrateDB uses '?' question mark.

    This wrapper performs the following conversions:

    - "format" style to "qmark" style
    - "pyformat" style to "named" style

    In both cases, if you want to use a literal "%s", you'll need to use "%%s".
    """

    # todo pgdiff
    # @aggressively_refresh()
    def execute(self, query, params=None) -> None:
        if params is None:
            return super().execute(query)

        # Extract names if params is a mapping, i.e. "pyformat" style is used.
        param_names = list(params) if isinstance(params, Mapping) else None
        query = self.convert_query(query, param_names=param_names)
        logging.info(f"sent query: {query}, {params}")
        return super().execute(query, params)

    def executemany(self, query, param_list) -> int | list | None:
        # Extract names if params is a mapping, i.e. "pyformat" style is used.
        # Peek carefully as a generator can be passed instead of a list/tuple.
        peekable, param_list = tee(iter(param_list))
        if (params := next(peekable, None)) and isinstance(params, Mapping):
            param_names = list(params)
        else:
            param_names = None

        query = self.convert_query(query, param_names=param_names)
        logging.info(f"sent query: {query}")
        return super().executemany(query, param_list)

    def convert_query(self, query, *, param_names=None) -> str:
        if param_names is None:
            # Convert from "format" style to "qmark" style.
            # todo pgdiff
            return FORMAT_QMARK_REGEX.sub("?", query).replace("%%", "%")
        else:
            # Convert from "pyformat" style to "named" style.
            return query % {name: f":{name}" for name in param_names}
