from django.db.models import Field


class CrateDBBaseField(Field):
    """
    Base field for CrateDB columns, it implements crate specific
    column options.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Defaults to True because by default CrateDB indexes everything.
        # On `True` we do not modify the syntax.
        self.db_index = kwargs.get("db_index", True)

    def db_type(self, connection):
        base_type = super().db_type(connection)
        if not self.db_index:
            return f"{base_type} INDEX OFF"
        return base_type


    def deconstruct(self):
        """
        Make `index_db` show up in migrations so it round-trips correctly.
        """
        name, path, args, kwargs = super().deconstruct()
        kwargs["db_index"] = self.db_index
        return name, path, args, kwargs