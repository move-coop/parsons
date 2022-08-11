from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector
from parsons import Table
import logging

logger = logging.getLogger(__name__)

MC_URI = 'https://secure.mcommons.com/api/'

class MobileCommons:
    """
        Instantiate the MobileCommons class.

        `Args:`
            username: str
                A valid email address connected toa  MobileCommons accouont. Not required if
                ``MOBILE_COMMONS_USERNAME`` env variable is set.
            password: str
                Password associated with zoom account. Not required if ``MOBILE_COMMONS_PASSWORD``
                env variable set.
            companyid: str
                The company id of the MobileCommons organization to connect to. Not required if
                username and password are for an account associated with only one MobileCommons
                organization.
        """
    def __init__(self, username=None, password=None, companyid=None):
        self.username = check_env.check('MOBILE_COMMONS_USERNAME', username)
        self.password = check_env.check('MOBILE_COMMONS_USERNAME', password)
        self.companyid = companyid
        self.client = APIConnector(uri=MC_URI, auth=(self.username,self.password))


