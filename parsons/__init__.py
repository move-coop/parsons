# Provide shortcuts to importing Parsons submodules and set up logging
import importlib
import logging
import os

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

# Table is referenced by many connectors, so we add it immediately to limit the damage
# of circular dependencies
__all__ = ["Table"]
for module_path, connector_name in (
    ("parsons.actblue.actblue", "ActBlue"),
    ("parsons.action_kit.action_kit", "ActionKit"),
    ("parsons.action_builder.action_builder", "ActionBuilder"),
    ("parsons.action_network.action_network", "ActionNetwork"),
    ("parsons.airtable.airtable", "Airtable"),
    ("parsons.alchemer.alchemer", "Alchemer"),
    ("parsons.alchemer.alchemer", "SurveyGizmo"),
    ("parsons.auth0.auth0", "Auth0"),
    ("parsons.aws.s3", "S3"),
    ("parsons.azure.azure_blob_storage", "AzureBlobStorage"),
    ("parsons.bill_com.bill_com", "BillCom"),
    ("parsons.bloomerang.bloomerang", "Bloomerang"),
    ("parsons.box.box", "Box"),
    ("parsons.braintree.braintree", "Braintree"),
    ("parsons.capitol_canary.capitol_canary", "CapitolCanary"),
    ("parsons.catalist.catalist", "CatalistMatch"),
    ("parsons.census.census", "Census"),
    ("parsons.civis.civisclient", "CivisClient"),
    ("parsons.controlshift.controlshift", "Controlshift"),
    ("parsons.copper.copper", "Copper"),
    ("parsons.crowdtangle.crowdtangle", "CrowdTangle"),
    ("parsons.databases.database_connector", "DatabaseConnector"),
    ("parsons.databases.discover_database", "discover_database"),
    ("parsons.databases.db_sync", "DBSync"),
    ("parsons.databases.mysql.mysql", "MySQL"),
    ("parsons.databases.postgres.postgres", "Postgres"),
    ("parsons.databases.redshift.redshift", "Redshift"),
    ("parsons.donorbox.donorbox", "Donorbox"),
    ("parsons.facebook_ads.facebook_ads", "FacebookAds"),
    ("parsons.formstack.formstack", "Formstack"),
    ("parsons.freshdesk.freshdesk", "Freshdesk"),
    ("parsons.geocode.census_geocoder", "CensusGeocoder"),
    ("parsons.github.github", "GitHub"),
    ("parsons.google.google_admin", "GoogleAdmin"),
    ("parsons.google.google_bigquery", "GoogleBigQuery"),
    ("parsons.google.google_civic", "GoogleCivic"),
    ("parsons.google.google_cloud_storage", "GoogleCloudStorage"),
    ("parsons.google.google_sheets", "GoogleSheets"),
    ("parsons.hustle.hustle", "Hustle"),
    ("parsons.mailchimp.mailchimp", "Mailchimp"),
    ("parsons.mobilecommons.mobilecommons", "MobileCommons"),
    ("parsons.mobilize_america.ma", "MobilizeAmerica"),
    ("parsons.nation_builder.nation_builder", "NationBuilder"),
    ("parsons.newmode.newmode", "Newmode"),
    ("parsons.ngpvan.van", "VAN"),
    ("parsons.notifications.gmail", "Gmail"),
    ("parsons.notifications.slack", "Slack"),
    ("parsons.notifications.smtp", "SMTP"),
    ("parsons.pdi.pdi", "PDI"),
    ("parsons.phone2action.p2a", "Phone2Action"),
    ("parsons.quickbase.quickbase", "Quickbase"),
    ("parsons.redash.redash", "Redash"),
    ("parsons.rockthevote.rtv", "RockTheVote"),
    ("parsons.salesforce.salesforce", "Salesforce"),
    ("parsons.scytl.scytl", "Scytl"),
    ("parsons.sftp.sftp", "SFTP"),
    ("parsons.shopify.shopify", "Shopify"),
    ("parsons.sisense.sisense", "Sisense"),
    ("parsons.targetsmart.targetsmart_api", "TargetSmartAPI"),
    ("parsons.targetsmart.targetsmart_automation", "TargetSmartAutomation"),
    ("parsons.turbovote.turbovote", "TurboVote"),
    ("parsons.twilio.twilio", "Twilio"),
    ("parsons.zoom.zoom", "Zoom"),
):
    try:
        globals()[connector_name] = getattr(importlib.import_module(module_path), connector_name)
        __all__.append(connector_name)
    except ImportError:
        logger.debug(f"Could not import {module_path}.{connector_name}; skipping")
