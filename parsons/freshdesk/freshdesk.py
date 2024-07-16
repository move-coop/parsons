from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector
import re
from parsons.etl import Table
import logging

logger = logging.getLogger(__name__)

PAGE_SIZE = 100


class Freshdesk:
    """
    Instantiate Freshdesk class

    `Args:`
        domain: str
            The subdomain of the Freshdesk account. Not required if ``FRESHDESK_DOMAIN``
            env variable set.
        api_key: str
            The Freshdesk provided application key. Not required if ``FRESHDESK_API_KEY``
            env variable set.
    `Returns:`
        Freshdesk class
    """

    def __init__(self, domain, api_key):

        self.api_key = check_env.check("FRESHDESK_API_KEY", api_key)
        self.domain = check_env.check("FRESHDESK_DOMAIN", domain)
        self.uri = f"https://{self.domain}.freshdesk.com/api/v2/"
        self.client = APIConnector(self.uri, auth=(self.api_key, "x"))

    def _get_request(self, endpoint, params=None):
        base_params = {"per_page": PAGE_SIZE}

        if params:
            base_params.update(params)

        r = self.client.request(endpoint, "GET", params=base_params)
        self.client.validate_response(r)
        data = r.json()

        # Paginate
        while "link" in r.headers.keys():
            logger.info(f"Retrieving another page of {PAGE_SIZE} records.")
            url = re.search("<(.*)>", r.headers["link"]).group(1)
            r = self.client.request(url, "GET", params=params)
            self.client.validate_response(r)
            data.extend(r.json())

        return data

    def _post_request(self, endpoint, data):
        """
        Send a POST request to the specified Freshdesk endpoint.
        `Args:`
            endpoint: str
                The endpoint of the Freshdesk API to which the request is being sent.
            data: dict
                The data to be sent in the request body.
        `Returns:`
            dict
                The JSON response from the API.
        """
        url = self.uri + endpoint
        r = self.client.request(url, "POST", json=data)
        self.client.validate_response(r)
        return r.json()

    @staticmethod
    def _transform_table(tbl, expand_custom_fields=None):
        if tbl.num_rows > 0:
            tbl.move_column("id", 0)
            tbl.sort()
            if expand_custom_fields:
                tbl.unpack_dict("custom_fields", prepend=False)

        return tbl

    def get_tickets(
        self,
        ticket_type=None,
        requester_id=None,
        requester_email=None,
        company_id=None,
        updated_since="2016-01-01",
        expand_custom_fields=False,
    ):
        """
        List tickets.

        See the `API Docs <https://developers.freshdesk.com/api/#list_all_tickets>`_
        for more information.

        .. warning::
            Deleted and Spam tickets are not included. However they can be pulled separately
            by utilizing the ``ticket_type`` parameter.

        .. warning::
            Freshdesk will return a maximum of 9,000 tickets. By default, only tickets created in
            the past 30 days are returned. To access additional tickets, utilize the
            ``updated_since`` parameter.

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
            updated_since: str
                Earliest date to include in results.
            expand_custom_fields: boolean
                Expand nested custom fields to their own columns.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        params = {
            "filter": ticket_type,
            "requester_id": requester_id,
            "requester_email": requester_email,
            "company_id": company_id,
            "updated_since": updated_since,
        }

        tbl = Table(self._get_request("tickets", params=params))
        logger.info(f"Found {tbl.num_rows} tickets.")
        return self._transform_table(tbl, expand_custom_fields)

    def get_contacts(
        self,
        email=None,
        mobile=None,
        phone=None,
        company_id=None,
        state=None,
        updated_since=None,
        expand_custom_fields=None,
    ):
        """
        Get contacts.

        See the `API Docs <https://developers.freshdesk.com/api/#list_all_contacts>`_
        for more information.

        `Args:`
            email: str
                Filter by email address.
            mobile: str
                Filter by mobile phone number.
            phone: str
                Filter by phone number.
            company_id: int
                Filter by company ID.
            state: str
                Filter by state.
            updated_since: str
                Earliest date to include in results.
            expand_custom_fields: boolean
                Expand nested custom fields to their own columns.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        params = {
            "email": email,
            "mobile": mobile,
            "phone": phone,
            "company_id": company_id,
            "state": state,
            "_updated_since": updated_since,
        }

        tbl = Table(self._get_request("contacts", params=params))
        logger.info(f"Found {tbl.num_rows} contacts.")
        return self._transform_table(tbl, expand_custom_fields)

    def get_companies(self, expand_custom_fields=False):
        """
        List companies.

        See the `API Docs <https://developers.freshdesk.com/api/#list_all_companies>`_
        for more information.

        `Args:`
            expand_custom_fields: boolean
                Expand nested custom fields to their own columns.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = Table(self._get_request("companies"))
        logger.info(f"Found {tbl.num_rows} companies.")
        return self._transform_table(tbl, expand_custom_fields)

    def get_agents(self, email=None, mobile=None, phone=None, state=None):
        """
        List agents.

        See the `API Docs <https://developers.freshdesk.com/api/#list_all_agents>`_
        for more information.

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

        params = {"email": email, "mobile": mobile, "phone": phone, "state": state}
        tbl = Table(self._get_request("agents", params=params))
        logger.info(f"Found {tbl.num_rows} agents.")
        tbl = self._transform_table(tbl)
        tbl = tbl.unpack_dict("contact", prepend=False)
        tbl.remove_column("signature")  # Removing since raw HTML might cause issues.

        return tbl

    def create_ticket(
        self, subject, description, email, priority, status, cc_emails=None, custom_fields=None
    ):
        """
        Create a ticket in Freshdesk.
        `Args:`
            subject: str
                The subject of the ticket.
            description: str
                The description of the ticket.
            email: str
                The email address of the requester.
            priority: int
                The priority of the ticket.
            status: int
                The status of the ticket.
            cc_emails: list (optional)
                List of email addresses to CC.
            custom_fields: dict (optional)
                Custom fields data.
        `Returns:`
            dict
                JSON response from the API.
        """
        endpoint = "tickets"
        data = {
            "subject": subject,
            "description": description,
            "email": email,
            "priority": priority,
            "status": status,
            "cc_emails": cc_emails if cc_emails else [],
            "custom_fields": custom_fields if custom_fields else {},
        }
        return self._post_request(endpoint, data)
