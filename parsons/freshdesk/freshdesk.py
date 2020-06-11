from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector
import re
from parsons.etl import Table
import logging

logger = logging.getLogger(__name__)

PAGE_SIZE = 100


class Freshdesk():
    """
    Instantiate FreshDesk Class

    `Args:`
        domain:
            The subdomain of the FreshDesk account. Not required if ``FRESHDESK_DOMAIN``
            env variable set.
        api_key:
            The FreshDesk provided application key. Not required if ``FRESHDESK_API_KEY``
            env variable set.
    `Returns:`
        FreshDesk Class
    """

    def __init__(self, domain, api_key):

        self.api_key = check_env.check('FRESHDESK_API_KEY', api_key)
        self.domain = check_env.check('FRESHDESK_DOMAIN', domain)
        self.uri = f'https://{self.domain}.freshdesk.com/api/v2/'
        self.client = APIConnector(self.uri, auth=(self.api_key, 'x'))

    def get_request(self, endpoint, params=None, **kwargs):
        # Internal method to make a get request.

        base_params = {'per_page': PAGE_SIZE}

        if params:
            base_params.update(params)

        r = self.client.request(self.uri + endpoint, 'GET', params=base_params)
        self.client.validate_response(r)
        data = r.json()

        # Paginate
        while 'link' in r.headers.keys():
            logger.info(f'Retrieving another page of {PAGE_SIZE} records.')
            url = re.search('<(.*)>', r.headers['link']).group(1)
            r = self.client.request(url, 'GET', params=params)
            self.client.validate_response(r)
            data.extend(r.json())

        return data

    def transform_table(self, tbl, expand_custom_fields=None):
        # Internal method to transform a table prior to returning
        if tbl.num_rows > 0:
            tbl.move_column('id', 0)
            tbl.sort()
            if expand_custom_fields:
                tbl.unpack_dict('custom_fields', prepend=False)

        return tbl

    def get_tickets(self, ticket_type=None, requester_id=None, requester_email=None,
                    company_id=None, updated_since='2016-01-01', expand_custom_fields=False):
        """
        List tickets.

        .. warning::
            Deleted and Spam tickets are not included. However they can be pulled separately
            by utilizing the ``ticket_type`` parameter.

        .. warning::
            Freshdesk will return a maximum of 9,000 tickets. To access additional tickets,
            utilize the ``updated_since`` parameter.

        `Args:`
            ticket_type: str
                Filter by type of ticket to filter by. Valid fields include ``new_and_my_open``,
                ``watching``, ``spam`` and ``deleted``.
            requester_id: int
                Filter by requester id.
            requester_email: str
                Filter by requester email.
            company_id: int
                Filter by company_id.
            expand_custom_fields: boolean
                Expand nested custom fields to their own columns.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        params = {'filter': ticket_type,
                  'requester_id': requester_id,
                  'requester_email': requester_email,
                  'company_id': company_id,
                  'updated_since': updated_since}

        tbl = Table(self.get_request('tickets', params=params))
        logger.info(f'Found {tbl.num_rows} tickets.')
        return self.transform_table(tbl, expand_custom_fields)

    def get_contacts(self, email=None, mobile=None, phone=None, company_id=None,
                     state=None, updated_since=None, expand_custom_fields=None):
        """
        Get contacts.

        `Args:`
            email: str
                Filter by email address.
            mobile: str
                Filter by mobile phone number.
            phone: str
                Filter by phone number.
            expand_custom_fields: boolean
                Expand nested custom fields to their own columns.
        """

        params = {'email': email,
                  'mobile': mobile,
                  'phone': phone,
                  'company_id': company_id,
                  'state': state,
                  '_updated_since': updated_since}

        tbl = Table(self.get_request('contacts', params=params))
        logger.info(f'Found {tbl.num_rows} contacts.')
        return self.transform_table(tbl, expand_custom_fields)

    def get_companies(self, expand_custom_fields=False):
        """
        List companies.

        `Args:`
            expand_custom_fields: boolean
                Expand nested custom fields to their own columns.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = Table(self.get_request('companies'))
        logger.info(f'Found {tbl.num_rows} companies.')
        return self.transform_table(tbl, expand_custom_fields)

    def get_agents(self, email=None, mobile=None, phone=None, state=None):
        """
        List agents.

        `Args:`
            email: str
                Filter by email address.
            mobile: str
                Filter by mobile phone number
            phone: str
                Filter by phone number
            state: str
                Filter by state
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        params = {'email': email,
                  'mobile': mobile,
                  'phone': phone,
                  'state': state}

        tbl = Table(self.get_request('agents', params=params))
        logger.info(f'Found {tbl.num_rows} agents.')
        tbl = self.transform_table(tbl)
        tbl = tbl.unpack_dict('contact', prepend=False)
        tbl.remove_column('signature')  # Removing since raw HTML might cause issues.

        return tbl
