from django.db.backends.base.operations import BaseDatabaseOperations


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
