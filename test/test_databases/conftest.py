import os

import pytest
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="class")
def postgres_container():
    """Initialize a Postgres container

    Sets environment variables so that parsons.Postgres(port=None)
    connects to this container automatically.
    """
    try:
        import docker

        docker.from_env().ping()
    except Exception:
        pytest.skip("Docker not available")

    with PostgresContainer("postgres:9.5") as postgres:
        os.environ["PGUSER"] = "test"
        os.environ["PGPASSWORD"] = "test"
        os.environ["PGHOST"] = "localhost"
        os.environ["PGDATABASE"] = "test"
        os.environ["PGPORT"] = postgres.get_exposed_port(5432)
        yield
