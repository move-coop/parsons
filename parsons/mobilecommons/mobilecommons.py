from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector
from parsons import Table
from bs4 import BeautifulSoup
from requests import HTTPError
import xmltodict
import logging

logger = logging.getLogger(__name__)

MC_URI = 'https://secure.mcommons.com/api/'

class MobileCommons:
    """
        Instantiate the MobileCommons class.

        `Args:`
            username: str
                A valid email address connected toa  MobileCommons accouont. Not required if
                ``MOBILECOMMONS_USERNAME`` env variable is set.
            password: str
                Password associated with zoom account. Not required if ``MOBILECOMMONS_PASSWORD``
                env variable set.
            companyid: str
                The company id of the MobileCommons organization to connect to. Not required if
                username and password are for an account associated with only one MobileCommons
                organization.
        """
    def __init__(self, username=None, password=None, companyid=None):
        self.username = check_env.check('MOBILECOMMONS_USERNAME', username)
        self.password = check_env.check('MOBILECOMMONS_PASSWORD', password)
        self.companyid_param = f'?company={companyid}' if companyid else ''
        self.client = APIConnector(uri=MC_URI, auth=(self.username,self.password))

    def get_broadcasts(self, start_time=None, end_time=None, status=None, campaign_id=None,
                       limit=None):

        broadcast_table = Table()

        #MC page limit is 1000 for broadcasts
        page_limit = 20 if limit > 20 or limit is None else limit
        params = f'limit={str(page_limit)}'
        response = self.client.request('broadcasts' + self.companyid_param, 'GET', params=params)
        if response.status_code == 200:
            response_dict = xmltodict.parse(response.text, attr_prefix='', cdata_key='',
                                            dict_constructor=dict)
            response_table = Table(response_dict['response']['broadcasts']['broadcast'])
            response_table.unpack_dict('campaign')
            broadcast_table.concat(response_table)
            page_count = int(response_dict['response']['broadcasts']['page_count'])
            i = 2
            while i <= page_count:
                page_params = params + f'&page={str(i)}'
                response = self.client.request('broadcasts' + self.companyid_param, 'GET',
                                               params=page_params)
                response_dict = xmltodict.parse(response.text, attr_prefix='', cdata_key='',
                                                dict_constructor=dict)
                response_table = Table(response_dict['response']['broadcasts']['broadcast'])
                broadcast_table.concat(response_table)
                i += 1
        else:
            error = f'Response Code {str(response.status_code)}'
            error_html = BeautifulSoup(response.text, features='html.parser')
            error += '\n' + error_html.h4.next
            error += '\n' + error_html.p.next
            raise HTTPError(error)

        return broadcast_table
