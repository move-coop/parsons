import os

from parsons.databases.database_connector import DatabaseConnector
from parsons.databases.redshift import Redshift
from parsons.databases.mysql import MySQL
from parsons.databases.postgres import Postgres
from parsons.google.google_bigquery import GoogleBigQuery


def discover_database() -> DatabaseConnector:
    """ Create an appropriate ``DatabaseConnector`` based on environmental variables.

    Will search the environmental variables for the proper credentials for the
    Redshift, MySQL, Postgres, and BigQuery connectors. See the documentation
    for the connectors to variables required to initialize them.

    If no suitable configuration is found, will raise an error.

    Note that the variables to be searched for are hard-coded in this function,
    since they are unlikely to change. If that is done, for some reason, or a
    new database connector is added, ``discover_database`` should be updated

    Returns:
        DatabaseConnector: The database connector configured in the environment.
    """
    if os.getenv("REDSHIFT_PASSWORD"):
        return Redshift()
    elif os.getenv("MYSQL_PASSWORD"):
        return MySQL()
    elif os.getenv("PGPASSWORD"):
        return Postgres()
    elif os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        return GoogleBigQuery()

    raise EnvironmentError("Could not find any database configuration.")
