from parsons import Table
from requests import request
from parsons.utilities import check_env
import datetime
from parsons.hustle.column_map import LEAD_COLUMN_MAP
import logging

logger = logging.getLogger(__name__)

HUSTLE_URI = 'https://api.hustle.com/v1/'
PAGE_LIMIT = 1000


class Hustle(object):

    def __init__(self, client_id, client_secret):

        self.uri = HUSTLE_URI
        self.client_id = check_env.check('HUSTLE_CLIENT_ID', client_id)
        self.client_secret = check_env.check('HUSTLE_CLIENT_SECRET', client_secret)
        self.auth_token = self._get_auth_token(client_id, client_secret)

    def _get_auth_token(self, client_id, client_secret):
        # Generate a temporary authorization token

        args = {client_id: client_id, client_secret: client_secret}

        r = self._request(endpoint='oauth/token', req_type='POST', args=args)

        self.auth_token = r[0]['access_token']
        self.token_expiration = datetime.datetime.now() + datetime.timedelta(seconds=7200)
        logger.debug("Authentication token generated")

    def _token_check(self):
        # Tokens are only valid for 7200 seconds. This checks to make sure that it has
        # not expired and generated another one if it has.

        logger.debug("Checking token expiration.")
        if datetime.datetime.now() >= self.token_expiration:

            logger.info("Refreshing authentication token.")
            self._get_auth_token(self.client_id, self.client_secret)

        else:

            pass

    def _request(self, endpoint, req_type='GET', args=None, payload=None, raise_on_error=True):

        url = self.uri + endpoint

        self._token_check()

        headers = f'Authorization: Bearer {self.auth_token}'

        parameters = {'limit': PAGE_LIMIT}

        if args:
            parameters.update(args)

        r = request(req_type, url, params=parameters, payload=payload, headers=headers)

        self._error_check(r, raise_on_error)

        result = [r.json()['items']]

        # Pagination
        while r.json['pagination']['hasNextPage'] == 'true':

            parameters['cursor'] = r.json['pagination']['cursor']
            r = request(req_type, url, params=args, payload=payload, headers=headers)
            result.append(r.json()['items'])
            self._error_check(r, raise_on_error)

        return r

    def _error_check(self, r, raise_on_error):
    	# Check for errors

        if r.status_code == 200:

            logger.debug(r.json())
            return None

        if raise_on_error:

            logger.info(r.json())
            r.raise_for_status()
            return None

        else:

            logger.info(r.json())
            return None

    def create_lead(self, group_id, first_name, phone_number, email=None, notes=None,
                    follow_up=None, custom_fields=None, tag_id=None):
        """
        Create a single lead.

        `Args:`
            group_id: str
                The group id to store the lead
            first_name: str
                The first name of the lead
            phone_number: str
                The phone number of the lead
            email: str
                The email address of the lead
            notes: str
                The notes for the lead
            follow_up: str
                Follow up for the lead
            custom_fields: dict
                A dictionary of custom fields, with key as the value name, and 
                value as the value.
        `Returns:`
                ``None``
        """

        # To Do: Check that you can send empty args
        # To Do: Find out if there is any error checking for the values in creating leads
        #		 e.g. phone number validation or string character limits.
        # To Do: Check that custom fields are just dicts - or what they are

        endpoint = f'groups/{group_id}/leads'

        lead = {'firstName': first_name,
                'lastName': last_name,
                'email': email,
                'phone_number': phone_number,
                'notes': notes,
                'follow_up': follow_up,
                'custom_fields': custom_fields,
                'tagIds': tag_id
                }

        logger.debug('Generating lead for {first_name} {last_name}.')
        return self_.request(endpoint, req_type="POST", payload=lead)

    def create_leads(self, table, group_id=None):
        """
        Create multiple leads. All unrecognized fields will be passed as custom fields.

        `Args:`
            table: Parsons table
                A Parsons table containing leads
            group_id:
                The group id for the leads. If ``None``, must be passed as a column
                value.
        `Returns:`
            ``None``
        """

        table.map_columns(LEAD_COLUMN_MAP)

        arg_list = ['first_name', 'last_name', 'email', 'phone_number', 'follow_up',
                    'tag_id', 'group_id']

        for row in table:

            lead = {'group_id': group_id}
            custom_fields = {}

            # Check for column names that map to arguments, if not assign
            # to custom fields
            for k, v in row.items():
                if k in arg_list:
                    lead[k] == v
                else:
                    custom_fields[k] == v

            # Group Id check
            if not group_id and 'group_id' not in table.columns:
                raise ValueError('Group Id must be passed as an argument or a column value.')
            if group_id:
                lead['group_id'] == group_id

            self.create_lead(**lead)

        logger.info("Created {table.num_rows} leads.")
