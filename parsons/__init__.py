import os
import logging

# Provide shortcuts to importing Parsons submodules

# If you want to be more targeted in your imports, you can set the PARSONS_SKIP_IMPORT_ALL
# environment variable and import classes directly from the Python module where they
# are defined.

if not os.environ.get('PARSONS_SKIP_IMPORT_ALL'):
    from parsons.ngpvan.van import VAN
    from parsons.targetsmart.targetsmart_api import TargetSmartAPI
    from parsons.targetsmart.targetsmart_automation import TargetSmartAutomation
    from parsons.databases.redshift.redshift import Redshift
    from parsons.databases.db_sync import DBSync
    from parsons.aws.s3 import S3
    from parsons.civis.civisclient import CivisClient
    from parsons.etl.table import Table
    from parsons.notifications.gmail import Gmail
    from parsons.google.google_civic import GoogleCivic
    from parsons.google.google_sheets import GoogleSheets
    from parsons.google.google_cloud_storage import GoogleCloudStorage
    from parsons.google.google_bigquery import GoogleBigQuery
    from parsons.phone2action.p2a import Phone2Action
    from parsons.mobilize_america.ma import MobilizeAmerica
    from parsons.facebook_ads.facebook_ads import FacebookAds
    from parsons.notifications.slack import Slack
    from parsons.turbovote.turbovote import TurboVote
    from parsons.sftp.sftp import SFTP
    from parsons.action_kit.action_kit import ActionKit
    from parsons.geocode.census_geocoder import CensusGeocoder
    from parsons.airtable.airtable import Airtable
    from parsons.copper.copper import Copper
    from parsons.controlshift.controlshift import Controlshift
    from parsons.crowdtangle.crowdtangle import CrowdTangle
    from parsons.hustle.hustle import Hustle
    from parsons.twilio.twilio import Twilio
    from parsons.salesforce.salesforce import Salesforce
    from parsons.databases.postgres.postgres import Postgres
    from parsons.freshdesk.freshdesk import Freshdesk
    from parsons.bill_com.bill_com import BillCom
    from parsons.newmode.newmode import Newmode
    from parsons.databases.mysql.mysql import MySQL
    from parsons.rockthevote.rtv import RockTheVote
    from parsons.mailchimp.mailchimp import Mailchimp
    from parsons.zoom.zoom import Zoom
    from parsons.action_network.action_network import ActionNetwork
    from parsons.pdi.pdi import PDI
    from parsons.azure.azure_blob_storage import AzureBlobStorage
    from parsons.github.github import GitHub
    from parsons.bloomerang.bloomerang import Bloomerang
    from parsons.box.box import Box
    from parsons.sisense.sisense import Sisense
    from parsons.alchemer.alchemer import SurveyGizmo, Alchemer
    from parsons.quickbase.quickbase import Quickbase
    from parsons.actblue.actblue import ActBlue

    __all__ = [
        'VAN',
        'TargetSmartAPI',
        'TargetSmartAutomation',
        'Redshift',
        'S3',
        'CivisClient',
        'DBSync',
        'Table',
        'Gmail',
        'GoogleCivic',
        'GoogleCloudStorage',
        'GoogleBigQuery',
        'GoogleSheets',
        'Phone2Action',
        'MobilizeAmerica',
        'FacebookAds',
        'Slack',
        'TurboVote',
        'SFTP',
        'ActionKit',
        'CensusGeocoder',
        'Airtable',
        'Copper',
        'Controlshift',
        'CrowdTangle',
        'Hustle',
        'Twilio',
        'Salesforce',
        'Postgres',
        'Freshdesk',
        'BillCom',
        'Newmode',
        'MySQL',
        'RockTheVote',
        'Mailchimp',
        'Zoom',
        'ActionNetwork',
        'PDI',
        'AzureBlobStorage',
        'GitHub',
        'Bloomerang',
        'Box',
        'Sisense',
        'SurveyGizmo',
        'Alchemer',
        'Quickbase',
        'ActBlue'
    ]

# Define the default logging config for Parsons and its submodules. For now the
# logger gets a StreamHandler by default. At some point a NullHandler may be more
# appropriate, so the end user must decide on logging behavior.

logger = logging.getLogger(__name__)
_handler = logging.StreamHandler()
_formatter = logging.Formatter('%(module)s %(levelname)s %(message)s')
_handler.setFormatter(_formatter)
logger.addHandler(_handler)

if os.environ.get('TESTING'):
    # Log less stuff in automated tests
    logger.setLevel('WARNING')
elif os.environ.get('DEBUG'):
    logger.setLevel('DEBUG')
else:
    logger.setLevel('INFO')
