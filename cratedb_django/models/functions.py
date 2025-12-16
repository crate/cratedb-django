from django.db.models.expressions import Func

from cratedb_django.fields import TextField

"""
class SomeModel(CrateModel):
    id = models.TextField(primary_key=True, db_default=UUID())
    some = models.TextField()
"""


class UUID(Func):
    """https://cratedb.com/docs/crate/reference/en/latest/general/builtins/scalar-functions.html#gen-random-text-uuid"""

    function = "gen_random_text_uuid"
    output_field = TextField(max_length=20)  # the length of a CrateDB random uid.
