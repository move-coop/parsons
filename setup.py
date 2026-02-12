"""Determine dependencies to install as part of the parsons package."""

from setuptools import setup

CORE_DEPENDENCIES = [
    "petl",
    "python-dateutil",
    "requests",
    "requests-oauthlib",
    "simplejson",
]
EXTRA_DEPENDENCIES = {
    "airtable": ["pyairtable"],
    "alchemer": ["surveygizmo"],
    "avro": ["fastavro"],
    "azure": ["azure-storage-blob"],
    "box": ["boxsdk >= 4.1.0, < 10", "requests-toolbelt >= 1.0.0"],
    "braintree": ["braintree"],
    "catalist": ["paramiko"],
    "civis": ["civis"],
    "dbt-redshift": ["dbt-redshift >= 1.5.0"],
    "dbt-bigquery": ["dbt-bigquery >= 1.5.0"],
    "dbt-postgres": ["dbt-postgres >= 1.5.0"],
    "dbt-snowflake": ["dbt-snowflake >= 1.5.0"],
    "facebook": ["joblib", "facebook-business"],
    "geocode": [
        "requests >= 2.27.0",
        "requests-toolbelt >= 0.9.0",
        "urllib3",
    ],
    "github": ["PyGitHub"],
    "google": [
        "apiclient",
        "google-api-python-client",
        "google-cloud-bigquery",
        "google-cloud-storage",
        "google-cloud-storage-transfer",
        "gspread",
        "httplib2",
        "oauth2client",
        "validate-email",
    ],
    "mysql": [
        "mysql-connector-python",
        "sqlalchemy >= 1.4.22",
    ],
    "newmode": ["newmode"],
    "ngpvan": ["suds-py3"],
    "mobilecommons": ["beautifulsoup4", "xmltodict"],
    "postgres": [
        "psycopg2-binary >= 2.0.0",
        "sqlalchemy >= 1.4.22",
    ],
    "redshift": [
        "boto3",
        "psycopg2-binary >= 2.0.0",
        "sqlalchemy >= 1.4.22",
    ],
    "s3": ["boto3"],
    "salesforce": ["simple-salesforce"],
    "scytl": ["defusedxml", "pytz"],
    "sftp": ["paramiko"],
    "slack": ["slack-sdk"],
    "smtp": ["validate-email"],
    "targetsmart": ["xmltodict", "defusedxml"],
    "twilio": ["twilio"],
    "ssh": [
        "sshtunnel",
        "psycopg2-binary >= 2.0.0",
        "sqlalchemy >= 1.4.22",
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
