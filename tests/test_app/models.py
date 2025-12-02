import datetime, uuid


from cratedb_django import fields
from cratedb_django.models import CrateModel

"""
We need to register the models here so they get correctly configured and
detected by django.
"""


class AllFieldsModel(CrateModel):
    field_int = fields.IntegerField(unique=False)
    field_int_unique = fields.IntegerField(unique=True)
    field_int_not_indexed = fields.IntegerField(db_index=False)
    field_int_not_null = fields.IntegerField(null=False)
    field_int_null = fields.IntegerField(null=True)
    field_int_default = fields.IntegerField(default=54321)
    field_float = fields.FloatField()
    field_char = fields.CharField(max_length=100)
    field_bool = fields.BooleanField()
    field_json = fields.ObjectField(default=dict)
    field_uuid = fields.UUIDField()

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
    field_int = fields.ArrayField(base_field=fields.IntegerField(), null=True)
    field_int_not_null = fields.ArrayField(
        fields.IntegerField(), null=False, default=[]
    )
    field_int_default = fields.ArrayField(fields.IntegerField(), default=[123, 321])
    field_float = fields.ArrayField(fields.FloatField())
    field_char = fields.ArrayField(fields.CharField(max_length=100))
    field_bool = fields.ArrayField(fields.BooleanField())
    field_json = fields.ArrayField(fields.ObjectField())
    field_uuid = fields.ArrayField(fields.UUIDField())
    field_nested = fields.ArrayField(fields.ArrayField(fields.CharField()))

    class Meta:
        app_label = "test_app"


class SimpleModel(CrateModel):
    field = fields.TextField()

    class Meta:
        app_label = "test_app"


class RefreshModel(CrateModel):
    field = fields.TextField()

    class Meta:
        app_label = "test_app"
        auto_refresh = True
