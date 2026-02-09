import json
import logging
import re
import warnings
from typing import Literal

from parsons import Table
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector

logger = logging.getLogger(__name__)

API_URL = "https://actionnetwork.org/api/v2"


class ActionNetwork:
    """
    Init function.

    Args:
        api_token (str, optional): The OSDI API token. Defaults to None.

    """

    def __init__(self, api_token=None):
        self.api_token = check_env.check("AN_API_TOKEN", api_token)
        self.headers = {
            "Content-Type": "application/json",
            "OSDI-API-Token": self.api_token,
        }
        self.api_url = API_URL
        self.api = APIConnector(self.api_url, headers=self.headers)

    def _get_page(self, object_name, page, per_page=25, filter=None):
        # returns data from one page of results
        if per_page > 25:
            per_page = 25
            logger.info(
                "Action Network's API will not return more than 25 entries per page. \
            Changing per_page parameter to 25."
            )
        params = {"page": page, "per_page": per_page, "filter": filter}
        return self.api.get_request(url=object_name, params=params)

    def _get_entry_list(self, object_name, limit=None, per_page=25, filter=None):
        # returns a list of entries for a given object, such as people, tags, or actions
        # Filter can only be applied to people, petitions, events, forms, fundraising_pages,
        # event_campaigns, campaigns, advocacy_campaigns, signatures, attendances, submissions,
        # donations and outreaches.
        # See Action Network API docs for more info: https://actionnetwork.org/docs/v2/
        count = 0
        page = 1
        return_list = []
        while True:
            response = self._get_page(object_name, page, per_page, filter=filter)
            page = page + 1
            response_list = response["_embedded"][list(response["_embedded"])[0]]
            if not response_list:
                return Table(return_list)
            return_list.extend(response_list)
            count = count + len(response_list)
            if limit and count >= limit:
                return Table(return_list[0:limit])

    # Advocacy Campaigns
    def get_advocacy_campaigns(self, limit=None, per_page=25, page=None, filter=None):
        """
        Get advocacy campaigns.

        Args:
            limit: Defaults to None.
            per_page: The number of entries per page to return. 25 maximum. Defaults to 25.
            page: Which page of results to return. Defaults to None.
            filter: The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/advocacy_campaigns.

        """
        if page:
            return self._get_page("advocacy_campaigns", page, per_page, filter)
        return self._get_entry_list("advocacy_campaigns", limit, per_page, filter)

    def get_advocacy_campaign(self, advocacy_campaign_id):
        """
        Get advocacy campaign.

        Args:
            advocacy_campaign_id: The unique id of the advocacy_campaign.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/advocacy_campaigns.

        """
        return self.api.get_request(f"advocacy_campaigns/{advocacy_campaign_id}")

    # Attendances
    def get_person_attendances(self, person_id, limit=None, per_page=25, page=None, filter=None):
        """
        Get person attendances.

        Args:
            limit: Defaults to None.
            person_id
            per_page: The number of entries per page to return. 25 maximum. Defaults to 25.
            page: Which page of results to return. Defaults to None.
            filter: The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/attendances.

        """
        if page:
            return self._get_page(f"people/{person_id}/attendances", page, per_page, filter)
        return self._get_entry_list(f"people/{person_id}/attendances", limit, per_page, filter)

    def get_event_attendances(self, event_id, limit=None, per_page=25, page=None, filter=None):
        """
        Get event attendances.

        Args:
            event_id: The unique id of the event.
            limit: The number of entries to return. When None, returns all entries. Defaults to None.
            per_page: The number of entries per page to return. 25 maximum. Defaults to 25.
            page: Which page of results to return. Defaults to None.
            filter: The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/attendances.

        """
        if page:
            return self._get_page(f"events/{event_id}/attendances", page, per_page, filter)
        return self._get_entry_list(f"events/{event_id}/attendances", limit, per_page, filter)

    def get_event_attendance(self, event_id, attendance_id):
        """
        Get event attendance.

        Args:
            event_id: The unique id of the event.
            attendance_id: The unique id of the attendance.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/attendances.

        """
        return self.api.get_request(f"events/{event_id}/attendances/{attendance_id}")

    def get_person_attendance(self, person_id, attendance_id):
        """
        Get person attendance.

        Args:
            person_id: The unique id of the person.
            attendance_id: The unique id of the attendance.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/attendances.

        """
        return self.api.get_request(f"people/{person_id}/attendances/{attendance_id}")

    def create_attendance(self, event_id, payload):
        """
        Create attendance.

        Args:
            event_id: The unique id of the event.
            payload: The payload for creating the event attendance.
            .. code-block:: Python

                {
                "_links" : {
                "osdi:person" : { "href" : "https://actionnetwork.org/api/v2/people/id" }
                }
                }.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/attendances.

        """
        return self.api.post_request(f"events/{event_id}/attendances", payload)

    def update_attendance(self, event_id, attendance_id, payload):
        """
        Update attendance.

        Args:
            event_id: The unique id of the event.
            attendance_id: The unique id of the attendance.
            payload: The payload for updating the event attendance

                .. code-block:: python

                {
                "identifiers": [
                "other-system:230125a"
                ]
                }.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/attendances.

        """
        return self.api.put_request(f"events/{event_id}/attendances/{attendance_id}", payload)

    # Campaigns
    def get_campaigns(self, limit=None, per_page=25, page=None, filter=None):
        """
        Get campaigns.

        Args:
            limit: Defaults to None.
            per_page: The number of entries per page to return. 25 maximum. Defaults to 25.
            page: Which page of results to return. Defaults to None.
            filter: The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/campaigns.

        """
        if page:
            return self._get_page("campaigns", page, per_page, filter)
        return self._get_entry_list("campaigns", limit, per_page, filter)

    def get_campaign(self, campaign_id):
        """
        Get campaign.

        Args:
            campaign_id: The unique id of the campaign.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/campaigns.

        """
        return self.api.get_request(f"campaigns/{campaign_id}")

    # Custom Fields
    def get_custom_fields(self):
        """
        Get custom fields.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/custom_fields.

        """
        return self.api.get_request("metadata/custom_fields")

    # Donations
    def get_donation(self, donation_id):
        """
        Get donation.

        Args:
            donation_id: The unique id of the donation.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/donations.

        """
        return self.api.get_request(url=f"donations/{donation_id}")

    def get_donations(self, limit=None, per_page=25, page=None, filter=None):
        """
        Get donations.

        Args:
            limit: The number of entries to return. When None, returns all entries. Defaults to None.
            per_page: The number of entries per page to return. 25 maximum. Defaults to 25.
            page: Which page of results to return. Defaults to None.
            filter: The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/donations.

        """
        if page:
            return self._get_page("donations", page, per_page, filter)
        return self._get_entry_list("donations", limit, per_page, filter)

    def get_fundraising_page_donations(
        self, fundraising_page_id, limit=None, per_page=25, page=None, filter=None
    ):
        """
        Get fundraising page donations.

        Args:
            fundraising_page_id: The id of the fundraiser.
            limit: The number of entries to return. When None, returns all entries. Defaults to None.
            per_page: The number of entries per page to return. 25 maximum. Defaults to 25.
            page: Which page of results to return. Defaults to None.
            filter: The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/donations.

        """
        if page:
            return self._get_page(
                f"fundraising_pages/{fundraising_page_id}/donations",
                page,
                per_page,
                filter,
            )
        return self._get_entry_list(
            f"fundraising_pages/{fundraising_page_id}/donations",
            limit,
            per_page,
            filter,
        )

    def get_person_donations(self, person_id, limit=None, per_page=25, page=None, filter=None):
        """
        Get person donations.

        Args:
            person_id: The id of the person.
            limit: The number of entries to return. When None, returns all entries. Defaults to None.
            per_page: The number of entries per page to return. 25 maximum. Defaults to 25.
            page: Which page of results to return. Defaults to None.
            filter: The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/donations.

        """
        if page:
            return self._get_page(
                f"people/{person_id}/donations",
                page,
                per_page,
                filter,
            )
        return self._get_entry_list(
            f"people/{person_id}/donations",
            limit,
            per_page,
            filter,
        )

    def create_donation(self, fundraising_page_id, donation_payload):
        """
        Create donation.

        Args:
            fundraising_page_id: The id of the fundraising page.
            donation_payload: The payload containing donation details.
            .. code-block:: Python

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
                }.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/donations.

        """
        return self.api.post_request(
            f"fundraising_pages/{fundraising_page_id}/donations", donation_payload
        )

    # Embeds
    def get_embeds(self, action_type, action_id):
        """
        Get embeds.

        Args:
            action_type: The action type (petition, events, etc.).
            action_id: The unique id of the action.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/embeds.

        """
        return self.api.get_request(f"{action_type}/{action_id}/embed")

    # Event Campaigns
    def get_event_campaigns(self, limit=None, per_page=25, page=None, filter=None):
        """
        Get event campaigns.

        Args:
            limit: Defaults to None.
            per_page: The number of entries per page to return. 25 maximum. Defaults to 25.
            page: Which page of results to return. Defaults to None.
            filter: The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/event_campaigns.

        """
        if page:
            return self._get_page("event_campaigns", page, per_page, filter)
        return self._get_entry_list("event_campaigns", limit, per_page, filter)

    def get_event_campaign(self, event_campaign_id):
        """
        Get event campaign.

        Args:
            event_campaign_id: The unique id of the event_campaign.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/event_campaigns.

        """
        return self.api.get_request(f"event_campaigns/{event_campaign_id}")

    def create_event_campaign(self, payload):
        """
        Create event campaign.

        Args:
            payload: The payload containing event campaign details

                .. code-block:: python

                {
                "title": "My Canvassing Event",
                "origin_system": "CanvassingEvents.com"
                }.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/event_campaigns.

        """
        return self.api.post_request("event_campaigns", payload)

    def create_event_in_event_campaign(self, event_campaign_id, payload):
        """
        Create event in event campaign.

        Args:
            event_campaign_id: The unique id of the event_campaign.
            payload: The payload containing event details

                .. code-block:: python

                {
                "title": "My Free Event",
                "origin_system": "FreeEvents.com"
                }.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/event_campaigns.

        """
        return self.api.post_request(f"event_campaigns/{event_campaign_id}/events", payload)

    def update_event_campaign(self, event_campaign_id, payload):
        """
        Update event campaign.

        Args:
            event_campaign_id: The unique id of the event_campaign.
            payload: The payload containing event campaign details

                .. code-block:: python

                {
                "description": "This is my new event campaign description"
                }.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/event_campaigns.

        """
        return self.api.put_request(f"event_campaigns/{event_campaign_id}", payload)

    # Events
    def get_events(self, limit=None, per_page=25, page=None, filter=None):
        """
        Get events.

        Args:
            limit: The number of entries to return. When None, returns all entries. Defaults to None.
            per_page: The number of entries per page to return. 25 maximum. Defaults to 25.
            page: Which page of results to return. Defaults to None.
            filter: The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/events.

        """
        if page:
            return self._get_page("events", page, per_page, filter)
        return self._get_entry_list("events", limit, per_page, filter)

    def get_event(self, event_id):
        """
        Get event.

        Args:
            event_id: The unique id of the event.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/events.

        """
        return self.api.get_request(f"events/{event_id}")

    def get_event_campaign_events(
        self, event_campaign_id, limit=None, per_page=25, page=None, filter=None
    ):
        """
        Get event campaign events.

        Args:
            event_campaign_id: The unique id of the event_campaign.
            limit: The number of entries to return. When None, returns all entries. Defaults to None.
            per_page: The number of entries per page to return. 25 maximum. Defaults to 25.
            page: Which page of results to return. Defaults to None.
            filter: The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/events.

        """
        if page:
            return self._get_page(
                f"event_campaigns/{event_campaign_id}/events", page, per_page, filter
            )
        return self._get_entry_list(
            f"event_campaigns/{event_campaign_id}/events", limit, per_page, filter
        )

    def create_event(self, title, start_date=None, location=None):
        """
        Create an event in Action Network.

        Args:
            title (str): The public title of the event.
            start_date (str | datetime, optional): The starting date & time. If a string, use format "YYYY-MM-DD
                HH:MM:SS"
                (hint: the default format you get when you use `str()` on a datetime). Defaults to None.
            location (dict, optional): A dict of location details. Can include any combination of the types of
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
                }. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/events.

        """
        data = {"title": title}

        if start_date:
            start_date = str(start_date)
            data["start_date"] = start_date

        if isinstance(location, dict):
            data["location"] = location

        event_dict = self.api.post_request(url=f"{self.api_url}/events", data=json.dumps(data))

        an_event_id = event_dict["_links"]["self"]["href"].split("/")[-1]
        event_dict["event_id"] = an_event_id

        return event_dict

    def update_event(self, event_id, payload):
        """
        Update an event in Action Network.

        Args:
            event_id (str): The unique id of the event.
            payload (dict): The payload containing event data (see https://actionnetwork.org/docs/v2/events)

                .. code-block:: python

                {
                "title": "My Free Event With A New Name",
                "description": "This is my free event description"
                }.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/events.

        """
        return self.api.put_request(f"events/{event_id}", payload)

    # Forms
    def get_forms(self, limit=None, per_page=25, page=None, filter=None):
        """
        Get forms.

        Args:
            limit: The number of entries to return. When None, returns all entries. Defaults to None.
            per_page: The number of entries per page to return. 25 maximum. Defaults to 25.
            page: Which page of results to return. Defaults to None.
            filter: The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/forms.

        """
        if page:
            return self._get_page("forms", page, per_page, filter)
        return self._get_entry_list("forms", limit, per_page, filter)

    def get_form(self, form_id):
        """
        Get form.

        Args:
            form_id: The unique id of the form.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/forms.

        """
        return self.api.get_request(f"forms/{form_id}")

    def create_form(self, payload):
        """
        Create a form in Action Network.

        Args:
            payload (dict): The payload containing form details

                .. code-block:: python

                {
                "title": "My Free Form",
                "origin_system": "FreeForms.com"
                }.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/forms.

        """
        return self.api.post_request("forms", payload)

    def update_form(self, form_id, payload):
        """
        Update a form in Action Network.

        Args:
            form_id: The unique id of the form.
            payload (dict): The payload containing form data (see https://actionnetwork.org/docs/v2/forms)

                .. code-block:: python

                {
                "title": "My Free Form",
                "origin_system": "FreeForms.com"
                }.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/forms.

        """
        return self.api.put_request(f"forms/{form_id}", payload)

    # Fundraising Pages
    def get_fundraising_page(self, fundraising_page_id):
        """
        Get fundraising page.

        Args:
            fundraising_page_id: The id of the fundraiser.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/fundraising_pages.

        """
        return self.api.get_request(url=f"fundraising_pages/{fundraising_page_id}")

    def get_fundraising_pages(self, limit=None, per_page=25, page=None, filter=None):
        """
        Get fundraising pages.

        Args:
            limit: The number of entries to return. When None, returns all entries. Defaults to None.
            per_page: The number of entries per page to return. 25 maximum. Defaults to 25.
            page: Which page of results to return. Defaults to None.
            filter: The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/fundraising_pages.

        """
        if page:
            return self._get_page("fundraising_pages", page, per_page, filter)
        return self._get_entry_list(
            "fundraising_pages",
            limit,
        )

    def create_fundraising_page(self, payload):
        """
        Create a fundraising page in Action Network.

        Args:
            payload (dict): The payload containing fundraising page details

                .. code-block:: python

                {
                "title": "My Free Fundraiser",
                "origin_system": "FreeFundraisers.com"
                }.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/fundraising_pages.

        """
        return self.api.post_request("fundraising_pages", payload)

    def update_fundraising_page(self, fundraising_page_id, payload: dict):
        """
        Update a fundraising page in Action Network.

        Args:
            fundraising_page_id: The id of the fundraiser.
            payload (dict): The payload containing updated fundraising page details

                .. code-block:: python

                {
                "title": "My Free Fundraiser",
                "origin_system": "FreeFundraisers.com"
                }.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/fundraising_pages.

        """
        return self.api.put_request(f"fundraising_pages/{fundraising_page_id}", payload)

    # Items
    def get_items(self, list_id, limit=None, per_page=25, page=None, filter=None):
        """
        Get items.

        Args:
            list_id: The unique id of the list.
            limit: The number of entries to return. When None, returns all entries. Defaults to None.
            per_page: The number of entries per page to return. 25 maximum. Defaults to 25.
            page: Which page of results to return. Defaults to None.
            filter: The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/items.

        """
        if page:
            return self._get_page(f"lists/{list_id}/items", page, per_page, filter)
        return self._get_entry_list(f"lists/{list_id}/items", limit, per_page, filter)

    def get_item(self, list_id, item_id):
        """
        Get item.

        Args:
            list_id: The unique id of the list.
            item_id: The unique id of the item.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/items.

        """
        return self.api.get_request(f"lists/{list_id}/items/{item_id}")

    # Lists
    def get_lists(self, limit=None, per_page=25, page=None, filter=None):
        """
        Get lists.

        Args:
            limit: The number of entries to return. When None, returns all entries. Defaults to None.
            per_page: The number of entries per page to return. 25 maximum. Defaults to 25.
            page: Which page of results to return. Defaults to None.
            filter: The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/lists.

        """
        if page:
            return self._get_page("lists", page, per_page, filter)
        return self._get_entry_list("lists", limit, per_page, filter)

    def get_list(self, list_id):
        """
        Get list.

        Args:
            list_id: The unique id of the list.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/lists.

        """
        return self.api.get_request(f"lists/{list_id}")

    # Messages
    def get_messages(
        self, limit=None, per_page=25, page=None, filter=None, unpack_statistics=False
    ):
        """
        Get messages.

        Args:
            limit: The number of entries to return. When None, returns all entries. Defaults to None.
            per_page: The number of entries per page to return. 25 maximum. Defaults to 25.
            page: Which page of results to return. Defaults to None.
            filter: The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied. Defaults to None.
            unpack_statistics: Whether to unpack the statistics dictionary into the table.
                Defaults to False.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/messages.

        """
        if page:
            return self._get_page("messages", page, per_page, filter)
        tbl = self._get_entry_list("messages", limit, per_page, filter)
        # Unpack statistics
        if unpack_statistics:
            tbl.unpack_dict("statistics", prepend=False, include_original=True)
        return tbl

    def get_message(self, message_id):
        """
        Get message.

        Args:
            message_id: The unique id of the message.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/messages.

        """
        return self.api.get_request(f"messages/{message_id}")

    def create_message(self, payload):
        """
        Create a message in Action Network.

        Args:
            payload (dict): The payload containing message details

                .. code-block:: python

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
                }.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/messages.

        """
        return self.api.post_request("messages", json=payload)

    def update_message(self, message_id, payload):
        """
        Update a message in Action Network.

        Args:
            message_id: The unique id of the message.
            payload (dict): The payload containing message details to be updated

                .. code-block:: python

                {
                "name": "Stop doing the bad thing email send 1",
                "subject": "Please! Stop doing the bad thing"
                }.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/messages.

        """
        return self.api.put_request(f"messages/{message_id}", json=payload)

    def schedule_message(self, message_id, scheduled_start_date):
        """
        Schedule a message in Action Network.

        Args:
            message_id: The unique id of the message.
            scheduled_start_date: The UTC timestamp to schedule the message at in ISO8601 format.
                e.g. "2015-03-14T12:00:00Z".

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/schedule_helper.

        """
        return self.api.post_request(
            f"messages/{message_id}/schedule/",
            {"scheduled_start_date": scheduled_start_date},
        )

    def send_message(self, message_id):
        """
        Send a message in Action Network.

        Args:
            message_id: The unique id of the message.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/send_helper.

        """
        return self.api.post_request(f"messages/{message_id}/send/", {})

    # Metadata
    def get_metadata(self):
        """
        Get metadata.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/metadata.

        """
        return self.api.get_request("metadata")

    # Outreaches
    def get_advocacy_campaign_outreaches(
        self, advocacy_campaign_id, limit=None, per_page=25, page=None, filter=None
    ):
        """
        Get advocacy campaign outreaches.

        Args:
            advocacy_campaign_id: The unique id of the advocacy_campaign.
            limit: The number of entries to return. When None, returns all entries. Defaults to None.
            per_page: The number of entries per page to return. 25 maximum. Defaults to 25.
            page: Which page of results to return. Defaults to None.
            filter: The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/outreaches.

        """
        if page:
            return self._get_page(
                f"advocacy_campaigns/{advocacy_campaign_id}/outreaches",
                page,
                per_page,
                filter,
            )
        return self._get_entry_list(
            f"advocacy_campaigns/{advocacy_campaign_id}/outreaches",
            limit,
            per_page,
            filter,
        )

    def get_person_outreaches(self, person_id, limit=None, per_page=25, page=None, filter=None):
        """
        Get person outreaches.

        Args:
            person_id: The unique id of the person.
            limit: The number of entries to return. When None, returns all entries. Defaults to None.
            per_page: The number of entries per page to return. 25 maximum. Defaults to 25.
            page: Which page of results to return. Defaults to None.
            filter: The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/outreaches.

        """
        if page:
            return self._get_page(f"people/{person_id}/outreaches", page, per_page, filter)
        return self._get_entry_list(f"people/{person_id}/outreaches", limit, per_page, filter)

    def get_advocacy_campaign_outreach(self, advocacy_campaign_id, outreach_id):
        """
        Get advocacy campaign outreach.

        Args:
            advocacy_campaign_id: The unique id of the campaign.
            outreach_id: The unique id of the outreach.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/outreaches.

        """
        return self.api.get_request(
            f"advocacy_campaigns/{advocacy_campaign_id}/outreaches/{outreach_id}"
        )

    def get_person_outreach(self, person_id, outreach_id):
        """
        Get person outreach.

        Args:
            person_id: The unique id of the campaign.
            outreach_id: The unique id of the outreach.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/outreaches.

        """
        return self.api.get_request(f"people/{person_id}/outreaches/{outreach_id}")

    def create_outreach(self, advocacy_campaign_id, payload):
        """
        Create an outreach in Action Network.

        Args:
            advocacy_campaign_id: The unique id of the campaign.
            payload: The payload containing outreach details

                .. code-block:: python

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
                }.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/outreaches.

        """
        return self.api.post_request(
            f"advocacy_campaigns/{advocacy_campaign_id}/outreaches", payload
        )

    def update_outreach(self, advocacy_campaign_id, outreach_id, payload):
        """
        Update an outreach in Action Network.

        Args:
            advocacy_campaign_id: The unique id of the campaign.
            outreach_id: The unique id of the outreach.
            payload: The payload containing outreach details to be updated

                .. code-block:: python

                {
                "subject": "Please vote no!"
                }.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/outreaches.

        """
        return self.api.put_request(
            f"advocacy_campaigns/{advocacy_campaign_id}/outreaches/{outreach_id}",
            payload,
        )

    # People
    def get_people(self, limit=None, per_page=25, page=None, filter=None):
        """
        Get people.

        Args:
            limit: The number of entries to return. When None, returns all entries. Defaults to None.
            per_page: The number of entries per page to return. 25 maximum. Defaults to 25.
            page: Which page of results to return. Defaults to None.
            filter: The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/people.

        """
        if page:
            return self._get_page("people", page, per_page, filter=filter)
        return self._get_entry_list("people", limit, per_page, filter=filter)

    def get_person(self, person_id):
        """
        Get person.

        Args:
            person_id: ID of the person.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/people.

        """
        return self.api.get_request(url=f"people/{person_id}")

    def upsert_person(
        self,
        email_address: str | list[str] | list[dict[str, str]] = None,
        given_name=None,
        family_name=None,
        tags=None,
        languages_spoken=None,
        postal_addresses=None,
        mobile_number=None,
        mobile_status: Literal["subscribed", "unsubscribed", None] = None,
        background_processing=False,
        **kwargs,
    ):
        """
        Creates or updates a person record.

        In order to update an existing record instead of creating a new one, you must supply an email or mobile number
        which matches a record in the database.

        Identifiers are intentionally not included as an option on this method, because their use can cause buggy
        behavior if they are not globally unique. ActionNetwork support strongly encourages developers not to use custom
        identifiers.

        Args:
            **kwargs
            background_processing: Defaults to False.
            mobile_status (Literal["subscribed", "unsubscribed", None], optional): Defaults to None.
            mobile_number: Defaults to None.
            postal_addresses: Defaults to None.
            languages_spoken: Defaults to None.
            tags: Defaults to None.
            family_name: Defaults to None.
            given_name: Defaults to None.
            email_address (str | list[str] | list[dict[str, str]], optional): Defaults to None.
            Documentation Reference: https://actionnetwork.org/docs/v2/people.

        """
        email_addresses_field = None
        if isinstance(email_address, str):
            email_addresses_field = [{"address": email_address}]
        elif isinstance(email_address, list):
            if isinstance(email_address[0], str):
                email_addresses_field = [{"address": email} for email in email_address]
                email_addresses_field[0]["primary"] = True
            if isinstance(email_address[0], dict):
                email_addresses_field = email_address
        else:
            raise ValueError(
                f"Unexpected type for email_address. Got {type(email_address)}, "
                "expected str or list."
            )

        mobile_numbers_field = None
        if isinstance(mobile_number, str):
            mobile_numbers_field = [{"number": re.sub("[^0-9]", "", mobile_number)}]
        elif isinstance(mobile_number, int):
            mobile_numbers_field = [{"number": str(mobile_number)}]
        elif isinstance(mobile_number, list):
            if len(mobile_number) > 1:
                raise Exception("Action Network allows only 1 phone number per activist")
            if isinstance(mobile_number[0], list):
                mobile_numbers_field = [
                    {"number": re.sub("[^0-9]", "", cell)} for cell in mobile_number
                ]
                mobile_numbers_field[0]["primary"] = True
            if isinstance(mobile_number[0], int):
                mobile_numbers_field = [{"number": cell} for cell in mobile_number]
                mobile_numbers_field[0]["primary"] = True

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
            raise Exception(
                "Either email_address or mobile_number is required and can be formatted "
                "as a string, list of strings, a dictionary, a list of dictionaries, or "
                "(for mobile_number only) an integer or list of integers"
            )

        data = {"person": {}}

        if email_addresses_field is not None:
            data["person"]["email_addresses"] = email_addresses_field
        if mobile_numbers_field is not None:
            data["person"]["phone_numbers"] = mobile_numbers_field
        if given_name is not None:
            data["person"]["given_name"] = given_name
        if family_name is not None:
            data["person"]["family_name"] = family_name
        if languages_spoken is not None:
            data["person"]["languages_spoken"] = languages_spoken
        if postal_addresses is not None:
            data["person"]["postal_addresses"] = postal_addresses
        if tags is not None:
            data["add_tags"] = tags

        data["person"]["custom_fields"] = {**kwargs}
        url = f"{self.api_url}/people"
        if background_processing:
            url = f"{url}?background_processing=true"

        response = self.api.post_request(url, data=json.dumps(data))

        identifiers = response["identifiers"]
        person_id = [
            entry_id.split(":")[1] for entry_id in identifiers if "action_network:" in entry_id
        ]
        if not person_id:
            logger.error(f"Response gave no valid person_id: {identifiers}")
        else:
            person_id = person_id[0]
        if response["created_date"] == response["modified_date"]:
            logger.info(f"Entry {person_id} successfully added.")
        else:
            logger.info(f"Entry {person_id} successfully updated.")
        return response

    def add_person(
        self,
        email_address=None,
        given_name=None,
        family_name=None,
        tags=None,
        languages_spoken=None,
        postal_addresses=None,
        mobile_number=None,
        mobile_status="subscribed",
        **kwargs,
    ):
        """
        Creates a person in the database.

        WARNING: this endpoint has been deprecated in favor of upsert_person.
        """
        logger.warning("Method 'add_person' has been deprecated. Please use 'upsert_person'.")
        # Pass inputs to preferred method:
        self.upsert_person(
            email_address=email_address,
            given_name=given_name,
            family_name=family_name,
            languages_spoken=languages_spoken,
            postal_addresses=postal_addresses,
            mobile_number=mobile_number,
            mobile_status=mobile_status,
            **kwargs,
        )

    def update_person(self, entry_id, background_processing=False, **kwargs):
        """
        Updates a person's data in Action Network, given their Action Network ID.

        Note that you can't alter a person's tags with this method. Instead, use upsert_person.

        Args:
            **kwargs
            background_processing: Defaults to False.
            entry_id
            Documentation Reference: https://actionnetwork.org/docs/v2/people.

        """
        data = {**kwargs}
        url = f"{self.api_url}/people/{entry_id}"
        if background_processing:
            url = f"{url}?background_processing=true"
        response = self.api.put_request(
            url=url,
            data=json.dumps(data),
            success_codes=[204, 201, 200],
        )
        logger.info(f"Person {entry_id} successfully updated")
        return response

    # Petitions
    def get_petitions(self, limit=None, per_page=25, page=None, filter=None):
        """
        Get petitions.

        Args:
            limit: The number of entries to return. When None, returns all entries. Defaults to None.
            per_page: The number of entries per page to return. 25 maximum. Defaults to 25.
            page: Which page of results to return. Defaults to None.
            filter: The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/petitions.

        """
        if page:
            return self._get_page("petitions", page, per_page, filter)
        return self._get_entry_list("petitions", limit, per_page, filter)

    def get_petition(self, petition_id):
        """
        Get petition.

        Args:
            petition_id: The unique id of the petition.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/petitions.

        """
        return self.api.get_request(f"petitions/{petition_id}")

    def create_petition(
        self, title, description, petition_text, target, background_processing=False
    ):
        """
        Create petition.

        Args:
            title: The title of the petition.
            description: The description of the petition.
            petition_text: The text of the petition.
            target: The target of the petition.
            background_processing: Whether to process the request in the background. Defaults to False.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/petitions.

        """
        data = {
            "title": title,
            "description": description,
            "petition_text": petition_text,
            "target": target,
        }
        url = f"{self.api_url}/petitions"
        if background_processing:
            url = f"{url}?background_processing={background_processing}"
        response = self.api.post_request(
            url=url,
            data=json.dumps(data),
        )
        logger.info(f"Petition {title} successfully created")
        return response

    def update_petition(
        self,
        petition_id,
        title,
        description,
        petition_text,
        target,
        background_processing=False,
    ):
        """
        Update petition.

        Args:
            petition_id: The unique id of the petition to be updated.
            title: The updated title of the petition.
            description: The updated description of the petition.
            petition_text: The updated text of the petition.
            target: The updated target of the petition.
            background_processing: Whether to process the request in the background. Defaults to False.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/petitions.

        """
        data = {
            "title": title,
            "description": description,
            "petition_text": petition_text,
            "target": target,
        }
        url = f"{self.api_url}/petitions/{petition_id}"
        if background_processing:
            url = f"{url}?background_processing={background_processing}"
        response = self.api.put_request(
            url=url,
            data=json.dumps(data),
        )
        logger.info(f"Petition {title} successfully updated")
        return response

    # Queries
    def get_queries(self, limit=None, per_page=25, page=None, filter=None):
        """
        Get queries.

        Args:
            limit: Defaults to None.
            per_page: The number of entries per page to return. 25 maximum. Defaults to 25.
            page: Which page of results to return. Defaults to None.
            filter: The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/queries.

        """
        if page:
            return self._get_page("queries", page, per_page, filter)
        return self._get_entry_list("queries", limit, per_page, filter)

    def get_query(self, query_id):
        """
        Get query.

        Args:
            query_id: The unique id of the query.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/queries.

        """
        return self.api.get_request(f"queries/{query_id}")

    # Signatures
    def get_petition_signatures(self, petition_id, limit=None, per_page=25, page=None, filter=None):
        """
        Get petition signatures.

        Args:
            petition_id: The unique id of the petition.
            limit: The number of entries to return. When None, returns all entries. Defaults to None.
            per_page: The number of entries per page to return. 25 maximum. Defaults to 25.
            page: Which page of results to return. Defaults to None.
            filter: The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/signatures.

        """
        if page:
            return self._get_page(f"petitions/{petition_id}/signatures", page, per_page, filter)
        return self._get_entry_list(f"petitions/{petition_id}/signatures", limit, per_page, filter)

    def get_person_signatures(self, person_id, limit=None, per_page=25, page=None, filter=None):
        """
        Get person signatures.

        Args:
            person_id: The unique id of the person.
            limit: The number of entries to return. When None, returns all entries. Defaults to None.
            per_page: The number of entries per page to return. 25 maximum. Defaults to 25.
            page: Which page of results to return. Defaults to None.
            filter: The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/signatures.

        """
        if page:
            return self._get_page(f"people/{person_id}/signatures", page, per_page, filter)
        return self._get_entry_list(f"people/{person_id}/signatures", limit, per_page, filter)

    def get_petition_signature(self, petition_id, signature_id):
        """
        Get petition signature.

        Args:
            petition_id: The unique id of the petition.
            signature_id: The unique id of the signature.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/signatures.

        """
        return self.api.get_request(f"petitions/{petition_id}/signatures/{signature_id}")

    def get_person_signature(self, person_id, signature_id):
        """
        Get person signature.

        Args:
            person_id: The unique id of the person.
            signature_id: The unique id of the signature.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/signatures.

        """
        return self.api.get_request(f"people/{person_id}/signatures/{signature_id}")

    def create_signature(self, petition_id, data):
        """
        Create signature.

        Args:
            petition_id: The unique id of the petition.
            data: The payload for creating the signature

                .. code-block:: python

                {
                "comments" : "Stop doing the thing",
                "_links" : {
                "osdi:person" : { "href" : "https://actionnetwork.org/api/v2/people/id" }
                }
                }.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/signatures.

        """
        return self.api.post_request(f"petitions/{petition_id}/signatures", data)

    def update_signature(self, petition_id, signature_id, data):
        """
        Update signature.

        Args:
            petition_id: The unique id of the petition.
            signature_id: The unique id of the signature.
            data: The signature payload to update

                .. code-block:: python

                {
                "comments": "Some new comments"
                }.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/signatures.

        """
        return self.api.put_request(f"petitions/{petition_id}/signatures/{signature_id}", data)

    # Submissions
    def get_form_submissions(self, form_id, limit=None, per_page=25, page=None, filter=None):
        """
        Get form submissions.

        Args:
            limit: Defaults to None.
            form_id
            per_page: The number of entries per page to return. 25 maximum. Defaults to 25.
            page: Which page of results to return. Defaults to None.
            filter: The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/submissions.

        """
        if page:
            return self._get_page(f"forms/{form_id}/submissions", page, per_page, filter)
        return self._get_entry_list(f"forms/{form_id}/submissions", limit, per_page, filter)

    def get_person_submissions(self, person_id, limit=None, per_page=25, page=None, filter=None):
        """
        Get person submissions.

        Args:
            person_id: The unique id of the person.
            limit: The number of entries to return. When None, returns all entries. Defaults to None.
            per_page: The number of entries per page to return. 25 maximum. Defaults to 25.
            page: Which page of results to return. Defaults to None.
            filter: The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/submissions.

        """
        if page:
            return self._get_page(f"people/{person_id}/submissions", page, per_page, filter)
        return self._get_entry_list(f"people/{person_id}/submissions", limit, per_page, filter)

    def get_form_submission(self, form_id, submission_id):
        """
        Get form submission.

        Args:
            form_id: The unique id of the form.
            submission_id: The unique id of the submission.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/submissions.

        """
        return self.api.get_request(f"forms/{form_id}/submissions/{submission_id}")

    def get_person_submission(self, person_id, submission_id):
        """
        Get person submission.

        Args:
            person_id: The unique id of the submission.
            submission_id: The unique id of the submission.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/submissions.

        """
        return self.api.get_request(f"people/{person_id}/submissions/{submission_id}")

    def create_submission(self, form_id, person_id):
        """
        Create submission.

        Args:
            form_id: The unique id of the form.
            person_id: The unique id of the person.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/submissions.

        """
        payload = {
            "_links": {
                "osdi:person": {"href": f"https://actionnetwork.org/api/v2/people/{person_id}"}
            }
        }
        return self.api.post_request(f"forms/{form_id}/submissions", data=json.dumps(payload))

    def update_submission(self, form_id, submission_id, data):
        """
        Update submission.

        Args:
            form_id: The unique id of the form.
            submission_id: The unique id of the submission.
            data: The payload for updating the submission

                .. code-block:: python

                {
                "_links" : {
                "osdi:person" : { "href" : "https://actionnetwork.org/api/v2/people/id" }
                }
                }.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/submissions.

        """
        return self.api.put_request(
            f"forms/{form_id}/submissions/{submission_id}", data=json.dumps(data)
        )

    # Surveys
    def get_surveys(self, limit=None, per_page=25, page=None, filter=None):
        """
        Survey resources are sometimes presented as collections of surveys.

        For example, calling the surveys endpoint will return a collection of all the surveys associated with your API
        key.

        Args:
            filter: Defaults to None.
            page: Defaults to None.
            limit: The number of entries to return. When None, returns all entries. Defaults to None.
            per_page: The number of entries per page to return. 25 maximum. Defaults to 25.

        """
        if page:
            return self._get_page("surveys", page, per_page, filter)
        return self._get_entry_list("surveys", limit, per_page, filter)

    def get_survey(self, survey_id):
        """
        Get survey.

        Args:
            survey_id: The unique id of the survey.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/surveys.

        """
        return self.api.get_request(f"surveys/{survey_id}")

    def create_survey(self, data):
        """
        Create survey.

        Args:
            data: The payload for creating the survey

                .. code-block:: python

                {
                "title": "My Free Survey",
                "origin_system": "FreeSurveys.com"
                }

                OR

                The payload for creating the survey with a creator link

                .. code-block:: python

                {
                "title": "My Free Survey",
                "origin_system": "FreeSurveys.com"
                "_links" : {
                "osdi:creator" : {
                "href" : "https://actionnetwork.org/api/v2/people/[person_id]"
                }
                }
                }.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/surveys.

        """
        return self.api.post_request("surveys", data=json.dumps(data))

    def update_survey(self, survey_id, data):
        """
        Update survey.

        Args:
            survey_id: The unique id of the survey.
            data: The payload for updating the survey

                .. code-block:: python

                {
                "title": "My Free Survey",
                "origin_system": "FreeSurveys.com",
                }.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/surveys.

        """
        return self.api.post_request(f"surveys/{survey_id}", data=json.dumps(data))

    # Tags
    def get_tags(self, limit=None, per_page=None):
        """
        Get tags.

        Args:
            limit: The number of entries to return. When None, returns all entries. Defaults to None.
            per_page: This is a deprecated argument. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/tags.

        """
        if per_page:
            warnings.warn(
                "per_page is a deprecated argument on get_tags()",
                category=DeprecationWarning,
                stacklevel=2,
            )
        return self._get_entry_list("tags", limit)

    def get_tag(self, tag_id):
        """
        Get tag.

        Args:
            tag_id: Id of the tag.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/tags.

        """
        return self.api.get_request(url=f"tags/{tag_id}")

    def add_tag(self, name):
        """
        Adds a tag to Action Network.

        Once created, tags CANNOT be edited or deleted.

        Args:
            name
            Documentation Reference: https://actionnetwork.org/docs/v2/tags.

        """
        data = {"name": name}
        response = self.api.post_request(url=f"{self.api_url}/tags", data=json.dumps(data))
        identifiers = response["identifiers"]
        person_id = [
            entry_id.split(":")[1] for entry_id in identifiers if "action_network:" in entry_id
        ][0]
        logger.info(f"Tag {person_id} successfully added to tags.")
        return response

    # Taggings
    def get_taggings(self, tag_id, limit=None, per_page=25, page=None, filter=None):
        """
        Get taggings.

        Args:
            tag_id: The unique id of the tag.
            limit: The number of entries to return. When None, returns all entries. Defaults to None.
            per_page: The number of entries per page to return. 25 maximum. Defaults to 25.
            page: Which page of results to return. Defaults to None.
            filter: The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/taggings.

        """
        if page:
            return self._get_page(f"tags/{tag_id}/taggings", page, per_page, filter)
        return self._get_entry_list(f"tags/{tag_id}/taggings", limit, per_page, filter)

    def get_tagging(self, tag_id, tagging_id):
        """
        Get tagging.

        Args:
            tag_id: The unique id of the tag.
            tagging_id: The unique id of the tagging.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/taggings.

        """
        return self.api.get_request(f"tags/{tag_id}/taggings/{tagging_id}")

    def create_tagging(self, tag_id, payload, background_processing=False):
        """
        Create tagging.

        Args:
            tag_id: The unique id of the tag.
            payload: The payload for creating the tagging

                .. code-block:: python

                {
                "_links" : {
                "osdi:person" : { "href" : "https://actionnetwork.org/api/v2/people/id" }
                }
                }.
            background_processing (bool, optional): If set `true`, utilize ActionNetwork's "background processing".
                This will return an immediate success, with an empty JSON body, and send your request to the background
                queue for eventual processing. https://actionnetwork.org/docs/v2/#background-processing.
                Defaults to False.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/taggings.

        """
        url = f"tags/{tag_id}/taggings"
        if background_processing:
            url = f"{url}?background_processing=true"
        return self.api.post_request(url, data=json.dumps(payload))

    def delete_tagging(self, tag_id, tagging_id, background_processing=False):
        """
        Delete tagging.

        Args:
            tag_id: The unique id of the tag.
            tagging_id: The unique id of the tagging to be deleted.
            background_processing (bool, optional): If set `true`, utilize ActionNetwork's "background processing".
                This will return an immediate success, with an empty JSON body, and send your request to the background
                queue for eventual processing. https://actionnetwork.org/docs/v2/#background-processing.
                Defaults to False.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/taggings.

        """
        url = f"tags/{tag_id}/taggings/{tagging_id}"
        if background_processing:
            url = f"{url}?background_processing=true"
        return self.api.delete_request(url)

    # Wrappers
    def get_wrappers(self, limit=None, per_page=25, page=None, filter=None):
        """
        Get wrappers.

        Args:
            limit: The number of entries to return. When None, returns all entries. Defaults to None.
            per_page: The number of entries per page to return. 25 maximum. Defaults to 25.
            page: Which page of results to return. Defaults to None.
            filter: The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/wrappers.

        """
        if page:
            return self._get_page("wrappers", page, per_page, filter)
        return self._get_entry_list("wrappers", limit, per_page, filter)

    def get_wrapper(self, wrapper_id):
        """
        Get wrapper.

        Args:
            wrapper_id: The unique id of the wrapper.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/wrappers.

        """
        return self.api.get_request(f"wrappers/{wrapper_id}")

    # Unique ID Lists
    def get_unique_id_lists(self, limit=None, per_page=25, page=None, filter=None):
        """
        Get unique id lists.

        Args:
            limit: The maximum number of unique ID lists to return. When None, returns all unique ID lists.
                Defaults to None.
            per_page: The number of unique ID lists to return per page. Defaults to 25.
            page: The specific page of unique ID lists to return. Defaults to None.
            filter: The filter criteria to apply when retrieving unique ID lists. Defaults to None.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/unique_id_lists.

        """
        if page:
            return self._get_page("unique_id_lists", page, per_page, filter)
        return self._get_entry_list("unique_id_lists", limit, per_page, filter)

    def get_unique_id_list(self, unique_id_list_id):
        """
        Get unique id list.

        Args:
            unique_id_list_id: The unique id of the unique ID list.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/unique_id_lists.

        """
        return self.api.get_request(f"unique_id_lists/{unique_id_list_id}")

    def create_unique_id_list(self, list_name, unique_ids):
        """
        Create unique id list.

        Args:
            list_name: The name for the new list.
            unique_ids: An array of unique IDs to upload.

        Returns:
            Documentation Reference: https://actionnetwork.org/docs/v2/unique_id_lists.

        """
        return self.api.post_request(
            "unique_id_lists",
            data=json.dumps({"name": list_name, "unique_ids": unique_ids}),
        )
