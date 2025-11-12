import uuid

from django.db import connection, models
from django.forms.models import model_to_dict

from cratedb_django.fields import ObjectField
from cratedb_django.fields.array import ArrayField
from cratedb_django.models import functions

from tests.test_app.models import ArraysModel


def test_field_with_uuid_default():
    """
    Tests a Model field with a db_default of UUID
    """

    class TestModel(models.Model):
        f = models.TextField(db_default=functions.UUID())

        class Meta:
            app_label = "ignore"

    with connection.schema_editor() as schema_editor:
        sql, params = schema_editor.column_sql(
            TestModel, TestModel._meta.get_field("f")
        )
        assert sql == "text DEFAULT (gen_random_text_uuid()) NOT NULL"


def test_field_array_creation():
    class SomeModel(models.Model):
        f1 = ArrayField(models.IntegerField())
        f2 = ArrayField(ArrayField(models.CharField(max_length=120)))
        f3 = ArrayField(ArrayField(ObjectField()))

        class Meta:
            app_label = "ignore"

    with connection.schema_editor() as schema_editor:
        sql, params = schema_editor.column_sql(
            SomeModel, SomeModel._meta.get_field("f1")
        )
        assert sql == "ARRAY(integer) NOT NULL"

    with connection.schema_editor() as schema_editor:
        sql, params = schema_editor.column_sql(
            SomeModel, SomeModel._meta.get_field("f2")
        )
        assert sql == "ARRAY(ARRAY(varchar(120))) NOT NULL"

    with connection.schema_editor() as schema_editor:
        sql, params = schema_editor.column_sql(
            SomeModel, SomeModel._meta.get_field("f3")
        )
        assert sql == "ARRAY(ARRAY(OBJECT)) NOT NULL"


def test_field_array_deconstruct():
    """
    Verify deconstruct works as intended, it's primarily used to 'serialize'
    the field and deserialize in other places like migrations.
    """

    class SomeModel(models.Model):
        f = ArrayField(models.CharField())

        class Meta:
            app_label = "ignore"

    name, path, args, kwargs = SomeModel._meta.get_field("f").deconstruct()

    assert name == "f"
    assert args == []
    assert path == "cratedb_django.fields.array.ArrayField"
    assert isinstance(kwargs["base_field"], models.CharField)


def test_field_array_insert():
    """
    Verify that we can insert all array fields from python objects.
    Basic querying is also verified in this test.
    """

    expected_defaults = {
        "field_int": None,
        "field_int_not_null": [],
        "field_float": [1.23],
        "field_char": ["only_defaults"],
        "field_bool": [True],
        "field_json": [{"somekey": "some default value"}],
        "field_uuid": [uuid.uuid4(), "dd766e9d-f41d-41ef-a8b7-6762d2a25834"],
        "field_nested": [["v1", "v2"]],
    }

    obj = ArraysModel(**expected_defaults)
    obj.save()

    ArraysModel.refresh()

    queryset = ArraysModel.objects.all()
    assert len(queryset) == 1
    assert queryset[0] == obj

    d = model_to_dict(queryset[0])

    # We remove values added by the database
    d.pop("id")
    d.pop("field_int_default")

    # Convert expected defaults `field_uuid` from UUID to str,
    # which is what django returns.
    expected_defaults["field_uuid"] = list(map(lambda x: str(x), d["field_uuid"]))
    assert d == expected_defaults
