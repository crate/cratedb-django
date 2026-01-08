from django.db.models import Field


class CrateDBBaseField(Field):
    """
    Base field for CrateDB columns, it implements crate specific
    column options.
    """

    def __init__(self, *args, **kwargs):
        self.column_store = kwargs.pop("column_store", True)
        super().__init__(*args, **kwargs)

        # CrateDB indexes everything by default
        self.db_index = kwargs.get("db_index", True)

    def db_type(self, connection):
        base_type = super().db_type(connection)

        if not self.db_index:
            base_type += " INDEX OFF"

        # column store has to go AFTER index.
        if not self.column_store:
            base_type += " STORAGE WITH(columnstore = false)"
        return base_type

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["db_index"] = self.db_index
        return name, path, args, kwargs
