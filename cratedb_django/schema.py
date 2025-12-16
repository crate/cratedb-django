import logging
import os
from typing import Sequence

from django.db.backends.base.schema import BaseDatabaseSchemaEditor

from cratedb_django.models.model import OMITTED


def check_field(model, field_name: str) -> None:
    try:
        model._meta.get_field(field_name)
    except Exception as e:
        raise ValueError(f"Column {field_name!r} does not exist in model") from e


class DatabaseSchemaEditor(BaseDatabaseSchemaEditor):
    # TODO DOCUMENT CAVEAT: IF YOU START WITH A DJANGO MIGRATIONS CREATED BY OTHER DATABASE LIKE POSTGRES,
    # NEW MIGRATIONS WITH NO-OP operations like drop constraint, might produce confusing behaviour, you might
    # expect things that will be no-op, like drop constraints.

    # TODO pgdiff
    # TODO, is this bug? why isn't supports_deferrable_unique_constraints respected on table creation?

    sql_create_unique = "select 1"

    sql_alter_column_type = "SELECT 1"
    sql_alter_column_null = "SELECT 2"
    sql_alter_column_not_null = "SELECT 3"
    sql_alter_column_default = "SELECT 4"
    sql_alter_column_no_default = "SELECT 5"

    sql_delete_column = "ALTER TABLE %(table)s DROP COLUMN %(column)s"
    sql_delete_table = "DROP TABLE %(table)s"

    def add_index(self, model, index):
        return None

    def rename_index(self, model, old_index, new_index):
        return None

    def remove_index(self, model, index):
        return None

    def add_constraint(self, model, constraint):
        return None

    def remove_constraint(self, model, constraint):
        return None

    def _model_indexes_sql(self, model):
        """
        todo pgdiff

        This overload stops django from issuing CREATE INDEX statements.
        https://forum.djangoproject.com/t/dont-issue-create-index-on-initial-migration/36227/4
        """
        return ()

    def _alter_column_null_sql(self, model, old_field, new_field):
        return ()

    def column_sql(self, model, field, include_default=False):
        if field.unique:
            # todo pgdiff
            if not os.getenv("SUPPRESS_UNIQUE_CONSTRAINT_WARNING", "false") == "true":
                logging.warning(
                    f"CrateDB does not support unique constraints but `{model}.{field}` is set as"
                    f" unique=True, it will be ignored."
                )
            field.unique = False
        return super().column_sql(
            model=model, field=field, include_default=include_default
        )

    def alter_field(self, model, old_field, new_field, strict=False):
        if old_field.get_internal_type != new_field.get_internal_type:
            # You cannot change types after table creation.
            return
        return super().alter_field(model, old_field, new_field, strict)

    def _column_generated_sql(self, field):
        """Returns the SQL to use in a GENERATED ALWAYS clause."""
        sql, params = super()._column_generated_sql(field)
        sql = sql.replace("VIRTUAL", "").replace("STORED", "")
        return sql, params

    def table_sql(self, model) -> tuple:
        sql = list(super().table_sql(model))

        partition_by = getattr(model._meta, "partition_by", OMITTED)
        if partition_by is not OMITTED:
            if not isinstance(partition_by, Sequence) or not partition_by:
                raise ValueError(
                    "partition_by has to be a non-empty sequence, e.g. ['id']"
                )
            if isinstance(partition_by, str):
                partition_by = [
                    partition_by,
                ]

            for field in partition_by:
                check_field(model, field)

            sql[0] += f" PARTITIONED BY ({", ".join(partition_by)})"

        clustered_by = getattr(model._meta, "clustered_by", OMITTED)
        if clustered_by is not OMITTED:
            if not isinstance(clustered_by, str) or not clustered_by:
                raise ValueError(
                    "clustered_by has to be a non-empty "
                    f"string, not {clustered_by!r}"
                )
            check_field(model, clustered_by)

        number_of_shards = getattr(model._meta, "number_of_shards", OMITTED)
        if number_of_shards is not OMITTED:
            if not isinstance(number_of_shards, int) or number_of_shards == 0:
                raise ValueError(
                    "number_of_shards has to be an integer "
                    f"bigger than 0, not {number_of_shards!r}"
                )

        if clustered_by and not number_of_shards:
            sql[0] += f" CLUSTERED BY ({clustered_by})"

        if clustered_by and number_of_shards:
            sql[0] += f" CLUSTERED BY ({clustered_by}) INTO {number_of_shards} shards"

        if not clustered_by and number_of_shards:
            sql[0] += f" CLUSTERED INTO ({number_of_shards})"

        return tuple(sql)
