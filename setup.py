import os
from setuptools import find_packages
from distutils.core import setup


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
            "airtable": ["airtable-python-wrapper==0.13.0"],
            "alchemer": ["surveygizmo"],
            "azure": ["azure-storage-blob"],
            "box": ["boxsdk"],
            "braintree": ["braintree"],
            "catalist": ["paramiko"],
            "civis": ["civis"],
            "facebook": ["joblib", "facebook-business"],
            "geocode": ["censusgeocode", "urllib3==1.26.18"],
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
            "mysql": ["mysql-connector-python", "SQLAlchemy"],
            "newmode": ["newmode"],
            "ngpvan": ["suds-py3"],
            "mobilecommons": ["bs4"],
            "postgres": ["psycopg2-binary", "SQLAlchemy"],
            "redshift": ["boto3", "psycopg2-binary", "SQLAlchemy"],
            "s3": ["boto3"],
            "salesforce": ["simple-salesforce"],
            "sftp": ["paramiko"],
            "slack": ["slackclient<2"],
            "smtp": ["validate-email"],
            "targetsmart": ["xmltodict"],
            "twilio": ["twilio"],
            "zoom": ["PyJWT"],
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

    setup(
        name="parsons",
        version="3.0.0",
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
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
        ],
        python_requires=">=3.7.0,<3.11.0",
    )


if __name__ == "__main__":
    main()
