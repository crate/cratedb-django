import logging

from django.db.models import fields, JSONField
from django.db.models.fields.generated import GeneratedField

from .base import CrateDBBaseField
from .json import ObjectField
from .array import ArrayField


class AutoField(CrateDBBaseField, fields.AutoField):
    pass


class BigAutoField(CrateDBBaseField, fields.BigAutoField):
    pass


class BigIntegerField(CrateDBBaseField, fields.BigIntegerField):
    pass


class BinaryField(CrateDBBaseField, fields.BinaryField):
    pass


class BooleanField(CrateDBBaseField, fields.BooleanField):
    pass


class CharField(CrateDBBaseField, fields.CharField):
    pass


class DateField(CrateDBBaseField, fields.DateField):
    pass


class DateTimeField(CrateDBBaseField, fields.DateTimeField):
    pass


class DecimalField(CrateDBBaseField, fields.DecimalField):
    pass


class DurationField(CrateDBBaseField, fields.DurationField):
    pass


class EmailField(CrateDBBaseField, fields.EmailField):
    pass


class FloatField(CrateDBBaseField, fields.FloatField):
    pass


class GeneratedField(CrateDBBaseField, GeneratedField):
    def __init__(self, *args, **kwargs):
        virtual = kwargs.get("db_persist")
        if virtual:
            logging.warning(
                f"{self} has db_persist=True, but CrateDB does not support virtual generated columns."
                f"`db_persist` will be ignored."
            )

        # Always set it as False because the default is None.
        kwargs["db_persist"] = False

        super().__init__(*args, **kwargs)


class GenericIPAddressField(CrateDBBaseField, fields.GenericIPAddressField):
    pass


class IntegerField(CrateDBBaseField, fields.IntegerField):
    pass


class PositiveBigIntegerField(CrateDBBaseField, fields.PositiveBigIntegerField):
    pass


class PositiveIntegerField(CrateDBBaseField, fields.PositiveIntegerField):
    pass


class PositiveSmallIntegerField(CrateDBBaseField, fields.PositiveSmallIntegerField):
    pass


class SlugField(CrateDBBaseField, fields.SlugField):
    pass


class SmallAutoField(CrateDBBaseField, fields.SmallAutoField):
    pass


class SmallIntegerField(CrateDBBaseField, fields.SmallIntegerField):
    pass


class TextField(CrateDBBaseField, fields.TextField):
    pass


class TimeField(CrateDBBaseField, fields.TimeField):
    pass


class URLField(CrateDBBaseField, fields.URLField):
    pass


class JSONField(CrateDBBaseField, JSONField):
    pass


class UUIDField(CrateDBBaseField, fields.UUIDField):
    """
    Represents a UUID field, the database will not generate a value the field just validates
    the expected length of an UUID, to automatically add a value upon object creation use
    the `default` parameter.

    Examples
    --------
    >>> UUIDField(default=uuid.uuid4)

    To use a CrateDB generated uuid use a `CharField` with `db_default=functions.UUID`, see
    TODO [doc]
    """

    pass


__all__ = [
    "ObjectField",
    "ArrayField",
    "AutoField",
    "BigAutoField",
    "BigIntegerField",
    "BinaryField",
    "BooleanField",
    "CharField",
    "DateField",
    "DateTimeField",
    "DecimalField",
    "DurationField",
    "EmailField",
    "FloatField",
    "GeneratedField",
    "GenericIPAddressField",
    "IntegerField",
    "PositiveBigIntegerField",
    "PositiveIntegerField",
    "PositiveSmallIntegerField",
    "SlugField",
    "SmallAutoField",
    "SmallIntegerField",
    "TextField",
    "TimeField",
    "URLField",
    "JSONField",
    "UUIDField",
]
