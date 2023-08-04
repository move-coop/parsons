import unittest
from unittest.mock import patch
from parsons.databases.database_connector import DatabaseConnector
from parsons.databases.redshift import Redshift
from parsons.databases.mysql import MySQL
from parsons.databases.postgres import Postgres
from parsons.google.google_bigquery import GoogleBigQuery
from parsons.databases.discover_database import discover_database


class TestDiscoverDatabase(unittest.TestCase):
    @patch("os.getenv")
    def test_no_database_detected(self, mock_getenv):
        mock_getenv.return_value = None
        with self.assertRaises(EnvironmentError):
            discover_database()

    @patch("os.getenv")
    def test_single_database_detected(self, mock_getenv):
        mock_getenv.side_effect = lambda var: var == "REDSHIFT_PASSWORD"
        self.assertIsInstance(discover_database(), Redshift)

    @patch("os.getenv")
    def test_multiple_databases_no_default(self, mock_getenv):
        mock_getenv.return_value = True
        with self.assertRaises(EnvironmentError):
            discover_database()

    @patch("os.getenv")
    def test_multiple_databases_with_default(self, mock_getenv):
        mock_getenv.return_value = True
        self.assertIsInstance(discover_database(default_connector=Redshift), Redshift)

    @patch("os.getenv")
    def test_multiple_databases_with_default_list(self, mock_getenv):
        mock_getenv.return_value = True
        self.assertIsInstance(
            discover_database(default_connector=[MySQL, Redshift]), Redshift
        )

    @patch("os.getenv")
    def test_multiple_databases_invalid_default(self, mock_getenv):
        mock_getenv.return_value = True
        with self.assertRaises(EnvironmentError):
            discover_database(default_connector=DatabaseConnector)


if __name__ == "__main__":
    unittest.main()
