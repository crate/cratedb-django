from tests.test_app.models import AllFieldsModel, SimpleModel, RefreshModel

from django.forms.models import model_to_dict
from django.db import connection
from django.test.utils import CaptureQueriesContext

from tests.utils import captured_queries


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
    """Test that an object is created and accounted for with all supported field types"""

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
