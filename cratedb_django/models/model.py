from enum import Enum, auto

from django.db import models, connection
from django.db.models.base import ModelBase

# If a meta option has the value OMITTED, it will be omitted
# from SQL creation. bool(Omitted) resolves to False.
_OMITTED = type("OMITTED", (), {"__bool__": lambda _: False})
OMITTED = _OMITTED()


class CrateMetaOptions(Enum):
    """
    Represents the specific options a CrateDB table can have.
    """

    auto_refresh = auto(), False, False
    partition_by = auto(), OMITTED, False
    clustered_by = auto(), OMITTED, False
    number_of_shards = auto(), OMITTED, False

    def __init__(self, _, current_value, used_in_parameters_table):
        self.current_value = current_value
        self.used_in_parameters_table = used_in_parameters_table

    @staticmethod
    def options():
        return list(CrateMetaOptions.__members__)

    @classmethod
    def by_name(cls, name):
        for m in cls:
            if m.value[1] == name:
                return m
        raise KeyError(name)


class MetaCrate(ModelBase):
    def __new__(cls, name, bases, attrs, **kwargs):
        _temp_crate_attrs = {}

        # todo document

        try:
            meta = attrs["Meta"]
            for option in CrateMetaOptions:
                _temp_crate_attrs[option.name] = getattr(
                    meta, option.name, option.current_value
                )
                if hasattr(meta, option.name):
                    delattr(meta, option.name)
        except KeyError:
            # Has no meta class
            pass

        o = super().__new__(cls, name, bases, attrs, **kwargs)

        # Return back the crate_attrs we took from meta to the already
        # created object.
        for k, v in _temp_crate_attrs.items():
            setattr(o._meta, k, v)
        return o


class CrateDBModel(models.Model, metaclass=MetaCrate):
    """
    A base class for Django models with extra CrateDB specific functionality,

    Methods:
        refresh: Refreshes the given model (table)
    """

    def save(self, *args, **kwargs):
        super().save(
            *args, **kwargs
        )  # perform the actual save (insert or update)
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
