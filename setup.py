import os
from pathlib import Path

from setuptools import setup


def main():
    limited_deps = os.environ.get("PARSONS_LIMITED_DEPENDENCIES", "")
    install_requires = []
    if limited_deps.strip().upper() in ("1", "YES", "TRUE", "ON"):
        install_requires = [
            "petl",
            "python-dateutil",
            "requests",
            "requests_oauthlib",
            "simplejson",
        ]
        extras_require = {
            "airtable": ["pyairtable"],
            "alchemer": ["surveygizmo"],
            "avro": ["fastavro"],
            "azure": ["azure-storage-blob"],
            "box": ["boxsdk < 10, >=4.1.0", "requests-toolbelt>=1.0.0"],
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
                "sqlalchemy >= 1.4.22, != 1.4.33, < 3.0.0",
            ],
            "newmode": ["newmode"],
            "ngpvan": ["suds-py3"],
            "mobilecommons": ["bs4"],
            "postgres": [
                "psycopg2-binary <= 2.9.9;python_version<'3.13'",
                "psycopg2-binary >= 2.9.10;python_version >= '3.13'",
                "sqlalchemy >= 1.4.22, != 1.4.33, < 3.0.0",
            ],
            "redshift": [
                "boto3",
                "psycopg2-binary <= 2.9.9;python_version<'3.13'",
                "psycopg2-binary >= 2.9.10;python_version >= '3.13'",
                "sqlalchemy >= 1.4.22, != 1.4.33, < 3.0.0",
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
                "psycopg2-binary <= 2.9.9;python_version<'3.13'",
                "psycopg2-binary >= 2.9.10;python_version >= '3.13'",
                "sqlalchemy >= 1.4.22, != 1.4.33, < 3.0.0",
            ],
        }
        extras_require["all"] = sorted({lib for libs in extras_require.values() for lib in libs})
    else:
        pyproject_path = Path(__file__).parent / "requirements.txt"
        install_requires = pyproject_path.read_text().strip().split("\n")
        extras_require = {"all": []}  # No op for forward-compatibility

    setup(
        install_requires=install_requires,
        extras_require=extras_require,
    )


if __name__ == "__main__":
    main()
