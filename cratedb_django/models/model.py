from django.db import models, connection
from django.db.models.base import ModelBase

# Tuple of all the extra options a CrateModel Meta class has.
# (name, default_value)
CRATE_META_OPTIONS = (
    ("auto_refresh", False),  # Automatically refresh a table on inserts.
)


class MetaCrate(ModelBase):
    def __new__(cls, name, bases, attrs, **kwargs):
        crate_attrs = {}

        # todo document

        try:
            meta = attrs["Meta"]
            for crate_attr in CRATE_META_OPTIONS:
                attr_name = crate_attr[0]
                if hasattr(meta, attr_name):
                    crate_attrs[attr_name] = meta.__dict__[attr_name]
                    delattr(meta, attr_name)

        except KeyError:
            # Has no meta class
            pass

        o = super().__new__(cls, name, bases, attrs, **kwargs)

        # Return back the crate_attrs we took from meta to the already
        # created object.
        for k, v in crate_attrs.items():
            setattr(o._meta, k, v)
        return o


class CrateModel(models.Model, metaclass=MetaCrate):
    """
    A base class for Django models with extra CrateDB specific functionality,

    Methods:
        refresh: Refreshes the given model (table)
    """

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # perform the actual save (insert or update)
        auto_refresh = getattr(self._meta, "auto_refresh", False)
        if auto_refresh and self.pk:  # If self.pk is available, its an insert.
            table_name = self._meta.db_table
            with connection.cursor() as cursor:
                cursor.execute(f"refresh table {table_name}")

    @classmethod
    def refresh(cls):
        with connection.cursor() as cursor:
            cursor.execute(f"refresh table {cls._meta.db_table}")

    class Meta:
        abstract = True
