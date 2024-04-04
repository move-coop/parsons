import os
from typing import Optional, Union, Type, List

from parsons.databases.database_connector import DatabaseConnector
from parsons.databases.redshift import Redshift
from parsons.databases.mysql import MySQL
from parsons.databases.postgres import Postgres
from parsons.google.google_bigquery import GoogleBigQuery as BigQuery


def discover_database(
    default_connector: Optional[
        Union[Type[DatabaseConnector], List[Type[DatabaseConnector]]]
    ] = None
) -> DatabaseConnector:
    """Create an appropriate ``DatabaseConnector`` based on environmental variables.

    Will search the environmental variables for the proper credentials for the
    Redshift, MySQL, Postgres, and BigQuery connectors. See the documentation
    for the connectors to variables required to initialize them.

    If no suitable configuration is found, will raise an error.

    If multiple suitable configurations are found, will raise an error unless
    a default connector class or list of classes is provided.

    Note that the variables to be searched for are hard-coded in this function,
    since they are unlikely to change. If that is done, for some reason, or a
    new database connector is added, ``discover_database`` should be updated

    Args:
        default_connector: Optional, single Class or list of Classes inheriting from
        DatabaseConnector to be used as default in case multiple database configurations
        are detected.

    Returns:
        DatabaseConnector: The database connector configured in the environment.
    """
    connectors = {
        "Redshift": Redshift,
        "MySQL": MySQL,
        "Postgres": Postgres,
        "GoogleBigQuery": BigQuery,
    }

    password_vars = {
        "Redshift": "REDSHIFT_PASSWORD",
        "MySQL": "MYSQL_PASSWORD",
        "Postgres": "PGPASSWORD",
        "GoogleBigQuery": "GOOGLE_APPLICATION_CREDENTIALS",
    }

    detected = [name for name in connectors.keys() if os.getenv(password_vars[name])]

    if len(detected) > 1:
        if default_connector is None:
            raise EnvironmentError(
                f"Multiple database configurations detected: {detected}."
                " Please specify a default connector."
            )

        if isinstance(default_connector, list):
            for connector in default_connector:
                if connector.__name__ in detected:
                    return connector()
            raise EnvironmentError(
                f"None of the default connectors {default_connector} were detected."
            )
        elif default_connector.__name__ in detected:
            return default_connector()
        else:
            raise EnvironmentError(
                f"Default connector {default_connector} not detected. Detected: {detected}."
            )

    elif detected:
        return connectors[detected[0]]()
    else:
        raise EnvironmentError("Could not find any database configuration.")
