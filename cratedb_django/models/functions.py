from django.db.models.expressions import Func

from cratedb_django.fields import TextField


class UUID(Func):
    """https://cratedb.com/docs/crate/reference/en/latest/general/builtins/scalar-functions.html#gen-random-text-uuid"""

    function = "gen_random_text_uuid"
    output_field = TextField(
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
