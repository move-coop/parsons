import pytest
import os
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="class")
def postgres_container():
    """Initialize a Postgres container

    Sets environment variables so that parsons.Postgres(port=None)
    connects to this container automatically.
    """
    with PostgresContainer("postgres:9.5") as postgres:
        os.environ["PGUSER"] = "test"
        os.environ["PGPASSWORD"] = "test"
        os.environ["PGHOST"] = "localhost"
        os.environ["PGDATABASE"] = "test"
        os.environ["PGPORT"] = postgres.get_exposed_port(5432)
        yield
