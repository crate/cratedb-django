from django.db.models.sql.compiler import (
    SQLCompiler,  # noqa: F401 Import needed for re-imports.
)

from django.db.models.sql.compiler import (
    SQLInsertCompiler,
    SQLUpdateCompiler,
    SQLAggregateCompiler,
    SQLDeleteCompiler,
)


class SQLInsertCompiler(SQLInsertCompiler):
    pass


class SQLDeleteCompiler(SQLDeleteCompiler):
    pass


class SQLUpdateCompiler(SQLUpdateCompiler):
    pass


class SQLAggregateCompiler(SQLAggregateCompiler):
    pass
