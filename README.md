# CrateDB django connector.

![PyPI - Version](https://img.shields.io/pypi/v/cratedb-django)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cratedb-django)
![PyPI - License](https://img.shields.io/pypi/l/cratedb-django)
![PyPI - Status](https://img.shields.io/pypi/status/cratedb-django)
[![🛠🐍 Unit tests](https://github.com/surister/cratedb-django/actions/workflows/tests.yml/badge.svg)](https://github.com/surister/cratedb-django/actions/workflows/tests.yml)

Connector to use CrateDB as a database in Django ORM.

# Documentation
https://cratedb.com/docs/guide/integrate/django/index.html


## How to install

uv

```shell
uv add cratedb-django
```

pipx

```shell
pipx install cratedb-django
```

## Install

Once the library is installed, use it in your `settings.py`, e.g.

```python
DATABASES = {
    "default": {
        "ENGINE": "cratedb_django",
        "SERVERS": ["localhost:4200"],
    }
}
```

After that, for a model to be used in CrateDB, you need to use `CrateDBModel` as a
base class.

```python
from django.db import models
from cratedb_django.models import CrateDBModel
from cratedb_django.models import functions

class Metrics(CrateDBModel):
    id = models.TextField(primary_key=True, db_default=functions.UUID())
    value = models.IntegerField()
```

Django migrations can be run in CrateDB, default django migrations are tested.
In spite of that, we recommend that you run anything transactional in a
transactional database, like PostgresSQL and use CrateDB as your analytical database.


# License

This project is open-source under a MIT license.

