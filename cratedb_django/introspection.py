import crate.client.cursor
from django.db.backends.base.introspection import (
    BaseDatabaseIntrospection,
    TableInfo,
)


class DatabaseIntrospection(BaseDatabaseIntrospection):
    ignored_tables = []

    def get_table_list(self, cursor: crate.client.cursor.Cursor):
        cursor.execute(
            """
            SELECT
              table_name,
              CASE
                when table_type = 'VIEW' then 'v'
                ELSE 't'
              END
            FROM
              "information_schema"."tables"
            """
        )

        return [
            TableInfo(*row)
            for row in cursor.fetchall()
            if row[0] not in self.ignored_tables
        ]
