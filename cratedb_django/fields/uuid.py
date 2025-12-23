from django.db.models import fields


class AutoUUIDField(fields.AutoField):
    """Auto field that uses the database uuid generation function."""

    def __init__(self, **kwargs):
        from cratedb_django.models import functions

        kwargs |= {"db_default": functions.UUID()}
        super().__init__(**kwargs)

    def get_prep_value(self, value):
        return value

    def get_internal_type(self):
        return "AutoUUIDField"

    def db_type(self, connection):
        """The column type"""
        # The size of an elasticflake:
        # $ select char_length(gen_random_text_uuid())
        # 20
        return "char(20)"

    def get_default(self):
        # This makes django ignore this column in inserts, since CrateDB does not support
        # the DEFAULT keyword. https://github.com/crate/crate/issues/14575
        return None
