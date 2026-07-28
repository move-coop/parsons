"""Tests for query_through_ssh.

The utility opens an SSH tunnel (``sshtunnel``) and a Postgres connection
(``psycopg2``), runs a query through it, and always tears both down. Those two
libraries are the external boundary, so they are mocked (see ``ssh_mocks`` in
conftest.py) and the real function runs against them.
"""

import logging

import pytest

from parsons.utilities.ssh_utilities import query_through_ssh

PARAMS = {
    "ssh_host": "ssh.example.com",
    "ssh_port": "22",
    "ssh_username": "user",
    "ssh_password": "pass",
    "db_host": "db.example.com",
    "db_port": "5432",
    "db_name": "testdb",
    "db_username": "dbuser",
    "db_password": "dbpass",
    "query": "SELECT * FROM table",
}


def test_query_through_ssh(ssh_mocks):
    ssh_mocks.cursor.fetchall.return_value = [("row1",), ("row2",)]

    result = query_through_ssh(**PARAMS)

    assert result == [("row1",), ("row2",)]
    # Opened the SSH tunnel with the ssh creds and remote db address (ports -> int).
    ssh_mocks.tunnel.assert_called_once_with(
        ("ssh.example.com", 22),
        ssh_username="user",
        ssh_password="pass",
        remote_bind_address=("db.example.com", 5432),
    )
    ssh_mocks.server.start.assert_called_once()
    # Connected psycopg2 to the tunnel's local bind port with the db creds.
    ssh_mocks.connect.assert_called_once_with(
        host="localhost", port=12345, database="testdb", user="dbuser", password="dbpass"
    )
    ssh_mocks.cursor.execute.assert_called_once_with("SELECT * FROM table")
    ssh_mocks.cursor.fetchall.assert_called_once()
    # Cleanup always runs in the finally block.
    ssh_mocks.con.close.assert_called_once()
    ssh_mocks.server.stop.assert_called_once()


def test_query_through_ssh_error_is_logged_and_reraised(ssh_mocks, caplog):
    ssh_mocks.cursor.execute.side_effect = RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"), caplog.at_level(logging.ERROR):
        query_through_ssh(**PARAMS)

    # The error is logged before being re-raised...
    assert "Error during query execution" in caplog.text
    # ...and the tunnel and connection are still torn down.
    ssh_mocks.con.close.assert_called_once()
    ssh_mocks.server.stop.assert_called_once()


def test_query_through_ssh_tunnel_failure_skips_cleanup(ssh_mocks, caplog):
    # If the tunnel never opens, neither the connection nor the server exist, so the
    # finally block must not try to tear down anything.
    ssh_mocks.tunnel.side_effect = RuntimeError("no tunnel")

    with pytest.raises(RuntimeError, match="no tunnel"), caplog.at_level(logging.ERROR):
        query_through_ssh(**PARAMS)

    ssh_mocks.connect.assert_not_called()
    ssh_mocks.con.close.assert_not_called()
    ssh_mocks.server.stop.assert_not_called()
