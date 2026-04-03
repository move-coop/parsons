# Provide shortcuts to importing Parsons submodules and set up logging
import importlib
import logging
import os
import warnings
from typing import TYPE_CHECKING

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
        "The behavior of 'pip install parsons' is changing so only core dependencies will be installed. Learn more: "
        "https://www.parsonsproject.org/pub/improving-the-parsons-installation-experience"
    ),
    category=FutureWarning,
    stacklevel=2,
)

# Table is referenced by many connectors, so we add it immediately to limit the damage
# of circular dependencies
__all__ = ["Table"]
for module_path, connector_name in (
    ("parsons.actblue.actblue", "ActBlue"),
    ("parsons.action_builder.action_builder", "ActionBuilder"),
    ("parsons.action_kit.action_kit", "ActionKit"),
    ("parsons.action_network.action_network", "ActionNetwork"),
    ("parsons.airmeet.airmeet", "Airmeet"),
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
    ("parsons.community.community", "Community"),
    ("parsons.controlshift.controlshift", "Controlshift"),
    ("parsons.copper.copper", "Copper"),
    ("parsons.crowdtangle.crowdtangle", "CrowdTangle"),
    ("parsons.databases.database_connector", "DatabaseConnector"),
    ("parsons.databases.db_sync", "DBSync"),
    ("parsons.databases.discover_database", "discover_database"),
    ("parsons.databases.mysql.mysql", "MySQL"),
    ("parsons.databases.postgres.postgres", "Postgres"),
    ("parsons.databases.redshift.redshift", "Redshift"),
    ("parsons.databases.sqlite.sqlite", "Sqlite"),
    ("parsons.donorbox.donorbox", "Donorbox"),
    ("parsons.empower.empower", "Empower"),
    ("parsons.facebook_ads.facebook_ads", "FacebookAds"),
    ("parsons.formstack.formstack", "Formstack"),
    ("parsons.freshdesk.freshdesk", "Freshdesk"),
    ("parsons.geocode.census_geocoder", "CensusGeocoder"),
    ("parsons.github.github", "GitHub"),
    ("parsons.google.google_admin", "GoogleAdmin"),
    ("parsons.google.google_bigquery", "GoogleBigQuery"),
    ("parsons.google.google_civic", "GoogleCivic"),
    ("parsons.google.google_cloud_storage", "GoogleCloudStorage"),
    ("parsons.google.google_docs", "GoogleDocs"),
    ("parsons.google.google_drive", "GoogleDrive"),
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
    ("parsons.quickbooks.quickbookstime", "QuickBooksTime"),
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
        module = importlib.import_module(module_path)
        globals()[connector_name] = getattr(module, connector_name)
        __all__.append(connector_name)
    except ImportError as e:
        logger.debug(f"Could not import {module_path}.{connector_name} with {e}; skipping")

if TYPE_CHECKING:
    # ruff: noqa: F401
    # This block is seen by IDEs (PyCharm, VS Code) but ignored at runtime.
    # Add new connectors here, along with in the for loop below
    from parsons.actblue.actblue import ActBlue
    from parsons.action_builder.action_builder import ActionBuilder
    from parsons.action_kit.action_kit import ActionKit
    from parsons.action_network.action_network import ActionNetwork
    from parsons.airmeet.airmeet import Airmeet
    from parsons.airtable.airtable import Airtable
    from parsons.alchemer.alchemer import Alchemer
    from parsons.alchemer.alchemer import Alchemer as SurveyGizmo
    from parsons.auth0.auth0 import Auth0
    from parsons.aws.s3 import S3
    from parsons.azure.azure_blob_storage import AzureBlobStorage
    from parsons.bill_com.bill_com import BillCom
    from parsons.bloomerang.bloomerang import Bloomerang
    from parsons.box.box import Box
    from parsons.braintree.braintree import Braintree
    from parsons.capitol_canary.capitol_canary import CapitolCanary
    from parsons.catalist.catalist import CatalistMatch
    from parsons.census.census import Census
    from parsons.civis.civisclient import CivisClient
    from parsons.community.community import Community
    from parsons.controlshift.controlshift import Controlshift
    from parsons.copper.copper import Copper
    from parsons.crowdtangle.crowdtangle import CrowdTangle
    from parsons.databases.database_connector import DatabaseConnector
    from parsons.databases.db_sync import DBSync
    from parsons.databases.discover_database import discover_database
    from parsons.databases.mysql.mysql import MySQL
    from parsons.databases.postgres.postgres import Postgres
    from parsons.databases.redshift.redshift import Redshift
    from parsons.databases.sqlite.sqlite import Sqlite
    from parsons.donorbox.donorbox import Donorbox
    from parsons.empower.empower import Empower
    from parsons.facebook_ads.facebook_ads import FacebookAds
    from parsons.formstack.formstack import Formstack
    from parsons.freshdesk.freshdesk import Freshdesk
    from parsons.geocode.census_geocoder import CensusGeocoder
    from parsons.github.github import GitHub
    from parsons.google.google_admin import GoogleAdmin
    from parsons.google.google_bigquery import GoogleBigQuery
    from parsons.google.google_civic import GoogleCivic
    from parsons.google.google_cloud_storage import GoogleCloudStorage
    from parsons.google.google_docs import GoogleDocs
    from parsons.google.google_drive import GoogleDrive
    from parsons.google.google_sheets import GoogleSheets
    from parsons.hustle.hustle import Hustle
    from parsons.mailchimp.mailchimp import Mailchimp
    from parsons.mobilecommons.mobilecommons import MobileCommons
    from parsons.mobilize_america.ma import MobilizeAmerica
    from parsons.nation_builder.nation_builder import NationBuilder
    from parsons.newmode.newmode import Newmode
    from parsons.ngpvan.van import VAN
    from parsons.notifications.gmail import Gmail
    from parsons.notifications.slack import Slack
    from parsons.notifications.smtp import SMTP
    from parsons.pdi.pdi import PDI
    from parsons.phone2action.p2a import Phone2Action
    from parsons.quickbase.quickbase import Quickbase
    from parsons.quickbooks.quickbookstime import QuickBooksTime
    from parsons.redash.redash import Redash
    from parsons.rockthevote.rtv import RockTheVote
    from parsons.salesforce.salesforce import Salesforce
    from parsons.scytl.scytl import Scytl
    from parsons.sftp.sftp import SFTP
    from parsons.shopify.shopify import Shopify
    from parsons.sisense.sisense import Sisense
    from parsons.targetsmart.targetsmart_api import TargetSmartAPI
    from parsons.targetsmart.targetsmart_automation import TargetSmartAutomation
    from parsons.turbovote.turbovote import TurboVote
    from parsons.twilio.twilio import Twilio
    from parsons.zoom.zoom import Zoom
