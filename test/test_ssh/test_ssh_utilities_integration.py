import psycopg2
import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.core.wait_strategies import LogMessageWaitStrategy
from testcontainers.postgres import PostgresContainer

from parsons.utilities.ssh_utilities import query_through_ssh


def setup_db_locally(env):
    conn = psycopg2.connect(
        host="localhost",
        port=env["db_actual_exposed_port"],
        user=env["db_user"],
        password=env["db_pass"],
        database=env["db_name"],
    )

    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS integration_test;")
        cur.execute("""
            CREATE TABLE integration_test (
                id INT,
                name TEXT,
                payload JSONB,
                is_active BOOLEAN,
                created_at TIMESTAMP
            );
        """)
        cur.execute("""
            INSERT INTO integration_test VALUES
            (1, 'Alice', '{"key": "value"}', TRUE, NOW()),
            (2, 'Bob', '{"key": "something"}', FALSE, NOW());
        """)
    conn.commit()
    conn.close()


@pytest.fixture(scope="module")
def setup_integration_env():
    with (
        Network() as network,
        PostgresContainer("postgres:16-alpine")
        .with_network(network)
        .with_network_aliases("pg-server") as postgres,
        DockerContainer("linuxserver/openssh-server")
        .with_network(network)
        .with_env("USER_PASSWORD", "testpass")
        .with_env("USER_NAME", "testuser")
        .with_env("PASSWORD_ACCESS", "true")
        .with_bind_ports(2222, 2222)
        .waiting_for(LogMessageWaitStrategy(".*sshd is listening.*")),
    ):
        yield {
            "ssh_host": "127.0.0.1",
            "ssh_port": 2222,
            "ssh_user": "testuser",
            "ssh_pass": "testpass",
            "db_host": "pg-server",
            "db_port": 5432,
            "db_name": postgres.dbname,
            "db_user": postgres.username,
            "db_pass": postgres.password,
            "db_actual_exposed_port": postgres.get_exposed_port(5432),
        }


@pytest.mark.docker
def test_query_through_ssh(setup_integration_env):
    env = setup_integration_env
    setup_db_locally(env)

    complex_query = """
        SELECT id, name, created_at
        FROM integration_test
        ORDER BY id ASC;
    """

    result = query_through_ssh(
        ssh_host=env["ssh_host"],
        ssh_port=env["ssh_port"],
        ssh_username=env["ssh_user"],
        ssh_password=env["ssh_pass"],
        db_host=env["db_host"],
        db_port=env["db_port"],
        db_name=env["db_name"],
        db_username=env["db_user"],
        db_password=env["db_pass"],
        query=complex_query,
    )

    assert result is not None
    assert len(result) == 2
    assert result[0][0] == 1
    assert result[0][1] == "Alice"
    assert result[1][1] == "Bob"


@pytest.mark.docker
def test_data_integrity_and_types(setup_integration_env):
    env = setup_integration_env
    setup_db_locally(env)

    query = "SELECT id, payload, is_active FROM integration_test;"
    result = query_through_ssh(
        ssh_host=env["ssh_host"],
        ssh_port=env["ssh_port"],
        ssh_username=env["ssh_user"],
        ssh_password=env["ssh_pass"],
        db_host=env["db_host"],
        db_port=env["db_port"],
        db_name=env["db_name"],
        db_username=env["db_user"],
        db_password=env["db_pass"],
        query=query,
    )

    assert result[0][1] == {"key": "value"}  # JSONB check
    assert result[0][2] is True  # Boolean check
