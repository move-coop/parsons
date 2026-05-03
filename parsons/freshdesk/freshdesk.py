import logging
import re
from datetime import date
from typing import Any, Literal

from requests.auth import HTTPBasicAuth

from parsons import Table
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector

logger = logging.getLogger(__name__)

PAGE_SIZE = 100


class Freshdesk:
    """
    Instantiate Freshdesk class.

    Args:
        domain:
            The subdomain of the Freshdesk account.
            Not required if ``FRESHDESK_DOMAIN`` env variable set.
        api_key:
            The Freshdesk provided application key.
            Not required if ``FRESHDESK_API_KEY`` env variable set.

    """

    def __init__(self, domain: str, api_key: str) -> None:
        self.api_key: str = check_env.check("FRESHDESK_API_KEY", api_key)
        self.domain: str = check_env.check("FRESHDESK_DOMAIN", domain)
        self.uri = f"https://{self.domain}.freshdesk.com/api/v2/"
        self.client = APIConnector(self.uri, auth=HTTPBasicAuth(self.api_key, "x"))

    def _get_request(self, endpoint: str, params: dict[str, str | int] | None = None) -> list:
        base_params: dict[str, str | int] = {"per_page": PAGE_SIZE}
        if params:
            base_params.update(params)

        r = self.client.request(endpoint, "GET", params=base_params)
        self.client.validate_response(r)
        data = r.json()

        # Paginate
        while "link" in r.headers:
            logger.info(f"Retrieving another page of {PAGE_SIZE} records.")
            url = re.search("<(.*)>", r.headers["link"]).group(1)
            r = self.client.request(url, "GET", params=params)
            self.client.validate_response(r)
            data.extend(r.json())

        return data

    def _post_request(self, endpoint: str, data: dict[str, Any]) -> dict:
        """
        Send a POST request to the specified Freshdesk endpoint.

        Args:
            endpoint:
                The endpoint of the Freshdesk API to which the request is being sent.
            data: The data to be sent in the request body.

        Returns:
            The JSON response from the API.

        """
        url = self.uri + endpoint

        r = self.client.request(url, "POST", json=data)
        self.client.validate_response(r)

        return r.json()

    @staticmethod
    def _transform_table(tbl: Table, expand_custom_fields: bool = False) -> Table:
        if tbl.num_rows > 0:
            tbl.move_column("id", 0)
            tbl.sort()
            if expand_custom_fields:
                tbl.unpack_dict("custom_fields", prepend=False)

        return tbl

    def get_tickets(
        self,
        ticket_type: Literal["new_and_my_open", "watching", "spam", "deleted"] | None = None,
        requester_id: int | None = None,
        requester_email: str | None = None,
        company_id: int | None = None,
        updated_since: date | str | None = "2016-01-01",
        expand_custom_fields: bool = False,
    ) -> Table:
        """
        List tickets.

        See the `API Docs <https://developers.freshdesk.com/api/#list_all_tickets>`__
        for more information.

        .. warning::

            Deleted and Spam tickets are not included.
            However they can be pulled separately
            by utilizing the `ticket_type` parameter.

        .. warning::

            Freshdesk will return a maximum of 9,000 tickets.
            By default, only tickets created in the past 30 days are returned.
            To access additional tickets, utilize the `updated_since` parameter.

        Args:
            ticket_type: Filter by type of ticket to filter by.
            requester_id: Filter by requester id.
            requester_email: Filter by requester email.
            company_id: Filter by company_id.
            updated_since: Earliest date to include in results.
            expand_custom_fields: Expand nested custom fields to their own columns.

        """
        if isinstance(updated_since, date):
            updated_since = updated_since.strftime("%Y-%m-%d")

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
        email: str | None = None,
        mobile: str | None = None,
        phone: str | None = None,
        company_id: int | None = None,
        state: str | None = None,
        updated_since: date | str | None = None,
        expand_custom_fields: bool = False,
    ) -> Table:
        """
        Get contacts.

        See the `API Docs <https://developers.freshdesk.com/api/#list_all_contacts>`__
        for more information.

        Args:
            email: Filter by email address.
            mobile: Filter by mobile phone number.
            phone: Filter by phone number.
            company_id: Filter by company ID.
            state: Filter by state.
            updated_since: Earliest date to include in results.
            expand_custom_fields: Expand nested custom fields to their own columns.

        """
        if isinstance(updated_since, date):
            updated_since = updated_since.strftime("%Y-%m-%d")

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

    def get_companies(self, expand_custom_fields: bool = False) -> Table:
        """
        List companies.

        See the `API Docs <https://developers.freshdesk.com/api/#list_all_companies>`__
        for more information.

        Args:
            expand_custom_fields: Expand nested custom fields to their own columns.

        """
        tbl = Table(self._get_request("companies"))

        logger.info(f"Found {tbl.num_rows} companies.")
        return self._transform_table(tbl, expand_custom_fields)

    def get_agents(
        self,
        email: str | None = None,
        mobile: str | None = None,
        phone: str | None = None,
        state: str | None = None,
    ) -> Table:
        """
        List agents.

        See the `API Docs <https://developers.freshdesk.com/api/#list_all_agents>`__
        for more information.

        Args:
            email: Filter by email address.
            mobile: Filter by mobile phone number
            phone: Filter by phone number
            state: Filter by state

        """
        filters = {"email", "mobile", "phone", "state"}
        params = {k: locals()[k] for k in filters if locals().get(k) is not None}

        tbl = Table(self._get_request("agents", params=params))
        logger.info(f"Found {tbl.num_rows} agents.")

        tbl = self._transform_table(tbl)
        tbl = tbl.unpack_dict("contact", prepend=False)
        tbl.remove_column("signature")  # Removing since raw HTML might cause issues.

        return tbl

    def create_ticket(
        self,
        subject: str,
        description: str,
        email: str,
        priority: int,
        status: int,
        cc_emails: list[str] | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Create a ticket in Freshdesk.

        Args:
            subject: The subject of the ticket.
            description: The description of the ticket.
            email: The email address of the requester.
            priority: The priority of the ticket.
            status: The status of the ticket.
            cc_emails: List of email addresses to CC.
            custom_fields: Custom fields data.

        Returns:
            JSON response from the API.

        """
        data = {
            "subject": subject,
            "description": description,
            "email": email,
            "priority": priority,
            "status": status,
            "cc_emails": cc_emails if cc_emails else [],
            "custom_fields": custom_fields if custom_fields else {},
        }

        return self._post_request("tickets", data)
