from parsons import Table
from requests import request
from parsons.utilities import check_env, json_format
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
        self.token_expiration = None
        self._get_auth_token(client_id, client_secret)

    def _get_auth_token(self, client_id, client_secret):
        # Generate a temporary authorization token

        data = {'client_id': client_id,
                'client_secret': client_secret,
                'grant_type': 'client_credentials'}

        r = request('POST', self.uri + 'oauth/token', data=data)
        logger.debug(r.json())

        self.auth_token = r.json()['access_token']
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

        headers = {'Authorization': f'Bearer {self.auth_token}'}

        parameters = {'limit': PAGE_LIMIT}

        if args:
            parameters.update(args)

        r = request(req_type, url, params=parameters, json=payload, headers=headers)

        self._error_check(r, raise_on_error)

        # If a single item return the dict
        if 'items' not in r.json().keys():

            return r.json()

        else:
            result = r.json()['items']

        # Pagination
        while r.json()['pagination']['hasNextPage'] == 'true':

            parameters['cursor'] = r.json['pagination']['cursor']
            r = request(req_type, url, params=parameters, headers=headers)
            self._error_check(r, raise_on_error)
            result.append(r.json()['items'])

        return result

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

    def get_agents(self, group_id):
        """
        Get a list of agents.

        `Args:`
            group_id: str
                The group id.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        return Table(self._request(f'/groups/{group_id}/agents'))

    def get_agent(self, agent_id):
        """
        Get a single agent.

        `Args:`
            agent_id: str
                The agent id.
        `Returns:`
            dict
        """

        return Table(self._request(f'/agents/{agent_id}'))

    def create_agent(self, group_id, name, full_name, phone_number, send_invite=False, email=None):
        """
        Create an agent.
        """

        agent = {'groupId': group_id,
                 'name': name,
                 'full_name': email,
                 'phone_number': phone_number,
                 'sendInvite': send_invite,
                 'email': email}

        # Remove empty args in dictionary
        agent = json_format.remove_empty_keys(agent)

        logger.debug('Generating {full_name} agent.')
        return self._request(f'groups/{group_id}/agent', req_type="POST", payload=agent)

    def get_organizations(self):
        """
        Get organizations.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        return Table(self._request('organizations'))

    def get_organization(self, organization_id):
        """
        Get a single organization.

        `Args:`
            organization_id: str
                The organization id.
        `Returns:`
            dict
        """

        return self._request(f'organizations/{organization_id}')

    def get_groups(self, organization_id):
        """
        Get groups.

        `Args:`
            organization_id: str
                Filter by organization id.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        return Table(self._request(f'organizations/{organization_id}/groups'))

    def get_group(self, group_id):
        """
        Get a single group.

        `Args:`
            group_id: str
                The group id.
        `Returns:`
            dict
        """

        return self._request(f'groups/{group_id}')

    def get_lead(self, lead_id):
        """
        Get a single lead..

        `Args`:
            lead_id: str
                The lead id.
        `Returns:`
            dict
        """

        logger.info(f'Retrieving {lead_id} lead.')
        return self._request(f'leads/{lead_id}')

    def get_leads(self, organization_id=None, group_id=None):
        """
        Get leads. One of ``organization_id`` and ``group_id`` must be passed
        as an argument. If both are passed, an error will be raised.

        `Args:`
            organization_id: str
                The organization id.
            group_id: str
                The group id.
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

    def create_lead(self, group_id, phone_number, first_name, last_name=None, email=None,
                    notes=None, follow_up=None, custom_fields=None, tag_ids=None):
        """
        Create a lead.

        `Args:`
            group_id: str
                The group id to assign the leads.
            first_name: str
                The first name of the lead.
            phone_number: str
                The phone number of the lead.
            last_name: str
                The last name of the lead.
            email: str
                The email address of the lead.
            notes: str
                The notes for the lead.
            follow_up: str
                Follow up for the lead.
            custom_fields: dict
                A dictionary of custom fields, with key as the value name, and
                value as the value.
            tag_ids: list
                A list of tag ids.
        `Returns:`
                ``None``
        """

        # To Do: Check that you can send empty args

        lead = {'firstName': first_name,
                'lastName': last_name,
                'email': email,
                'phoneNumber': phone_number,
                'notes': notes,
                'followUp': follow_up,
                'customFields': custom_fields,
                'tagIds': tag_ids
                }

        # Remove empty args in dictionary
        lead = json_format.remove_empty_keys(lead)

        logger.debug('Generating lead for {first_name} {last_name}.')
        return self._request(f'groups/{group_id}/leads', req_type="POST", payload=lead)

    def create_leads(self, table, group_id=None):
        """
        Create multiple leads. All unrecognized fields will be passed as custom fields. Column
        names must map to the following names.

        .. list-table::
            :widths: 20 80
            :header-rows: 1

            * - Column Name
              - Valid Column Names
            * - first_name
              - ``first_name``, ``first``, ``fn``, ``firstname``
            * - last_name
              - ``last_name``, ``last``, ``ln``, ``lastname``
            * - phone_number
              - ``phone_number``, ``phone``, ``cell``, ``phonenumber``
            * - email
              - ``email``, ``email_address``, ``emailaddress``
            * - follow_up
              - ``follow_up``, ``followup``

        `Args:`
            table: Parsons table
                A Parsons table containing leads
            group_id:
                The group id to assign the leads. If ``None``, must be passed as a column
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
                    lead[k] = v
                else:
                    custom_fields[k] = v

            lead['custom_fields'] = custom_fields

            # Group Id check
            if not group_id and 'group_id' not in table.columns:
                raise ValueError('Group Id must be passed as an argument or a column value.')
            if group_id:
                lead['group_id'] == group_id

            self.create_lead(**lead)

        logger.info(f"Created {table.num_rows} leads.")

    def update_lead(self, lead_id, first_name=None, last_name=None, email=None,
                    global_opt_out=None, notes=None, follow_up=None, tag_ids=None):
        """
        Update a lead.

        `Args`:
            lead_id: str
                The lead id
            first_name: str
                The first name of the lead
            last_name: str
                The last name of the lead
            email: str
                The email address of the lead
            global_opt_out: boolean
                Opt out flag for the lead
            notes: str
                The notes for the lead
            follow_up: str
                Follow up for the lead
        """

        lead = {'leadId': lead_id,
                'firstName': first_name,
                'lastName': last_name,
                'email': email,
                'globalOptedOut': global_opt_out,
                'notes': notes,
                'followUp': follow_up,
                'tagIds': tag_ids}

        # Remove empty args in dictionary
        lead = json_format.remove_empty_keys(lead)

        logger.debug('Updating lead for {first_name} {last_name}.')
        return self._request(f'leads/{lead_id}', req_type="PUT", payload=lead)
