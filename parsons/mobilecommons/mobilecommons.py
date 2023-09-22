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
            params: dict
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

        # Make get call and parse XML into list of dicts
        response_dict = self.parse_get_request(endpoint=endpoint, params=params)

        # if there's only one row, then it is returned as a dict, otherwise as a list
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

        # MC GET responses sometimes include a page_count parameter to indicate how many pages
        # are left, but when the response doesn't it does include a 'num' parameter that, when
        # you reach an empty page, equals 0. The following logic attempts to handle both cases
        try:
            avail_pages = int(response_dict['response'][first_data_key]['page_count'])
            total_records = avail_pages * page_limit
            page_indicator = 'page_count'

        except KeyError:
            page_indicator = 'num'
            # If page_count is not available, we cannot calculate total_records
            total_records = float('inf')

        # Go fetch other pages of data
        page = 1
        empty_page = False
        while final_table.num_rows < (limit or total_records) and not empty_page:
            page += 1
            page_params = {'page': str(page), **params}
            logger.info(f'Fetching rows {(page - 1) * page_limit + 1} - {(page)*page_limit} '
                        f'of {limit}')
            # Send get request
            response_dict = self.parse_get_request(endpoint=endpoint, params=page_params)
            # Check to see if page was empty if num parameter is available
            if page_indicator == 'num':
                empty_page = int(response_dict['response'][first_data_key]['num']) > 0

            if not empty_page:
                # Extract data
                response_table = Table(response_dict['response'][first_data_key][second_data_key])
                # Append to final table
                final_table.concat(response_table)
                final_table.materialize()

        return Table(final_table[:limit])

    def check_response_status_code(self, response):
        if response.status_code != 200:
            error = f'Response Code {str(response.status_code)}'
            error_html = BeautifulSoup(response.text, features='html.parser')
            error += '\n' + error_html.h4.next
            error += '\n' + error_html.p.next
            raise HTTPError(error)

    def parse_get_request(self, endpoint, params):
        response = self.client.request(endpoint, 'GET', params=params)

        # If there's an error with initial response, raise error
        self.check_response_status_code(response)

        # If good response, compile data into final_table
        # Parse xml to nested dictionary and load to parsons table
        response_dict = xmltodict.parse(response.text, attr_prefix='', cdata_key='',
                                        dict_constructor=dict)
        return response_dict

    def mc_post_request(self, endpoint, params):
        """
        A function for POST requests that handles MobileCommons xml responses

        `Args:`
            endpoint: str
                The endpoint, which will be appended to the base URL for each request
            params: dict
                Parameters to be passed into GET request
        `Returns:`
            xml response parsed into list or dictionary
        """

        response = self.client.request(endpoint, 'POST', params=params)

        response_dict = xmltodict.parse(response.text, attr_prefix='', cdata_key='',
                                        dict_constructor=dict)
        if response_dict['response']['success'] == 'true':
            return response_dict['response']
        else:
            raise HTTPError(response_dict['response']['error'])


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


    def create_profile(self, phone, first_name=None, last_name=None, zip=None, addressline1=None,
                       addressline2=None, city=None, state=None, opt_in_path_id=None):
        """
        A function for creating a single MobileCommons profile

        `Args:`
            phone: str
                Phone number to assign profile
            first_name: str
                Profile first name
            last_name: str
                Profile last name
            zip: str
                Profile 5 digit postal code
            addressline1: str
                Profile address line 1
            addressline2: str
                Profile address line 2
            city: str
                Profile city
            state: str
                Profile state
            opt_in_path_id: str
                ID of the opt-in path to send new profile through. This will determine the welcome
                text they receive.

        `Returns:`
            ID of created profile
        """

        params = {
            'phone_number': phone,
            'first_name': first_name,
            'last_name': last_name,
            'postal_code': zip,
            'street1': addressline1,
            'street2': addressline2,
            'city': city,
            'state': state,
            'opt_in_path_id': opt_in_path_id,
            **self.default_params
        }
        
        response = self.mc_post_request('profile_update', params=params)
        return response['profile']['id']