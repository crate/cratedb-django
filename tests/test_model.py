import pytest

from cratedb_django.fields import ObjectField
from cratedb_django.fields.array import ArrayField
from cratedb_django.models import CrateModel
from cratedb_django.models.model import CRATE_META_OPTIONS

from django.forms.models import model_to_dict
from django.db import connection, models
from django.test.utils import CaptureQueriesContext

from tests.utils import captured_queries
from tests.test_app.models import AllFieldsModel, SimpleModel, RefreshModel


def test_model_refresh():
    """Test that Model.refresh() works"""
    expected_query = "refresh table test_app_simplemodel"
    with CaptureQueriesContext(connection) as ctx:
        SimpleModel.refresh()
        assert expected_query in ctx.captured_queries[0]["sql"]


def test_model_refresh_meta():
    """Test that a refresh statement is sent after updating
    or inserting when auto_refresh=True in Meta"""

    with captured_queries(connection) as ctx:
        # Test insert
        RefreshModel.objects.create(field="sometext")
        assert ctx.latest_query.stmt == "refresh table test_app_refreshmodel"


def test_model_auto_pk_value_exists():
    """Test that when we create a model object with Django created
    'id', the value gets added to the Object"""
    obj = SimpleModel.objects.create(field="test_model_auto_pk_value_exists")
    SimpleModel.refresh()
    assert obj.id
    assert obj.pk
    assert obj.id == obj.pk
    assert isinstance(obj.id, int)


def test_insert_model_field():
    """Test that we can insert a model and refresh it"""
    assert SimpleModel.objects.count() == 0
    with captured_queries(connection) as ctx:
        SimpleModel.objects.create(field="test_insert_model_field")
        assert 'INSERT INTO "test_app_simplemodel"' in ctx.latest_query.stmt

        SimpleModel.refresh()
        assert SimpleModel.objects.count() == 1


def test_update_model():
    with captured_queries(connection) as ctx:
        obj = SimpleModel.objects.create(field="text")
        pk = obj.pk
        assert obj.field == "text"

        obj.field = "sometext"
        obj.save()

        assert obj.field == "sometext"
        assert pk == obj.pk  # Pk did not change

        # TODO: If we do not refresh here it breaks, there should only be 1 record at this time
        # but there are 2, see issue: https://github.com/surister/cratedb-django/issues/7
        SimpleModel.refresh()
        # assert SimpleModel.objects.count() == 1
        # pprint.pp(ctx.captured_queries)


def test_delete_from_model():
    with captured_queries(connection) as ctx:
        assert SimpleModel.objects.count() == 0

        SimpleModel.objects.create()
        SimpleModel.refresh()

        assert SimpleModel.objects.count() == 1
        SimpleModel.objects.all().delete()
        assert ctx.latest_query.stmt == 'DELETE FROM "test_app_simplemodel"'

        SimpleModel.refresh()
        assert SimpleModel.objects.count() == 0


def test_insert_all_fields():
    """Test that an object is created and accounted
    for with all supported field types"""

    expected = {
        "id": 29147646,
        "field_int": 1,
        "field_int_unique": 2,
        "field_int_not_indexed": 3,
        "field_int_not_null": 4,
        "field_int_null": 5,
        "field_int_default": 6,
        "field_float": 0.1,
        "field_char": "somechar",
        "field_bool": True,
        # "field_date": datetime.datetime(2025, 4, 22, 0, 0, tzinfo=datetime.timezone.utc),
        # "field_datetime": datetime.datetime(1, 1, 1, 1, 1, 1, 1),
        "field_json": {"hello": "world"},
        "field_uuid": "00bde3702f844402b750c1b37d589084",
    }
    AllFieldsModel.objects.create(**expected)
    AllFieldsModel.refresh()
    assert AllFieldsModel.objects.count() == 1

    obj = AllFieldsModel.objects.get()
    assert model_to_dict(obj) == expected


def test_model_meta():
    """
    Tests that default values are properly set even when not specified
    """

    class NoMetaOptions(CrateModel):
        class Meta:
            app_label = "ignore"

    class RefreshMetaOptions(CrateModel):
        class Meta:
            app_label = "ignore"
            auto_refresh = True

    # Check all defaults are set.
    for key, default_value in CRATE_META_OPTIONS.items():
        assert key in NoMetaOptions._meta.__dict__
        assert getattr(NoMetaOptions._meta, key) is default_value

    # Check the combination of user-defined + default.
    assert RefreshMetaOptions._meta.auto_refresh is True
    assert RefreshMetaOptions._meta.partition_by is CRATE_META_OPTIONS["partition_by"]


def test_model_meta_partition_by():
    """Test partition_by option in Meta class."""

    class MetaOptions(CrateModel):
        one = models.TextField()
        two = models.TextField()
        three = models.TextField()

        class Meta:
            app_label = "ignore"
            partition_by = ["one"]

    with connection.schema_editor() as schema_editor:
        sql, params = schema_editor.table_sql(MetaOptions)
        assert "PARTITIONED BY (one)" in sql

    MetaOptions._meta.partition_by = ["one", "two", "three"]
    with connection.schema_editor() as schema_editor:
        sql, params = schema_editor.table_sql(MetaOptions)
        assert "PARTITIONED BY (one, two, three)" in sql

    MetaOptions._meta.partition_by = []
    with pytest.raises(ValueError, match="partition_by has to be a non-empty sequence"):
        with connection.schema_editor() as schema_editor:
            schema_editor.table_sql(MetaOptions)

    MetaOptions._meta.partition_by = "one"
    with connection.schema_editor() as schema_editor:
        sql, params = schema_editor.table_sql(MetaOptions)
        assert "PARTITIONED BY (one)" in sql

    MetaOptions._meta.partition_by = "missing_column"
    with pytest.raises(
        ValueError, match="Column 'missing_column' does not exist in model"
    ):
        with connection.schema_editor() as schema_editor:
            schema_editor.table_sql(MetaOptions)


def test_array_field_creation():
    from cratedb_django.fields.array import ArrayField

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


def test_array_deconstruct():
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


def test_model_id():
    """
    Tests the auto-generated id added by Django.
    """

    class SomeModel(CrateModel):
        class Meta:
            app_label = "ignore"

    assert SomeModel._meta.get_field("id")
    assert len(SomeModel._meta.fields) == 1

    with connection.schema_editor() as schema_editor:
        sql, params = schema_editor.column_sql(
            SomeModel, SomeModel._meta.get_field("id")
        )
        assert (
            sql
            == "INTEGER GENERATED ALWAYS AS CAST((random() * 1.0E9) AS integer) NOT NULL PRIMARY KEY"
        )

    class SomeModel(CrateModel):
        id = models.TextField(primary_key=True)

        class Meta:
            app_label = "ignore"

    assert SomeModel._meta.get_field("id")
    assert len(SomeModel._meta.fields) == 1

    with connection.schema_editor() as schema_editor:
        sql, params = schema_editor.column_sql(
            SomeModel, SomeModel._meta.get_field("id")
        )
        assert sql == "text NOT NULL PRIMARY KEY"
