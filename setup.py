"""
Determine dependencies to install as part of the parsons package.

This file is required by our "friendly dependencies" feature.
If PARSONS_LIMITED_DEPENDENCIES environment variable is set, only core set of dependencies is installed by default.
Dependencies used by specific parsons connectors are made available via extras packages. In addition,
dependencies are installed with as few version limitations as possible to maximise compatibility for advanced users.

Due to isolated environments described in PEP 517, which are used when installing published source packages,
this envionment variable and partial installation via extras only works when installing from local source code.

See https://www.parsonsproject.org/pub/friendly-dependencies.
"""

import os
from pathlib import Path

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
    "box": ["boxsdk >= 4.1.0, != 4.4.0, < 10", "requests-toolbelt >= 1.0.0"],
    "braintree": ["braintree"],
    "catalist": ["paramiko"],
    "civis": ["civis"],
    "dbt-duckdb": ["dbt-duckdb >= 1.8.0", "dbt-core>=1.8.0"],
    "dbt-redshift": ["dbt-redshift >= 1.8.0", "dbt-core>=1.8.0"],
    "dbt-bigquery": ["dbt-bigquery >= 1.8.0", "dbt-core>=1.8.0"],
    "dbt-postgres": ["dbt-postgres >= 1.8.0", "dbt-core>=1.8.0"],
    "dbt-snowflake": ["dbt-snowflake >= 1.8.0", "dbt-core>=1.8.0"],
    "facebook": ["facebook-business", "joblib"],
    "geocode": [
        "censusgeocode",
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
    "pandas": ["pandas"],
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
    "scytl": ["defusedxml"],
    "sftp": ["paramiko"],
    "slack": ["slack-sdk"],
    "smtp": ["validate-email"],
    "targetsmart": ["defusedxml", "paramiko", "xmltodict"],
    "twilio": ["twilio"],
    "ssh": [
        "psycopg2-binary >= 2.0.0",
        "sqlalchemy >= 1.4.22",
        "sshtunnel",
    ],
}


def get_install_requires(*, limited: bool = False) -> list[str]:
    """
    Get the list of install requirements.

    Args:
    limited:
        If True, return only core dependencies defined in CORE_DEPENDENCIES.
        If False, return all dependencies from requirements.txt
    """
    if not limited:
        requirements_txt_path = Path(__file__).parent / "requirements.txt"
        return requirements_txt_path.read_text().strip().split("\n")

    return CORE_DEPENDENCIES


def get_extras_require(*, limited: bool = False) -> dict[str, list[str]]:
    """
    Get the extras_require dictionary.

    Args:
    limited:
        If True, return extras as defined in EXTRA_DEPENDENCIES.
        If False, return empty dict for forward-compatibility.
    """
    if not limited:
        return {"all": []}

    extras_require = EXTRA_DEPENDENCIES
    extras_require["all"] = sorted({lib for libs in extras_require.values() for lib in libs})

    return extras_require


if __name__ == "__main__":
    limited_deps_env = os.environ.get("PARSONS_LIMITED_DEPENDENCIES", "")
    use_limited = limited_deps_env.strip().upper() in ("1", "YES", "TRUE", "ON")

    setup(
        install_requires=get_install_requires(limited=use_limited),
        extras_require=get_extras_require(limited=use_limited),
    )
