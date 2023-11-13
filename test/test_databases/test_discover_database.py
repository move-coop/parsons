import unittest
from unittest.mock import patch
from parsons.databases.redshift import Redshift
from parsons.databases.mysql import MySQL
from parsons.databases.postgres import Postgres
from parsons import GoogleBigQuery as BigQuery
from parsons.databases.discover_database import discover_database


class TestDiscoverDatabase(unittest.TestCase):
    @patch.object(BigQuery, "__init__", return_value=None)
    @patch.object(Postgres, "__init__", return_value=None)
    @patch.object(MySQL, "__init__", return_value=None)
    @patch.object(Redshift, "__init__", return_value=None)
    @patch("os.getenv")
    def test_no_database_detected(self, mock_getenv, *_):
        mock_getenv.return_value = None
        with self.assertRaises(EnvironmentError):
            discover_database()

    @patch.object(BigQuery, "__init__", return_value=None)
    @patch.object(Postgres, "__init__", return_value=None)
    @patch.object(MySQL, "__init__", return_value=None)
    @patch.object(Redshift, "__init__", return_value=None)
    @patch("os.getenv")
    def test_single_database_detected(self, mock_getenv, *_):
        mock_getenv.side_effect = (
            lambda var: "password" if var == "REDSHIFT_PASSWORD" else None
        )
        self.assertIsInstance(discover_database(), Redshift)

    @patch.object(BigQuery, "__init__", return_value=None)
    @patch.object(Postgres, "__init__", return_value=None)
    @patch.object(MySQL, "__init__", return_value=None)
    @patch.object(Redshift, "__init__", return_value=None)
    @patch("os.getenv")
    def test_single_database_detected_with_other_default(self, mock_getenv, *_):
        mock_getenv.side_effect = (
            lambda var: "password" if var == "REDSHIFT_PASSWORD" else None
        )
        self.assertIsInstance(discover_database(default_connector=Postgres), Redshift)

    @patch.object(BigQuery, "__init__", return_value=None)
    @patch.object(Postgres, "__init__", return_value=None)
    @patch.object(MySQL, "__init__", return_value=None)
    @patch.object(Redshift, "__init__", return_value=None)
    @patch("os.getenv")
    def test_single_database_detected_with_other_default_list(self, mock_getenv, *_):
        mock_getenv.side_effect = (
            lambda var: "password" if var == "REDSHIFT_PASSWORD" else None
        )
        self.assertIsInstance(
            discover_database(default_connector=[Postgres, MySQL]), Redshift
        )

    @patch.object(BigQuery, "__init__", return_value=None)
    @patch.object(Postgres, "__init__", return_value=None)
    @patch.object(MySQL, "__init__", return_value=None)
    @patch.object(Redshift, "__init__", return_value=None)
    @patch("os.getenv")
    def test_multiple_databases_no_default(self, mock_getenv, *_):
        mock_getenv.return_value = "password"
        with self.assertRaises(EnvironmentError):
            discover_database()

    @patch.object(BigQuery, "__init__", return_value=None)
    @patch.object(Postgres, "__init__", return_value=None)
    @patch.object(MySQL, "__init__", return_value=None)
    @patch.object(Redshift, "__init__", return_value=None)
    @patch("os.getenv")
    def test_multiple_databases_with_default(self, mock_getenv, *_):
        mock_getenv.return_value = "password"
        self.assertIsInstance(discover_database(default_connector=Redshift), Redshift)

    @patch.object(BigQuery, "__init__", return_value=None)
    @patch.object(Postgres, "__init__", return_value=None)
    @patch.object(MySQL, "__init__", return_value=None)
    @patch.object(Redshift, "__init__", return_value=None)
    @patch("os.getenv")
    def test_multiple_databases_with_default_list(self, mock_getenv, *_):
        mock_getenv.return_value = "password"
        self.assertIsInstance(
            discover_database(default_connector=[MySQL, Redshift]), MySQL
        )

    @patch.object(BigQuery, "__init__", return_value=None)
    @patch.object(Postgres, "__init__", return_value=None)
    @patch.object(MySQL, "__init__", return_value=None)
    @patch.object(Redshift, "__init__", return_value=None)
    @patch("os.getenv")
    def test_multiple_databases_invalid_default(self, mock_getenv, *_):
        mock_getenv.side_effect = (
            lambda var: "password"
            if var == "REDSHIFT_PASSWORD" or var == "MYSQL_PASSWORD"
            else None
        )
        with self.assertRaises(EnvironmentError):
            discover_database(default_connector=Postgres)

    @patch.object(BigQuery, "__init__", return_value=None)
    @patch.object(Postgres, "__init__", return_value=None)
    @patch.object(MySQL, "__init__", return_value=None)
    @patch.object(Redshift, "__init__", return_value=None)
    @patch("os.getenv")
    def test_multiple_databases_invalid_default_list(self, mock_getenv, *_):
        mock_getenv.side_effect = (
            lambda var: "password"
            if var == "REDSHIFT_PASSWORD" or var == "MYSQL_PASSWORD"
            else None
        )
        with self.assertRaises(EnvironmentError):
            discover_database(default_connector=[Postgres, BigQuery])


if __name__ == "__main__":
    unittest.main()
