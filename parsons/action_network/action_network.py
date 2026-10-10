import logging
import re
import warnings
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Literal, TypedDict, TypeVar, overload

from typing_extensions import NotRequired

from parsons.etl.table import Table
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector, _JsonType
from parsons.utilities.bearer_auth import BearerAuth

logger = logging.getLogger(__name__)

API_URL = "https://actionnetwork.org/api/v2"
MAX_PER_PAGE = 25

MobileStatusType = Literal["subscribed", "unsubscribed"]

T = TypeVar("T")


class MobileInfo(TypedDict):
    """Represent the mobile phone information for a person."""

    number: str
    primary: NotRequired[bool]
    status: NotRequired[MobileStatusType]


class EmailInfo(TypedDict):
    """Represent the email information for a person."""

    address: str
    primary: NotRequired[bool]
    status: NotRequired[
        MobileStatusType
        | Literal[
            "bouncing",
            "previous bounce",
            "spam complaint",
            "previous spam complaint",
        ]
    ]


class ActionNetwork:
    """Parsons connector for interacting with Action Network endpoints."""

    def __init__(self, api_token: str | None = None) -> None:
        """
        Instantiate the ActionNetwork class.

        Args:
            api_token:
                OSDI API token.
                Can be set with ``AN_API_TOKEN`` environment variable.

        """
        headers = {"Content-Type": "application/json"}
        api_token = check_env.check("AN_API_TOKEN", api_token)
        auth = BearerAuth(api_token, header_name="OSDI-API-Token", token_name=None)
        self.api = APIConnector(API_URL, headers=headers, auth=auth)

    def _get_page(
        self,
        object_name: str,
        page: int,
        per_page: int = MAX_PER_PAGE,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType]:
        """
        Get a single page of records from an endpoint.

        Args:
            object_name: The name of the endpoint to request data from.
            page: Which page of results to return.
            per_page: The number of entries per page. Cannot exceed 25.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        if per_page > MAX_PER_PAGE:
            per_page = MAX_PER_PAGE
            log_msg = "Action Network's API will not return more than 25 entries per page. Changing per_page parameter to 25."
            logger.info(log_msg)

        params = {"page": page, "per_page": per_page, "filter": query}
        return self.api.get_request(object_name, params=params)

    def _get_entry_list(
        self,
        object_name: str,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> Table:
        """
        Get a list of records from an endpoint.

        Objects include people, tags, or actions.
        Filter can only be applied to people, petitions, events, forms, fundraising_pages,
        event_campaigns, campaigns, advocacy_campaigns, signatures, attendances, submissions,
        donations and outreaches.

        Args:
            object_name: The name of the endpoint to request data from.
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Reference Documentation:
            `<https://actionnetwork.org/docs/v2/>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        count = 0
        page = 1
        return_list = []
        while True:
            response = self._get_page(object_name, page, per_page, query=query)
            page = page + 1
            embedded = response["_embedded"]
            response_list: Sequence[_JsonType] = embedded[next(iter(embedded))]
            if not response_list:
                return Table(return_list)

            return_list.extend(response_list)
            count = count + len(response_list)
            if limit and count >= limit:
                return Table(return_list[0:limit])

    def _extract_identifiers(self, json_response: Mapping[str, _JsonType]) -> dict[str, str]:
        """Extract the identifiers from a JSON response."""
        raw_identifiers = json_response["identifiers"]
        identifiers = {
            key: val for identifier in raw_identifiers for key, val in [identifier.split(":", 1)]
        }
        if "action_network" not in identifiers:
            logger.error(
                "Identifiers did not contain `action_network` identifier. Found: %s",
                identifiers,
            )

        return identifiers

    @overload
    def _deprecate_kw_arg(self, value: T, old_name: str, new_name: str) -> T: ...

    @overload
    def _deprecate_kw_arg(self, value: None, old_name: str, new_name: str) -> None: ...

    def _deprecate_kw_arg(self, value: T | None, old_name: str, new_name: str) -> T | None:
        """Handle DeprecationWarning when a deprecated keyword argument is used."""
        if value:
            warnings.warn(
                f"The keyword argument `{old_name}` is deprecated, use `{new_name}` instead.",
                DeprecationWarning,
                stacklevel=3,
            )
        return value

    @overload
    def _deprecate_pos_arg(self, value: T, arg_name: str) -> T: ...

    @overload
    def _deprecate_pos_arg(self, value: None, arg_name: str) -> None: ...

    def _deprecate_pos_arg(self, value: T | None, arg_name: str) -> T | None:
        """Handle DeprecationWarning when a positional argument is used that is a keyword-only argument."""
        if value:
            warnings.warn(
                (
                    f"Passing the argument `{arg_name}` as a positional argument "
                    "is deprecated, you should pass it as a keyword argument instead."
                ),
                DeprecationWarning,
                stacklevel=3,
            )
        return value

    @overload
    def get_advocacy_campaigns(
        self,
        limit: int | None = ...,
        per_page: int = ...,
        page: None = ...,
        query: str | None = None,
        *,
        filter: str | None = ...,
    ) -> Table: ...

    @overload
    def get_advocacy_campaigns(
        self,
        limit: int | None,
        per_page: int,
        page: int,
        query: str | None,
        *,
        filter: str | None,
    ) -> dict[str, _JsonType]: ...

    def get_advocacy_campaigns(
        self,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a list of advocacy campaigns.

        Args:
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/advocacy_campaigns>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = "advocacy_campaigns"

        if page:
            return self._get_page(endpoint, page, per_page, query)

        return self._get_entry_list(endpoint, limit, per_page, query)

    def get_advocacy_campaign(self, advocacy_campaign_id: str) -> dict[str, _JsonType]:
        """
        Get the information for a single advocacy campaign.

        Args:
            advocacy_campaign_id: Unique ID of the advocacy_campaign

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/advocacy_campaigns>`__

        """
        endpoint = f"advocacy_campaigns/{advocacy_campaign_id}"
        return self.api.get_request(endpoint)

    @overload
    def get_person_attendances(
        self,
        person_id: str,
        limit: int | None = ...,
        per_page: int = ...,
        page: None = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
    ) -> Table: ...

    @overload
    def get_person_attendances(
        self,
        person_id: str,
        limit: int | None,
        per_page: int,
        page: int,
        query: str | None,
        *,
        filter: str | None,
    ) -> dict[str, _JsonType]: ...

    def get_person_attendances(
        self,
        person_id: str,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a list of event attendances, by person.

        Args:
            person_id: Unique ID of the person
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/attendances>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = f"people/{person_id}/attendances"

        if page:
            return self._get_page(endpoint, page, per_page, query)

        return self._get_entry_list(endpoint, limit, per_page, query)

    @overload
    def get_event_attendances(
        self,
        event_id: str,
        limit: int | None = ...,
        per_page: int = ...,
        page: None = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
    ) -> Table: ...

    @overload
    def get_event_attendances(
        self,
        event_id: str,
        limit: int | None,
        per_page: int,
        page: int,
        query: str | None,
        *,
        filter: str | None,
    ) -> dict[str, _JsonType]: ...

    def get_event_attendances(
        self,
        event_id: str,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a list of event attendances, by event.

        Args:
            event_id: Unique ID of the event
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/attendances>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = f"events/{event_id}/attendances"

        if page:
            return self._get_page(endpoint, page, per_page, query)

        return self._get_entry_list(endpoint, limit, per_page, query)

    def get_event_attendance(self, event_id: str, attendance_id: str) -> dict[str, _JsonType]:
        """
        Get the information for a single event attendance record, by event.

        Args:
            event_id: Unique ID of the event
            attendance_id: Unique ID of the attendance

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/attendances>`__

        """
        endpoint = f"events/{event_id}/attendances/{attendance_id}"
        return self.api.get_request(endpoint)

    def get_person_attendance(self, person_id: str, attendance_id: str) -> dict[str, _JsonType]:
        """
        Get the information for a single event attendance record, by person.

        Args:
            person_id: Unique ID of the person
            attendance_id: Unique ID of the attendance

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/attendances>`__

        """
        endpoint = f"people/{person_id}/attendances/{attendance_id}"
        return self.api.get_request(endpoint)

    def create_attendance(
        self, event_id: str, payload: Mapping[str, _JsonType]
    ) -> dict[str, _JsonType]:
        """
        Create a single new event attendance record.

        Args:
            event_id: Unique ID of the event
            payload:
                Payload for creating the event attendance

                .. code-block:: python

                    {
                        "_links" : {
                            "osdi:person" : { "href" : "https://actionnetwork.org/api/v2/people/id" }
                        }
                    }

        Returns:
            Information for a newly created Event Attendance record.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/attendances>`__

        """
        endpoint = f"events/{event_id}/attendances"
        return self.api.post_request(endpoint, json=payload)

    def update_attendance(
        self, event_id: str, attendance_id: str, payload: Mapping[str, _JsonType]
    ) -> dict[str, _JsonType]:
        """
        Update the information for a single event attendance record.

        Args:
            event_id: Unique ID of the event
            attendance_id: Unique ID of the attendance
            payload:
                Payload for updating the event attendance

                .. code-block:: python

                    {
                        "identifiers": [
                            "other-system:230125a"
                        ]
                    }

        Returns:
            Information for an updated Event Attendance record.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/attendances>`__

        """
        endpoint = f"events/{event_id}/attendances/{attendance_id}"
        return self.api.put_request(endpoint, json=payload)

    @overload
    def get_campaigns(
        self,
        limit: int | None = ...,
        per_page: int = ...,
        page: None = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
    ) -> Table: ...

    @overload
    def get_campaigns(
        self,
        limit: int | None,
        per_page: int,
        page: int,
        query: str | None,
        *,
        filter: str | None,
    ) -> dict[str, _JsonType]: ...

    def get_campaigns(
        self,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a list of campaigns.

        Args:
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/campaigns>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = "campaigns"

        if page:
            return self._get_page(endpoint, page, per_page, query)

        return self._get_entry_list(endpoint, limit, per_page, query)

    def get_campaign(self, campaign_id: str) -> dict[str, _JsonType]:
        """
        Get information on a single campaign.

        Args:
            campaign_id: Unique ID of the campaign

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/campaigns>`__

        """
        endpoint = f"campaigns/{campaign_id}"
        return self.api.get_request(endpoint)

    def get_custom_fields(self) -> dict[str, _JsonType]:
        """
        Get a list of custom fields.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/custom_fields>`__

        """
        endpoint = "metadata/custom_fields"
        return self.api.get_request(endpoint)

    def get_donation(self, donation_id: str) -> dict[str, _JsonType]:
        """
        Get information on a single donation.

        Args:
            donation_id: Unique ID of the donation

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/donations>`__

        """
        endpoint = f"donations/{donation_id}"
        return self.api.get_request(endpoint)

    @overload
    def get_donations(
        self,
        limit: int | None = ...,
        per_page: int = ...,
        page: None = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
    ) -> Table: ...

    @overload
    def get_donations(
        self,
        limit: int | None,
        per_page: int,
        page: int,
        query: str | None,
        *,
        filter: str | None,
    ) -> dict[str, _JsonType]: ...

    def get_donations(
        self,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a list of donations.

        Args:
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/donations>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = "donations"

        if page:
            return self._get_page(endpoint, page, per_page, query)

        return self._get_entry_list(endpoint, limit, per_page, query)

    @overload
    def get_fundraising_page_donations(
        self,
        fundraising_page_id: str,
        limit: int | None = ...,
        per_page: int = ...,
        page: None = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
    ) -> Table: ...

    @overload
    def get_fundraising_page_donations(
        self,
        fundraising_page_id: str,
        limit: int | None,
        per_page: int,
        page: int,
        query: str | None,
        *,
        filter: str | None,
    ) -> dict[str, _JsonType]: ...

    def get_fundraising_page_donations(
        self,
        fundraising_page_id: str,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a list of donations, by fundraising page.

        Args:
            fundraising_page_id: The ID of the fundraiser
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/donations>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = f"fundraising_pages/{fundraising_page_id}/donations"

        if page:
            return self._get_page(endpoint, page, per_page, query)

        return self._get_entry_list(endpoint, limit, per_page, query)

    @overload
    def get_person_donations(
        self,
        person_id: str,
        limit: int | None = ...,
        per_page: int = ...,
        page: None = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
    ) -> Table: ...

    @overload
    def get_person_donations(
        self,
        person_id: str,
        limit: int | None,
        per_page: int,
        page: int,
        query: str | None,
        *,
        filter: str | None,
    ) -> dict[str, _JsonType]: ...

    def get_person_donations(
        self,
        person_id: str,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a list of donations, by person.

        Args:
            person_id: The ID of the person
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/donations>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = f"people/{person_id}/donations"

        if page:
            return self._get_page(endpoint, page, per_page, query)

        return self._get_entry_list(endpoint, limit, per_page, query)

    def create_donation(
        self, fundraising_page_id: str, donation_payload: Mapping[str, _JsonType]
    ) -> dict[str, _JsonType]:
        """
        Create a single new donation record.

        Args:
            fundraising_page_id: The ID of the fundraising page
            donation_payload:
                Payload containing donation details

                .. code-block:: python

                    {
                        "recipients": [
                            {
                                "display_name": "Campaign To Elect Tom",
                                "amount": "3.00"
                            }
                        ],
                        "created_date": "2013-01-01T00:00:00Z",
                        "_links" : {
                            "osdi:person" : { "href" : "link" }
                        }
                    }

        Returns:
            Information for a newly created Donation record.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/donations>`__

        """
        endpoint = f"fundraising_pages/{fundraising_page_id}/donations"
        return self.api.post_request(endpoint, json=donation_payload)

    def get_embeds(self, action_type: str, action_id: str) -> dict[str, _JsonType]:
        """
        Get a list of ``embeds`` used to embed the action on another website.

        Args:
            action_type: Action type (petition, events, etc.)
            action_id: Unique ID of the action

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/embeds>`__

        """
        endpoint = f"{action_type}/{action_id}/embed"
        return self.api.get_request(endpoint)

    @overload
    def get_event_campaigns(
        self,
        limit: int | None = ...,
        per_page: int = ...,
        page: None = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
    ) -> Table: ...

    @overload
    def get_event_campaigns(
        self,
        limit: int | None,
        per_page: int,
        page: int,
        query: str | None,
        *,
        filter: str | None,
    ) -> dict[str, _JsonType]: ...

    def get_event_campaigns(
        self,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a list of event campaigns.

        Args:
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/event_campaigns>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = "event_campaigns"

        if page:
            return self._get_page(endpoint, page, per_page, query)

        return self._get_entry_list(endpoint, limit, per_page, query)

    def get_event_campaign(self, event_campaign_id: str) -> dict[str, _JsonType]:
        """
        Get the information for a single event campaign.

        Args:
            event_campaign_id: Unique ID of the event_campaign

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/event_campaigns>`__

        """
        endpoint = f"event_campaigns/{event_campaign_id}"
        return self.api.get_request(endpoint)

    def create_event_campaign(self, payload: Mapping[str, _JsonType]) -> dict[str, _JsonType]:
        """
        Create a single new event campaign record.

        Args:
            payload:
                Payload containing event campaign details

                .. code-block::python

                    {
                        "title": "My Canvassing Event",
                        "origin_system": "CanvassingEvents.com"
                    }

        Returns:
            Information for a newly created Event Campaign record.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/event_campaigns>`__

        """
        endpoint = "event_campaigns"
        return self.api.post_request(endpoint, json=payload)

    def create_event_in_event_campaign(
        self, event_campaign_id: str, payload: Mapping[str, _JsonType]
    ) -> dict[str, _JsonType]:
        """
        Create a single new event record, within an event campaign.

        Args:
            event_campaign_id: Unique ID of the event_campaign
            payload:
                Payload containing event details

                .. code-block::python

                    {
                        "title": "My Free Event",
                        "origin_system": "FreeEvents.com"
                    }

        Returns:
            Information for a newly created Event record within an Event Campaign.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/event_campaigns>`__

        """
        endpoint = f"event_campaigns/{event_campaign_id}/events"
        return self.api.post_request(endpoint, json=payload)

    def update_event_campaign(
        self, event_campaign_id: str, payload: Mapping[str, _JsonType]
    ) -> dict[str, _JsonType]:
        """
        Update the information for a single event campaign.

        Args:
            event_campaign_id: Unique ID of the event_campaign
            payload:
                Payload containing event campaign details

                .. code-block::python

                    {
                        "description": "This is my new event campaign description"
                    }

        Returns:
            Information for an updated Event Campaign record.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/event_campaigns>`__

        """
        endpoint = f"event_campaigns/{event_campaign_id}"
        return self.api.put_request(endpoint, json=payload)

    @overload
    def get_events(
        self,
        limit: int | None = ...,
        per_page: int = ...,
        page: None = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
    ) -> Table: ...

    @overload
    def get_events(
        self,
        limit: int | None,
        per_page: int,
        page: int,
        query: str | None,
        *,
        filter: str | None,
    ) -> dict[str, _JsonType]: ...

    def get_events(
        self,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a list of events.

        Args:
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/events>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = "events"

        if page:
            return self._get_page(endpoint, page, per_page, query)

        return self._get_entry_list(endpoint, limit, per_page, query)

    def get_event(self, event_id: str) -> dict[str, _JsonType]:
        """
        Get a single event, by ID.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/events>`__

        """
        endpoint = f"events/{event_id}"
        return self.api.get_request(endpoint)

    @overload
    def get_event_campaign_events(
        self,
        event_campaign_id: str,
        limit: int | None = ...,
        per_page: int = ...,
        page: None = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
    ) -> Table: ...

    @overload
    def get_event_campaign_events(
        self,
        event_campaign_id: str,
        limit: int | None,
        per_page: int,
        page: int,
        query: str | None,
        *,
        filter: str | None,
    ) -> dict[str, _JsonType]: ...

    def get_event_campaign_events(
        self,
        event_campaign_id: str,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a list of events, for an event campaign, by ID.

        Args:
            event_campaign_id: Unique ID of the event_campaign
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/events>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = f"event_campaigns/{event_campaign_id}/events"

        if page:
            return self._get_page(endpoint, page, per_page, query)

        return self._get_entry_list(endpoint, limit, per_page, query)

    def create_event(
        self, title: str, start_date: datetime | str | None = None, location: dict | None = None
    ) -> dict[str, _JsonType]:
        """
        Create a single new event.

        Args:
            title:
                Public title of the event
            start_date:
                Starting date & time.
                If a string, use format ``YYYY-MM-DD HH:MM:SS``
                (hint: the default format you get when you use ``str()`` on a datetime)
            location:
                Location details.
                Can include any combination of the types of
                values in the following example:

                .. code-block:: python

                    my_location = {
                        "venue": "White House",
                        "address_lines": [
                            "1600 Pennsylvania Ave"
                        ],
                        "locality": "Washington",
                        "region": "DC",
                        "postal_code": "20009",
                        "country": "US"
                    }

        Returns:
            Information for a newly created Event record.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/events>`__

        """
        endpoint = "events"
        payload = {"title": title}
        if start_date:
            payload["start_date"] = str(start_date)
        if isinstance(location, dict):
            payload["location"] = location

        event_dict: dict[str, _JsonType] = self.api.post_request(endpoint, json=payload)
        # Get Event ID from URL
        event_dict["event_id"] = event_dict["_links"]["self"]["href"].split("/")[-1]  # type:ignore[ty:unresolved-attribute, ty:invalid-argument-type, ty:not-subscriptable]

        return event_dict

    def update_event(self, event_id: str, payload: Mapping[str, _JsonType]) -> dict[str, _JsonType]:
        """
        Update the information for a single event.

        Args:
            event_id: Unique ID of the event
            payload:
                Payload containing event data.
                See `<https://actionnetwork.org/docs/v2/events>`__

                .. code-block::python

                    {
                        "title": "My Free Event With A New Name",
                        "description": "This is my free event description"
                    }

        Returns:
            A JSON response confirming that the Event was updated.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/events>`__

        """
        endpoint = f"events/{event_id}"
        return self.api.put_request(endpoint, json=payload)

    @overload
    def get_forms(
        self,
        limit: int | None = ...,
        per_page: int = ...,
        page: None = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
    ) -> Table: ...

    @overload
    def get_forms(
        self,
        limit: int | None,
        per_page: int,
        page: int,
        query: str | None,
        *,
        filter: str | None,
    ) -> dict[str, _JsonType]: ...

    def get_forms(
        self,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a list of forms.

        Args:
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/forms>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = "forms"

        if page:
            return self._get_page(endpoint, page, per_page, query)

        return self._get_entry_list(endpoint, limit, per_page, query)

    def get_form(self, form_id: str) -> dict[str, _JsonType]:
        """
        Get a single form, by ID.

        Args:
            form_id: Unique ID of the form

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/forms>`__

        """
        endpoint = f"forms/{form_id}"
        return self.api.get_request(endpoint)

    def create_form(self, payload: Mapping[str, _JsonType]) -> dict[str, _JsonType]:
        """
        Create a single new form.

        Args:
            payload:
                Payload containing form details

                .. code-block::python

                    {
                        "title": "My Free Form",
                        "origin_system": "FreeForms.com"
                    }

        Returns:
            Information for a newly created Form record.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/forms>`__

        """
        endpoint = "forms"
        return self.api.post_request(endpoint, json=payload)

    def update_form(self, form_id: str, payload: Mapping[str, _JsonType]) -> dict[str, _JsonType]:
        """
        Update the information for a single form, by ID.

        Args:
            form_id: Unique ID of the form
            payload:
                Payload containing form data (see `<https://actionnetwork.org/docs/v2/forms>`__)

                .. code-block::python

                    {
                        "title": "My Free Form",
                        "origin_system": "FreeForms.com"
                    }

        Returns:
            A JSON response confirming that the Form was updated.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/forms>`__

        """
        endpoint = f"forms/{form_id}"
        return self.api.put_request(endpoint, json=payload)

    def get_fundraising_page(self, fundraising_page_id: str) -> dict[str, _JsonType]:
        """
        Get a single fundraising page, by ID.

        Args:
            fundraising_page_id: The ID of the fundraiser

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/fundraising_pages>`__

        """
        endpoint = f"fundraising_pages/{fundraising_page_id}"
        return self.api.get_request(endpoint)

    @overload
    def get_fundraising_pages(
        self,
        limit: int | None = ...,
        per_page: int = ...,
        page: None = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
    ) -> Table: ...

    @overload
    def get_fundraising_pages(
        self,
        limit: int | None,
        per_page: int,
        page: int,
        query: str | None,
        *,
        filter: str | None,
    ) -> dict[str, _JsonType]: ...

    def get_fundraising_pages(
        self,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a list of fundraising pages.

        Args:
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/fundraising_pages>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = "fundraising_pages"

        if page:
            return self._get_page(endpoint, page, per_page, query)

        return self._get_entry_list(endpoint, limit)

    def create_fundraising_page(self, payload: Mapping[str, _JsonType]) -> dict[str, _JsonType]:
        """
        Create a single new fundraising page.

        Args:
            payload:
                Payload containing fundraising page details

                .. code-block::python

                    {
                        "title": "My Free Fundraiser",
                        "origin_system": "FreeFundraisers.com"
                    }

        Returns:
            Information for a newly created Fundraising record.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/fundraising_pages>`__

        """
        endpoint = "fundraising_pages"
        return self.api.post_request(endpoint, json=payload)

    def update_fundraising_page(
        self, fundraising_page_id: str, payload: Mapping[str, _JsonType]
    ) -> dict[str, _JsonType]:
        """
        Update the information for a single fundraising page, by ID.

        Args:
            fundraising_page_id: The ID of the fundraiser
            payload:
                Payload containing updated fundraising page details

                .. code-block::python

                    {
                        "title": "My Free Fundraiser",
                        "origin_system": "FreeFundraisers.com"
                    }

        Returns:
            A JSON response confirming that the Fundraising Page was updated.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/fundraising_pages>`__

        """
        endpoint = f"fundraising_pages/{fundraising_page_id}"
        return self.api.put_request(endpoint, json=payload)

    @overload
    def get_items(
        self,
        list_id: str,
        limit: int | None = ...,
        per_page: int = ...,
        page: None = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
    ) -> Table: ...

    @overload
    def get_items(
        self,
        list_id: str,
        limit: int | None,
        per_page: int,
        page: int,
        query: str | None,
        *,
        filter: str | None,
    ) -> dict[str, _JsonType]: ...

    def get_items(
        self,
        list_id: str,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a single list, by ID.

        Args:
            list_id: Unique ID of the list
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/items>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = f"lists/{list_id}/items"

        if page:
            return self._get_page(endpoint, page, per_page, query)

        return self._get_entry_list(endpoint, limit, per_page, query)

    def get_item(self, list_id: str, item_id: str) -> dict[str, _JsonType]:
        """
        Get a single item, by ID, from a list, by ID.

        Args:
            list_id: Unique ID of the list
            item_id: Unique ID of the item

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/items>`__

        """
        endpoint = f"lists/{list_id}/items/{item_id}"
        return self.api.get_request(endpoint)

    def get_lists(
        self,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a list of lists.

        Args:
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/lists>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = "lists"

        if page:
            return self._get_page(endpoint, page, per_page, query)

        return self._get_entry_list(endpoint, limit, per_page, query)

    def get_list(self, list_id: str) -> dict[str, _JsonType]:
        """
        Get a single list, by ID.

        Args:
           list_id: Unique ID of the list

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/lists>`__

        """
        endpoint = f"lists/{list_id}"
        return self.api.get_request(endpoint)

    @overload
    def get_messages(
        self,
        limit: int | None = ...,
        per_page: int = ...,
        page: None = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
        unpack_statistics: bool = ...,
    ) -> Table: ...

    @overload
    def get_messages(
        self,
        limit: int | None,
        per_page: int,
        page: int,
        query: str | None,
        *,
        filter: str | None,
        unpack_statistics: bool,
    ) -> dict[str, _JsonType]: ...

    def get_messages(
        self,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
        unpack_statistics: bool = False,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a list of messages.

        Args:
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.
            unpack_statistics: Whether to unpack the statistics dictionary into the table.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/messages>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = "messages"

        if page:
            return self._get_page(endpoint, page, per_page, query)

        tbl = self._get_entry_list(endpoint, limit, per_page, query)
        if unpack_statistics:
            tbl.unpack_dict("statistics", prepend=False, include_original=True)

        return tbl

    def get_message(self, message_id: str) -> dict[str, _JsonType]:
        """
        Get a single message, by ID.

        Args:
            message_id: Unique ID of the message

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/messages>`__

        """
        endpoint = f"messages/{message_id}"
        return self.api.get_request(endpoint)

    def create_message(self, payload: Mapping[str, _JsonType]) -> dict[str, _JsonType]:
        """
        Create a single new message.

        Args:
            payload:
                Payload containing message details

                .. code-block::python

                    {
                      "subject": "Stop doing the bad thing",
                      "body": "<p>The mayor should stop doing the bad thing.</p>",
                      "from": "Progressive Action Now",
                      "reply_to": "jane@progressiveactionnow.org",
                      "targets": [
                        {
                          "href": "https://actionnetwork.org/api/v2/queries/id"
                        }
                      ],
                      "_links": {
                        "osdi:wrapper": {
                          "href": "https://actionnetwork.org/api/v2/wrappers/id"
                        }
                      }
                    }

        Returns:
            Information for a newly created Message record.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/messages>`__

        """
        endpoint = "messages"
        return self.api.post_request(endpoint, json=payload)

    def update_message(
        self, message_id: str, payload: Mapping[str, _JsonType]
    ) -> dict[str, _JsonType]:
        """
        Update the information for a single message, by ID.

        Args:
            message_id: Unique ID of the message
            payload:
                Payload containing message details to be updated

                .. code-block::python

                    {
                        "name": "Stop doing the bad thing email send 1",
                        "subject": "Please! Stop doing the bad thing"
                    }

        Returns:
            A JSON response confirming that the Message was updated.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/messages>`__

        """
        endpoint = f"messages/{message_id}"
        return self.api.put_request(endpoint, json=payload)

    def schedule_message(self, message_id: str, scheduled_start_date: str) -> dict[str, _JsonType]:
        """
        Schedule sending a message, by ID.

        Args:
            message_id: Unique ID of the message
            scheduled_start_date:
                UTC timestamp to schedule the message at in ISO8601 format.
                e.g. "2015-03-14T12:00:00Z"

        Returns:
            A JSON response confirming the Message was scheduled.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/schedule_helper>`__

        """
        endpoint = f"messages/{message_id}/schedule/"
        payload = {"scheduled_start_date": scheduled_start_date}
        return self.api.post_request(endpoint, json=payload)

    def send_message(self, message_id: str) -> dict[str, _JsonType]:
        """
        Immediately send a message, by ID.

        Args:
            message_id: Unique ID of the message

        Returns:
            A JSON response confirming the Message was sent.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/send_helper>`__

        """
        endpoint = f"messages/{message_id}/send/"
        return self.api.post_request(endpoint)

    def get_metadata(self) -> dict[str, _JsonType]:
        """
        Get all metadata.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/metadata>`__

        """
        endpoint = "metadata"
        return self.api.get_request(endpoint)

    @overload
    def get_advocacy_campaign_outreaches(
        self,
        advocacy_campaign_id: str,
        limit: int | None = ...,
        per_page: int = ...,
        page: None = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
    ) -> Table: ...

    @overload
    def get_advocacy_campaign_outreaches(
        self,
        advocacy_campaign_id: str,
        limit: int | None,
        per_page: int,
        page: int,
        query: str | None,
        *,
        filter: str | None,
    ) -> dict[str, _JsonType]: ...

    def get_advocacy_campaign_outreaches(
        self,
        advocacy_campaign_id: str,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a list of outreaches, for a single advocacy campaign, by ID.

        Args:
            advocacy_campaign_id: Unique ID of the advocacy_campaign
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/outreaches>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = f"advocacy_campaigns/{advocacy_campaign_id}/outreaches"

        if page:
            return self._get_page(endpoint, page, per_page, query)

        return self._get_entry_list(endpoint, limit, per_page, query)

    @overload
    def get_person_outreaches(
        self,
        person_id: str,
        limit: int | None = ...,
        per_page: int = ...,
        page: None = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
    ) -> Table: ...

    @overload
    def get_person_outreaches(
        self,
        person_id: str,
        limit: int | None,
        per_page: int,
        page: int,
        query: str | None,
        *,
        filter: str | None,
    ) -> dict[str, _JsonType]: ...

    def get_person_outreaches(
        self,
        person_id: str,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a list of outreaches, for a single person, by ID.

        Args:
            person_id: Unique ID of the person
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/outreaches>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = f"people/{person_id}/outreaches"

        if page:
            return self._get_page(endpoint, page, per_page, query)

        return self._get_entry_list(endpoint, limit, per_page, query)

    def get_advocacy_campaign_outreach(
        self, advocacy_campaign_id: str, outreach_id: str
    ) -> dict[str, _JsonType]:
        """
        Get a single outreach, by ID, for an advocacy campaign, by ID.

        Args:
            advocacy_campaign_id: Unique ID of the campaign
            outreach_id: Unique ID of the outreach

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/outreaches>`__

        """
        endpoint = f"advocacy_campaigns/{advocacy_campaign_id}/outreaches/{outreach_id}"
        return self.api.get_request(endpoint)

    def get_person_outreach(self, person_id: str, outreach_id: str) -> dict[str, _JsonType]:
        """
        Get a single outreach, by ID, for an person, by ID.

        Args:
            person_id: Unique ID of the campaign
            outreach_id: Unique ID of the outreach

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/outreaches>`__

        """
        endpoint = f"people/{person_id}/outreaches/{outreach_id}"
        return self.api.get_request(endpoint)

    def create_outreach(
        self, advocacy_campaign_id: str, payload: Mapping[str, _JsonType]
    ) -> dict[str, _JsonType]:
        """
        Create a single new outreach, for an advocacy campaign, by ID.

        Args:
            advocacy_campaign_id: Unique ID of the campaign
            payload:
                Payload containing outreach details

                .. code-block::python

                    {
                        "targets": [
                            {
                                "given_name": "Joe",
                                "family_name": "Schmoe"
                            }
                        ],
                        "_links" : {
                            "osdi:person" : { "href" : "https://actionnetwork.org/api/v2/people/id" }
                        }
                    }

        Returns:
            Information for a newly created Outreach record.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/outreaches>`__

        """
        endpoint = f"advocacy_campaigns/{advocacy_campaign_id}/outreaches"
        return self.api.post_request(endpoint, json=payload)

    def update_outreach(
        self, advocacy_campaign_id: str, outreach_id: str, payload: Mapping[str, _JsonType]
    ) -> dict[str, _JsonType]:
        """
        Update the information for a single outreach, by ID, for an advocacy campaign, by ID.

        Args:
            advocacy_campaign_id: Unique ID of the campaign
            outreach_id: Unique ID of the outreach
            payload:
                Payload containing outreach details to be updated

                .. code-block::python

                    {"subject": "Please vote no!"}

        Returns:
            A JSON response confirming that the Outreach was updated.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/outreaches>`__

        """
        endpoint = f"advocacy_campaigns/{advocacy_campaign_id}/outreaches/{outreach_id}"
        return self.api.put_request(endpoint, json=payload)

    @overload
    def get_people(
        self,
        limit: int | None = ...,
        per_page: int = ...,
        page: None = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
    ) -> Table: ...

    @overload
    def get_people(
        self,
        limit: int | None = ...,
        per_page: int = ...,
        page: int = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
    ) -> dict[str, _JsonType]: ...

    def get_people(
        self,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a list of people.

        Args:
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/people>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = "people"

        if page:
            return self._get_page(endpoint, page, per_page, query=query)

        return self._get_entry_list(endpoint, limit, per_page, query=query)

    def get_person(self, person_id: str) -> dict[str, _JsonType]:
        """
        Get a single person, by ID.

        Args:
            person_id: ID of the person.

        Returns:
            Information for a single person. If the entry doesn't exist,
            Action Network returns ``{'error': 'Couldn't find person with id = <id>'}``.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/people>`__

        """
        endpoint = f"people/{person_id}"
        return self.api.get_request(endpoint)

    def _handle_upsert_email_address(
        self, email_address: list[EmailInfo] | list[str] | str | None = None
    ) -> list[EmailInfo] | None:
        if email_address is None:
            return None
        if isinstance(email_address, str):
            return [EmailInfo({"address": email_address})]
        if isinstance(email_address, list):
            email_addresses = []
            for email in email_address:
                if isinstance(email, str):
                    email_addresses.append(EmailInfo({"address": email}))
                elif isinstance(email, dict) and "address" in email:
                    email_addresses.append(email)
                else:
                    err_msg = f"Unexpected type in `email_address` list. Got {type(email)}."
                    raise TypeError(err_msg)
            if not any(email["primary"] for email in email_addresses):
                email_addresses[0]["primary"] = True
            return email_addresses

        err_msg = f"Unexpected type for `email_address`. Got {type(email_address)}."
        raise TypeError(err_msg)

    def _handle_upsert_mobile_number(
        self, mobile_number: MobileInfo | str | int | list[str | int] | None = None
    ) -> list[MobileInfo] | None:
        if mobile_number is None:
            return None
        if isinstance(mobile_number, dict) and "number" in mobile_number:
            mobile_number["number"] = re.sub("[^0-9]", "", mobile_number["number"])
            return [mobile_number]
        if isinstance(mobile_number, str):
            return [MobileInfo({"number": re.sub("[^0-9]", "", mobile_number)})]
        if isinstance(mobile_number, int):
            return [MobileInfo({"number": str(mobile_number)})]
        if isinstance(mobile_number, list):
            if len(mobile_number) > 1:
                err_msg = "Action Network allows only 1 phone number per activist"
                raise ValueError(err_msg)
            if isinstance(first_cell := mobile_number[0], (str, int)):
                return [MobileInfo({"number": str(first_cell), "primary": True})]

        err_msg = f"Unexpected type for `mobile_number`. Got {type(mobile_number)}."
        raise TypeError(err_msg)

    def upsert_person(
        self,
        email_address: list[EmailInfo] | list[str] | str | None = None,
        given_name: str | None = None,
        family_name: str | None = None,
        tags: list[str] | None = None,
        languages_spoken: list[str] | None = None,
        postal_addresses: list[dict] | None = None,
        mobile_number: MobileInfo | str | int | list[str | int] | None = None,
        mobile_status: MobileStatusType | None = None,
        bp: bool = False,
        *,
        background_processing: bool = False,
        **kwargs,
    ) -> dict[str, _JsonType]:
        """
        Create or update a person record.

        In order to update an existing record instead of creating a new one,
        you must supply an email or mobile number which matches a record in the database.

        Identifiers are intentionally not included as an option on
        this method, because their use can cause buggy behavior if
        they are not globally unique. ActionNetwork support strongly
        encourages developers not to use custom identifiers.

        Args:
            email_address:
                Either email_address or mobile_number are required. Can be any of the following

                - a string with the person's email
                - a list of strings with a person's emails
                - a list of dictionaries with the following fields

                    - address (REQUIRED)
                    - primary (OPTIONAL): Boolean indicating User's primary email address
                    - status (OPTIONAL): can taken on any of these values

                        - ``subscribed``
                        - ``unsubscribed``
                        - ``bouncing``
                        - ``previous bounce``
                        - ``spam complaint``
                        - ``previous spam complaint``

            given_name:
                Person's given name
            family_name:
                Person's family name
            tags:
                A list of strings of pre-existing tags to be applied to the person.
            languages_spoken:
                A list of strings of the languages spoken by the person
            postal_addresses:
                A list of dictionaries.
                For details, see Action Network's documentation:
                `<https://actionnetwork.org/docs/v2/person_signup_helper>`__
            mobile_number:
                Either email_address or mobile_number are required. Can be any of the following

                - a string with the person's cell phone number
                - an integer with the person's cell phone number
                - a list of strings with the person's cell phone numbers (can only contain 1 number)
                - a list of integers with the person's cell phone numbers (can only contain 1 number)
                - a dictionary with the following fields

                    - number (REQUIRED)
                    - primary (OPTIONAL): Boolean indicating User's primary mobile number
                    - status (OPTIONAL): can taken on any of these values

                        - ``subscribed``
                        - ``unsubscribed``

            mobile_status:
                If included, will update the SMS opt-in status of the phone in ActionNetwork.
                If not included, won't update the status.
                New numbers are set to ``unsubscribed`` by default.

        Keyword Args:
            background_processing:
                Whether to utilize ActionNetwork's ``background processing``.
                This will return an immediate success, with an empty JSON body.
                Your request will be sent to the background queue for eventual processing.
                `<https://actionnetwork.org/docs/v2/#background-processing>`__
            `**kwargs`:
                Any additional fields to store about the person.
                Action Network allows any custom field.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/people>`__

        """
        email_addresses_field = self._handle_upsert_email_address(email_address)
        mobile_numbers_field = self._handle_upsert_mobile_number(mobile_number)

        # Including status in this field changes the opt-in status in
        # ActionNetwork. This is not always desireable, so we should
        # only do so when a status is included.
        if mobile_status and mobile_numbers_field:
            for field in mobile_numbers_field:
                field["status"] = mobile_status

        # If the mobile_number field is passed a list of dictionaries, just use that directly
        if mobile_number and isinstance(mobile_number, list) and isinstance(mobile_number[0], dict):
            mobile_numbers_field = mobile_number

        if not email_addresses_field and not mobile_numbers_field:
            err_msg = (
                "Either email_address or mobile_number is required and can be formatted "
                "as a string, list of strings, a dictionary, a list of dictionaries, or "
                "(for mobile_number only) an integer or list of integers."
            )
            raise ValueError(err_msg)

        payload = {"person": {}}
        if email_addresses_field is not None:
            payload["person"]["email_addresses"] = email_addresses_field
        if mobile_numbers_field is not None:
            payload["person"]["phone_numbers"] = mobile_numbers_field
        if given_name is not None:
            payload["person"]["given_name"] = given_name
        if family_name is not None:
            payload["person"]["family_name"] = family_name
        if languages_spoken is not None:
            payload["person"]["languages_spoken"] = languages_spoken
        if postal_addresses is not None:
            payload["person"]["postal_addresses"] = postal_addresses
        if tags is not None:
            payload["add_tags"] = tags
        payload["person"]["custom_fields"] = {**kwargs}

        bg_proc = background_processing or self._deprecate_pos_arg(bp, "background_processing")
        endpoint = f"{API_URL}/people{'?background_processing=true' if bg_proc else ''}"
        response = self.api.post_request(endpoint, json=payload)

        person_id = self._extract_identifiers(response).get("action_network")
        was_added = response["created_date"] == response["modified_date"]
        logger.info("Entry %s successfully %s.", person_id, "added" if was_added else "updated")

        return response

    def add_person(
        self,
        email_address: list[EmailInfo] | str | list[str] | None = None,
        given_name: str | None = None,
        family_name: str | None = None,
        tags: list[str] | None = None,
        languages_spoken: list[str] | None = None,
        postal_addresses: list[dict] | None = None,
        mobile_number: MobileInfo | str | int | list[str | int] | None = None,
        mobile_status: MobileStatusType | None = "subscribed",
        **kwargs,
    ) -> dict[str, _JsonType]:
        """
        Create a single new person.

        .. version-deprecated:: v0.21.0

            Deprecated in favor of :meth:`upsert_person`.

        """
        logger.warning("Method 'add_person' has been deprecated. Please use 'upsert_person'.")
        return self.upsert_person(
            email_address=email_address,
            given_name=given_name,
            family_name=family_name,
            tags=tags,
            languages_spoken=languages_spoken,
            postal_addresses=postal_addresses,
            mobile_number=mobile_number,
            mobile_status=mobile_status,
            **kwargs,
        )

    def update_person(
        self, entry_id: str, bp: bool = False, *, background_processing: bool = False, **kwargs
    ) -> dict[str, _JsonType]:
        """
        Update the information for a single person, by ID.

        .. note::

            You can't alter a person's tags with this method.
            Use :meth:`upsert_person` instead.

        Args:
            entry_id: Person's Action Network id

        Keyword Args:
            background_processing:
                Whether to utilize ActionNetwork's ``background processing``.
                This will return an immediate success, with an empty JSON body.
                Your request will be sent to the background queue for eventual processing.
                `<https://actionnetwork.org/docs/v2/#background-processing>`__
            `**kwargs`:
                Fields to be updated. The possible fields are

                - email_address:
                  Can be any of the following:

                    - a string with the person's email
                    - a dictionary with the following fields

                        - email_address (REQUIRED)
                        - primary (OPTIONAL): Boolean indicating User's primary email address
                        - status (OPTIONAL): can taken on any of these values

                            - "subscribed"
                            - "unsubscribed"
                            - "bouncing"
                            - "previous bounce"
                            - "spam complaint"
                            - "previous spam complaint"

                - given_name:
                      Person's given name
                - family_name:
                      Person's family name
                - languages_spoken:
                      Optional field. A list of strings of the languages spoken by the person
                - postal_addresses:
                      Optional field. A list of dictionaries.
                      For details, see Action Network's documentation:
                      `<https://actionnetwork.org/docs/v2/people#put>`__
                - custom_fields:
                      A dictionary of any other fields to store about the person.

        Returns:
            A JSON response confirming that the Person was updated.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/people>`__

        """
        bg_proc = background_processing or self._deprecate_pos_arg(bp, "background_processing")
        endpoint = f"{API_URL}/people/{entry_id}{'?background_processing=true' if bg_proc else ''}"
        response = self.api.put_request(endpoint, json={**kwargs}, success_codes=[204, 201, 200])
        logger.info("Person %s successfully updated", entry_id)
        return response

    @overload
    def get_petitions(
        self,
        limit: int | None = ...,
        per_page: int = ...,
        page: None = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
    ) -> Table: ...

    @overload
    def get_petitions(
        self,
        limit: int | None = ...,
        per_page: int = ...,
        page: int = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
    ) -> dict[str, _JsonType]: ...

    def get_petitions(
        self,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a list of petitions.

        Args:
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/petitions>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = "petitions"

        if page:
            return self._get_page(endpoint, page, per_page, query)

        return self._get_entry_list(endpoint, limit, per_page, query)

    def get_petition(self, petition_id: str) -> dict[str, _JsonType]:
        """
        Get a single petition, by ID.

        Args:
            petition_id: Unique ID of the petition

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/petitions>`__

        """
        endpoint = f"petitions/{petition_id}"
        return self.api.get_request(endpoint)

    def create_petition(
        self,
        title: str,
        description: str,
        petition_text: str,
        target: str,
        bp: bool = False,
        *,
        background_processing: bool = False,
    ) -> dict[str, _JsonType]:
        """
        Create a single new petition.

        Args:
            title: Title of the petition
            description: Description of the petition
            petition_text: Text of the petition
            target: Target of the petition
            background_processing:
                Whether to utilize ActionNetwork's ``background processing``.
                This will return an immediate success, with an empty JSON body.
                Your request will be sent to the background queue for eventual processing.
                `<https://actionnetwork.org/docs/v2/#background-processing>`__

        Returns:
            Information for a newly created Petition record.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/petitions>`__

        """
        bg_proc = background_processing or self._deprecate_pos_arg(bp, "background_processing")
        endpoint = f"{API_URL}/petitions{'?background_processing=true' if bg_proc else ''}"
        payload = {
            "title": title,
            "description": description,
            "petition_text": petition_text,
            "target": target,
        }
        response = self.api.post_request(endpoint, json=payload)
        logger.info("Petition %s successfully created", title)
        return response

    def update_petition(
        self,
        petition_id: str,
        title: str,
        description: str,
        petition_text: str,
        target: str,
        bp: bool = False,
        *,
        background_processing: bool = False,
    ) -> dict[str, _JsonType]:
        """
        Update the information for a single petition, by ID.

        Args:
            petition_id: Unique ID of the petition to be updated
            title: Updated title of the petition
            description: Updated description of the petition
            petition_text: Updated text of the petition
            target: Updated target of the petition
            background_processing:
                Whether to utilize ActionNetwork's ``background processing``.
                This will return an immediate success, with an empty JSON body.
                Your request will be sent to the background queue for eventual processing.
                `<https://actionnetwork.org/docs/v2/#background-processing>`__

        Returns:
            A JSON response confirming that the Petition was updated.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/petitions>`__

        """
        bg_proc = background_processing or self._deprecate_pos_arg(bp, "background_processing")
        endpoint = (
            f"{API_URL}/petitions/{petition_id}{'?background_processing=true' if bg_proc else ''}"
        )
        payload = {
            "title": title,
            "description": description,
            "petition_text": petition_text,
            "target": target,
        }
        response = self.api.put_request(endpoint, json=payload)
        logger.info("Petition %s successfully updated", title)
        return response

    @overload
    def get_queries(
        self,
        limit: int | None = ...,
        per_page: int = ...,
        page: None = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
    ) -> Table: ...

    @overload
    def get_queries(
        self,
        limit: int | None,
        per_page: int,
        page: int,
        query: str | None,
        *,
        filter: str | None,
    ) -> dict[str, _JsonType]: ...

    def get_queries(
        self,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a list of queries.

        Args:
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/queries>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = "queries"

        if page:
            return self._get_page(endpoint, page, per_page, query)

        return self._get_entry_list(endpoint, limit, per_page, query)

    def get_query(self, query_id: str) -> dict[str, _JsonType]:
        """
        Get a single query, by ID.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/queries>`__

        """
        endpoint = f"queries/{query_id}"
        return self.api.get_request(endpoint)

    @overload
    def get_petition_signatures(
        self,
        petition_id: str,
        limit: int | None = ...,
        per_page: int = ...,
        page: None = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
    ) -> Table: ...

    @overload
    def get_petition_signatures(
        self,
        petition_id: str,
        limit: int | None,
        per_page: int,
        page: int,
        query: str | None,
        *,
        filter: str | None,
    ) -> dict[str, _JsonType]: ...

    def get_petition_signatures(
        self,
        petition_id: str,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a list of signatures, for a petition, by ID.

        Args:
            petition_id: Unique ID of the petition
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/signatures>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = f"petitions/{petition_id}/signatures"

        if page:
            return self._get_page(endpoint, page, per_page, query)

        return self._get_entry_list(endpoint, limit, per_page, query)

    @overload
    def get_person_signatures(
        self,
        person_id: str,
        limit: int | None = ...,
        per_page: int = ...,
        page: None = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
    ) -> Table: ...

    @overload
    def get_person_signatures(
        self,
        person_id: str,
        limit: int | None,
        per_page: int,
        page: int,
        query: str | None,
        *,
        filter: str | None,
    ) -> dict[str, _JsonType]: ...

    def get_person_signatures(
        self,
        person_id: str,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a list of signatures, for a person, by ID.

        Args:
            person_id: Unique ID of the person
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/signatures>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = f"people/{person_id}/signatures"

        if page:
            return self._get_page(endpoint, page, per_page, query)

        return self._get_entry_list(endpoint, limit, per_page, query)

    def get_petition_signature(self, petition_id: str, signature_id: str) -> dict[str, _JsonType]:
        """
        Get a single signature, by ID, for a petition, by ID.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/signatures>`__

        """
        endpoint = f"petitions/{petition_id}/signatures/{signature_id}"
        return self.api.get_request(endpoint)

    def get_person_signature(self, person_id: str, signature_id: str) -> dict[str, _JsonType]:
        """
        Get a single signature, by ID, for a person, by ID.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/signatures>`__

        """
        endpoint = f"people/{person_id}/signatures/{signature_id}"
        return self.api.get_request(endpoint)

    def create_signature(self, petition_id: str, data: dict) -> dict[str, _JsonType]:
        """
        Create a single new signature, for a petition, by ID.

        Args:
            petition_id: Unique ID of the petition
            data:
               Payload for creating the signature

                .. code-block:: python

                   {
                       "comments" : "Stop doing the thing",
                       "_links" : {
                           "osdi:person" : { "href" : "https://actionnetwork.org/api/v2/people/id" }
                       }
                   }

        Returns:
            Information for a newly created Signature record.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/signatures>`__

        """
        endpoint = f"petitions/{petition_id}/signatures"
        return self.api.post_request(endpoint, json=data)

    def update_signature(
        self, petition_id: str, signature_id: str, data: dict
    ) -> dict[str, _JsonType]:
        """
        Update the information for a single signature, by ID, for a petition, by ID.

        Args:
            petition_id: Unique ID of the petition
            signature_id: Unique ID of the signature
            data:
                Signature payload to update

                .. code-block:: python

                    {
                        "comments": "Some new comments"
                    }

        Returns:
            Information for an updated Signature record.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/signatures>`__

        """
        endpoint = f"petitions/{petition_id}/signatures/{signature_id}"
        return self.api.put_request(endpoint, json=data)

    @overload
    def get_form_submissions(
        self,
        form_id: str,
        limit: int | None = ...,
        per_page: int = ...,
        page: None = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
    ) -> Table: ...

    @overload
    def get_form_submissions(
        self,
        form_id: str,
        limit: int | None,
        per_page: int,
        page: int,
        query: str | None,
        *,
        filter: str | None,
    ) -> dict[str, _JsonType]: ...

    def get_form_submissions(
        self,
        form_id: str,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a list of submissions, for a form, by ID.

        Args:
            form_id: Unique ID of the form
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/submissions>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = f"forms/{form_id}/submissions"

        if page:
            return self._get_page(endpoint, page, per_page, query)

        return self._get_entry_list(endpoint, limit, per_page, query)

    @overload
    def get_person_submissions(
        self,
        person_id: str,
        limit: int | None = ...,
        per_page: int = ...,
        page: None = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
    ) -> Table: ...

    @overload
    def get_person_submissions(
        self,
        person_id: str,
        limit: int | None,
        per_page: int,
        page: int,
        query: str | None,
        *,
        filter: str | None,
    ) -> dict[str, _JsonType]: ...

    def get_person_submissions(
        self,
        person_id: str,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a list of submissions, for a person, by ID.

        Args:
            person_id: Unique ID of the person
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/submissions>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = f"people/{person_id}/submissions"

        if page:
            return self._get_page(endpoint, page, per_page, query)

        return self._get_entry_list(endpoint, limit, per_page, query)

    def get_form_submission(self, form_id: str, submission_id: str) -> dict[str, _JsonType]:
        """
        Get a single submission, by ID, for a form, by ID.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/submissions>`__

        """
        endpoint = f"forms/{form_id}/submissions/{submission_id}"
        return self.api.get_request(endpoint)

    def get_person_submission(self, person_id: str, submission_id: str) -> dict[str, _JsonType]:
        """
        Get a single form submission, by ID, for a person, by ID.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/submissions>`__

        """
        endpoint = f"people/{person_id}/submissions/{submission_id}"
        return self.api.get_request(endpoint)

    def create_submission(self, form_id: str, person_id: str) -> dict[str, _JsonType]:
        """
        Create a single new submission, for a form, by ID, for a person, by ID.

        Returns:
            A JSON response indicating the success or failure of the submission creation

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/submissions>`__

        """
        endpoint = f"forms/{form_id}/submissions"
        payload = {
            "_links": {
                "osdi:person": {"href": f"https://actionnetwork.org/api/v2/people/{person_id}"}
            }
        }
        return self.api.post_request(endpoint, json=payload)

    def update_submission(
        self, form_id: str, submission_id: str, data: dict
    ) -> dict[str, _JsonType]:
        """
        Update the information for a single submission, by ID, for a form, by ID.

        Args:
            form_id: Unique ID of the form
            submission_id: Unique ID of the submission
            data:
                Payload for updating the submission

                .. code-block:: python

                    {
                        "_links" : {
                            "osdi:person" : { "href" : "https://actionnetwork.org/api/v2/people/id" }
                        }
                    }

        Returns:
            Information for an updated Submission record.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/submissions>`__

        """
        endpoint = f"forms/{form_id}/submissions/{submission_id}"
        return self.api.put_request(endpoint, json=data)

    @overload
    def get_surveys(
        self,
        limit: int | None = ...,
        per_page: int = ...,
        page: None = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
    ) -> Table: ...

    @overload
    def get_surveys(
        self,
        limit: int | None,
        per_page: int,
        page: int,
        query: str | None,
        *,
        filter: str | None,
    ) -> dict[str, _JsonType]: ...

    def get_surveys(
        self,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a list of surveys.

        Args:
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/surveys>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = "surveys"

        if page:
            return self._get_page(endpoint, page, per_page, query)

        return self._get_entry_list(endpoint, limit, per_page, query)

    def get_survey(self, survey_id: str) -> dict[str, _JsonType]:
        """
        Get a single survey, by ID.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/surveys>`__

        """
        endpoint = f"surveys/{survey_id}"
        return self.api.get_request(endpoint)

    def create_survey(self, data: dict) -> dict[str, _JsonType]:
        """
        Create a single new survey.

        Args:
            data:

                .. code-block:: python
                   :caption: Payload for creating the survey

                    {
                        "title": "My Free Survey",
                        "origin_system": "FreeSurveys.com"
                    }

                OR

                .. code-block:: python
                   :caption: Payload for creating the survey with a creator link

                    {
                        "title": "My Free Survey",
                        "origin_system": "FreeSurveys.com"
                            "_links" : {
                                "osdi:creator" : {
                                "href" : "https://actionnetwork.org/api/v2/people/[person_id]"
                                }
                        }
                    }

        Returns:
            Information for a newly created Survey record.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/surveys>`__

        """
        endpoint = "surveys"
        return self.api.post_request(endpoint, json=data)

    def update_survey(self, survey_id: str, data: dict) -> dict[str, _JsonType]:
        """
        Update the information for a survey, by ID.

        Args:
            survey_id: Unique ID of the survey
            data:
                Payload for updating the survey

                .. code-block:: python

                    {
                        "title": "My Free Survey",
                        "origin_system": "FreeSurveys.com",
                    }

        Returns:
            Information for an updated Survey record.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/surveys>`__

        """
        endpoint = f"surveys/{survey_id}"
        return self.api.post_request(endpoint, json=data)

    def get_tags(
        self,
        limit: int | None = None,
        per_page: int | None = None,
    ) -> Table:
        """
        Get a list of tags.

        Args:
            limit: The maximum number of entries to retrieve.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/tags>`__

        """
        if per_page:
            warnings.warn(
                "per_page is a deprecated argument on get_tags()",
                DeprecationWarning,
                stacklevel=2,
            )

        return self._get_entry_list("tags", limit)

    def get_tag(self, tag_id: str) -> dict[str, _JsonType]:
        """
        Get a single tag, by ID.

        Returns:
            Information for a single tag. If the entry doesn't exist,
            Action Network returns ``{'error': 'Couldn't find tag with id = <id>'}``.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/tags>`__

        """
        endpoint = f"tags/{tag_id}"
        return self.api.get_request(endpoint)

    def add_tag(self, name: str) -> dict[str, _JsonType]:
        """
        Create a single new tag.

        .. warning::

            Once created, tags **cannot** be edited or deleted.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/tags>`__

        """
        endpoint = f"{API_URL}/tags"
        payload = {"name": name}
        response = self.api.post_request(endpoint, json=payload)
        person_id = self._extract_identifiers(response).get("action_network")
        logger.info("Tag %s successfully added to tags.", person_id)
        return response

    @overload
    def get_taggings(
        self,
        tag_id: str,
        limit: int | None = ...,
        per_page: int = ...,
        page: None = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
    ) -> Table: ...

    @overload
    def get_taggings(
        self,
        tag_id: str,
        limit: int | None,
        per_page: int,
        page: int,
        query: str | None,
        *,
        filter: str | None,
    ) -> dict[str, _JsonType]: ...

    def get_taggings(
        self,
        tag_id: str,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a list of taggings, for a tag, by ID.

        Args:
            tag_id: Unique ID of the tag
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/taggings>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = f"tags/{tag_id}/taggings"

        if page:
            return self._get_page(endpoint, page, per_page, query)

        return self._get_entry_list(endpoint, limit, per_page, query)

    def get_tagging(self, tag_id: str, tagging_id: str) -> dict[str, _JsonType]:
        """
        Get a single tagging, by ID, for a tag, by ID.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/taggings>`__

        """
        endpoint = f"tags/{tag_id}/taggings/{tagging_id}"
        return self.api.get_request(endpoint)

    def create_tagging(
        self, tag_id: str, payload: dict, bp: bool = False, *, background_processing: bool = False
    ) -> dict[str, _JsonType]:
        """
        Create a single new tagging, for a tag, by ID.

        Args:
            tag_id: Unique ID of the tag
            payload:
                Payload for creating the tagging

                .. code-block:: python

                    {
                        "_links" : {
                            "osdi:person" : { "href" : "https://actionnetwork.org/api/v2/people/id" }
                        }
                    }

            background_processing:
                Whether to utilize ActionNetwork's ``background processing``.
                This will return an immediate success, with an empty JSON body.
                Your request will be sent to the background queue for eventual processing.
                `<https://actionnetwork.org/docs/v2/#background-processing>`__

        Returns:
            Information for a newly created Tagging record.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/taggings>`__

        """
        bg_proc = background_processing or self._deprecate_pos_arg(bp, "background_processing")
        endpoint = f"tags/{tag_id}/taggings{'?background_processing=true' if bg_proc else ''}"
        return self.api.post_request(endpoint, json=payload)

    def delete_tagging(
        self,
        tag_id: str,
        tagging_id: str,
        bp: bool = False,
        *,
        background_processing: bool = False,
    ) -> _JsonType:
        """
        Delete a single tagging, by ID, for a tag, by ID.

        Args:
            tag_id: Unique ID of the tag
            tagging_id: Unique ID of the tagging to be deleted

        Keyword Args:
            background_processing:
                Whether to utilize ActionNetwork's ``background processing``.
                This will return an immediate success, with an empty JSON body.
                Your request will be sent to the background queue for eventual processing.
                `<https://actionnetwork.org/docs/v2/#background-processing>`__

        Returns:
            A JSON response indicating the success or failure of deleting the Tagging.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/taggings>`__

        """
        bg_proc = background_processing or self._deprecate_pos_arg(bp, "background_processing")
        endpoint = (
            f"tags/{tag_id}/taggings/{tagging_id}{'?background_processing=true' if bg_proc else ''}"
        )
        return self.api.delete_request(endpoint)

    @overload
    def get_wrappers(
        self,
        limit: int | None = ...,
        per_page: int = ...,
        page: None = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
    ) -> Table: ...

    @overload
    def get_wrappers(
        self,
        limit: int | None,
        per_page: int,
        page: int,
        query: str | None,
        *,
        filter: str | None,
    ) -> dict[str, _JsonType]: ...

    def get_wrappers(
        self,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a list of wrappers.

        Args:
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/wrappers>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = "wrappers"

        if page:
            return self._get_page(endpoint, page, per_page, query)

        return self._get_entry_list(endpoint, limit, per_page, query)

    def get_wrapper(self, wrapper_id: str) -> dict[str, _JsonType]:
        """
        Get a single wrapper, by ID.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/wrappers>`__

        """
        endpoint = f"wrappers/{wrapper_id}"
        return self.api.get_request(endpoint)

    @overload
    def get_unique_id_lists(
        self,
        limit: int | None = ...,
        per_page: int = ...,
        page: None = ...,
        query: str | None = ...,
        *,
        filter: str | None = ...,
    ) -> Table: ...

    @overload
    def get_unique_id_lists(
        self,
        limit: int | None,
        per_page: int,
        page: int,
        query: str | None,
        *,
        filter: str | None,
    ) -> dict[str, _JsonType]: ...

    def get_unique_id_lists(
        self,
        limit: int | None = None,
        per_page: int = MAX_PER_PAGE,
        page: int | None = None,
        query: str | None = None,
        *,
        filter: str | None = None,
    ) -> dict[str, _JsonType] | Table:
        """
        Get a list of Unique ID lists.

        Args:
            limit: The maximum number of entries to retrieve.
            per_page: The number of entries per page. Cannot exceed 25.
            page: Which page of results to return.
            query:
                OData query for filtering results.
                E.g. ``modified_date gt '2014-03-25'``.
                If ``None``, no filter is applied.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/unique_id_lists>`__

        """
        query = query or self._deprecate_kw_arg(filter, "filter", "query")
        endpoint = "unique_id_lists"

        if page:
            return self._get_page(endpoint, page, per_page, query)

        return self._get_entry_list(endpoint, limit, per_page, query)

    def get_unique_id_list(self, unique_id_list_id: str) -> dict[str, _JsonType]:
        """
        Get a single Unique ID list, by ID.

        Returns:
            A JSON response with Unique ID list details

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/unique_id_lists>`__

        """
        endpoint = f"unique_id_lists/{unique_id_list_id}"
        return self.api.get_request(endpoint)

    def create_unique_id_list(self, list_name: str, unique_ids: list[str]) -> dict[str, _JsonType]:
        """
        Create a single new Unique ID list.

        Args:
            list_name: Name for the new list
            unique_id: An array of unique IDs to upload

        Returns:
            Information for a newly created Unique ID List record.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/unique_id_lists>`__

        """
        endpoint = "unique_id_lists"
        payload = {"name": list_name, "unique_ids": unique_ids}
        return self.api.post_request(endpoint, json=payload)
