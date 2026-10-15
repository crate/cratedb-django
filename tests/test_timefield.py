import datetime
from types import SimpleNamespace
from unittest.mock import Mock
from django.db import models

import pytest

from cratedb_django.operations import DatabaseOperations


@pytest.fixture
def operations():
    return DatabaseOperations(None)


# 1. Adapting None should return None.
def test_adapt_timefield_none(operations):
    assert operations.adapt_timefield_value(None) is None


# 2. A normal time should become a datetime with the anchor date.
def test_adapt_timefield_value(operations):
    value = datetime.time(22, 43, 10, 1021)

    result = operations.adapt_timefield_value(value)

    assert result == datetime.datetime(
        1970, 1, 1, 22, 43, 10, 1021
    )


# 3. Timezone-aware time values should raise ValueError.
def test_adapt_timezone_aware_time(operations):
    value = datetime.time(
        12, 30, tzinfo=datetime.timezone.utc
    )

    with pytest.raises(
        ValueError,
        match="timezone-aware times",
    ):
        operations.adapt_timefield_value(value)


# 4. Non-time values should be returned unchanged.
def test_adapt_non_time_value(operations):
    value = "22:43:10"

    assert operations.adapt_timefield_value(value) == value


# 5. Database expressions should be returned unchanged.
def test_adapt_expression(operations):
    expression = Mock()
    expression.resolve_expression = Mock()

    result = operations.adapt_timefield_value(expression)

    assert result is expression


# 6. A None database value should remain None.
def test_convert_timefield_none(operations):
    expression = SimpleNamespace(output_field=None)

    assert operations.convert_timefield_value(
        None, expression, None
    ) is None


# 7. A datetime should be converted to its time component.
def test_convert_datetime_to_time(operations):
    value = datetime.datetime(
        2026, 10, 15, 22, 43, 10, 1021
    )
    expression = SimpleNamespace(output_field=None)

    result = operations.convert_timefield_value(
        value, expression, None
    )

    assert result == datetime.time(22, 43, 10, 1021)


# 8. Integer values should be interpreted as epoch milliseconds.



# 9. Unexpected database value types should raise TypeError.
def test_convert_unexpected_value(operations):
    expression = SimpleNamespace(output_field=None)

    with pytest.raises(
        TypeError,
        match="Unexpected value for a TimeField column",
    ):
        operations.convert_timefield_value(
            "22:43:10", expression, None
        )




# 11. The converter should be registered for TimeField expressions.
def test_timefield_converter_is_registered(operations):
    output_field = Mock()
    output_field.get_internal_type.return_value = "TimeField"
    expression = SimpleNamespace(output_field=output_field)

    converters = operations.get_db_converters(expression)

    assert operations.convert_timefield_value in converters


# 12. The converter should not be registered for other field types.
def test_converter_not_registered_for_other_fields(operations):
    output_field = Mock()
    output_field.get_internal_type.return_value = "IntegerField"
    expression = SimpleNamespace(output_field=output_field)

    converters = operations.get_db_converters(expression)

    assert operations.convert_timefield_value not in converters
def test_django_timefield_string_preparation():
    field = models.TimeField()
    result = field.to_python("22:43:10.001021")

    assert result == datetime.time(22, 43, 10, 1021)