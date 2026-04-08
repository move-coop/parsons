# Provide shortcuts to importing Parsons submodules and set up logging
import importlib
import logging
import os
import warnings

from parsons.etl.table import Table

# Define the default logging config for Parsons and its submodules. For now the
# logger gets a StreamHandler by default. At some point a NullHandler may be more
# appropriate, so the end user must decide on logging behavior.

logger = logging.getLogger(__name__)
_handler = logging.StreamHandler()
_formatter = logging.Formatter("%(module)s %(levelname)s %(message)s")
_handler.setFormatter(_formatter)
logger.addHandler(_handler)

if os.environ.get("TESTING"):
    # Log less stuff in automated tests
    logger.setLevel("WARNING")
elif os.environ.get("DEBUG"):
    logger.setLevel("DEBUG")
else:
    logger.setLevel("INFO")

# Temporary deprecation warning for changes to install process
warnings.warn(
    (
        "The behavior of 'pip install parsons' has changed so only core dependencies are installed."
        "Learn more: https://www.parsonsproject.org/pub/improving-the-parsons-installation-experience"
    ),
    category=RuntimeWarning,
    stacklevel=2,
)

_CONNECTORS = {
    "ActBlue": "parsons.actblue.actblue",
    "ActionBuilder": "parsons.action_builder.action_builder",
    "ActionKit": "parsons.action_kit.action_kit",
    "ActionNetwork": "parsons.action_network.action_network",
    "Airmeet": "parsons.airmeet.airmeet",
    "Airtable": "parsons.airtable.airtable",
    "Alchemer": "parsons.alchemer.alchemer",
    "SurveyGizmo": "parsons.alchemer.alchemer",
    "Auth0": "parsons.auth0.auth0",
    "S3": "parsons.aws.s3",
    "AzureBlobStorage": "parsons.azure.azure_blob_storage",
    "BillCom": "parsons.bill_com.bill_com",
    "Bloomerang": "parsons.bloomerang.bloomerang",
    "Box": "parsons.box.box",
    "Braintree": "parsons.braintree.braintree",
    "CapitolCanary": "parsons.capitol_canary.capitol_canary",
    "CatalistMatch": "parsons.catalist.catalist",
    "Census": "parsons.census.census",
    "CivisClient": "parsons.civis.civisclient",
    "Community": "parsons.community.community",
    "Controlshift": "parsons.controlshift.controlshift",
    "Copper": "parsons.copper.copper",
    "CrowdTangle": "parsons.crowdtangle.crowdtangle",
    "DatabaseConnector": "parsons.databases.database_connector",
    "DBSync": "parsons.databases.db_sync",
    "discover_database": "parsons.databases.discover_database",
    "MySQL": "parsons.databases.mysql.mysql",
    "Postgres": "parsons.databases.postgres.postgres",
    "Redshift": "parsons.databases.redshift.redshift",
    "Sqlite": "parsons.databases.sqlite.sqlite",
    "Donorbox": "parsons.donorbox.donorbox",
    "Empower": "parsons.empower.empower",
    "FacebookAds": "parsons.facebook_ads.facebook_ads",
    "Formstack": "parsons.formstack.formstack",
    "Freshdesk": "parsons.freshdesk.freshdesk",
    "CensusGeocoder": "parsons.geocode.census_geocoder",
    "GitHub": "parsons.github.github",
    "GoogleAdmin": "parsons.google.google_admin",
    "GoogleBigQuery": "parsons.google.google_bigquery",
    "GoogleCivic": "parsons.google.google_civic",
    "GoogleCloudStorage": "parsons.google.google_cloud_storage",
    "GoogleDocs": "parsons.google.google_docs",
    "GoogleDrive": "parsons.google.google_drive",
    "GoogleSheets": "parsons.google.google_sheets",
    "Hustle": "parsons.hustle.hustle",
    "Mailchimp": "parsons.mailchimp.mailchimp",
    "MobileCommons": "parsons.mobilecommons.mobilecommons",
    "MobilizeAmerica": "parsons.mobilize_america.ma",
    "NationBuilder": "parsons.nation_builder.nation_builder",
    "Newmode": "parsons.newmode.newmode",
    "VAN": "parsons.ngpvan.van",
    "Gmail": "parsons.notifications.gmail",
    "Slack": "parsons.notifications.slack",
    "SMTP": "parsons.notifications.smtp",
    "PDI": "parsons.pdi.pdi",
    "Phone2Action": "parsons.phone2action.p2a",
    "Quickbase": "parsons.quickbase.quickbase",
    "QuickBooksTime": "parsons.quickbooks.quickbookstime",
    "Redash": "parsons.redash.redash",
    "RockTheVote": "parsons.rockthevote.rtv",
    "Salesforce": "parsons.salesforce.salesforce",
    "Scytl": "parsons.scytl.scytl",
    "SFTP": "parsons.sftp.sftp",
    "Shopify": "parsons.shopify.shopify",
    "Sisense": "parsons.sisense.sisense",
    "TargetSmartAPI": "parsons.targetsmart.targetsmart_api",
    "TargetSmartAutomation": "parsons.targetsmart.targetsmart_automation",
    "TurboVote": "parsons.turbovote.turbovote",
    "Twilio": "parsons.twilio.twilio",
    "Zoom": "parsons.zoom.zoom",
}

__all__ = ["Table"] + list(_CONNECTORS.keys())


def __getattr__(name):
    if name not in _CONNECTORS:
        raise AttributeError(f"module {__name__} has no attribute {name}")
    module_path = _CONNECTORS[name]
    try:
        module = importlib.import_module(module_path)
        connector = getattr(module, name)
        globals()[name] = connector
        return connector
    except ImportError as e:
        logger.error(f"Failed to import {name} from {module_path}.")
        raise ImportError(
            "The behavior of 'pip install parsons' has changed. "
            "Only core dependencies are installed by default. Learn more: "
            "https://www.parsonsproject.org/pub/improving-the-parsons-installation-experience"
        ) from e
