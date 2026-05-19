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
    Args:
        api_token: str
            OSDI API token

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
        Args:
            limit:
               Number of entries to return. When None, returns all entries.
            per_page:
               Number of entries per page to return. 25 maximum.
            page:
               Which page of results to return
            filter:
               OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
               When None, no filter is applied.

        Returns:
            A JSON with all of the advocacy_campaigns (letters) entries

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/advocacy_campaigns>`__

        """
        if page:
            return self._get_page("advocacy_campaigns", page, per_page, filter)
        return self._get_entry_list("advocacy_campaigns", limit, per_page, filter)

    def get_advocacy_campaign(self, advocacy_campaign_id):
        """
        Args:
            advocacy_campaign_id:
               Unique ID of the advocacy_campaign

        Returns:
            A JSON with advocacy_campaign entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/advocacy_campaigns>`__

        """
        return self.api.get_request(f"advocacy_campaigns/{advocacy_campaign_id}")

    # Attendances
    def get_person_attendances(self, person_id, limit=None, per_page=25, page=None, filter=None):
        """
        Args:
            person_id:
                Unique ID of the person
            limit:
                Number of entries to return. When None, returns all entries.
            per_page:
                Number of entries per page to return. 25 maximum.
            page:
                Which page of results to return
            filter:
                OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.

        Returns:
            A JSON with all the attendances entries

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/attendances>`__

        """
        if page:
            return self._get_page(f"people/{person_id}/attendances", page, per_page, filter)
        return self._get_entry_list(f"people/{person_id}/attendances", limit, per_page, filter)

    def get_event_attendances(self, event_id, limit=None, per_page=25, page=None, filter=None):
        """
        Args:
            event_id:
                Unique ID of the event
            limit:
                Number of entries to return. When None, returns all entries.
            per_page:
                Number of entries per page to return. 25 maximum.
            page:
                Which page of results to return
            filter:
                OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.

        Returns:
            A JSON with the attendances entries related to the event

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/attendances>`__

        """
        if page:
            return self._get_page(f"events/{event_id}/attendances", page, per_page, filter)
        return self._get_entry_list(f"events/{event_id}/attendances", limit, per_page, filter)

    def get_event_attendance(self, event_id, attendance_id):
        """
        Args:
            event_id:
                Unique ID of the event
            attendance_id:
                Unique ID of the attendance

        Returns:
            A JSON with the attendance entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/attendances>`__

        """
        return self.api.get_request(f"events/{event_id}/attendances/{attendance_id}")

    def get_person_attendance(self, person_id, attendance_id):
        """
        Args:
            person_id:
                Unique ID of the person
            attendance_id:
                Unique ID of the attendance

        Returns:
            A JSON with the attendance entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/attendances>`__

        """
        return self.api.get_request(f"people/{person_id}/attendances/{attendance_id}")

    def create_attendance(self, event_id, payload):
        """
        Args:
            event_id:
                Unique ID of the event
            payload:
                Payload for creating the event attendance

                .. code-block:: python

                    {
                        "_links" : {
                            "osdi:person" : { "href" : "https://actionnetwork.org/api/v2/people/id" }
                        }
                    }

        Returns:
            A JSON response after creating the event attendance

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/attendances>`__

        """
        return self.api.post_request(f"events/{event_id}/attendances", payload)

    def update_attendance(self, event_id, attendance_id, payload):
        """
        Args:
            event_id:
                Unique ID of the event
            attendance_id:
                Unique ID of the attendance
            payload:
                Payload for updating the event attendance

                .. code-block:: python

                    {
                        "identifiers": [
                            "other-system:230125a"
                        ]
                    }

        Returns:
            A JSON response after updating the event attendance

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/attendances>`__

        """
        return self.api.put_request(f"events/{event_id}/attendances/{attendance_id}", payload)

    # Campaigns
    def get_campaigns(self, limit=None, per_page=25, page=None, filter=None):
        """
        Args:
            limit:
                Number of entries to return. When None, returns all entries.
            per_page:
                Number of entries per page to return. 25 maximum.
            page:
                Page of results to return
            filter:
                OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.

        Returns:
            A JSON with all of the campaigns entries

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/campaigns>`__

        """
        if page:
            return self._get_page("campaigns", page, per_page, filter)
        return self._get_entry_list("campaigns", limit, per_page, filter)

    def get_campaign(self, campaign_id):
        """
        Args:
            campaign_id:
               Unique ID of the campaign

        Returns:
            A JSON with the campaign entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/campaigns>`__

        """
        return self.api.get_request(f"campaigns/{campaign_id}")

    # Custom Fields
    def get_custom_fields(self):
        """
        Args:
            None

        Returns:
            A JSON with the custom_fields associated with your API key.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/custom_fields>`__

        """
        return self.api.get_request("metadata/custom_fields")

    # Donations
    def get_donation(self, donation_id):
        """
        Args:
            donation_id: Unique ID of the donation

        Returns:
            A JSON with donation data

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/donations>`__

        """
        return self.api.get_request(url=f"donations/{donation_id}")

    def get_donations(self, limit=None, per_page=25, page=None, filter=None):
        """
        Args:
            limit:
                Number of entries to return. When None, returns all entries.
            per_page:
                Number of entries per page to return. 25 maximum.
            page:
                Which page of results to return
            filter:
                OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.

        Returns:
            A JSON with all the donations entries

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/donations>`__

        """
        if page:
            return self._get_page("donations", page, per_page, filter)
        return self._get_entry_list("donations", limit, per_page, filter)

    def get_fundraising_page_donations(
        self, fundraising_page_id, limit=None, per_page=25, page=None, filter=None
    ):
        """
        Args:
            fundraising_page_id:
                The ID of the fundraiser
            limit:
                Number of entries to return. When None, returns all entries.
            per_page:
                Number of entries per page to return. 25 maximum.
            page:
                Which page of results to return
            filter:
                OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.

        Returns:
            A JSON with fundraising_page entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/donations>`__

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
        Args:
            person_id:
                The ID of the person
            limit:
                Number of entries to return. When None, returns all entries.
            per_page:
                Number of entries per page to return. 25 maximum.
            page:
                Which page of results to return
            filter:
                OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.

        Returns:
            A JSON with all donations related to person

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/donations>`__

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
        Args:
            fundraising_page_id:
                The ID of the fundraising page
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
            A JSON response confirming the creation of the donation

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/donations>`__

        """
        return self.api.post_request(
            f"fundraising_pages/{fundraising_page_id}/donations", donation_payload
        )

    # Embeds
    def get_embeds(self, action_type, action_id):
        """
        Args:
            action_type:
              Action type (petition, events, etc.)
            action_id:
              Unique ID of the action

        Returns:
            A JSON with the embeds (for you to be able to embed action outside of ActionNetwork).

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/embeds>`__

        """
        return self.api.get_request(f"{action_type}/{action_id}/embed")

    # Event Campaigns
    def get_event_campaigns(self, limit=None, per_page=25, page=None, filter=None):
        """
        Args:
            limit:
                Number of entries to return. When None, returns all entries.
            per_page:
                Number of entries per page to return. 25 maximum.
            page:
                Which page of results to return
            filter:
                OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.

        Returns:
            A JSON with all the event_campaigns entries

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/event_campaigns>`__

        """
        if page:
            return self._get_page("event_campaigns", page, per_page, filter)
        return self._get_entry_list("event_campaigns", limit, per_page, filter)

    def get_event_campaign(self, event_campaign_id):
        """
        Args:
            event_campaign_id:
                Unique ID of the event_campaign

        Returns:
            A JSON with event_campaign entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/event_campaigns>`__

        """
        return self.api.get_request(f"event_campaigns/{event_campaign_id}")

    def create_event_campaign(self, payload):
        """
        Args:
            payload:
                Payload containing event campaign details

                .. code-block::python

                    {
                        "title": "My Canvassing Event",
                        "origin_system": "CanvassingEvents.com"
                    }

        Returns:
            A JSON response confirming the creation of the event campaign

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/event_campaigns>`__

        """
        return self.api.post_request("event_campaigns", payload)

    def create_event_in_event_campaign(self, event_campaign_id, payload):
        """
        Args:
            event_campaign_id:
                Unique ID of the event_campaign
            payload:
                Payload containing event details

                .. code-block::python

                    {
                        "title": "My Free Event",
                        "origin_system": "FreeEvents.com"
                    }

        Returns:
            A JSON response confirming the creation of the event in the event campaign

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/event_campaigns>`__

        """
        return self.api.post_request(f"event_campaigns/{event_campaign_id}/events", payload)

    def update_event_campaign(self, event_campaign_id, payload):
        """
        Args:
            event_campaign_id:
                Unique ID of the event_campaign
            payload:
                Payload containing event campaign details

                .. code-block::python

                    {
                        "description": "This is my new event campaign description"
                    }

        Returns:
            A JSON response confirming Update of the event campaign

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/event_campaigns>`__

        """
        return self.api.put_request(f"event_campaigns/{event_campaign_id}", payload)

    # Events
    def get_events(self, limit=None, per_page=25, page=None, filter=None):
        """
        Args:
            limit:
                Number of entries to return. When None, returns all entries.
            per_page:
                Number of entries per page to return. 25 maximum.
            page:
                Which page of results to return
            filter:
                OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.

        Returns:
             A JSON with all the events entries

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/events>`__

        """
        if page:
            return self._get_page("events", page, per_page, filter)
        return self._get_entry_list("events", limit, per_page, filter)

    def get_event(self, event_id):
        """
        Args:
            event_id:
                Unique ID of the event

        Returns:
            A JSON with event entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/events>`__

        """
        return self.api.get_request(f"events/{event_id}")

    def get_event_campaign_events(
        self, event_campaign_id, limit=None, per_page=25, page=None, filter=None
    ):
        """
        Args:
            event_campaign_id:
               Unique ID of the event_campaign
            limit:
                Number of entries to return. When None, returns all entries.
            per_page:
                Number of entries per page to return. 25 maximum.
            page:
                Which page of results to return
            filter:
                OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.

        Returns:
            A JSON with all the eventes related to the event_campaign entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/events>`__

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
        Create an event in Action Network

        Args:
            title: str
                Public title of the event
            start_date: str OR datetime
                OPTIONAL: The starting date & time. If a string, use format "YYYY-MM-DD HH:MM:SS"
                (hint: the default format you get when you use `str()` on a datetime)
            location: dict
                OPTIONAL: A dict of location details. Can include any combination of the types of
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
            Dict of Action Network Event data.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/events>`__

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
        Update an event in Action Network

        Args:
            event_id: str
                Unique ID of the event
            payload: dict
                Payload containing event data (see `<https://actionnetwork.org/docs/v2/events>`__)

                .. code-block::python

                    {
                        "title": "My Free Event With A New Name",
                        "description": "This is my free event description"
                    }

        Returns:
            A JSON response confirming Update of the event

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/events>`__

        """
        return self.api.put_request(f"events/{event_id}", payload)

    # Forms
    def get_forms(self, limit=None, per_page=25, page=None, filter=None):
        """
        Args:
            limit:
                Number of entries to return. When None, returns all entries.
            per_page:
                Number of entries per page to return. 25 maximum.
            page:
                Which page of results to return
            filter:
                OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.

        Returns:
            A JSON with all the forms entries

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/forms>`__

        """
        if page:
            return self._get_page("forms", page, per_page, filter)
        return self._get_entry_list("forms", limit, per_page, filter)

    def get_form(self, form_id):
        """
        Args:
            form_id:
               Unique ID of the form

        Returns:
            A JSON with form entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/forms>`__

        """
        return self.api.get_request(f"forms/{form_id}")

    def create_form(self, payload):
        """
        Create a form in Action Network

        Args:
            payload: dict
                Payload containing form details

                .. code-block::python

                    {
                        "title": "My Free Form",
                        "origin_system": "FreeForms.com"
                    }

        Returns:
            A JSON response confirming the creation of the form

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/forms>`__

        """
        return self.api.post_request("forms", payload)

    def update_form(self, form_id, payload):
        """
        Update a form in Action Network

        Args:
            form_id:
                Unique ID of the form
            payload: dict
                Payload containing form data (see `<https://actionnetwork.org/docs/v2/forms>`__)

                .. code-block::python

                    {
                        "title": "My Free Form",
                        "origin_system": "FreeForms.com"
                    }

        Returns:
            A JSON response confirming Update of the form

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/forms>`__

        """
        return self.api.put_request(f"forms/{form_id}", payload)

    # Fundraising Pages
    def get_fundraising_page(self, fundraising_page_id):
        """
        Args:
            fundraising_page_id:
                The ID of the fundraiser

        Returns:
            A JSON with fundraising_page entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/fundraising_pages>`__

        """
        return self.api.get_request(url=f"fundraising_pages/{fundraising_page_id}")

    def get_fundraising_pages(self, limit=None, per_page=25, page=None, filter=None):
        """
        Args:
            limit:
                Number of entries to return. When None, returns all entries.
            per_page:
                Number of entries per page to return. 25 maximum.
            page:
                Which page of results to return
            filter:
                OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.

        Returns:
            A JSON with all the fundraising_pages entries

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/fundraising_pages>`__

        """
        if page:
            return self._get_page("fundraising_pages", page, per_page, filter)
        return self._get_entry_list(
            "fundraising_pages",
            limit,
        )

    def create_fundraising_page(self, payload):
        """
        Create a fundraising page in Action Network

        Args:
            payload: dict
                Payload containing fundraising page details

                .. code-block::python

                    {
                        "title": "My Free Fundraiser",
                        "origin_system": "FreeFundraisers.com"
                    }

        Returns:
            A JSON response confirming the creation of the fundraising page

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/fundraising_pages>`__

        """
        return self.api.post_request("fundraising_pages", payload)

    def update_fundraising_page(self, fundraising_page_id, payload):
        """
        Update a fundraising page in Action Network

        Args:
            fundraising_page_id:
                The ID of the fundraiser
            payload: dict
                Payload containing updated fundraising page details

                .. code-block::python

                    {
                        "title": "My Free Fundraiser",
                        "origin_system": "FreeFundraisers.com"
                    }

        Returns:
            A JSON response confirming Update of the fundraising page

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/fundraising_pages>`__

        """
        return self.api.put_request(f"fundraising_pages/{fundraising_page_id}", payload)

    # Items
    def get_items(self, list_id, limit=None, per_page=25, page=None, filter=None):
        """
        Args:
            list_id:
                Unique ID of the list
            limit:
                Number of entries to return. When None, returns all entries.
            per_page:
                Number of entries per page to return. 25 maximum.
            page:
                Which page of results to return
            filter:
                OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.

        Returns:
            A JSON with all the list item entries

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/items>`__

        """
        if page:
            return self._get_page(f"lists/{list_id}/items", page, per_page, filter)
        return self._get_entry_list(f"lists/{list_id}/items", limit, per_page, filter)

    def get_item(self, list_id, item_id):
        """
        Args:
            list_id:
                Unique ID of the list
            item_id:
                Unique ID of the item

        Returns:
            A JSON with the item entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/items>`__

        """
        return self.api.get_request(f"lists/{list_id}/items/{item_id}")

    # Lists
    def get_lists(self, limit=None, per_page=25, page=None, filter=None):
        """
        Args:
            limit:
                Number of entries to return. When None, returns all entries.
            per_page:
                Number of entries per page to return. 25 maximum.
            page:
                Which page of results to return
            filter:
                OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.

        Returns:
            A JSON with all the list entries

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/lists>`__

        """
        if page:
            return self._get_page("lists", page, per_page, filter)
        return self._get_entry_list("lists", limit, per_page, filter)

    def get_list(self, list_id):
        """
        Args:
           list_id:
              Unique ID of the list

        Returns:
            A JSON with the list entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/lists>`__

        """
        return self.api.get_request(f"lists/{list_id}")

    # Messages
    def get_messages(
        self, limit=None, per_page=25, page=None, filter=None, unpack_statistics=False
    ):
        """
        Args:
            limit:
                Number of entries to return. When None, returns all entries.
            per_page:
                Number of entries per page to return. 25 maximum.
            page:
                Which page of results to return
            filter:
                OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.
            unpack_statistics:
                Whether to unpack the statistics dictionary into the table. Default to False.

        Returns:
            A Parsons Table with all the messages related entries

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/messages>`__

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
        Args:
            message_id:
               Unique ID of the message

        Returns:
            A JSON with the signature entry.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/messages>`__

        """
        return self.api.get_request(f"messages/{message_id}")

    def create_message(self, payload):
        """
        Create a message in Action Network

        Args:
            payload: dict
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
            A JSON response confirming the creation of the message

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/messages>`__

        """
        return self.api.post_request("messages", json=payload)

    def update_message(self, message_id, payload):
        """
        Update a message in Action Network

        Args:
            message_id:
               Unique ID of the message
            payload: dict
                Payload containing message details to be updated

                .. code-block::python

                    {
                        "name": "Stop doing the bad thing email send 1",
                        "subject": "Please! Stop doing the bad thing"
                    }

        Returns:
            A JSON response confirming Update of the message

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/messages>`__

        """
        return self.api.put_request(f"messages/{message_id}", json=payload)

    def schedule_message(self, message_id, scheduled_start_date):
        """
        Schedule a message in Action Network

        Args:
            message_id:
               Unique ID of the message
            scheduled_start_date:
                UTC timestamp to schedule the message at in ISO8601 format.
                e.g. "2015-03-14T12:00:00Z"

        Returns:
            A JSON response confirming the scheduling

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/schedule_helper>`__

        """
        return self.api.post_request(
            f"messages/{message_id}/schedule/",
            {"scheduled_start_date": scheduled_start_date},
        )

    def send_message(self, message_id):
        """
        Send a message in Action Network

        Args:
            message_id:
               Unique ID of the message

        Returns:
            A JSON response confirming the message was sent

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/send_helper>`__

        """
        return self.api.post_request(f"messages/{message_id}/send/", {})

    # Metadata
    def get_metadata(self):
        """
        Args:
           None

        Returns:
            A JSON with the metadata entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/metadata>`__

        """
        return self.api.get_request("metadata")

    # Outreaches
    def get_advocacy_campaign_outreaches(
        self, advocacy_campaign_id, limit=None, per_page=25, page=None, filter=None
    ):
        """
        Args:
            advocacy_campaign_id:
                Unique ID of the advocacy_campaign
            limit:
                Number of entries to return. When None, returns all entries.
            per_page:
                Number of entries per page to return. 25 maximum.
            page:
                Which page of results to return
            filter:
                OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.

        Returns:
           A JSON with all the outreaches entries related to the advocacy_campaign_id

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/outreaches>`__

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
        Args:
            person_id:
                Unique ID of the person
            limit:
                Number of entries to return. When None, returns all entries.
            per_page:
                Number of entries per page to return. 25 maximum.
            page:
                Which page of results to return
            filter:
                OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.

        Returns:
            A JSON with all the outreaches entries related to our group

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/outreaches>`__

        """
        if page:
            return self._get_page(f"people/{person_id}/outreaches", page, per_page, filter)
        return self._get_entry_list(f"people/{person_id}/outreaches", limit, per_page, filter)

    def get_advocacy_campaign_outreach(self, advocacy_campaign_id, outreach_id):
        """
        Args:
            advocacy_campaign_id:
                Unique ID of the campaign
            outreach_id:
                Unique ID of the outreach

        Returns:
            A JSON with the outreach entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/outreaches>`__

        """
        return self.api.get_request(
            f"advocacy_campaigns/{advocacy_campaign_id}/outreaches/{outreach_id}"
        )

    def get_person_outreach(self, person_id, outreach_id):
        """
        Args:
            person_id:
                Unique ID of the campaign
            outreach_id:
                Unique ID of the outreach

        Returns:
            A JSON with the outreach entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/outreaches>`__

        """
        return self.api.get_request(f"people/{person_id}/outreaches/{outreach_id}")

    def create_outreach(self, advocacy_campaign_id, payload):
        """
        Create an outreach in Action Network

        Args:
            advocacy_campaign_id:
                Unique ID of the campaign
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
            A JSON response confirming the creation of the outreach

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/outreaches>`__

        """
        return self.api.post_request(
            f"advocacy_campaigns/{advocacy_campaign_id}/outreaches", payload
        )

    def update_outreach(self, advocacy_campaign_id, outreach_id, payload):
        """
        Update an outreach in Action Network

        Args:
            advocacy_campaign_id:
                Unique ID of the campaign
            outreach_id:
                Unique ID of the outreach
            payload:
                Payload containing outreach details to be updated

                .. code-block::python

                    {
                        "subject": "Please vote no!"
                    }

        Returns:
            A JSON response confirming Update of the outreach

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/outreaches>`__

        """
        return self.api.put_request(
            f"advocacy_campaigns/{advocacy_campaign_id}/outreaches/{outreach_id}",
            payload,
        )

    # People
    def get_people(self, limit=None, per_page=25, page=None, filter=None):
        """
        Args:
            limit:
                Number of entries to return. When None, returns all entries.
            per_page:
                Number of entries per page to return. 25 maximum.
            page:
                Which page of results to return
            filter:
                OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.

        Returns:
            A list of JSONs of people stored in Action Network.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/people>`__

        """
        if page:
            return self._get_page("people", page, per_page, filter=filter)
        return self._get_entry_list("people", limit, per_page, filter=filter)

    def get_person(self, person_id):
        """
        Args:
            person_id:
                ID of the person.

        Returns:
            A  JSON of the entry. If the entry doesn't exist, Action Network returns
            ``{'error': 'Couldn't find person with id = <id>'}``.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/people>`__

        """
        return self.api.get_request(url=f"people/{person_id}")

    def upsert_person(
        self,
        email_address: str
        | list[str]
        | list[dict[Literal["address", "primary", "status"], str | bool]]
        | None = None,
        given_name=None,
        family_name=None,
        tags=None,
        languages_spoken=None,
        postal_addresses=None,
        mobile_number: str
        | int
        | list[str | int]
        | list[dict[Literal["address", "primary", "status"], str | bool]]
        | None = None,
        mobile_status: Literal["subscribed", "unsubscribed"] | None = None,
        background_processing=False,
        **kwargs,
    ):
        """
        Creates or updates a person record. In order to update an existing record instead of
        creating a new one, you must supply an email or mobile number which matches a record
        in the database.

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

                        - "subscribed"
                        - "unsubscribed"
                        - "bouncing"
                        - "previous bounce"
                        - "spam complaint"
                        - "previous spam complaint"

            given_name:
                Person's given name
            family_name:
                Person's family name
            tags:
                Optional field. A list of strings of pre-existing tags to be applied to the person.
            languages_spoken:
                Optional field. A list of strings of the languages spoken by the person
            postal_addresses:
                Optional field. A list of dictionaries.
                For details, see Action Network's documentation:
                `<https://actionnetwork.org/docs/v2/person_signup_helper>`__
            mobile_number:
                Either email_address or mobile_number are required. Can be any of the following

                - a string with the person's cell phone number
                - an integer with the person's cell phone number
                - a list of strings with the person's cell phone numbers
                - a list of integers with the person's cell phone numbers
                - a dictionary with the following fields

                    - number (REQUIRED)
                    - primary (OPTIONAL): Boolean indicating User's primary mobile number
                    - status (OPTIONAL): can taken on any of these values

                        - "subscribed"
                        - "unsubscribed"

            mobile_status:
                None, 'subscribed' or 'unsubscribed'. If included, will update the SMS opt-in
                status of the phone in ActionNetwork. If not included, won't update the status.
                None by default, causes no updates to mobile number status. New numbers are set
                to "unsubscribed" by default.
            background_processing: bool
                If set `true`, utilize ActionNetwork's "background processing". This will return
                an immediate success, with an empty JSON body, and send your request to the
                background queue for eventual processing.
                `<https://actionnetwork.org/docs/v2/#background-processing>`__
            `**kwargs`:
                Any additional fields to store about the person. Action Network allows
                any custom field.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/people>`__

        """
        email_addresses_field: list[dict] | None = None
        if isinstance(email_address, str):
            email_addresses_field = [{"address": email_address}]
        elif isinstance(email_address, list):
            if isinstance(email_address[0], str):
                email_addresses_field = [{"address": email} for email in email_address]
                email_addresses_field[0]["primary"] = True
            elif isinstance(email_address[0], dict):
                email_addresses_field = email_address
        else:
            raise ValueError(
                f"Unexpected type for email_address. Got {type(email_address)}, "
                "expected str or list."
            )

        mobile_numbers_field: list[dict] | None = None
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
        email_address: str
        | list[str]
        | list[dict[Literal["address", "primary", "status"], str | bool]]
        | None = None,
        given_name=None,
        family_name=None,
        tags=None,
        languages_spoken=None,
        postal_addresses=None,
        mobile_number: str
        | int
        | list[str | int]
        | list[dict[Literal["address", "primary", "status"], str | bool]]
        | None = None,
        mobile_status: Literal["subscribed", "unsubscribed"] | None = "subscribed",
        **kwargs,
    ):
        """
        Creates a person in the database. WARNING: this endpoint has been deprecated in favor of
        upsert_person.
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
        Updates a person's data in Action Network, given their Action Network ID. Note that you
        can't alter a person's tags with this method. Instead, use upsert_person.

        Args:
            entry_id:
                Person's Action Network id
            background_processing: bool
                If set `true`, utilize ActionNetwork's "background processing". This will return
                an immediate success, with an empty JSON body, and send your request to the
                background queue for eventual processing.
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

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/people>`__

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
        Args:
            limit:
                Number of entries to return. When None, returns all entries.
            per_page:
                Number of entries per page to return. 25 maximum.
            page:
                Which page of results to return
            filter:
                OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.

        Returns:
            A JSON with all of the petitions entries

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/petitions>`__

        """
        if page:
            return self._get_page("petitions", page, per_page, filter)
        return self._get_entry_list("petitions", limit, per_page, filter)

    def get_petition(self, petition_id):
        """
        Args:
            petition_id:
               Unique ID of the petition

        Returns:
            A JSON with the petition entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/petitions>`__

        """
        return self.api.get_request(f"petitions/{petition_id}")

    def create_petition(
        self, title, description, petition_text, target, background_processing=False
    ):
        """
        Args:
            title:
                Title of the petition
            description:
                Description of the petition
            petition_text:
                Text of the petition
            target:
                Target of the petition
            background_processing:
                Whether to process the request in the background

        Returns:
            A JSON with the response from the API

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/petitions>`__

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
        Args:
            petition_id:
                Unique ID of the petition to be updated
            title:
                Updated title of the petition
            description:
                Updated description of the petition
            petition_text:
                Updated text of the petition
            target:
                Updated target of the petition
            background_processing:
                Whether to process the request in the background

        Returns:
            A JSON with the response from the API

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/petitions>`__

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
        Args:
            limit:
                Number of entries to return. When None, returns all entries.
            per_page:
                Number of entries per page to return. 25 maximum.
            page:
                Which page of results to return
            filter:
                OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.

        Returns:
            A JSON with all the query entries

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/queries>`__

        """
        if page:
            return self._get_page("queries", page, per_page, filter)
        return self._get_entry_list("queries", limit, per_page, filter)

    def get_query(self, query_id):
        """
        Args:
            query_id:
                Unique ID of the query

        Returns:
            A JSON with the query entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/queries>`__

        """
        return self.api.get_request(f"queries/{query_id}")

    # Signatures
    def get_petition_signatures(self, petition_id, limit=None, per_page=25, page=None, filter=None):
        """
        Args:
            petition_id:
                Unique ID of the petition
            limit:
                Number of entries to return. When None, returns all entries.
            per_page:
                Number of entries per page to return. 25 maximum.
            page:
                Which page of results to return
            filter:
                OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.

        Returns:
            A JSON with all the signatures related to the petition entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/signatures>`__

        """
        if page:
            return self._get_page(f"petitions/{petition_id}/signatures", page, per_page, filter)
        return self._get_entry_list(f"petitions/{petition_id}/signatures", limit, per_page, filter)

    def get_person_signatures(self, person_id, limit=None, per_page=25, page=None, filter=None):
        """
        Args:
            person_id:
                Unique ID of the person
            limit:
                Number of entries to return. When None, returns all entries.
            per_page:
                Number of entries per page to return. 25 maximum.
            page:
                Which page of results to return
            filter:
                OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.

        Returns:
            A JSON with all the signatures related to the petition entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/signatures>`__

        """
        if page:
            return self._get_page(f"people/{person_id}/signatures", page, per_page, filter)
        return self._get_entry_list(f"people/{person_id}/signatures", limit, per_page, filter)

    def get_petition_signature(self, petition_id, signature_id):
        """
        Args:
            petition_id:
                Unique ID of the petition
            signature_id:
                Unique ID of the signature

        Returns:
            A JSON with the signature entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/signatures>`__

        """
        return self.api.get_request(f"petitions/{petition_id}/signatures/{signature_id}")

    def get_person_signature(self, person_id, signature_id):
        """
        Args:
            person_id:
               Unique ID of the person
            signature_id:
               Unique ID of the signature

        Returns:
            A JSON with the signature entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/signatures>`__

        """
        return self.api.get_request(f"people/{person_id}/signatures/{signature_id}")

    def create_signature(self, petition_id, data):
        """
        Args:
            petition_id:
               Unique ID of the petition
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
            A JSON with the created signature entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/signatures>`__

        """
        return self.api.post_request(f"petitions/{petition_id}/signatures", data)

    def update_signature(self, petition_id, signature_id, data):
        """
        Args:
            petition_id:
                Unique ID of the petition
            signature_id:
                Unique ID of the signature
            data:
                Signature payload to update

                .. code-block:: python

                    {
                        "comments": "Some new comments"
                    }

        Returns:
            A JSON with Updated signature entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/signatures>`__

        """
        return self.api.put_request(f"petitions/{petition_id}/signatures/{signature_id}", data)

    # Submissions
    def get_form_submissions(self, form_id, limit=None, per_page=25, page=None, filter=None):
        """
        Args:
            form_id:
                Unique ID of the form
            limit:
                Number of entries to return. When None, returns all entries.
            per_page:
                Number of entries per page to return. 25 maximum.
            page:
                Which page of results to return
            filter:
                OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.

        Returns:
            A JSON with all the submissions entries related to the form

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/submissions>`__

        """
        if page:
            return self._get_page(f"forms/{form_id}/submissions", page, per_page, filter)
        return self._get_entry_list(f"forms/{form_id}/submissions", limit, per_page, filter)

    def get_person_submissions(self, person_id, limit=None, per_page=25, page=None, filter=None):
        """
        Args:
            person_id:
                Unique ID of the person
            limit:
                Number of entries to return. When None, returns all entries.
            per_page:
                Number of entries per page to return. 25 maximum.
            page:
                Which page of results to return
            filter:
                OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.

        Returns:
            A JSON with all the submissions entries related with our group

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/submissions>`__

        """
        if page:
            return self._get_page(f"people/{person_id}/submissions", page, per_page, filter)
        return self._get_entry_list(f"people/{person_id}/submissions", limit, per_page, filter)

    def get_form_submission(self, form_id, submission_id):
        """
        Args:
            form_id:
                Unique ID of the form
            submission_id:
                Unique ID of the submission

        Returns:
            A JSON with the submission entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/submissions>`__

        """
        return self.api.get_request(f"forms/{form_id}/submissions/{submission_id}")

    def get_person_submission(self, person_id, submission_id):
        """
        Args:
            person_id:
                Unique ID of the submission
            submission_id:
                Unique ID of the submission

        Returns:
            A JSON with the submission entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/submissions>`__

        """
        return self.api.get_request(f"people/{person_id}/submissions/{submission_id}")

    def create_submission(self, form_id, person_id):
        """
        Args:
            form_id:
                Unique ID of the form
            person_id:
                Unique ID of the person

        Returns:
            A JSON response indicating the success or failure of the submission creation

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/submissions>`__

        """
        payload = {
            "_links": {
                "osdi:person": {"href": f"https://actionnetwork.org/api/v2/people/{person_id}"}
            }
        }
        return self.api.post_request(f"forms/{form_id}/submissions", data=json.dumps(payload))

    def update_submission(self, form_id, submission_id, data):
        """
        Args:
            form_id:
                Unique ID of the form
            submission_id:
                Unique ID of the submission
            data:
                Payload for updating the submission

                .. code-block:: python

                    {
                        "_links" : {
                            "osdi:person" : { "href" : "https://actionnetwork.org/api/v2/people/id" }
                        }
                    }

        Returns:
            A JSON with Updated submission entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/submissions>`__

        """
        return self.api.put_request(
            f"forms/{form_id}/submissions/{submission_id}", data=json.dumps(data)
        )

    # Surveys
    def get_surveys(self, limit=None, per_page=25, page=None, filter=None):
        """
        Survey resources are sometimes presented as collections of surveys.
        For example, calling the surveys endpoint will return a collection
        of all the surveys associated with your API key.

        Args:
            limit:
                Number of entries to return. When None, returns all entries.
            per_page:
                Number of entries per page to return. 25 maximum.

        """
        if page:
            return self._get_page("surveys", page, per_page, filter)
        return self._get_entry_list("surveys", limit, per_page, filter)

    def get_survey(self, survey_id):
        """
        Args:
            survey_id:
                Unique ID of the survey

        Returns:
            A JSON with the survey entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/surveys>`__

        """
        return self.api.get_request(f"surveys/{survey_id}")

    def create_survey(self, data):
        """
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
            A JSON with the created survey entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/surveys>`__

        """
        return self.api.post_request("surveys", data=json.dumps(data))

    def update_survey(self, survey_id, data):
        """
        Args:
            survey_id:
                Unique ID of the survey
            data:
                Payload for updating the survey

                .. code-block:: python

                    {
                        "title": "My Free Survey",
                        "origin_system": "FreeSurveys.com",
                    }

        Returns:
            A JSON with Updated survey entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/surveys>`__

        """
        return self.api.post_request(f"surveys/{survey_id}", data=json.dumps(data))

    # Tags
    def get_tags(self, limit=None, per_page=None):
        """
        Args:
            limit:
                Number of entries to return. When None, returns all entries.
            per_page:
                This is a deprecated argument.

        Returns:
            A list of JSONs of tags in Action Network.

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

    def get_tag(self, tag_id):
        """
        Args:
            tag_id:
                ID of the tag.

        Returns:
            A  JSON of the entry. If the entry doesn't exist, Action Network returns
            "{'error': 'Couldn't find tag with id = <id>'}"

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/tags>`__

        """
        return self.api.get_request(url=f"tags/{tag_id}")

    def add_tag(self, name):
        """
        Adds a tag to Action Network. Once created, tags CANNOT be edited or deleted.

        Args:
            name:
                Tag's name. This is the ONLY editable field

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/tags>`__

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
        Args:
            tag_id:
                Unique ID of the tag
            limit:
                Number of entries to return. When None, returns all entries.
            per_page:
                Number of entries per page to return. 25 maximum.
            page:
                Which page of results to return
            filter:
                OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.

        Returns:
            A JSON with all the tagging entries associated with the tag_id

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/taggings>`__

        """
        if page:
            return self._get_page(f"tags/{tag_id}/taggings", page, per_page, filter)
        return self._get_entry_list(f"tags/{tag_id}/taggings", limit, per_page, filter)

    def get_tagging(self, tag_id, tagging_id):
        """
        Args:
           tag_id:
              Unique ID of the tag
           tagging_id:
              Unique ID of the tagging

        Returns:
            A JSON with the tagging entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/taggings>`__

        """
        return self.api.get_request(f"tags/{tag_id}/taggings/{tagging_id}")

    def create_tagging(self, tag_id, payload, background_processing=False):
        """
        Args:
            tag_id:
                Unique ID of the tag
            payload:
                Payload for creating the tagging

                .. code-block:: python

                    {
                        "_links" : {
                            "osdi:person" : { "href" : "https://actionnetwork.org/api/v2/people/id" }
                        }
                    }

            background_processing: bool
                If set `true`, utilize ActionNetwork's "background processing". This will return
                an immediate success, with an empty JSON body, and send your request to the
                background queue for eventual processing.
                `<https://actionnetwork.org/docs/v2/#background-processing>`__

        Returns:
            A JSON response after creating the tagging

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/taggings>`__

        """
        url = f"tags/{tag_id}/taggings"
        if background_processing:
            url = f"{url}?background_processing=true"
        return self.api.post_request(url, data=json.dumps(payload))

    def delete_tagging(self, tag_id, tagging_id, background_processing=False):
        """
        Args:
            tag_id:
                Unique ID of the tag
            tagging_id:
                Unique ID of the tagging to be deleted
            background_processing: bool
                If set `true`, utilize ActionNetwork's "background processing". This will return
                an immediate success, with an empty JSON body, and send your request to the
                background queue for eventual processing.
                `<https://actionnetwork.org/docs/v2/#background-processing>`__

        Returns:
            A JSON response after deleting the tagging

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/taggings>`__

        """
        url = f"tags/{tag_id}/taggings/{tagging_id}"
        if background_processing:
            url = f"{url}?background_processing=true"
        return self.api.delete_request(url)

    # Wrappers
    def get_wrappers(self, limit=None, per_page=25, page=None, filter=None):
        """
        Args:
            limit:
                Number of entries to return. When None, returns all entries.
            per_page:
                Number of entries per page to return. 25 maximum.
            page:
                Which page of results to return
            filter:
                OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.

        Returns:
            A JSON with all the wrapper entries

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/wrappers>`__

        """
        if page:
            return self._get_page("wrappers", page, per_page, filter)
        return self._get_entry_list("wrappers", limit, per_page, filter)

    def get_wrapper(self, wrapper_id):
        """
        Args:
           wrapper_id:
              Unique ID of the wrapper
           tagging_id:
              Unique ID of the tagging

        Returns:
            A JSON with the wrapper entry

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/wrappers>`__

        """
        return self.api.get_request(f"wrappers/{wrapper_id}")

    # Unique ID Lists
    def get_unique_id_lists(self, limit=None, per_page=25, page=None, filter=None):
        """
        Args:
            limit:
                The maximum number of unique ID lists to return.
                When None, returns all unique ID lists.
            per_page:
                Number of unique ID lists to return per page. Default is 25.
            page:
                The specific page of unique ID lists to return.
            filter:
                The filter criteria to apply when retrieving unique ID lists.

        Returns:
            A JSON response with Unique ID lists.

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/unique_id_lists>`__

        """
        if page:
            return self._get_page("unique_id_lists", page, per_page, filter)
        return self._get_entry_list("unique_id_lists", limit, per_page, filter)

    def get_unique_id_list(self, unique_id_list_id):
        """
        Args:
            unique_id_list_id:
                Unique ID of Unique ID list

        Returns:
            A JSON response with Unique ID list details

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/unique_id_lists>`__

        """
        return self.api.get_request(f"unique_id_lists/{unique_id_list_id}")

    def create_unique_id_list(self, list_name, unique_ids):
        """
        Args:
            list_name:
                Name for the new list
            unique_ids:
                An array of unique IDs to upload

        Returns:
            A JSON response with Unique ID list details

        Documentation Reference:
            `<https://actionnetwork.org/docs/v2/unique_id_lists>`__

        """
        return self.api.post_request(
            "unique_id_lists",
            data=json.dumps({"name": list_name, "unique_ids": unique_ids}),
        )
