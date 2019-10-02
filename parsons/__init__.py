# Provide shortcuts to importing Parsons submodules
# Eg. This allows for: `from parsons import VAN`
from parsons.ngpvan.van import VAN
from parsons.targetsmart.targetsmart_api import TargetSmartAPI
from parsons.targetsmart.targetsmart_automation import TargetSmartAutomation
from parsons.mobile_commons.mobile_commons import MobileCommons
from parsons.databases.redshift.redshift import Redshift
from parsons.aws.s3 import S3
from parsons.civis.civisclient import CivisClient
from parsons.etl.table import Table
from parsons.notifications.gmail import Gmail
from parsons.google.google_civic import GoogleCivic
from parsons.google.google_sheets import GoogleSheets
from parsons.google.google_cloud_storage import GoogleCloudStorage
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
from parsons.crowdtangle.crowdtangle import CrowdTangle
from parsons.hustle.hustle import Hustle

__all__ = [
    'VAN',
    'TargetSmartAPI',
    'TargetSmartAutomation',
    'MobileCommons',
    'Redshift',
    'S3',
    'CivisClient',
    'Table',
    'Gmail',
    'GoogleCivic',
    'GoogleCloudStorage',
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
    'Hustle'
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
