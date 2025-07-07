import os
from distutils.core import setup
from pathlib import Path

from setuptools import find_packages


def main():
    limited_deps = os.environ.get("PARSONS_LIMITED_DEPENDENCIES", "")
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
            "azure": ["azure-storage-blob"],
            "box": ["boxsdk"],
            "braintree": ["braintree"],
            "catalist": ["paramiko"],
            "civis": ["civis"],
            "dbt-redshift": ["dbt-redshift>=1.5.0"],
            "dbt-bigquery": ["dbt-bigquery>=1.5.0"],
            "dbt-postgres": ["dbt-postgres>=1.5.0"],
            "dbt-snowflake": ["dbt-snowflake>=1.5.0"],
            "facebook": ["joblib", "facebook-business"],
            "geocode": ["censusgeocode", "urllib3==1.26.19"],
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
                "psycopg2-binary<=2.9.9;python_version<'3.13'",
                "psycopg2-binary>=2.9.10;python_version>='3.13'",
                "sqlalchemy >= 1.4.22, != 1.4.33, < 3.0.0",
            ],
            "redshift": [
                "boto3",
                "psycopg2-binary<=2.9.9;python_version<'3.13'",
                "psycopg2-binary>=2.9.10;python_version>='3.13'",
                "sqlalchemy >= 1.4.22, != 1.4.33, < 3.0.0",
            ],
            "s3": ["boto3"],
            "salesforce": ["simple-salesforce"],
            "scytl": ["defusedxml", "pytz"],
            "sftp": ["paramiko"],
            "slack": ["slackclient<2"],
            "smtp": ["validate-email"],
            "targetsmart": ["xmltodict", "defusedxml"],
            "twilio": ["twilio"],
            "ssh": [
                "sshtunnel",
                "psycopg2-binary<=2.9.9;python_version<'3.13'",
                "psycopg2-binary>=2.9.10;python_version>='3.13'",
                "sqlalchemy >= 1.4.22, != 1.4.33, < 3.0.0",
            ],
        }
        extras_require["all"] = sorted({lib for libs in extras_require.values() for lib in libs})
    else:
        THIS_DIR = os.path.abspath(os.path.dirname(__file__))
        with open(os.path.join(THIS_DIR, "requirements.txt")) as reqs:
            install_requires = reqs.read().strip().split("\n")
        # No op for forward-compatibility
        extras_require = {"all": []}

    this_directory = Path(__file__).parent
    long_description = (this_directory / "README.md").read_text()

    setup(
        name="parsons",
        version="5.1.0",  # ensure this version number is in format of n.n.n, not n or n.n
        author="The Movement Cooperative",
        author_email="info@movementcooperative.org",
        url="https://github.com/move-coop/parsons",
        keywords=["PROGRESSIVE", "API", "ETL"],
        packages=find_packages(),
        install_requires=install_requires,
        extras_require=extras_require,
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Programming Language :: Python :: 3.13",
        ],
        python_requires=">=3.9,<3.14",
        long_description=long_description,
        long_description_content_type="text/markdown",
    )


if __name__ == "__main__":
    main()
