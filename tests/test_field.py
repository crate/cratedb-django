import uuid

from django.db import connection, models
from django.db.models import F
from django.forms.models import model_to_dict

from cratedb_django.fields import CharField
from cratedb_django.models import CrateModel
from cratedb_django.models import functions
from cratedb_django import fields
from cratedb_django.models.functions import UUID
from tests.test_app.models import ArraysModel
from tests.test_app.models import GeneratedModel

from tests.utils import get_sql_of


def test_field_with_uuid_default():
    """
    Tests a Model field with a db_default of UUID
    """

    class TestModel(models.Model):
        f = fields.TextField(db_default=functions.UUID())

        class Meta:
            app_label = "_crate_test"

    with connection.schema_editor() as schema_editor:
        sql, params = schema_editor.column_sql(
            TestModel, TestModel._meta.get_field("f")
        )
        assert sql == "text DEFAULT (gen_random_text_uuid()) NOT NULL"


def test_field_array_creation():
    class SomeModel(CrateModel):
        f1 = fields.ArrayField(fields.IntegerField())
        f2 = fields.ArrayField(fields.ArrayField(fields.CharField(max_length=120)))
        f3 = fields.ArrayField(fields.ArrayField(fields.ObjectField()))

        class Meta:
            app_label = "_crate_test"

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
        assert sql == "ARRAY(ARRAY(OBJECT(dynamic))) NOT NULL"


def test_field_array_deconstruct():
    """
    Verify deconstruct works as intended, it's primarily used to 'serialize'
    the field and deserialize in other places like migrations.
    """

    class SomeModel(CrateModel):
        f = fields.ArrayField(fields.CharField())

        class Meta:
            app_label = "_crate_test"

    name, path, args, kwargs = SomeModel._meta.get_field("f").deconstruct()

    assert name == "f"
    assert args == []
    assert path == "cratedb_django.fields.array.ArrayField"
    assert isinstance(kwargs["base_field"], fields.CharField)


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

    # Convert expected defaults `field_uuid` from UUID to `str`,
    # which is what django returns.
    expected_defaults["field_uuid"] = list(map(lambda x: str(x), d["field_uuid"]))
    assert d == expected_defaults


def test_array_deconstruct():
    """
    Verify deconstruct works as intended, it's primarily used to 'serialize'
    the field and deserialize in other places like migrations.
    """

    class SomeModel(CrateModel):
        f = fields.ArrayField(fields.CharField())

        class Meta:
            app_label = "_crate_test"

    name, path, args, kwargs = SomeModel._meta.get_field("f").deconstruct()

    assert name == "f"
    assert args == []
    assert path == "cratedb_django.fields.array.ArrayField"
    assert isinstance(kwargs["base_field"], models.CharField)


def test_generated_field():
    """
    Verify that a generated field works in CrateDB.
    """

    class SomeModel(CrateModel):
        f1 = fields.IntegerField()
        f2 = fields.IntegerField()
        f = fields.GeneratedField(
            expression=F("f1") / F("f2"), output_field=models.IntegerField()
        )
        ff = fields.GeneratedField(
            expression=F("f1") + 1, output_field=models.IntegerField(), db_persist=False
        )
        f_func = fields.GeneratedField(
            expression=UUID(), output_field=models.CharField(max_length=120)
        )

        class Meta:
            app_label = "_crate_test"

    sql, params = get_sql_of(SomeModel).field("f")
    assert sql.strip() == 'integer GENERATED ALWAYS AS (("f1" / "f2"))'
    assert not params

    # db_persist should be ignored.
    sql, params = get_sql_of(SomeModel).field("ff")
    assert sql.strip() == 'integer GENERATED ALWAYS AS (("f1" + %s))'
    assert params == [
        1,
    ]

    sql, params = get_sql_of(SomeModel).field("f_func")
    assert sql.strip() == "varchar(120) GENERATED ALWAYS AS (gen_random_text_uuid())"
    assert not params


def test_insert_generated_field():
    """Verify a real insert with many generated fields"""
    obj = GeneratedModel.objects.create(f1=1, f2=2)
    assert obj.f == 0
    assert obj.ff == 2
    assert obj.f_func


def test_object_field_creation():
    """Verifies that ObjectField applies correctly the column policy"""

    class SomeModel(CrateModel):
        f = fields.ObjectField()
        f1 = fields.ObjectField(policy="ignored")
        f2 = fields.ObjectField(
            policy="strict",
            schema={
                "name": CharField(max_length=None),
                "obj": fields.ObjectField(
                    policy="strict", schema={"age": fields.IntegerField()}
                ),
            },
        )

        class Meta:
            app_label = "_crate_test"

    sql, params = get_sql_of(SomeModel).field("f")
    assert sql == "OBJECT(dynamic) NOT NULL"

    sql, params = get_sql_of(SomeModel).field("f1")
    assert sql == "OBJECT(ignored) NOT NULL"

    sql, params = get_sql_of(SomeModel).field("f2")
    assert (
        sql
        == "OBJECT(strict) as (name varchar,obj OBJECT(strict) as (age integer)) NOT NULL"
    )


def test_uuid_field():
    """Verify that UUIDField sets the expected character size"""

    class SomeModel(CrateModel):
        f = fields.UUIDField()

        class Meta:
            app_label = "_crate_test"

    sql, params = get_sql_of(SomeModel).field("f")
    assert sql == "varchar(36) NOT NULL"
