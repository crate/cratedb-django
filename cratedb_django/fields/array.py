from django.db.models import Field
from cratedb_django.fields import CrateDBBaseField


class ArrayField(CrateDBBaseField):
    """
    An array-like field.
    """

    def __init__(self, base_field: Field, **kwargs):
        # The internal type of the array, named like this to
        # be compatible with postgres driver.
        self.base_field = base_field

        super().__init__(**kwargs)

    def db_type(self, connection):
        return f"ARRAY({self.base_field.db_type(connection)})"

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs.update(
            {
                "base_field": self.base_field.clone(),
            }
        )
        return name, path, args, kwargs
