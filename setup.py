"""Determine dependencies to install as part of the parsons package."""

from setuptools import setup

CORE_DEPENDENCIES = [
    "petl >= 1.7.17",
    "python-dateutil >= 2",
    "requests >= 2",
    "requests-oauthlib >= 1",
    "simplejson >= 3.18",
]
EXTRA_DEPENDENCIES = {
    "airtable": ["pyairtable >= 3"],
    "alchemer": ["surveygizmo >= 1"],
    "avro": ["fastavro >= 1.12"],
    "azure": ["azure-storage-blob>= 12"],
    "box": ["boxsdk >= 4, != 4.4.0, < 10", "requests-toolbelt >= 1"],
    "braintree": ["braintree >= 4"],
    "catalist": ["paramiko >= 3"],
    "civis": ["civis >= 2"],
    "dbt-redshift": [
        "dbt-redshift >= 1.5",
        "dbt-core >= 1.5",
        "lxml >= 6.0.1",
    ],
    "dbt-bigquery": ["dbt-bigquery >= 1.5", "dbt-core >= 1.5"],
    "dbt-postgres": ["dbt-postgres >= 1.5", "dbt-core >= 1.5"],
    "dbt-snowflake": ["dbt-snowflake >= 1.5", "dbt-core >= 1.5"],
    "facebook": ["joblib >= 1", "facebook-business >= 20"],
    "geocode": [
        "censusgeocode >= 0.5",
        "urllib3 >= 2.6.3",
    ],
    "github": ["PyGitHub >= 2"],
    "google": [
        "apiclient >= 1.0.4",
        "google-api-python-client >= 2.150",
        "google-cloud-bigquery >= 3.35",
        "google-cloud-storage >= 3.1",
        "google-cloud-storage-transfer >= 1.12",
        "gspread >= 4",
        "httplib2 >= 0.15",
        "oauth2client >= 4",
        "protobuf >= 6",
        "validate-email >= 1",
    ],
    "mysql": [
        "mysql-connector-python >= 7",
        "sqlalchemy >= 1.4",
    ],
    "newmode": ["newmode >= 0.1.6"],
    "ngpvan": ["suds-py3 >= 1.4"],
    "mobilecommons": ["beautifulsoup4 >= 4", "xmltodict >= 1"],
    "pandas": ["pandas >= 2.3.3"],
    "postgres": [
        "psycopg2-binary >= 2.9.11",
        "sqlalchemy >= 1.4",
    ],
    "redshift": [
        "boto3 >= 1",
        "psycopg2-binary >= 2.9.11",
        "sqlalchemy >= 1.4",
    ],
    "s3": ["boto3 >= 1"],
    "salesforce": ["simple-salesforce >= 1"],
    "scytl": ["defusedxml >= 0.7"],
    "sftp": ["paramiko >= 3"],
    "slack": ["slack-sdk >= 3.26"],
    "smtp": ["validate-email >= 1"],
    "targetsmart": ["xmltodict >= 1", "defusedxml >= 0.7"],
    "twilio": ["twilio >= 9"],
    "ssh": [
        "sshtunnel >= 0.4",
        "psycopg2-binary >= 2.9.11",
        "sqlalchemy >= 1.4",
    ],
}


def get_extras_require() -> dict[str, list[str]]:
    """
    Get the extras_require dictionary, with added "all" extra that contains the values of all other extras.
    """
    extras_require = EXTRA_DEPENDENCIES
    extras_require["all"] = sorted({lib for libs in extras_require.values() for lib in libs})

    return extras_require


if __name__ == "__main__":
    setup(
        install_requires=CORE_DEPENDENCIES,
        extras_require=get_extras_require(),
    )
