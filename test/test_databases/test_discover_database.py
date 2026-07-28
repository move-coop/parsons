import pytest

from parsons import GoogleBigQuery as BigQuery
from parsons.databases.discover_database import discover_database
from parsons.databases.mysql import MySQL
from parsons.databases.postgres import Postgres
from parsons.databases.redshift import Redshift


@pytest.fixture
def stub_db_constructors(mocker):
    """Stub each DB constructor so discover_database can build one without real config."""
    for db in (BigQuery, Postgres, MySQL, Redshift):
        mocker.patch.object(db, "__init__", return_value=None)


@pytest.fixture
def getenv(mocker):
    """Patch ``os.getenv``; program its return_value / side_effect per test."""
    return mocker.patch("os.getenv")


def _password_for(*present):
    """A getenv side effect returning 'password' only for the given *_PASSWORD vars."""
    return lambda var: "password" if var in present else None


def test_no_database_detected(stub_db_constructors, getenv):
    getenv.return_value = None

    with pytest.raises(EnvironmentError, match="Could not find any database configuration"):
        discover_database()


def test_single_database_detected(stub_db_constructors, getenv):
    getenv.side_effect = _password_for("REDSHIFT_PASSWORD")

    assert isinstance(discover_database(), Redshift)


def test_single_database_detected_with_other_default(stub_db_constructors, getenv):
    getenv.side_effect = _password_for("REDSHIFT_PASSWORD")

    assert isinstance(discover_database(default_connector=Postgres), Redshift)


def test_single_database_detected_with_other_default_list(stub_db_constructors, getenv):
    getenv.side_effect = _password_for("REDSHIFT_PASSWORD")

    assert isinstance(discover_database(default_connector=[Postgres, MySQL]), Redshift)


def test_multiple_databases_no_default(stub_db_constructors, getenv):
    getenv.return_value = "password"

    with pytest.raises(
        EnvironmentError,
        match="Multiple database configurations detected: .+ Please specify a default connector",
    ):
        discover_database()


def test_multiple_databases_with_default(stub_db_constructors, getenv):
    getenv.return_value = "password"

    assert isinstance(discover_database(default_connector=Redshift), Redshift)


def test_multiple_databases_with_default_list(stub_db_constructors, getenv):
    getenv.return_value = "password"

    assert isinstance(discover_database(default_connector=[MySQL, Redshift]), MySQL)


def test_multiple_databases_invalid_default(stub_db_constructors, getenv):
    getenv.side_effect = _password_for("REDSHIFT_PASSWORD", "MYSQL_PASSWORD")

    with pytest.raises(EnvironmentError, match=r"Default connector .+ not detected. Detected: .+"):
        discover_database(default_connector=Postgres)


def test_multiple_databases_invalid_default_list(stub_db_constructors, getenv):
    getenv.side_effect = _password_for("REDSHIFT_PASSWORD", "MYSQL_PASSWORD")

    with pytest.raises(EnvironmentError, match="None of the default connectors .+ were detected"):
        discover_database(default_connector=[Postgres, BigQuery])
