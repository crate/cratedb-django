from django.db.models.expressions import Func

from cratedb_django.fields import TextField


class UUID(Func):
    """https://cratedb.com/docs/crate/reference/en/latest/general/builtins/scalar-functions.html#gen-random-text-uuid"""

    function = "gen_random_text_uuid"
    output_field = TextField(
        max_length=20
    )  # the length of a CrateDB random uid.


class Abs(Func):
    """https://cratedb.com/docs/crate/reference/en/latest/general/builtins/scalar-functions.html#abs-number"""

    function = "abs"


class Upper(Func):
    """https://cratedb.com/docs/crate/reference/en/latest/general/builtins/scalar-functions.html#upper-string"""

    function = "upper"


class Lower(Func):
    """https://cratedb.com/docs/crate/reference/en/latest/general/builtins/scalar-functions.html#lower-string"""

    function = "lower"


class Reverse(Func):
    """https://cratedb.com/docs/crate/reference/en/latest/general/builtins/scalar-functions.html#reverse-text"""

    function = "reverse"


class Concat(Func):
    """https://cratedb.com/docs/crate/reference/en/latest/general/builtins/scalar-functions.html#concat-first-arg-second-arg-parameter"""

    function = "concat"


class ConcatWs(Func):
    """https://cratedb.com/docs/crate/reference/en/latest/general/builtins/scalar-functions.html#concat-ws-separator-second-arg-parameter"""

    function = "concat_ws"


class Format(Func):
    """https://cratedb.com/docs/crate/reference/en/latest/general/builtins/scalar-functions.html#format-format-string-parameter-parameter"""

    function = "format"
