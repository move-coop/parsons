import os
from distutils.core import setup
from pathlib import Path
from setuptools import find_packages


def main():
    limited_deps = os.environ.get("PARSONS_LIMITED_DEPENDENCIES", "")
    if limited_deps.strip().upper() in ("1", "YES", "TRUE", "ON"):
        install_requires = [
            "petl==1.7.15",
            "python-dateutil==2.8.2",
            "requests==2.31.0",
            "requests_oauthlib==1.3.0",
            "simplejson==3.16.0",
        ]
        extras_require = {
            "airtable": ["airtable-python-wrapper==0.13.0"],
            "alchemer": ["surveygizmo==1.2.3"],
            "azure": ["azure-storage-blob==12.3.2"],
            "box": ["boxsdk==2.10.0"],
            "braintree": ["braintree==4.26.0"],
            "catalist": ["paramiko==3.4.0"],
            "civis": ["civis==1.16.1"],
            "dbt-redshift": ["dbt_redshift==1.4.0", "slackclient==1.3.2"],
            "dbt-bigquery": ["dbt_redshift==1.4.0", "slackclient==1.3.2"],
            "dbt-postgres": ["dbt_redshift==1.4.0", "slackclient==1.3.2"],
            "dbt-snowflake": ["dbt-snowflake", "slackclient==1.3.2"],
            "facebook": ["joblib==1.2.0", "facebook-business==13.0.0"],
            "geocode": ["censusgeocode==0.4.3.post1", "urllib3==1.26.18"],
            "github": ["PyGitHub==1.51"],
            "google": [
                "apiclient==1.0.4",
                "google-api-python-client==1.7.7",
                "google-cloud-bigquery==3.18.0",
                "google-cloud-storage==2.10.0",
                "google-cloud-storage-transfer==1.9.1",
                "gspread==3.7.0",
                "httplib2==0.22.0",
                "oauth2client==4.1.3",
                "validate-email==1.3",
            ],
            "mysql": ["mysql-connector-python==8.0.18", "SQLAlchemy==1.3.23"],
            "newmode": ["newmode==0.1.6"],
            "ngpvan": ["suds-py3==1.3.4.0"],
            "mobilecommons": ["beautifulsoup4==4.12.3"],
            "postgres": ["psycopg2-binary==2.9.3", "SQLAlchemy==1.3.23"],
            "redshift": ["boto3<2.0,>=1.17.98", "psycopg2-binary==2.9.3", "SQLAlchemy==1.3.23"],
            "s3": ["boto3<2.0,>=1.17.98"],
            "salesforce": ["simple-salesforce==1.11.6"],
            "sftp": ["paramiko==3.4.0"],
            "slack": ["slackclient==1.3.2"],
            "smtp": ["validate-email==1.3"],
            "targetsmart": ["xmltodict==0.11.0"],
            "twilio": ["twilio==8.2.1"],
            "zoom": ["PyJWT==2.4.0"],
        }
        extras_require["all"] = sorted(
            {lib for libs in extras_require.values() for lib in libs}
        )
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
        version="3.1.0",
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
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
        ],
        python_requires=">=3.8.0,<3.12.0",
        long_description=long_description,
        long_description_content_type='text/markdown'
    )


if __name__ == "__main__":
    main()
