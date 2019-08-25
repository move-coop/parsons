"""Mobile Commons API."""

from parsons.mobile_commons.mobile_commons_connector\
    import MobileCommonsConnector
from parsons.mobile_commons.campaigns import Campaigns
from parsons.mobile_commons.profiles import Profiles
from parsons.mobile_commons.groups import Groups
import logging

logger = logging.getLogger(__name__)


class MobileCommons(Campaigns, Profiles, Groups):
    """Initialize the MobileCommons class.

    `Args:`
        username : str
            The username for a mobile commons account with API permissions.
            If it's not passed in, it will attempt to get it from the
            environement, MC_USER.
        password: str
            The password associated with the username. If it's not passed
            in, it will attempt to get it from the environement, MC_PASS.
        company: str
            Specify which account/company you want to use for this session.
            If you leave it off, your default account will be used.
        uri: str
            Base uri to make api calls.
    """

    def __init__(self, username=None, password=None, company=None,
                 uri='https://secure.mcommons.com/api/'):

        self.connection = MobileCommonsConnector(
            username=username,
            password=password,
            company=company,
            uri=uri)
