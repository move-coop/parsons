import unittest
from unittest.mock import MagicMock, patch

from parsons.utilities.ssh_utilities import query_through_ssh


class TestSSHTunnelUtility(unittest.TestCase):
    @patch("parsons.utilities.ssh_utilities.sshtunnel.SSHTunnelForwarder")
    @patch("parsons.utilities.ssh_utilities.psycopg2.connect")
    def test_query_through_ssh(self, mock_connect, mock_tunnel):
        # Setup mock for SSHTunnelForwarder
        mock_tunnel_instance = MagicMock()
        mock_tunnel.return_value = mock_tunnel_instance
        mock_tunnel_instance.start.return_value = None
        mock_tunnel_instance.stop.return_value = None
        mock_tunnel_instance.local_bind_port = 12345

        # Setup mock for psycopg2.connect
        mock_conn_instance = MagicMock()
        mock_connect.return_value = mock_conn_instance
        mock_cursor = MagicMock()
        mock_conn_instance.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("row1",), ("row2",)]

        # Define the parameters for the test
        ssh_host = "ssh.example.com"
        ssh_port = 22
        ssh_username = "user"
        ssh_password = "pass"
        db_host = "db.example.com"
        db_port = 5432
        db_name = "testdb"
        db_username = "dbuser"
        db_password = "dbpass"
        query = "SELECT * FROM table"

        # Execute the function under test
        result = query_through_ssh(
            ssh_host,
            ssh_port,
            ssh_username,
            ssh_password,
            db_host,
            db_port,
            db_name,
            db_username,
            db_password,
            query,
        )

        # Assert that the result is as expected
        assert result == [("row1",), ("row2",)]
        mock_tunnel.assert_called_once_with(
            (ssh_host, ssh_port),
            ssh_username=ssh_username,
            ssh_password=ssh_password,
            remote_bind_address=(db_host, db_port),
        )
        mock_connect.assert_called_once_with(
            host="localhost", port=12345, database=db_name, user=db_username, password=db_password
        )
        mock_cursor.execute.assert_called_once_with(query)
        mock_cursor.fetchall.assert_called_once()


if __name__ == "__main__":
    unittest.main()
