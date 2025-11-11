import datetime, uuid

from django.db import models

from cratedb_django.fields import ObjectField
from cratedb_django.fields.array import ArrayField
from cratedb_django.models import CrateModel

"""
We need to register the models here so they get correctly configured and
detected by django.
"""


class AllFieldsModel(CrateModel):
    field_int = models.IntegerField(unique=False)
    field_int_unique = models.IntegerField(unique=True)
    field_int_not_indexed = models.IntegerField(db_index=False)
    field_int_not_null = models.IntegerField(null=False)
    field_int_null = models.IntegerField(null=True)
    field_int_default = models.IntegerField(default=54321)
    field_float = models.FloatField()
    field_char = models.CharField(max_length=100)
    field_bool = models.BooleanField()
    field_json = ObjectField(default=dict)
    field_uuid = models.UUIDField()

    @classmethod
    def create_dummy(cls):
        return cls.objects.create(
            field_int=1,
            field_int_unique=2,
            field_int_not_indexed=3,
            field_int_not_null=4,
            field_int_null=5,
            field_int_default=6,
            field_float=0.1,
            field_char="somechar",
            field_bool=True,
            field_date=datetime.datetime.today().date(),
            field_datetime=datetime.datetime.today(),
            field_json={"hello": "world"},
            field_uuid=uuid.uuid4(),
        )

    class Meta:
        app_label = "test_app"


class ArraysModel(CrateModel):
    field_int = ArrayField(base_field=models.IntegerField(), null=True)
    field_int_not_null = ArrayField(models.IntegerField(), null=False, default=[])
    field_int_default = ArrayField(models.IntegerField(), default=[123, 321])
    field_float = ArrayField(models.FloatField())
    field_char = ArrayField(models.CharField(max_length=100))
    field_bool = ArrayField(models.BooleanField())
    field_json = ArrayField(ObjectField())
    field_uuid = ArrayField(models.UUIDField())
    field_nested = ArrayField(ArrayField(models.CharField()))

    class Meta:
        app_label = "test_app"


class SimpleModel(CrateModel):
    field = models.TextField()

    class Meta:
        app_label = "test_app"


class RefreshModel(CrateModel):
    field = models.TextField()

    class Meta:
        app_label = "test_app"
        auto_refresh = True
