from cratedb_django.fields import JSONField


class ObjectField(JSONField):
    def from_db_value(self, value, expression, connection):
        return value

    def get_internal_type(self):
        return "ObjectField"
