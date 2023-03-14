"""
Figure out what to do about campaign subscribers, which has page_count key. Also find out
if limit is a page count limit, or a limit on the total number of rows returned.
"""

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
format_date = lambda x: parse_date(x).strftime(DATE_FMT) if x is not None else None

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

    def mc_get_request(self, endpoint, first_data_key, second_data_key, params,
                       elements_to_unpack=None, limit=None):
        """
        A function for GET requests that handles MobileCommons xml responses and pagination

        `Args:`
            endpoint: str
                The endpoint, which will be appended to the base URL for each request
            first_data_key: str
                The first key used to extract the desired data from the response dictionary derived
                from the xml response. E.g. 'broadcasts'
            second_data_key: str
                The second key used to extract the desired data from the response dictionary derived
                from the xml response. The value of this key is a list of values. E.g. 'broadcast'
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
            data = response_dict['response'][first_data_key][second_data_key]
            if isinstance(data, dict):
                data = [data]
            response_table = Table(data)
            # Unpack any specified elements
            if elements_to_unpack:
                for col in elements_to_unpack:
                    response_table.unpack_dict(col)
            # Append to final table
            final_table.concat(response_table)
            final_table.materialize()
            # Calculate how many more pages we need to get in order to reach user set record limit
            req_pages = math.ceil(limit/1000)
            # Calculate how many records we need from last page to match limit exactly
            final_page_limit = limit % 1000
            # MC endpoints don't consistently  include page counts, and therefore must make calls
            # until number of records on a page is 0
            num = int(response_dict['response'][first_data_key]['num'])
            # Go fetch other pages of data
            page = 1
            while page < req_pages and num > 0:
                page += 1
                page_params = {'page': str(page), **params}
                logger.info(f'Fetching rows {page*page_limit} - {(page+1)*page_limit} '
                            f'of {limit}')
                response = self.client.request(endpoint, 'GET', params=page_params)
                response_dict = xmltodict.parse(response.text, attr_prefix='', cdata_key='',
                                                dict_constructor=dict)
                # Check to see if page was empty
                num = int(response_dict['response'][first_data_key]['num'])
                if num > 0:
                    # Extract data
                    response_table = Table(response_dict['response'][first_data_key][second_data_key])
                    # If this is the last page, grab only subset of data
                    if page == req_pages:
                        response_table = Table(response_table.table.rowslice(final_page_limit))
                    # Append to final table
                    final_table.concat(response_table)
                    final_table.materialize()

        return final_table

    def get_broadcasts(self, first_date=None, last_date=None, status=None, campaign_id=None,
                       limit=None):
        """
        A function for get broadcasts

        `Args:`
            first_date: str
                The date of the earliest possible broadcast you'd like returned.
            last_date: str
                The date of the latest possible broadcast you'd like returned.
            status: str
                'draft', 'scheduled', or 'generated'
            campaign_id: int
                Specify to return broadcasts from a specific campaign
            limit: int
                Max rows you want returned

        `Returns:`
            Parsons table with requested broadcasts
        """

        params = {
            'start_time': format_date(first_date),
            'end_time': format_date(last_date),
            'campaign_id': campaign_id,
            'status': status,
            **self.default_params
        }

        return self.mc_get_request(endpoint='broadcasts', first_data_key='broadcasts',
                                   second_data_key='broadcast', params=params,
                                   elements_to_unpack=['campaign'], limit=limit)


    def get_campaign_subscribers(self, campaign_id: int, first_date: str=None, last_date: str=None,
                                 opt_in_path_id: int=None, limit: int=None):
        """
        A function for getting subscribers of a specified campaign

        `Args:`
            campaign_id: int
                The campaign for which you'd like to get subscribers. You can get this from the url
                of the campaign's page after select a campaign at
                https://secure.mcommons.com/campaigns
            first_date: str
                The date of the earliest possible subscription returned.
            last_date: str
                The date of the latest possible subscription you'd like returned.
            opt_in_path_id: int
                Optional parameter to narrow results to on particular opt-in path. You can get this
                from the url of the opt in paths page https://secure.mcommons.com/opt_in_paths
            limit: int
                Max rows you want returned

        `Returns:`
            Parsons table with requested broadcasts
        """

        params = {
            'campaign_id': campaign_id,
            'from': format_date(first_date),
            'to': format_date(last_date),
            'opt_in_path_id': opt_in_path_id,
            **self.default_params
        }

        return self.mc_get_request(endpoint='campaign_subscribers', first_data_key='subscriptions',
                                   second_data_key='sub', params=params, limit=limit)


    def get_profiles(self, phones: list=None, first_date: str = None, last_date: str = None,
                     include_custom_columns: bool=False, include_subscriptions: bool=False,
                     limit: int = None):
        """
        A function for getting profiles, which are MobileCommons people records

        `Args:`
            phones: list
                A list of phone numbers including country codes for which you want profiles returned
                MobileCommons claims to recognize most formats.
            first_date: str
                The date of the earliest possible subscription returned.
            last_date: str
                The date of the latest possible subscription you'd like returned.
            include_custom_columns: bool
                Optional parameter to that, if set to True, will return custom column values for
                profiles as a list of dictionaries contained within a column.
            include_subscriptions: bool
                Optional parameter to that, if set to True, will return a list of campaigns a
                given profile is subscribed to in a single column
            limit: int
                Max rows you want returned

        `Returns:`
            Parsons table with requested broadcasts
        """

        custom_cols = 'true' if include_custom_columns == True else 'false'
        subscriptions='true' if include_subscriptions == True else 'false'

        params = {
            'phone_number': phones,
            'from': format_date(first_date),
            'to': format_date(last_date),
            'include_custom_columns': custom_cols,
            'include_subscriptions': subscriptions,
            **self.default_params
        }

        return self.mc_get_request(endpoint='profiles', first_data_key='profiles',
                                   second_data_key='profile',
                                   elements_to_unpack=['source', 'address'], params=params,
                                   limit=limit)
