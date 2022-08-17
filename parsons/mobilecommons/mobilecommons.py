from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector
from parsons import Table
from bs4 import BeautifulSoup
from requests import HTTPError
import xmltodict
import logging
import math

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

    def mc_get_request(self, endpoint, data_key, params, cols_to_unpack, limit):
        final_table = Table()
        page_limit = 1000 if limit > 1000 or limit is None else limit
        logger.info(f'Working on fetching first {page_limit} rows. '
                    f'Each 1000 rows will take aproximately 40 seconds to fetch.')
        params += f'limit={str(page_limit)}'
        response = self.client.request(endpoint + self.companyid_param, 'GET', params=params)
        if response.status_code == 200:
            response_dict = xmltodict.parse(response.text, attr_prefix='', cdata_key='',
                                            dict_constructor=dict)
            response_table = Table(response_dict['response'][endpoint][data_key])
            for col in cols_to_unpack:
                response_table.unpack_dict(col)
            final_table.concat(response_table)
            avail_pages = int(response_dict['response'][endpoint]['page_count'])
            req_pages = math.ceil(limit/page_limit)
            pages_to_get = avail_pages if avail_pages < req_pages else req_pages
            i = 2
            while i <= pages_to_get:
                page_params = params + f'&page={str(i)}'
                logger.info(f'Fetching rows {str(i*page_limit)} - {str((i+1)*page_limit)} '
                            f'of {limit}')
                response = self.client.request(endpoint + self.companyid_param, 'GET',
                                               params=page_params)
                response_dict = xmltodict.parse(response.text, attr_prefix='', cdata_key='',
                                                dict_constructor=dict)
                response_table = Table(response_dict['response'][endpoint][data_key])
                final_table.concat(response_table)
                i += 1
        else:
            error = f'Response Code {str(response.status_code)}'
            error_html = BeautifulSoup(response.text, features='html.parser')
            error += '\n' + error_html.h4.next
            error += '\n' + error_html.p.next
            raise HTTPError(error)

        return final_table

    def get_broadcasts(self, start_time=None, end_time=None, status=None, campaign_id=None,
                         limit=None):
        params = ''
        return self.mc_get_request(endpoint='broadcasts', data_key='broadcast',
                                   params=params, cols_to_unpack=['campaign'], limit=limit)
