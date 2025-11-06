from django.db import models, connection
from django.db.models.base import ModelBase

# If a meta option has the value OMITTED, it will be omitted
# from SQL creation. bool(Omitted) resolves to False.
_OMITTED = type("OMITTED", (), {"__bool__": lambda _: False})
OMITTED = _OMITTED()

# dict of all the extra options a CrateModel Meta class has.
# (name, default_value)
CRATE_META_OPTIONS = {
    "auto_refresh": False,  # Automatically refresh a table on inserts.
    "partition_by": OMITTED,
    "clustered_by": OMITTED,
    "number_of_shards": OMITTED,
}


class MetaCrate(ModelBase):
    def __new__(cls, name, bases, attrs, **kwargs):
        crate_attrs = {}

        # todo document

        try:
            meta = attrs["Meta"]
            for key, default_value in CRATE_META_OPTIONS.items():
                crate_attrs[key] = getattr(meta, key, default_value)
                if hasattr(meta, key):
                    delattr(meta, key)
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
        if auto_refresh and self.pk:  # If self.pk is available, it's an insert.
            table_name = self._meta.db_table
            with connection.cursor() as cursor:
                cursor.execute(f"refresh table {table_name}")

    @classmethod
    def refresh(cls):
        with connection.cursor() as cursor:
            cursor.execute(f"refresh table {cls._meta.db_table}")

    class Meta:
        abstract = True
