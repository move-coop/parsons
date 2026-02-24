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
    except Exception as e:
        pytest.skip(f"Docker not available: {e}")

    container = PostgresContainer("postgres:9.5")
    try:
        container.start()
    except Exception as e:
        pytest.skip(f"Could not start Postgres container: {e}")

    os.environ["PGUSER"] = "test"
    os.environ["PGPASSWORD"] = "test"
    os.environ["PGHOST"] = "localhost"
    os.environ["PGDATABASE"] = "test"
    os.environ["PGPORT"] = container.get_exposed_port(5432)

    yield

    container.stop()
