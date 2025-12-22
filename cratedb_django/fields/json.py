from enum import StrEnum
from enum import auto
from typing import Literal
from typing import Optional


from cratedb_django.fields import CrateDBBaseField
from cratedb_django.fields import JSONField


class ObjectPolicy(StrEnum):
    strict = auto()
    dynamic = auto()
    ignored = auto()


class ObjectField(JSONField):
    crate_type = "OBJECT"

    def __init__(
        self,
        policy: Literal["strict", "dynamic", "ignored"] = "dynamic",
        schema: Optional[dict[str, CrateDBBaseField]] = None,
        *args,
        **kwargs,
    ):
        self.policy = ObjectPolicy(policy)
        self.schema = schema
        super().__init__(*args, **kwargs)

    def db_type(self, connection):
        sql = f"{self.crate_type}({self.policy})"

        if self.policy == ObjectPolicy.strict:
            sql += f" as ({self._to_dml_schema(connection, self.schema)})"
        return sql

    def _to_dml_schema(
        self, connection, schema: dict[str, CrateDBBaseField], sql: str = None
    ) -> str:
        """Returns the DDL of the given schema"""
        sql = sql or ""
        for field_nam, field in schema.items():
            field_ddl = (
                self._to_dml_schema(connection, sql=sql, schema=field)
                if isinstance(field, dict)
                else field.db_type(connection=connection)
            )
            sql += f"""{field_nam} {field_ddl},"""

        # Removes the semicolon in the latest column definition
        sql = sql[: len(sql) - 1] if sql.endswith(",") else sql
        return sql

    def from_db_value(self, value, expression, connection):
        return value

    def get_internal_type(self):
        return "ObjectField"
