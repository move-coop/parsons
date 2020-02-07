# Provide shortcuts to importing Parsons submodules
# The try...except pattern allows installations with --no-deps
# and then importing from specific libraries without parsons
# breaking if dependent libraries are not available.

try:
    from parsons.ngpvan.van import VAN
except ImportError:
    VAN = None

try:
    from parsons.targetsmart.targetsmart_api import TargetSmartAPI
except ImportError:
    TargetSmartAPI = None

try:
    from parsons.targetsmart.targetsmart_automation import TargetSmartAutomation
except ImportError:
    TargetSmartAutomation = None

try:
    from parsons.databases.redshift.redshift import Redshift
except ImportError:
    Redshift = None

try:
    from parsons.aws.s3 import S3
except ImportError:
    S3 = None

try:
    from parsons.civis.civisclient import CivisClient
except ImportError:
    CivisClient = None

try:
    from parsons.etl.table import Table
except ImportError:
    Table = None

try:
    from parsons.notifications.gmail import Gmail
except ImportError:
    Gmail = None

try:
    from parsons.google.google_civic import GoogleCivic
except ImportError:
    GoogleCivic = None

try:
    from parsons.google.google_sheets import GoogleSheets
except ImportError:
    GoogleSheets = None

try:
    from parsons.google.google_cloud_storage import GoogleCloudStorage
except ImportError:
    GoogleCloudStorage = None

try:
    from parsons.google.google_bigquery import GoogleBigQuery
except ImportError:
    GoogleBigQuery = None

try:
    from parsons.phone2action.p2a import Phone2Action
except ImportError:
    Phone2Action = None

try:
    from parsons.mobilize_america.ma import MobilizeAmerica
except ImportError:
    MobilizeAmerica = None

try:
    from parsons.facebook_ads.facebook_ads import FacebookAds
except ImportError:
    FacebookAds = None

try:
    from parsons.notifications.slack import Slack
except ImportError:
    Slack = None

try:
    from parsons.turbovote.turbovote import TurboVote
except ImportError:
    TurboVote = None

try:
    from parsons.sftp.sftp import SFTP
except ImportError:
    SFTP = None

try:
    from parsons.action_kit.action_kit import ActionKit
except ImportError:
    ActionKit = None

try:
    from parsons.geocode.census_geocoder import CensusGeocoder
except ImportError:
    CensusGeocoder = None

try:
    from parsons.airtable.airtable import Airtable
except ImportError:
    Airtable = None

try:
    from parsons.copper.copper import Copper
except ImportError:
    Copper = None

try:
    from parsons.crowdtangle.crowdtangle import CrowdTangle
except ImportError:
    CrowdTangle = None

try:
    from parsons.hustle.hustle import Hustle
except ImportError:
    Hustle = None

try:
    from parsons.twilio.twilio import Twilio
except ImportError:
    Twilio = None

try:
    from parsons.salesforce.salesforce import Salesforce
except ImportError:
    Salesforce = None

try:
    from parsons.databases.postgres.postgres import Postgres
except ImportError:
    Postgres = None

try:
    from parsons.freshdesk.freshdesk import Freshdesk
except ImportError:
    Freshdesk = None


__all__ = [
    'VAN',
    'TargetSmartAPI',
    'TargetSmartAutomation',
    'Redshift',
    'S3',
    'CivisClient',
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
    'CrowdTangle',
    'Hustle',
    'Twilio',
    'Salesforce',
    'Postgres',
    'Freshdesk'
    ]

# Define the default logging config for Parsons and its submodules. For now the
# logger gets a StreamHandler by default. At some point a NullHandler may be more
# appropriate, so the end user must decide on logging behavior.
import logging
import os
logger = logging.getLogger(__name__)
_handler = logging.StreamHandler()
_formatter = logging.Formatter('%(module)s %(levelname)s %(message)s')
_handler.setFormatter(_formatter)
logger.addHandler(_handler)
if os.environ.get('TESTING'):
    # Log less stuff in automated tests
    logger.setLevel('WARNING')
else:
    logger.setLevel('INFO')
