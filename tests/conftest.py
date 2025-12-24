import logging

import pytest
import os
import django
from django.db import connection
from django.apps import apps

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")
django.setup()


try:
    from django.core.management import execute_from_command_line
except ImportError as exc:
    raise ImportError(
        "Couldn't import Django. Are you sure it's installed and "
        "available on your PYTHONPATH environment variable? Did you "
        "forget to activate a virtual environment?"
    ) from exc

# Runs migrations at the beginning of every full test run, to check that migrations can run.
execute_from_command_line(["manage.py", "makemigrations"])
execute_from_command_line(["manage.py", "migrate"])

logging.info("All migrations run successfully")

# The app name to define transient Models in unittests,
# transient models don't get created in database and get
# pruned from the app registry after every test.
_CRATE_TEST_APP = "_crate_test"


@pytest.fixture(scope="function", autouse=True)
def clean_database(request):
    """
    After every test removes all the rows inserted in the table.
    """

    yield

    # This deletes the defined models after every tests,
    # enabling us to re-use the same Model name in all tests.
    if _CRATE_TEST_APP in apps.all_models:
        apps.all_models.pop(_CRATE_TEST_APP)

    models = [
        model
        for model in request.module.__dict__.values()
        if isinstance(model, django.db.models.base.ModelBase)
    ]

    for model in models:
        if model._meta.app_label != _CRATE_TEST_APP and not model._meta.abstract:
            with connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM {model._meta.db_table}")
                cursor.execute(f"REFRESH TABLE {model._meta.db_table}")


@pytest.fixture(scope="function", autouse=False)
def cleanup_migrations(request):
    """
    Removes every table created from the migrations, not necessary in CI but very useful
    in local while debugging migrations and model field creations, set autouse=True to use it.
    :return:
    """
    yield

    models = [
        model
        for model in request.module.__dict__.values()
        if isinstance(model, django.db.models.base.ModelBase)
    ]
    for model in models:
        with connection.cursor() as cursor:
            cursor.execute(f"DROP TABLE IF EXISTS {model._meta.db_table}")
