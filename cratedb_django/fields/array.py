from django.db.models import Field, CharField


class ArrayField(Field):
    def __init__(self, base_field: Field, **kwargs):
        # The internal type, called like this to
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
