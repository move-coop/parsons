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

    def mc_get_request(self, endpoint, data_key, params, elements_to_unpack, limit):
        """
        A function for GET requests that handles MobileCommons xml responses and pagination

        `Args:`
            endpoint: str
                The endpoint, which will be appended to the base URL for each request
            data_key: str
                The key used to extract the desired data from the response dictionary derived from
                the xml response
            params: str
                Parameters to be passed into GET request
            elements_to_unpack: list
                A list of elements that contain dictionaries to be unpacked into new columns in the
                final table
            limit: int
                The maximum number of rows to return
        `Returns:`
            Parsons table with requested data
        """

        # Create a table to compile results from different pages in
        final_table = Table()
        # Max page_limit is 1000 for MC
        page_limit = 1000 if limit > 1000 or limit is None else limit
        params += f'limit={str(page_limit)}'

        logger.info(f'Working on fetching first {page_limit} rows. This can take a long time.'
                    f'Each 1000 rows can take between 30-60 seconds to fetch.')

        response = self.client.request(endpoint + self.companyid_param, 'GET', params=params)

        # If good response, compile data into final_table
        if response.status_code == 200:
            # Parse xml to nested dictionary and load to parsons table
            response_dict = xmltodict.parse(response.text, attr_prefix='', cdata_key='',
                                            dict_constructor=dict)
            response_table = Table(response_dict['response'][endpoint][data_key])
            # Unpack any specified elements
            for col in elements_to_unpack:
                response_table.unpack_dict(col)
            # Append to final table
            final_table.concat(response_table)
            # Check to see if there are more pages and determine how many to retrieve
            avail_pages = int(response_dict['response'][endpoint]['page_count'])
            req_pages = math.ceil(limit/page_limit)
            pages_to_get = avail_pages if avail_pages < req_pages else req_pages
            # Go fetch other pages of data
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
        # If initial response is bad, raise error
        else:
            error = f'Response Code {str(response.status_code)}'
            error_html = BeautifulSoup(response.text, features='html.parser')
            error += '\n' + error_html.h4.next
            error += '\n' + error_html.p.next
            raise HTTPError(error)

        return final_table

    def get_broadcasts(self, start_time=None, end_time=None, status=None, campaign_id=None,
                         limit=None):
        """
        Retrieve broadcast data

        `Args:`
            :param start_time:
            :param end_time:
            :param status:
            :param campaign_id:
            :param limit:
            :return:
        """
        # Still working on compiling the params, but this function does work atm with no params specified
        params = ''
        return self.mc_get_request(endpoint='broadcasts', data_key='broadcast',
                                   params=params, elements_to_unpack=['campaign'], limit=limit)
