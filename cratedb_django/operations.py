import datetime

from django.db.backends.base.operations import BaseDatabaseOperations


TIME_ANCHOR_DATE = datetime.date(1970, 1, 1)
_EPOCH = datetime.datetime(1970, 1, 1)


class DatabaseOperations(BaseDatabaseOperations):
    compiler_module = "cratedb_django.compiler"
    integer_field_ranges = {
        "SmallIntegerField": (-32768, 32767),
        "IntegerField": (-2147483648, 2147483647),
        "BigIntegerField": (-9223372036854775808, 9223372036854775806),
        "PositiveBigIntegerField": (0, 9223372036854775806),
        "PositiveSmallIntegerField": (0, 32767),
        "PositiveIntegerField": (0, 2147483647),
        "SmallAutoField": (-32768, 32767),
        "AutoField": (-2147483648, 2147483647),
        "BigAutoField": (-9223372036854775808, 9223372036854775806),
        "AutoUUIDField": (None, None),
    }

    def quote_name(self, name) -> str:
        if name.startswith('"') and name.endswith('"'):
            return name  # Quoting once is enough.
        return f'"{name}"'

    def sql_flush(
        self, style, tables, *, reset_sequences=False, allow_cascade=False
    ) -> list[str]:
        return [f"DELETE FROM {table}" for table in tables]

    def return_insert_columns(self, fields):
        """Returns the 'RETURNING...' part of the INSERT statement."""

        # We are supposed to return a (string) sql part with parameter binding and a (list) with
        # parameters, for example: ('returning ?, ?, ?', ['id1', 'id2', 'id'])
        # So the parameter binding happens at the cursor level.
        #
        # There is a bug that does not allow us to bind into the returning part of the query
        # See: https://github.com/crate/crate/issues/17813
        # until that is fixed we set everything in the sql part,
        # for example, ('returning id1, id2, id3', [])

        columns = ",".join(column.name for column in fields)
        return [f"returning {columns}", []]
    
    
    def adapt_timefield_value(self, value):
        if value is None:
            return None

        # Allow database expressions to be handled by Django.
        if hasattr(value, "resolve_expression"):
            return value
        
        if not isinstance(value, datetime.time):
            return value

        if value.utcoffset() is not None:
            raise ValueError("Django does not support timezone-aware times.")

        return datetime.datetime.combine(TIME_ANCHOR_DATE, value)

    def get_db_converters(self, expression):
        converters = super().get_db_converters(expression)

        if expression.output_field.get_internal_type() == "TimeField":
            converters.append(self.convert_timefield_value)

        return converters

    def convert_timefield_value(self, value, expression, connection):
        if value is None:
            return None

        if isinstance(value, int):
            value = _EPOCH + datetime.timedelta(milliseconds=value)

        elif not isinstance(value, datetime.datetime):
            raise TypeError(
                f"Unexpected value for a TimeField column: {type(value).__name__}"
            )

        if value.tzinfo is not None:
            value = value.astimezone(datetime.timezone.utc)

        return value.time()