import json
import logging
import re
import warnings

from parsons import Table
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector

logger = logging.getLogger(__name__)

API_URL = "https://actionnetwork.org/api/v2"


class ActionNetwork(object):
    """
    `Args:`
        api_token: str
            The OSDI API token
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
            if limit:
                if count >= limit:
                    return Table(return_list[0:limit])

    # Advocacy Campaigns
    def get_advocacy_campaigns(self, limit=None, per_page=25, page=None, filter=None):
        """
        `Args:`
            limit:
               The number of entries to return. When None, returns all entries.
           per_page:
               The number of entries per page to return. 25 maximum.
           page:
               Which page of results to return
           filter:
               The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
               When None, no filter is applied.

        `Returns:`
            A  JSON with all of the advocacy_campaigns (letters) entries
        """
        if page:
            return self._get_page("advocacy_campaigns", page, per_page, filter)
        return self._get_entry_list("advocacy_campaigns", limit, per_page, filter)

    def get_advocacy_campaign(self, advocacy_campaign_id):
        """
        `Args:`
            advocacy_campaign_id:
               The unique id of the advocacy_campaign
        `Returns:`
            A  JSON with advocacy_campaign entry
        """
        return self.api.get_request(f"advocacy_campaigns/{advocacy_campaign_id}")

    # Attendances
    def get_person_attendances(
        self, person_id, limit=None, per_page=25, page=None, filter=None
    ):
        """
        `Args:`
            person_id:
               The unique id of the person
            limit:
               The number of entries to return. When None, returns all entries.
           per_page:
               The number of entries per page to return. 25 maximum.
           page:
               Which page of results to return
           filter:
               The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
               When None, no filter is applied.
        `Returns:`
            A  JSON with all the attendances entries
        """
        if page:
            return self._get_page(
                f"people/{person_id}/attendances", page, per_page, filter
            )
        return self._get_entry_list(
            f"people/{person_id}/attendances", limit, per_page, filter
        )

    def get_event_attendances(
        self, event_id, limit=None, per_page=25, page=None, filter=None
    ):
        """
        `Args:`
            event_id: the unique id of the event
            limit:
               The number of entries to return. When None, returns all entries.
           per_page
               The number of entries per page to return. 25 maximum.
           page
               Which page of results to return
           filter
               The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
               When None, no filter is applied.
        `Returns:`
            A  JSON with the attendances entries related to the event
        """
        if page:
            return self._get_page(
                f"events/{event_id}/attendances", page, per_page, filter
            )
        return self._get_entry_list(
            f"events/{event_id}/attendances", limit, per_page, filter
        )

    def get_event_attendance(self, event_id, attendance_id):
        """
        `Args:`
            event_id:
               The unique id of the event
            attendance_id:
               The unique id of the attendance
        `Returns:`
            A  JSON with the attendance entry
        """
        return self.api.get_request(f"events/{event_id}/attendances/{attendance_id}")

    def get_person_attendance(self, person_id, attendance_id):
        """
        `Args:`
            person_id:
               The unique id of the person
            attendance_id:
               The unique id of the attendance
        `Returns:`
            A  JSON with the attendance entry
        """
        return self.api.get_request(f"people/{person_id}/attendances/{attendance_id}")

    # Campaigns
    def get_campaigns(self, limit=None, per_page=25, page=None, filter=None):
        """
        `Args:`
            limit:
               The number of entries to return. When None, returns all entries.
           per_page:
               The number of entries per page to return. 25 maximum.
           page:
               Which page of results to return
           filter:
               The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
               When None, no filter is applied.
        `Returns:`
            A  JSON with all of the campaigns entries
        """
        if page:
            return self._get_page("campaigns", page, per_page, filter)
        return self._get_entry_list("campaigns", limit, per_page, filter)

    def get_campaign(self, campaign_id):
        """
        `Args:`
            campaign_id:
               The unique id of the campaign
        `Returns:`
            A  JSON with the campaign entry
        """
        return self.api.get_request(f"campaigns/{campaign_id}")

    # Custom Fields
    def get_custom_fields(self):
        """
        `Args:`
            None
        `Returns:`
            A  JSON with the custom_fields associated with your API key.
        """
        return self.api.get_request("metadata/custom_fields")

    # Donations
    def get_donation(self, donation_id):
        """
        `Args:`
            donation_id: The unique id of the donation
        `Returns:`
            A  JSON with donation data
        """
        return self.api.get_request(url=f"donations/{donation_id}")

    def get_donations(self, limit=None, per_page=25, page=None, filter=None):
        """
        `Args:`
             limit:
                The number of entries to return. When None, returns all entries.
            per_page:
                The number of entries per page to return. 25 maximum.
            page:
                Which page of results to return
            filter:
                The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.
        `Returns:`
            A  JSON with all the donations entries
        """
        if page:
            return self._get_page("donations", page, per_page, filter)
        return self._get_entry_list("donations", limit, per_page, filter)

    def get_fundraising_page_donations(
        self, fundraising_page_id, limit=None, per_page=25, page=None, filter=None
    ):
        """
        `Args:`
             fundraising_page_id: The id of the fundraiser
             limit:
                The number of entries to return. When None, returns all entries.
            per_page
                The number of entries per page to return. 25 maximum.
            page
                Which page of results to return
            filter
                The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.

        `Returns:`
            A  JSON with fundraising_page entry
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

    def get_person_donations(
        self, person_id, limit=None, per_page=25, page=None, filter=None
    ):
        """
        `Args:`
             person_id: The id of the person
             limit:
                The number of entries to return. When None, returns all entries.
            per_page
                The number of entries per page to return. 25 maximum.
            page
                Which page of results to return
            filter
                The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.

        `Returns:`
            A  JSON with all donations related to person
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

    # Embeds
    def get_embeds(self, action_type, action_id):
        """
        `Args:`
            action_type:
              The action type (petition, events, etc.)
            action_id:
              The unique id of the action
        `Returns:`
            A  JSON with the embeds (for you to be able to embed action outside of ActionNetwork).
        """
        return self.api.get_request(f"{action_type}/{action_id}/embed")

    # Event Campaigns
    def get_event_campaigns(self, limit=None, per_page=25, page=None, filter=None):
        """
        `Args:`
            limit:
               The number of entries to return. When None, returns all entries.
           per_page:
               The number of entries per page to return. 25 maximum.
           page:
               Which page of results to return
           filter:
               The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
               When None, no filter is applied.
        `Returns:`
            A  JSON with all the event_campaigns entries
        """
        if page:
            return self._get_page("event_campaigns", page, per_page, filter)
        return self._get_entry_list("event_campaigns", limit, per_page, filter)

    def get_event_campaign(self, event_campaign_id):
        """
        `Args:`
            event_campaign_id:
               The unique id of the event_campaign
        `Returns:`
            A  JSON with event_campaign entry
        """
        return self.api.get_request(f"event_campaigns/{event_campaign_id}")

    # Events
    def get_events(self, limit=None, per_page=25, page=None, filter=None):
        """
         `Args:`
        limit:
            The number of entries to return. When None, returns all entries.
        per_page
            The number of entries per page to return. 25 maximum.
        page
            Which page of results to return
        filter
            The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
            When None, no filter is applied.
         `Returns:`
             A  JSON with all the events entries
        """
        if page:
            return self._get_page("events", page, per_page, filter)
        return self._get_entry_list("events", limit, per_page, filter)

    def get_event(self, event_id):
        """
        `Args:`
            event_id: the unique id of the event
        `Returns:`
            A  JSON with event entry
        """
        return self.api.get_request(f"events/{event_id}")

    def get_event_campaign_events(
        self, event_campaign_id, limit=None, per_page=25, page=None, filter=None
    ):
        """
        `Args:`
            event_campaign_id:
               The unique id of the event_campaign
            limit:
                The number of entries to return. When None, returns all entries.
            per_page
                The number of entries per page to return. 25 maximum.
            page
                Which page of results to return
            filter
                The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.
        `Returns:`
            A  JSON with all the eventes related to the event_campaign entry
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

        `Args:`
            title: str
                The public title of the event
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

        `Returns:`
            Dict of Action Network Event data.
        """

        data = {"title": title}

        if start_date:
            start_date = str(start_date)
            data["start_date"] = start_date

        if isinstance(location, dict):
            data["location"] = location

        event_dict = self.api.post_request(
            url=f"{self.api_url}/events", data=json.dumps(data)
        )

        an_event_id = event_dict["_links"]["self"]["href"].split("/")[-1]
        event_dict["event_id"] = an_event_id

        return event_dict

    # Forms
    def get_forms(self, limit=None, per_page=25, page=None, filter=None):
        """
        `Args:`
             limit:
                The number of entries to return. When None, returns all entries.
            per_page
                The number of entries per page to return. 25 maximum.
            page
                Which page of results to return
            filter
                The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.
        `Returns:`
            A  JSON with all the forms entries
        """
        if page:
            return self._get_page("forms", page, per_page, filter)
        return self._get_entry_list("forms", limit, per_page, filter)

    def get_form(self, form_id):
        """
        `Args:`
            form_id:
               The unique id of the form
        `Returns:`
            A  JSON with form entry
        """
        return self.api.get_request(f"forms/{form_id}")

    # Fundraising Pages
    def get_fundraising_page(self, fundraising_page_id):
        """
        `Args:`
            fundraising_page_id: The id of the fundraiser
        `Returns:`
            A  JSON with fundraising_page entry
        """
        return self.api.get_request(url=f"fundraising_pages/{fundraising_page_id}")

    def get_fundraising_pages(self, limit=None, per_page=25, page=None, filter=None):
        """
        `Args:`
             limit:
                The number of entries to return. When None, returns all entries.
            per_page
                The number of entries per page to return. 25 maximum.
            page
                Which page of results to return
            filter
                The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.

        `Returns:`
            A  JSON with all the fundraising_pages entries
        """
        if page:
            return self._get_page("fundraising_pages", page, per_page, filter)
        return self._get_entry_list(
            "fundraising_pages",
            limit,
        )

    # Items
    def get_items(self, list_id, limit=None, per_page=25, page=None, filter=None):
        """
        `Args:`
            list_id:
                The unique id of the list
            limit:
               The number of entries to return. When None, returns all entries.
           per_page:
               The number of entries per page to return. 25 maximum.
           page:
               Which page of results to return
           filter:
               The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
               When None, no filter is applied.


        `Returns:`
            A  JSON with all the list item entries
        """
        if page:
            return self._get_page(f"lists/{list_id}/items", page, per_page, filter)
        return self._get_entry_list(f"lists/{list_id}/items", limit, per_page, filter)

    def get_item(self, list_id, item_id):
        """
        `Args:`
           list_id:
              The unique id of the list
            item_id:
              The unique id of the item
        `Returns:`
            A  JSON with the item entry
        """
        return self.api.get_request(f"lists/{list_id}/items/{item_id}")

    # Lists
    def get_lists(self, limit=None, per_page=25, page=None, filter=None):
        """
        `Args:`
            limit:
               The number of entries to return. When None, returns all entries.
           per_page:
               The number of entries per page to return. 25 maximum.
           page:
               Which page of results to return
           filter:
               The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
               When None, no filter is applied.


        `Returns:`
            A  JSON with all the list entries
        """
        if page:
            return self._get_page("lists", page, per_page, filter)
        return self._get_entry_list("lists", limit, per_page, filter)

    def get_list(self, list_id):
        """
        `Args:`
           list_id:
              The unique id of the list
        `Returns:`
            A  JSON with the list entry
        """
        return self.api.get_request(f"lists/{list_id}")

    # Messages
    def get_messages(self, limit=None, per_page=25, page=None, filter=None):
        """
        `Args:`
            limit:
               The number of entries to return. When None, returns all entries.
           per_page:
               The number of entries per page to return. 25 maximum.
           page:
               Which page of results to return
           filter:
               The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
               When None, no filter is applied.


        `Returns:`
            A  JSON with all the messages related entries
        """
        if page:
            return self._get_page("messages", page, per_page, filter)
        return self._get_entry_list("messages", limit, per_page, filter)

    def get_message(self, message_id):
        """
        `Args:`
            message_id:
               The unique id of the message
        `Returns:`
            A  JSON with the signature entry.
        """
        return self.api.get_request(f"messages/{message_id}")

    # Metadata
    def get_metadata(self):
        """
        `Args:`
           None
        `Returns:`
            A  JSON with the metadata entry
        """
        return self.api.get_request("metadata")

    # Outreaches
    def get_advocacy_campaign_outreaches(
        self, advocacy_campaign_id, limit=None, per_page=25, page=None, filter=None
    ):
        """
        `Args:`
            advocacy_campaign_id:
               The unique id of the advocacy_campaign
            limit:
               The number of entries to return. When None, returns all entries.
           per_page:
               The number of entries per page to return. 25 maximum.
           page:
               Which page of results to return
           filter:
               The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
               When None, no filter is applied.

        `Returns:`
           A  JSON with all the outreaches entries related to the advocacy_campaign_id
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

    def get_person_outreaches(
        self, person_id, limit=None, per_page=25, page=None, filter=None
    ):
        """
        `Args:`
            person_id:
               The unique id of the person
            limit:
               The number of entries to return. When None, returns all entries.
           per_page:
               The number of entries per page to return. 25 maximum.
           page:
               Which page of results to return
           filter:
               The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
               When None, no filter is applied.

        `Returns:`
            A  JSON with all the outreaches entries related to our group
        """
        if page:
            return self._get_page(
                f"people/{person_id}/outreaches", page, per_page, filter
            )
        return self._get_entry_list(
            f"people/{person_id}/outreaches", limit, per_page, filter
        )

    def get_advocacy_campaign_outreach(self, advocacy_campaign_id, outreach_id):
        """
        `Args:`
            advocacy_campaign_id:
               The unique id of the campaign
            outreach_id:
               The unique id of the outreach
        `Returns:`
            A  JSON with the outreach entry
        """
        return self.api.get_request(
            f"advocacy_campaigns/{advocacy_campaign_id}/outreaches/{outreach_id}"
        )

    def get_person_outreach(self, person_id, outreach_id):
        """
        `Args:`
            person_id:
               The unique id of the campaign
            outreach_id:
               The unique id of the outreach
        `Returns:`
            A  JSON with the outreach entry
        """
        return self.api.get_request(f"people/{person_id}/outreaches/{outreach_id}")

    # People
    def get_people(self, limit=None, per_page=25, page=None, filter=None):
        """
        `Args:`
            limit:
                The number of entries to return. When None, returns all entries.
            per_page
                The number of entries per page to return. 25 maximum.
            page
                Which page of results to return
            filter
                The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.
        `Returns:`
            A list of JSONs of people stored in Action Network.
        """
        if page:
            return self._get_page("people", page, per_page, filter=filter)
        return self._get_entry_list("people", limit, per_page, filter=filter)

    def get_person(self, person_id):
        """
        `Args:`
            person_id:
                Id of the person.
        `Returns:`
            A  JSON of the entry. If the entry doesn't exist, Action Network returns
            ``{'error': 'Couldn't find person with id = <id>'}``.
        """
        return self.api.get_request(url=f"people/{person_id}")

    def upsert_person(
        self,
        email_address=None,
        given_name=None,
        family_name=None,
        tags=None,
        languages_spoken=None,
        postal_addresses=None,
        mobile_number=None,
        mobile_status="subscribed",
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

        `Args:`
            email_address:
                Either email_address or mobile_number are required. Can be any of the following
                    - a string with the person's email
                    - a list of strings with a person's emails
                    - a dictionary with the following fields
                        - email_address (REQUIRED)
                        - primary (OPTIONAL): Boolean indicating the user's primary email address
                        - status (OPTIONAL): can taken on any of these values
                            - "subscribed"
                            - "unsubscribed"
                            - "bouncing"
                            - "previous bounce"
                            - "spam complaint"
                            - "previous spam complaint"
            given_name:
                The person's given name
            family_name:
                The person's family name
            tags:
                Optional field. A list of strings of pre-existing tags to be applied to the person.
            languages_spoken:
                Optional field. A list of strings of the languages spoken by the person
            postal_addresses:
                Optional field. A list of dictionaries.
                For details, see Action Network's documentation:
                https://actionnetwork.org/docs/v2/person_signup_helper
            mobile_number:
                Either email_address or mobile_number are required. Can be any of the following
                    - a string with the person's cell phone number
                    - an integer with the person's cell phone number
                    - a list of strings with the person's cell phone numbers
                    - a list of integers with the person's cell phone numbers
                    - a dictionary with the following fields
                        - number (REQUIRED)
                        - primary (OPTIONAL): Boolean indicating the user's primary mobile number
                        - status (OPTIONAL): can taken on any of these values
                            - "subscribed"
                            - "unsubscribed"
            mobile_status:
                'subscribed' or 'unsubscribed'
            background_request: bool
                If set `true`, utilize ActionNetwork's "background processing". This will return
                an immediate success, with an empty JSON body, and send your request to the
                background queue for eventual processing.
                https://actionnetwork.org/docs/v2/#background-processing
            **kwargs:
                Any additional fields to store about the person. Action Network allows
                any custom field.
        Adds a person to Action Network
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

        mobile_numbers_field = None
        if isinstance(mobile_number, str):
            mobile_numbers_field = [
                {"number": re.sub("[^0-9]", "", mobile_number), "status": mobile_status}
            ]
        elif isinstance(mobile_number, int):
            mobile_numbers_field = [
                {"number": str(mobile_number), "status": mobile_status}
            ]
        elif isinstance(mobile_number, list):
            if len(mobile_number) > 1:
                raise ("Action Network allows only 1 phone number per activist")
            if isinstance(mobile_number[0], list):
                mobile_numbers_field = [
                    {"number": re.sub("[^0-9]", "", cell), "status": mobile_status}
                    for cell in mobile_number
                ]
                mobile_numbers_field[0]["primary"] = True
            if isinstance(mobile_number[0], int):
                mobile_numbers_field = [
                    {"number": cell, "status": mobile_status} for cell in mobile_number
                ]
                mobile_numbers_field[0]["primary"] = True
            if isinstance(mobile_number[0], dict):
                mobile_numbers_field = mobile_number

        if not email_addresses_field and not mobile_numbers_field:
            raise (
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
            entry_id.split(":")[1]
            for entry_id in identifiers
            if "action_network:" in entry_id
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
        Creates a person in the database. WARNING: this endpoint has been deprecated in favor of
        upsert_person.
        """
        logger.warning(
            "Method 'add_person' has been deprecated. Please use 'upsert_person'."
        )
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

        `Args:`
            entry_id:
                The person's Action Network id
            background_processing: bool
                If set `true`, utilize ActionNetwork's "background processing". This will return
                an immediate success, with an empty JSON body, and send your request to the
                background queue for eventual processing.
                https://actionnetwork.org/docs/v2/#background-processing
            **kwargs:
                Fields to be updated. The possible fields are
                    email_address:
                        Can be any of the following
                            - a string with the person's email
                            - a dictionary with the following fields
                                - email_address (REQUIRED)
                                    - primary (OPTIONAL): Boolean indicating the user's
                                    primary email address
                                - status (OPTIONAL): can taken on any of these values
                                    - "subscribed"
                                    - "unsubscribed"
                                    - "bouncing"
                                    - "previous bounce"
                                    - "spam complaint"
                                    - "previous spam complaint"
                    given_name:
                        The person's given name
                    family_name:
                        The person's family name
                    languages_spoken:
                        Optional field. A list of strings of the languages spoken by the person
                    postal_addresses:
                        Optional field. A list of dictionaries.
                        For details, see Action Network's documentation:
                        https://actionnetwork.org/docs/v2/people#put
                    custom_fields:
                        A dictionary of any other fields to store about the person.
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
        `Args:`
            limit:
               The number of entries to return. When None, returns all entries.
           per_page:
               The number of entries per page to return. 25 maximum.
           page:
               Which page of results to return
           filter:
               The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
               When None, no filter is applied.
        `Returns:`
            A  JSON with all of the petitions entries
        """
        if page:
            return self._get_page("petitions", page, per_page, filter)
        return self._get_entry_list("petitions", limit, per_page, filter)

    def get_petition(self, petition_id):
        """
        `Args:`
            petition_id:
               The unique id of the petition
        `Returns:`
            A  JSON with the petition entry
        """
        return self.api.get_request(f"petitions/{petition_id}")

    # Queries
    def get_queries(self, limit=None, per_page=25, page=None, filter=None):
        """
        `Args:`
            limit:
               The number of entries to return. When None, returns all entries.
           per_page:
               The number of entries per page to return. 25 maximum.
           page:
               Which page of results to return
           filter:
               The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
               When None, no filter is applied.


        `Returns:`
            A  JSON with all the query entries
        """
        if page:
            return self._get_page("queries", page, per_page, filter)
        return self._get_entry_list("queries", limit, per_page, filter)

    def get_query(self, query_id):
        """
        `Args:`
           query_id:
              The unique id of the query
        `Returns:`
            A  JSON with the query entry
        """
        return self.api.get_request(f"queries/{query_id}")

    # Signatures
    def get_petition_signatures(
        self, petition_id, limit=None, per_page=25, page=None, filter=None
    ):
        """
        `Args:`
            petition_id:
               The unique id of the petition
            limit:
               The number of entries to return. When None, returns all entries.
           per_page:
               The number of entries per page to return. 25 maximum.
           page:
               Which page of results to return
           filter:
               The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
               When None, no filter is applied.
        `Returns:`
            A  JSON with all the signatures related to the petition entry
        """
        if page:
            return self._get_page(
                f"petitions/{petition_id}/signatures", page, per_page, filter
            )
        return self._get_entry_list(
            f"petitions/{petition_id}/signatures", limit, per_page, filter
        )

    def get_person_signatures(
        self, person_id, limit=None, per_page=25, page=None, filter=None
    ):
        """
        `Args:`
            person_id:
               The unique id of the person
            limit:
               The number of entries to return. When None, returns all entries.
           per_page:
               The number of entries per page to return. 25 maximum.
           page:
               Which page of results to return
           filter:
               The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
               When None, no filter is applied.


        `Returns:`
            A  JSON with all the signatures related to the petition entry
        """
        if page:
            return self._get_page(
                f"people/{person_id}/signatures", page, per_page, filter
            )
        return self._get_entry_list(
            f"people/{person_id}/signatures", limit, per_page, filter
        )

    def get_petition_signature(self, petition_id, signature_id):
        """
        `Args:`
            petition_id:
               The unique id of the petition
            signature_id:
               The unique id of the signature
        `Returns:`
            A  JSON with the signature entry
        """
        return self.api.get_request(
            f"petitions/{petition_id}/signatures/{signature_id}"
        )

    def get_person_signature(self, person_id, signature_id):
        """
        `Args:`
            person_id:
               The unique id of the person
            signature_id:
               The unique id of the signature
        `Returns:`
            A  JSON with the signature entry
        """
        return self.api.get_request(f"people/{person_id}/signatures/{signature_id}")

    # Submissions
    def get_form_submissions(
        self, form_id, limit=None, per_page=25, page=None, filter=None
    ):
        """
        `Args:`
            form_id:
               The unique id of the form
            limit:
               The number of entries to return. When None, returns all entries.
           per_page:
               The number of entries per page to return. 25 maximum.
           page:
               Which page of results to return
           filter:
               The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
               When None, no filter is applied.

        `Returns:`
            A  JSON with all the submissions entries related to the form
        """
        if page:
            return self._get_page(
                f"forms/{form_id}/submissions", page, per_page, filter
            )
        return self._get_entry_list(
            f"forms/{form_id}/submissions", limit, per_page, filter
        )

    def get_person_submissions(
        self, person_id, limit=None, per_page=25, page=None, filter=None
    ):
        """
        `Args:`
            person_id:
               The unique id of the person
            limit:
               The number of entries to return. When None, returns all entries.
           per_page:
               The number of entries per page to return. 25 maximum.
           page:
               Which page of results to return
           filter:
               The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
               When None, no filter is applied.
        `Returns:`
            A  JSON with all the submissions entries related with our group
        """
        if page:
            return self._get_page(
                f"people/{person_id}/submissions", page, per_page, filter
            )
        return self._get_entry_list(
            f"people/{person_id}/submissions", limit, per_page, filter
        )

    def get_form_submission(self, form_id, submission_id):
        """
        `Args:`
            form_id:
               The unique id of the form
            submission_id:
               The unique id of the submission
        `Returns:`
            A  JSON with the submission entry
        """
        return self.api.get_request(f"forms/{form_id}/submissions/{submission_id}")

    def get_person_submission(self, person_id, submission_id):
        """
        `Args:`
            person_id:
               The unique id of the submission
            submission_id:
               The unique id of the submission
        `Returns:`
            A  JSON with the submission entry
        """
        return self.api.get_request(f"people/{person_id}/submissions/{submission_id}")

    # Tags
    def get_tags(self, limit=None, per_page=None):
        """
        `Args:`
            limit:
                The number of entries to return. When None, returns all entries.
            per_page:
                This is a deprecated argument.
        `Returns:`
            A list of JSONs of tags in Action Network.
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
        `Args:`
            tag_id:
                Id of the tag.
        `Returns:`
            A  JSON of the entry. If the entry doesn't exist, Action Network returns
            "{'error': 'Couldn't find tag with id = <id>'}"
        """
        return self.api.get_request(url=f"tags/{tag_id}")

    def add_tag(self, name):
        """
        `Args:`
            name:
                The tag's name. This is the ONLY editable field
        Adds a tag to Action Network. Once created, tags CANNOT be edited or deleted.
        """
        data = {"name": name}
        response = self.api.post_request(
            url=f"{self.api_url}/tags", data=json.dumps(data)
        )
        identifiers = response["identifiers"]
        person_id = [
            entry_id.split(":")[1]
            for entry_id in identifiers
            if "action_network:" in entry_id
        ][0]
        logger.info(f"Tag {person_id} successfully added to tags.")
        return response

    # Taggings
    def get_taggings(self, tag_id, limit=None, per_page=25, page=None, filter=None):
        """
        `Args:`
            tag_id:
                The unique id of the tag
            limit:
               The number of entries to return. When None, returns all entries.
           per_page:
               The number of entries per page to return. 25 maximum.
           page:
               Which page of results to return
           filter:
               The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
               When None, no filter is applied.


        `Returns:`
            A  JSON with all the tagging entries associated with the tag_id
        """
        if page:
            return self._get_page(f"tags/{tag_id}/taggings", page, per_page, filter)
        return self._get_entry_list(f"tags/{tag_id}/taggings", limit, per_page, filter)

    def get_tagging(self, tag_id, tagging_id):
        """
        `Args:`
           tag_id:
              The unique id of the tag
           tagging_id:
              The unique id of the tagging
        `Returns:`
            A  JSON with the tagging entry
        """
        return self.api.get_request(f"tags/{tag_id}/taggings/{tagging_id}")

    # Wrappers
    def get_wrappers(self, limit=None, per_page=25, page=None, filter=None):
        """
        `Args:`
            limit:
               The number of entries to return. When None, returns all entries.
           per_page:
               The number of entries per page to return. 25 maximum.
           page:
               Which page of results to return
           filter:
               The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
               When None, no filter is applied.


        `Returns:`
            A  JSON with all the wrapper entries
        """
        if page:
            return self._get_page("wrappers", page, per_page, filter)
        return self._get_entry_list("wrappers", limit, per_page, filter)

    def get_wrapper(self, wrapper_id):
        """
        `Args:`
           wrapper_id:
              The unique id of the wrapper
           tagging_id:
              The unique id of the tagging
        `Returns:`
            A  JSON with the wrapper entry
        """
        return self.api.get_request(f"wrappers/{wrapper_id}")
