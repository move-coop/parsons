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
    """
    Instantiate Hustle Class

    `Args:`
        client_id:
            The client id provided by Hustle.
        client_secret:
            The client secret provided by Hustle.
    `Returns:`
        Hustle Class
    """

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
        logger.info("Authentication token generated")

    def _token_check(self):
        # Tokens are only valid for 7200 seconds. This checks to make sure that it has
        # not expired and generate another one if it has.

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
            r = request(req_type, url, params=parameters, payload=payload, headers=headers)
            self._error_check(r, raise_on_error)
            result.append(r.json()['items'])

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

    def create_lead(self, group_id, first_name, phone_number, last_name=None, email=None,
                    notes=None, follow_up=None, custom_fields=None, tag_id=None):
        """
        Create a single lead.

        `Args:`
            group_id: str
                The group id to store the lead
            first_name: str
                The first name of the lead
            phone_number: str
                The phone number of the lead
            last_name: str
                The last name of the lead
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
        # e.g. phone number validation or string character limits.
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
        return self._request(endpoint, req_type="POST", payload=lead)

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

        logger.info(f"Created {table.num_rows} leads.")

    def update_lead(self, lead_id, first_name=None, last_name=None, email=None,
                    global_opt_out=None, notes=None, follow_up=None, tag_ids=None):

        endpoint = f'leads/{lead_id}'

        lead = {'leadId': lead_id,
                'firstName': first_name,
                'lastName': last_name,
                'email': email,
                'globalOptOut': global_opt_out,
                'notes': notes,
                'followUp': follow_up,
                'tagIds': tag_ids}

        # Remove empty args in dictionary
        for k, v in lead.items():
            if not v:
                del lead[k]

        logger.debug('Updating lead for {first_name} {last_name}.')
        return self._request(endpoint, req_type="PUT", payload=lead)

    def get_lead(self, lead_id):
        """
        Get lead metadata.

        `Args`:
            lead_id: str
                The lead id.
        `Returns:`
            dict
        """

        endpoint = f'leads/{lead_id}'
        logger.info('Retrieving {lead_id} lead.')
        return self._request(endpoint)

    def get_leads(self, organization_id=None, group_id=None):
        """
        Get leads metadata. One of ``organization_id`` and ``group_id`` must be passed
        as an argument. If both are passed, an error will be raised.

        `Args:`
            organization_id: str
                The organization id
            group_id:
                The group id
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        if organization_id is None and group_id is None:
            raise ValueError('Either organization_id or group_id required.')

        if organization_id is not None and group_id is not None:
            raise ValueError('Only one of organization_id and group_id may be populated.')

        if organization_id:
            endpoint = f'organizations/{organization_id}/leads'
            logger.info(f'Retrieving {organization_id} organization leads.')
        if group_id:
            endpoint = f'groups/{group_id}/leads'
            logger.info(f'Retrieving {group_id} group leads.')

        return Table(self._request(endpoint))


