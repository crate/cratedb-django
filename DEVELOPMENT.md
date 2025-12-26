# cratedb-django development guide.

This document contains all necessary instructions to get a working local development environment.
The easiest and preferred way to work on the project is using [uv](https://docs.astral.sh/uv/getting-started/).

## Clone the project

```shell
git clone https://github.com/surister/cratedb-django
```

## Install dependencies
```shell
uv sync
```

## Run tests
Django's default migrations are run against a CrateDB instance everytime the tests are run. Additionally,
many ORM's features depend on requesting some database metadata or construction a correct connection hence
it's **expected to have a running database instance that your local environment can have access to**.

The test database credentials can be set at `tests.settings.DATABASE`, the default value is `["localhost:4200"]`.

```shell
uv run pytest
```

## Lint

```bash
uv run ruff check .
```

## Build

```shell
uv build
```

## Upload new version to pypi

Create a new release on https://github.com/crate/django-cratedb/releases and the workflow will
take care of it.


## Before hacking

It is recommended to have some good knowledge of Django, the documentation on how to develop
a django database backend is scarce, the best way is to be familiar with Django internals and
read Django's source code, alternatively Postgres and CockroachDB connectors can be a good
place to start from.



