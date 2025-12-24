from cratedb_django.base import DatabaseWrapper

import pytest
from django.core.exceptions import ImproperlyConfigured


def test_get_connection_params():
    """Verify the parameters set in settings.DATABASE"""
    # Django always passes all parameters, even if empty/None.
    base_opts = {
        "ENGINE": "cratedb_django",
        "SERVERS": ["http://localhost:4200"],
        "USER": "crate",
        "OPTIONS": {},
        "ATOMIC_REQUESTS": False,
        "AUTOCOMMIT": True,
        "CONN_MAX_AGE": 0,
        "CONN_HEALTH_CHECKS": False,
        "TIME_ZONE": None,
        "NAME": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
        "TEST": {
            "CHARSET": None,
            "COLLATION": None,
            "MIGRATE": True,
            "MIRROR": None,
            "NAME": None,
        },
    }

    c = DatabaseWrapper(base_opts).get_connection_params()
    assert c["servers"] == ["http://localhost:4200"]
    assert c["username"] == "crate"
    assert c["password"] is None

    opts = dict(base_opts)
    expected_host = "http://some_host:4200"
    opts["HOST"] = expected_host
    opts["SERVERS"] = ["http://ignored:4200"]
    c = DatabaseWrapper(opts).get_connection_params()
    assert c["servers"] == [expected_host]

    opts = dict(base_opts)
    opts["SERVERS"] = []
    opts["HOST"] = ""
    with pytest.raises(ImproperlyConfigured, match=r"Missing SERVERS parameter"):
        DatabaseWrapper(opts).get_connection_params()

    opts = dict(base_opts)
    opts["PORT"] = "4200"
    with pytest.raises(ImproperlyConfigured, match=r"Unexpected 'PORT' setting"):
        DatabaseWrapper(opts).get_connection_params()

    opts = dict(base_opts)
    opts["OPTIONS"] = {"some_option": "1"}
    with pytest.raises(
        ImproperlyConfigured, match=r"Unexpected OPTIONS parameter some_option"
    ):
        DatabaseWrapper(opts).get_connection_params()

    opts = dict(base_opts)
    opts["OPTIONS"] = {"verify_ssl_cert": False}
    c = DatabaseWrapper(opts).get_connection_params()
    assert c["verify_ssl_cert"] == False

    opts = dict(base_opts)
    opts["USER"] = ""
    c = DatabaseWrapper(opts).get_connection_params()
    assert c["username"] is None
