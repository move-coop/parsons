import unittest
from unittest.mock import patch, MagicMock
from parsons.utilities.ssh_utilities import SSHTunnelUtility


class TestSSHTunnelUtility(unittest.TestCase):

    @patch("parsons.utilities.ssh_utilities.SSHTunnelForwarder")
    def test_ssh_tunnel_creation(self, mock_tunnel):
        # Setup mock for SSHTunnelForwarder
        mock_tunnel_instance = MagicMock()
        mock_tunnel.return_value = mock_tunnel_instance
        mock_tunnel_instance.__enter__.return_value = mock_tunnel_instance
        mock_tunnel_instance.__exit__.return_value = None  # Ensure __exit__ does nothing harmful
        # Attempt to use SSHTunnelUtility
        with SSHTunnelUtility(
            ssh_host="example.com",
            ssh_username="user",
            ssh_password="pass",
            remote_bind_address=("remote.db.address", 3306),
        ) as tunnel:
            self.assertEqual(mock_tunnel_instance, tunnel)


if __name__ == "__main__":
    unittest.main()
