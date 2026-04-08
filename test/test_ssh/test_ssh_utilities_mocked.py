from unittest.mock import AsyncMock, MagicMock, patch

import asyncssh
import psycopg2
import pytest
from asyncssh.constants import DISC_CONNECTION_LOST

from parsons.utilities.ssh_utilities import query_through_ssh


@pytest.fixture
def mock_ssh_context():
    """Fixture to mock the entire asyncssh connection and tunnel lifecycle."""
    with patch("asyncssh.connect", new_callable=AsyncMock) as mock_connect:
        mock_conn = MagicMock(spec=asyncssh.SSHClientConnection)
        mock_conn.forward_local_port = AsyncMock()
        mock_conn.wait_closed = AsyncMock()
        mock_conn.close = MagicMock()

        mock_tunnel = MagicMock()
        mock_tunnel.get_port = MagicMock(return_value=54321)
        mock_tunnel.wait_closed = AsyncMock()
        mock_tunnel.close = MagicMock()

        mock_connect.return_value = mock_conn
        mock_conn.forward_local_port.return_value = mock_tunnel

        yield {"connect": mock_connect, "connection": mock_conn, "tunnel": mock_tunnel}


@pytest.fixture
def mock_db_context():
    """Fixture to mock psycopg2 connection and cursor."""
    with patch("psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        yield {"connect": mock_connect, "connection": mock_conn, "cursor": mock_cursor}


def test_query_through_ssh_success(mock_ssh_context, mock_db_context):
    expected_data = [("row1",), ("row2",)]
    mock_db_context["cursor"].fetchall.return_value = expected_data

    result = query_through_ssh(
        ssh_host="ssh.example.com",
        ssh_port=22,
        ssh_username="user",
        ssh_password="password",
        db_host="db.internal",
        db_port=5432,
        db_name="testdb",
        db_username="dbuser",
        db_password="dbpassword",
        query="SELECT * FROM table",
    )

    assert result == expected_data
    mock_ssh_context["connect"].assert_called_once()
    mock_db_context["connect"].assert_called_once_with(
        host="127.0.0.1",
        port=54321,
        user="dbuser",
        password="dbpassword",
        database="testdb",
    )
    mock_ssh_context["tunnel"].close.assert_called_once()
    mock_ssh_context["connection"].close.assert_called_once()


def test_query_through_ssh_ssh_failure(mock_ssh_context):
    error_msg = "Connection lost to the remote host"
    mock_ssh_context["connect"].side_effect = asyncssh.Error(DISC_CONNECTION_LOST, error_msg)

    with pytest.raises(asyncssh.Error, match=error_msg):
        query_through_ssh("host", 22, "user", "pass", "db", 5432, "name", "u", "p", "SELECT 1")

    mock_ssh_context["connection"].forward_local_port.assert_not_called()


def test_query_through_ssh_db_failure(mock_ssh_context, mock_db_context):
    mock_db_context["connect"].side_effect = psycopg2.OperationalError("DB Connection Error")

    with pytest.raises(psycopg2.OperationalError, match="DB Connection Error"):
        query_through_ssh("host", 22, "user", "pass", "db", 5432, "name", "u", "p", "SELECT 1")

    mock_ssh_context["tunnel"].close.assert_called_once()
    mock_ssh_context["connection"].close.assert_called_once()
