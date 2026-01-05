from django.db.models.expressions import Func

from cratedb_django import fields


class LiteralKeywordMixin:
    """
    Returns the `function` as a keyword literal as opposed to a function. This
    is compatible as a `db_default` and as an expression in generated fields.

    Useful for easily creating scalar functions with just a name, for example:
    `current_date` or `current_timestamp`
    """

    def db_default(self):
        return self.function

    def resolve_expression(
        self,
        query=None,
        allow_joins=True,
        reuse=None,
        summarize=False,
        for_save=False,
    ):
        members = {"as_sql": lambda *_: (self.function, [])}
        return type("LiteralKeyword", (), members)


class UUID(Func):
    """https://cratedb.com/docs/crate/reference/en/latest/general/builtins/scalar-functions.html#gen-random-text-uuid"""

    function = "gen_random_text_uuid"
    output_field = fields.TextField(
        max_length=20
    )  # the length of a CrateDB random uid.


class Abs(Func):
    """
    https://cratedb.com/docs/crate/reference/en/latest/general/builtins/scalar-functions.html#abs
    """

    function = "abs"


class Upper(Func):
    """
    https://cratedb.com/docs/crate/reference/en/latest/general/builtins/scalar-functions.html#upper
    """

    function = "upper"


class Lower(Func):
    """
    https://cratedb.com/docs/crate/reference/en/latest/general/builtins/scalar-functions.html#lower
    """

    function = "lower"


class Reverse(Func):
    """
    https://cratedb.com/docs/crate/reference/en/latest/general/builtins/scalar-functions.html#reverse
    """

    function = "reverse"


class CURRENT_DATE(LiteralKeywordMixin, Func):
    """
    https://cratedb.com/docs/crate/reference/en/latest/general/builtins/scalar-functions.html#current-date
    """

    function = "CURRENT_DATE"
    output_field = fields.CharField()

