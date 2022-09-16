from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector
from parsons.utilities.datetime import parse_date
from parsons import Table
from bs4 import BeautifulSoup
from requests import HTTPError
import xmltodict
import logging
import math

logger = logging.getLogger(__name__)

MC_URI = 'https://secure.mcommons.com/api/'
DATE_FMT = '%Y-%m-%d'
format_date = lambda x: parse_date(x).strftime(DATE_FMT)

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
            company_id: str
                The company id of the MobileCommons organization to connect to. Not required if
                username and password are for an account associated with only one MobileCommons
                organization.
        """
    def __init__(self, username=None, password=None, company_id=None):
        self.username = check_env.check('MOBILECOMMONS_USERNAME', username)
        self.password = check_env.check('MOBILECOMMONS_PASSWORD', password)
        self.default_params = {'company': company_id} if company_id else {}
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
        page_limit = min((limit or 1000), 1000)
        params = {'limit': page_limit, **self.default_params, **params}

        logger.info(f'Working on fetching first {page_limit} rows. This can take a long time.')

        response = self.client.request(endpoint, 'GET', params=params)

        # If there's an error with initial response, raise error
        if response.status_code != 200:
            error = f'Response Code {str(response.status_code)}'
            error_html = BeautifulSoup(response.text, features='html.parser')
            error += '\n' + error_html.h4.next
            error += '\n' + error_html.p.next
            raise HTTPError(error)

        # If good response, compile data into final_table
        else:
            # Parse xml to nested dictionary and load to parsons table
            response_dict = xmltodict.parse(response.text, attr_prefix='', cdata_key='',
                                            dict_constructor=dict)
            # if there's only one row, then it is returned as a dict, otherwise is a list
            data = response_dict['response'][endpoint][data_key]
            if isinstance(data, dict):
                data = [data]
            response_table = Table(data)
            # Unpack any specified elements
            for col in elements_to_unpack:
                response_table.unpack_dict(col)
            # Append to final table
            final_table.concat(response_table)
            # Check to see if there are more pages and determine how many to retrieve
            avail_pages = int(response_dict['response'][endpoint]['page_count'])
            req_pages = math.ceil(limit/1000)
            pages_to_get = min(avail_pages, req_pages)
            # Go fetch other pages of data
            for i in range(2, pages_to_get + 1):
                page_params = {'page': str(i), **{params}}
                logger.info(f'Fetching rows {i*page_limit} - {(i+1)*page_limit} '
                            f'of {limit}')
                response = self.client.request(endpoint, 'GET', params=page_params)
                response_dict = xmltodict.parse(response.text, attr_prefix='', cdata_key='',
                                                dict_constructor=dict)
                response_table = Table(response_dict['response'][endpoint][data_key])
                final_table.concat(response_table)

        return final_table

    def get_broadcasts(self, start=None, end=None, status=None, campaign_id=None, limit=None):
        """
        A function for get broadcasts

        `Args:`
            start: str
                The date of the earliest possible broadcast you'd like returned.
            end: str
                The date of the latest possible broadcast you'd like returned.
            params: str
                Parameters to be passed into GET request
            status: str
                'draft', 'scheduled', or 'generated'
            campaign_id: int
                Specify to return broadcasts from a specific campaign

        `Returns:`
            Parsons table with requested broadcasts
        """

        params = {
            'start_time': format_date(start),
            'end_time': format_date(end),
            'campaign_id': campaign_id,
            'status': status,
            **self.default_params
        }

        return self.mc_get_request(endpoint='broadcasts', data_key='broadcast',
                                   params=params, elements_to_unpack=['campaign'], limit=limit)
