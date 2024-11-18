import json
import logging
import requests
import time
import math

from parsons.etl.table import Table
from parsons.utilities import check_env

logger = logging.getLogger(__name__)


class ActionKit(object):
    """
    Instantiate the ActionKit class

    `Args:`
        domain: str
            The ActionKit domain (e.g. ``myorg.actionkit.com``) Not required if
            ``ACTION_KIT_DOMAIN`` env variable set.
        username: str
            The authorized ActionKit username. Not required if ``ACTION_KIT_USERNAME`` env
            variable set.
        password: str
            The authorized ActionKit user password. Not required if ``ACTION_KIT_PASSWORD``
            env variable set.
    """

    _default_headers = {
        "content-type": "application/json",
        "accepts": "application/json",
    }

    def __init__(self, domain=None, username=None, password=None):
        self.domain = check_env.check("ACTION_KIT_DOMAIN", domain)
        self.username = check_env.check("ACTION_KIT_USERNAME", username)
        self.password = check_env.check("ACTION_KIT_PASSWORD", password)
        self.conn = self._conn()

    def _conn(self, default_headers=_default_headers):
        client = requests.Session()
        client.auth = (self.username, self.password)
        client.headers.update(default_headers)
        return client

    def _base_endpoint(self, endpoint, entity_id=None):
        # Create the base endpoint URL

        url = f"https://{self.domain}/rest/v1/{endpoint}/"

        if entity_id:
            return url + f"{entity_id}/"
        return url

    def _base_get(self, endpoint, entity_id=None, exception_message=None, params=None):
        # Make a general get request to ActionKit

        resp = self.conn.get(self._base_endpoint(endpoint, entity_id), params=params)
        if exception_message and resp.status_code == 404:
            raise Exception(self.parse_error(resp, exception_message))
        return resp.json()

    def _base_post(self, endpoint, exception_message, return_full_json=False, **kwargs):
        # Make a general post request to ActionKit

        resp = self.conn.post(self._base_endpoint(endpoint), data=json.dumps(kwargs))

        if resp.status_code != 201:
            raise Exception(self.parse_error(resp, exception_message))

        # Some of the methods should just return pointer to location of created
        # object.
        if "headers" in resp.__dict__ and not return_full_json:
            return resp.__dict__["headers"]["Location"]

        # Not all responses return a json
        try:
            return resp.json()

        except ValueError:
            return None

    def parse_error(self, resp, exception_message):
        # AK provides some pretty robust/helpful error reporting. We should surface them with
        # our exceptions.

        if "errors" in resp.json().keys():
            if isinstance(resp.json()["errors"], list):
                exception_message += "\n" + ",".join(resp.json()["errors"])
            else:
                for k, v in resp.json()["errors"].items():
                    exception_message += str("\n" + k + ": " + ",".join(v))

        return exception_message

    def get_user(self, user_id):
        """
        Get a user.

        `Args:`
            user_id: int
                The user id of the record to get.
        `Returns`:
            User json object
        """

        return self._base_get(
            endpoint="user", entity_id=user_id, exception_message="User not found"
        )

    def get_user_fields(self):
        """
        Get list of valid user fields that can be passed with the
        :meth:`ActionKit.create_user` method.

        `Returns`:
            List of user fields
        """

        resp = self._base_get(endpoint="user/schema")

        return list(resp["fields"].keys())

    def create_user(self, email, **kwargs):
        """
        Create a user.

        `Args:`
            email: str
                Email for the user
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
        `Returns:`
            User json object
        """

        return self._base_post(
            endpoint="user",
            exception_message="Could not create user",
            email=email,
            **kwargs,
        )

    def add_phone(self, user_id, phone_type, phone):
        """
        Add a phone number to a user.

        `Args:`
            user_id: string
                The id of the user.
            phone_type: string
                The type of the phone (e.g., "Home").
            phone: string
                The phone number.
        `Returns:`
            Phone json object
        """
        return self._base_post(
            endpoint="phone",
            exception_message="Could not create phone",
            user=f"/rest/v1/user/{user_id}/",
            phone_type=phone_type,
            phone=phone,
        )

    def delete_actionfield(self, actionfield_id):
        """
        Delete an actionfield.

        `Args:`
            actionfield_id: int
                The id of the actionfield to delete
        `Returns:`
            ``None``
        """

        resp = self.conn.delete(self._base_endpoint("actionfield", actionfield_id))
        logger.info(f"{resp.status_code}: {actionfield_id}")

    def update_user(self, user_id, **kwargs):
        """
        Update a user.

        `Args:`
            user_id: int
                The user id of the person to update
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
        `Returns:`
            ``HTTP response from the patch request``
        """

        resp = self.conn.patch(self._base_endpoint("user", user_id), data=json.dumps(kwargs))
        logger.info(f"{resp.status_code}: {user_id}")

        return resp

    def update_phone(self, phone_id, **kwargs):
        """
        Update a phone record.

        `Args:`
            phone_id: int
                The phone id of the phone to update
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                at the /rest/v1/phone/schema/ path on any ActionKit instance.
        `Returns:`
            ``HTTP response from the patch request``
        """

        resp = self.conn.patch(self._base_endpoint("phone", phone_id), data=json.dumps(kwargs))
        logger.info(f"{resp.status_code}: {phone_id}")

        return resp

    def get_event(self, event_id):
        """Get an event.

        `Args:`
            event_id: int
                The id for the event.
        `Returns:`
            dict
                Event json object.

        """
        return self._base_get(f"event/{event_id}")

    def get_events(self, limit=None, **kwargs):
        """Get multiple events.

        `Args:`
            limit: int
                The number of events to return. If omitted, all events are returned.
            **kwargs:
                Optional arguments to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.

                Additionally, expressions to filter the data can also be provided. For addition
                info, visit `Django's docs on field lookups <https://docs.djangoproject.com/\
                en/3.1/topics/db/queries/#field-lookups>`_.

                .. code-block:: python

                    ak.get_events(name__contains="FirstName")
        `Returns:`
            Parsons.Table
                The events data.
        """
        return self.paginated_get("event", limit=limit, **kwargs)

    def update_event(self, event_id, **kwargs):
        """
        Update an event.

        `Args:`
            event_id: int
                The event id of the event to update
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
        `Returns:`
            ``None``
        """

        resp = self.conn.patch(self._base_endpoint("event", event_id), data=json.dumps(kwargs))
        logger.info(f"{resp.status_code}: {event_id}")

    def create_event_field(self, event_id, name, value):
        """
        Create an event field (custom field on an event). Note that if an event
        field with this name already exists, this will add a second record.

        `Args:`
            event_id: int
                The id for the event.
            name: string
                The name of the event field.
            value: string
                The value of the event field.
        `Returns:`
            Event field json object
        """
        return self._base_post(
            endpoint="eventfield",
            exception_message="Could not create event field",
            event=f"/rest/v1/event/{event_id}/",
            name=name,
            value=value,
        )

    def update_event_field(self, eventfield_id, name, value):
        """
        Update an event field.

        `Args:`
            eventfield_id: int
                The id of the event field to update.
            name: string
                The name of the event field.
            value: string
                The value of the event field.
        `Returns:`
            ``None``
        """
        resp = self.conn.patch(
            self._base_endpoint("eventfield", eventfield_id),
            data=json.dumps(
                {
                    "name": name,
                    "value": value,
                }
            ),
        )
        logger.info(f"{resp.status_code}: {eventfield_id}")

    def get_blackholed_email(self, email):
        """
        Get a blackholed email. A blackholed email is an email that has been prevented from
        receiving bulk and transactional emails from ActionKit. `Documentation <https://\
        docs.actionkit.com/docs/manual/guide/mailings_tools.html#blackhole>`_.

        `Args:`
            email: str
                Blackholed email of the record to get.
        `Returns`:
            Parsons.Table
                The blackholed email data.
        """

        return self.paginated_get("blackholedemail", email=email)

    def blackhole_email(self, email):
        """
        Prevent an email from receiving bulk and transactional emails from ActionKit.
        `Documentation <https://docs.actionkit.com/docs/manual/guide/\
        mailings_tools.html#blackhole>`_.

        `Args:`
            user_id: str
                Email to blackhole
        `Returns:`
            API location of new resource
        """

        return self._base_post(
            endpoint="blackholedemail",
            exception_message="Could not blackhole email",
            email=email,
        )

    def delete_user_data(self, email, **kwargs):
        """
        Delete user data.

        `Args:`
            email: str
                Email of user to delete data
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://docs.actionkit.com/docs/manual/api/\
                rest/users.html>`_.
        `Returns:`
            API location of anonymized user
        """

        return self._base_post(
            endpoint="eraser",
            exception_message="Could not delete user data",
            email=email,
            **kwargs,
        )

    def delete_user(self, user_id):
        """
        Delete a user.

        `Args:`
            user_id: int
                The user id of the person to delete
        `Returns:`
            ``None``
        """

        resp = self.conn.delete(self._base_endpoint("user", user_id))
        logger.info(f"{resp.status_code}: {user_id}")

    def get_campaign(self, campaign_id):
        """
        Get a campaign.

        `Args:`
            campaign_id: int
                The campaign id of the record.
        `Returns`:
            Campaign json object
        """

        return self._base_get(
            endpoint="campaign",
            entity_id=campaign_id,
            exception_message="Campaign not found",
        )

    def get_campaign_fields(self):
        """
        Get list of valid campaign fields that can be passed with the
        :meth:`ActionKit.create_campaign` and :meth:`ActionKit.update_campaign` methods.

        `Returns`:
            List of campaign fields
        """

        resp = self._base_get(endpoint="campaign/schema")
        return list(resp["fields"].keys())

    def create_campaign(self, name, **kwargs):
        """
        Create a campaign.

        `Args:`
            name: str
                The name of the campaign to create
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
        `Returns`:
            API location of new resource
        """

        return self._base_post(
            endpoint="campaign",
            exception_message="Could not create campaign",
            name=name,
            **kwargs,
        )

    def search_events_in_campaign(
        self,
        campaign_id,
        limit=None,
        order_by="id",
        ascdesc="asc",
        filters=None,
        exclude=None,
        **kwargs,
    ):
        """
        Get events in a campaign, with optional search filters.

        `Args:`
            campaign_id: int
                The id of the event campaign.
            limit: int
                The maximum number of objects to return.
            order_by: string
                Event attribute to order the results by. Defaults to id, which will normally
                be equivalent to ordering by created_at. See `ActionKit's docs on ordering
                <https://roboticdogs.actionkit.com/docs//manual/api/rest/overview.html#ordering>`_.
            ascdesc: string
                If "asc" (the default), returns events ordered by the attribute specified by
                the order_by parameter. If "desc", returns events in reverse order.
            filters: dictionary
                A dictionary for filtering by the attributes of the event or related object.
                Not all attributes are available for filtering, but an eventfield will work.
                For additional info, visit `Django's docs on field lookups
                <https://docs.djangoproject.com/en/3.1/topics/db/queries/#field-lookups>`_ and
                `ActionKit's docs on the search API
                <https://roboticdogs.actionkit.com/docs/manual/api/rest/examples/eventsearch.html>`_.

                .. code-block:: python

                    {
                        "title": "Example Event Title",
                        "field__name": "example_event_field_name",
                        "field__value": "Example event field value",
                    }
            exclude: dictionary
                A dictionary for excluding by the attributes of the event or related object.
                Uses the same format as the filters argument.
            **kwargs:
                A dictionary of other options for filtering. See `ActionKit's docs on the
                search API
                <https://roboticdogs.actionkit.com/docs/manual/api/rest/examples/eventsearch.html>`_.
        `Returns:`
            Parsons.Table
                The list of events.
        """
        if filters:
            for field, value in filters.items():
                kwargs[f"filter[{field}]"] = value
        if exclude:
            for field, value in exclude.items():
                kwargs[f"exclude[{field}]"] = value
        if ascdesc == "asc":
            kwargs["order_by"] = order_by
        else:
            kwargs["order_by"] = f"-{order_by}"
        return self.paginated_get(
            f"campaign/{campaign_id}/event_search",
            limit=limit,
            **kwargs,
        )

    def get_event_create_page(self, event_create_page_id):
        """
        Get a event create page.

        `Args:`
            event_create_page_id: int
                The event create page id of the record to get.
        `Returns`:
            Event create page json object
        """

        return self._base_get(
            endpoint="eventcreatepage",
            entity_id=event_create_page_id,
            exception_message="Event create page not found",
        )

    def get_event_create_page_fields(self):
        """
        Get list of event create page fields that can be passed with the
        :meth:`ActionKit.create_event_create_page`.

        `Returns`:
            List of event create page fields
        """

        resp = self._base_get(endpoint="eventcreatepage/schema")
        return list(resp["fields"].keys())

    def create_event_create_page(self, name, campaign_id, title, **kwargs):
        """
        Add an event page to a campaign.

        `Args:`
            campaign_id: int
                The campaign to assoicate page with
            name: str
                The name of the page to create
            title: str
                The title of the page to create
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
        `Returns`:
            API location of new resource
        """

        return self._base_post(
            endpoint="eventcreatepage",
            exception_message="Could not create event create page",
            campaign=f"/rest/v1/campaign/{campaign_id}/",
            name=name,
            title=title,
            **kwargs,
        )

    def get_event_create_form(self, event_create_form_id):
        """
        Get a event create form.

        `Args:`
            event_create_form_id: int
                The event create form id of the record to get.
        `Returns`:
            Event create form json object
        """

        return self._base_get(
            endpoint="eventcreateform",
            entity_id=event_create_form_id,
            exception_message="Event create page not found",
        )

    def get_event_create_form_fields(self):
        """
        Get list of valid event create form fields that can be passed with the
        :meth:`ActionKit.create_event_create_form` method.

        `Returns`:
            List of event create form fields
        """

        resp = self._base_get(endpoint="eventcreateform/schema")
        return list(resp["fields"].keys())

    def create_event_create_form(self, page_id, thank_you_text, **kwargs):
        """
        Create a event create form.

        `Args:`
            page_id: int
                The page to associate the form with
            thank_you_text: str
                Free form thank you text
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
        `Returns:`
            API location of new resource
        """

        return self._base_post(
            endpoint="eventcreateform",
            exception_message="Could not event create form",
            page=f"/rest/v1/eventcreatepage/{page_id}/",
            thank_you_text=thank_you_text,
            **kwargs,
        )

    def get_event_signup_page(self, event_signup_page_id):
        """
        Get event signup page.

        `Args:`
            event_signup_page_id: int
                The event signup page id of the record to get.
        `Returns`:
            Event signup page json object
        """

        return self._base_get(
            endpoint="eventsignuppage",
            entity_id=event_signup_page_id,
            exception_message="User page signup page not found",
        )

    def get_event_signup_page_fields(self):
        """
        Get list of valid event signup page fields that can be passed with the
        :meth:`ActionKit.create_event_signup_page` method.

        `Returns`:
            List of event signup page fields
        """

        resp = self._base_get(endpoint="eventsignuppage/schema")
        return list(resp["fields"].keys())

    def create_event_signup_page(self, name, campaign_id, title, **kwargs):
        """
        Add an event signup page to a campaign.

        `Args:`
            campaign_id: int
                The campaign to assoicate page with
            name: str
                The name of the page to create
            title: str
                The title of the page to create
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
        `Returns`:
            API location of new resource
        """

        return self._base_post(
            endpoint="eventsignuppage",
            exception_message="Could not create signup page",
            campaign=f"/rest/v1/campaign/{campaign_id}/",
            name=name,
            title=title,
            **kwargs,
        )

    def get_event_signup_form(self, event_signup_form_id):
        """
        Get a user.

        `Args:`
            event_signup_form_id: str
                The event signup form id of the record to get.
        `Returns`:
            Event signup form json object
        """

        return self._base_get(
            endpoint="eventsignupform",
            entity_id=event_signup_form_id,
            exception_message="User page signup form not found",
        )

    def get_event_signup_form_fields(self):
        """
        Get list of valid event signup form fields that can be passed with the
        :meth:`ActionKit.create_event_signup_form` method.

        `Returns`:
            List of event signup form fields
        """

        resp = self._base_get(endpoint="eventsignupform/schema")
        return list(resp["fields"].keys())

    def create_event_signup_form(self, page_id, thank_you_text, **kwargs):
        """
        Create a event signup form.

        `Args:`
            page_id: int
                The page to associate the form with
            thank_you_text: str
                Free form thank you text
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
        `Returns:`
            API location of new resource
        """

        return self._base_post(
            endpoint="eventsignupform",
            exception_message="Could not event create signup form",
            page=f"/rest/v1/page/{page_id}/",
            thank_you_text=thank_you_text,
            **kwargs,
        )

    def update_event_signup(self, event_signup_id, **kwargs):
        """
        Update an event signup.

        `Args:`
            event_signup_id: int
                The id of the event signup to update
            event_signup_dict: dict
                A dictionary of fields to update for the event signup.
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
        `Returns:`
            ``None``
        """

        resp = self.conn.patch(
            self._base_endpoint("eventsignup", event_signup_id), data=json.dumps(kwargs)
        )
        logger.info(f"{resp.status_code}: {event_signup_id}")

    def get_mailer(self, entity_id):
        """
        Get a mailer.

        `Args:`
            entity_id: int
                The entity id of the record to get.
        `Returns`:
            Mailer json object
        """

        return self._base_get(endpoint="mailer", entity_id=entity_id)

    def create_mailer(self, **kwargs):
        """
        Create a mailer.

        `Args:`
            **kwargs:
                Arguments and fields to pass to the client. A full list can be found in the
                `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/manual/api/\
                rest/mailer.html>`_.
        `Returns:`
            URI of new mailer
        """

        return self._base_post(
            endpoint="mailer", exception_message="Could not create mailer", **kwargs
        )

    def copy_mailer(self, mailer_id):
        """
        copy a mailer
        returns new copy of mailer which should be updatable.
        """
        resp = self.conn.post(self._base_endpoint("mailer", entity_id=mailer_id) + "/copy")
        return resp

    def update_mailing(self, mailer_id, **kwargs):
        """
        Update a mailing.

        `Args:`
            mailing_id: int
                The id of the mailing to update
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
        `Returns:`
            ``HTTP response from the patch request``
        """

        resp = self.conn.patch(self._base_endpoint("mailer", mailer_id), data=json.dumps(kwargs))
        logger.info(f"{resp.status_code}: {mailer_id}")
        return resp

    def rebuild_mailer(self, mailing_id):
        """
        Rebuild a mailer.

        `Args:`
            mailing_id: int
                Id of the mailer.
        `Returns:`
            URI to poll for progress
        """

        return self._base_post(
            endpoint="mailer/" + str(mailing_id) + "/rebuild",
            exception_message="Could not rebuild mailer",
        )

    def queue_mailer(self, mailing_id):
        """
        Queue a mailer.

        `Args:`
            mailing_id: int
                Id of the mailer.
        `Returns:`
            URI to poll for progress
        """

        return self._base_post(
            endpoint="mailer/" + str(mailing_id) + "/queue",
            exception_message="Could not queue mailer",
        )

    def paginated_get(self, object_type, limit=None, **kwargs):
        """Get multiple objects of a given type.

        `Args:`
            object_type: string
                The type of object to search for.
            limit: int
                The number of objects to return. If omitted, all objects are returned.
            **kwargs:
                Optional arguments to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.

                Additionally, expressions to filter the data can also be provided. For addition
                info, visit `Django's docs on field lookups <https://docs.djangoproject.com/\
                en/3.1/topics/db/queries/#field-lookups>`_.

                .. code-block:: python

                    ak.paginated_get(name__contains="FirstName")
        `Returns:`
            Parsons.Table
                The objects data.
        """
        # "The maximum number of objects returned per request is 100. Use paging
        # to get more objects."
        # (https://roboticdogs.actionkit.com/docs//manual/api/rest/overview.html#ordering)
        # get only `limit` objects if it's below 100, otherwise get 100 at a time
        kwargs["_limit"] = min(100, limit or 1_000_000_000)
        json_data = self._base_get(object_type, params=kwargs)
        data = json_data["objects"]

        next_url = json_data.get("meta", {}).get("next")
        while next_url:
            resp = self.conn.get(f"https://{self.domain}{next_url}")
            data.extend(resp.json().get("objects", []))
            next_url = resp.json().get("meta", {}).get("next")
            if limit and len(data) >= limit:
                break

        return Table(data[:limit])

    def paginated_get_custom_limit(
        self,
        object_type,
        limit=None,
        threshold_field=None,
        threshold_value=None,
        ascdesc="asc",
        **kwargs,
    ):
        """Get multiple objects of a given type, stopping based on the value of a field.

        `Args:`
            object_type: string
                The type of object to search for.
            limit: int
                The maximum number of objects to return. Even if the threshold
                value is not reached, if the limit is set, then at most this many
                objects will be returned.
            threshold_field: string
                The field used to determine when to stop.
                Must be one of the options for ordering by.
            threshold_value: string
                The value of the field to stop at.
            ascdesc: string
                If "asc" (the default), return all objects below the threshold value.
                If "desc", return all objects above the threshold value.
            **kwargs:
                You can also add expressions to filter the data beyond the limit/threshold values
                above. For additional info, visit `Django's docs on field lookups
                <https://docs.djangoproject.com/en/3.1/topics/db/queries/#field-lookups>`_.

                .. code-block:: python

                    ak.paginated_get(name__contains="FirstName")
        `Returns:`
            Parsons.Table
                The objects data.
        """
        # "The maximum number of objects returned per request is 100. Use paging
        # to get more objects."
        # (https://roboticdogs.actionkit.com/docs//manual/api/rest/overview.html#ordering)
        kwargs["_limit"] = min(100, limit or 1_000_000_000)
        if ascdesc == "asc":
            kwargs["order_by"] = threshold_field
        else:
            kwargs["order_by"] = "-" + threshold_field
        json_data = self._base_get(object_type, params=kwargs)
        data = json_data["objects"]
        next_url = json_data.get("meta", {}).get("next")
        while next_url:
            last = data[-1].get(threshold_field)
            if ascdesc == "asc" and last > threshold_value:
                break
            if ascdesc == "desc" and last < threshold_value:
                break
            resp = self.conn.get(f"https://{self.domain}{next_url}")
            data += resp.json().get("objects", [])
            next_url = resp.json().get("meta", {}).get("next")
            if limit and len(data) >= limit:
                break
        # This could be more efficient but it's still O(n) so no big deal
        i = len(data) - 1  # start at the end; 0-indexed means the end is length - 1
        if ascdesc == "asc":
            while data[i].get(threshold_field) > threshold_value:
                i = i - 1
        else:
            while data[i].get(threshold_field) < threshold_value:
                i = i - 1
        data = data[:i]
        return Table(data[:limit])

    def get_order(self, order_id):
        """
        Get an order.

        `Args:`
            order_id: int
                The order id of the record to get.
        `Returns`:
            User json object
        """

        return self._base_get(
            endpoint="order", entity_id=order_id, exception_message="Order not found"
        )

    def update_order(self, order_id, **kwargs):
        """
        Update an order.

        `Args:`
            order_id: int
                The id of the order to update
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
        `Returns:`
            ``None``
        """

        resp = self.conn.patch(self._base_endpoint("order", order_id), data=json.dumps(kwargs))
        logger.info(f"{resp.status_code}: {order_id}")

    def update_order_user_detail(self, user_detail_id, **kwargs):
        """
        Update an order user detail.

        `Args:`
            user_detail_id: int
                The id of the order user detail to update
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                at the /rest/v1/orderuserdetail/schema/ path on any ActionKit instance.
        `Returns:`
            ``HTTP response from the patch request``
        """

        resp = self.conn.patch(
            self._base_endpoint("orderuserdetail", user_detail_id), data=json.dumps(kwargs)
        )
        logger.info(f"{resp.status_code}: {user_detail_id}")

        return resp

    def get_orderrecurring(self, orderrecurring_id):
        """
        Get an orderrecurring.

        `Args:`
            orderrecurring_id: int
                The orderrecurring id of the record to get.
        `Returns`:
            User json object
        """

        return self._base_get(
            endpoint="orderrecurring",
            entity_id=orderrecurring_id,
            exception_message="Orderrecurring not found",
        )

    def cancel_orderrecurring(self, recurring_id):
        """
        Cancel a recurring order.

        `Args:`
            recurring_id: int
                The id of the recurring order to update (NOT the order_id)
        `Returns:`
            ``None``
        """

        resp = self.conn.post(self._base_endpoint("orderrecurring", str(recurring_id) + "/cancel"))
        logger.info(f"{resp.status_code}: {recurring_id}")
        return resp

    def update_orderrecurring(self, orderrecurring_id, **kwargs):
        """
        Update a recurring order.

        `Args:`
            orderrecurring_id: int
                The id of the orderrecurring to update
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
        `Returns:`
            ``None``
        """

        resp = self.conn.patch(
            self._base_endpoint("orderrecurring", orderrecurring_id),
            data=json.dumps(kwargs),
        )
        logger.info(f"{resp.status_code}: {orderrecurring_id}")

    def get_orders(self, limit=None, **kwargs):
        """Get multiple orders.

        `Args:`
            limit: int
                The number of orders to return. If omitted, all orders are returned.
            **kwargs:
                Optional arguments to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.

                Additionally, expressions to filter the data can also be provided. For addition
                info, visit `Django's docs on field lookups <https://docs.djangoproject.com/\
                en/3.1/topics/db/queries/#field-lookups>`_.

                .. code-block:: python

                    ak.get_orders(import_id="my-import-123")
        `Returns:`
            Parsons.Table
                The orders data.
        """
        return self.paginated_get("order", limit=limit, **kwargs)

    def update_paymenttoken(self, paymenttoken_id, **kwargs):
        """
        Update a saved payment token.

        `Args:`
            paymenttoken_id: int
                The id of the payment token to update
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
        `Returns:`
            ``HTTP response``
        """

        resp = self.conn.patch(
            self._base_endpoint("paymenttoken", paymenttoken_id),
            data=json.dumps(kwargs),
        )
        logger.info(f"{resp.status_code}: {paymenttoken_id}")
        return resp

    def get_page_followup(self, page_followup_id):
        """
        Get a page followup.

        `Args:`
            page_followup_id: int
                The user id of the record to get.
        `Returns`:
            Page followup json object
        """

        return self._base_get(
            endpoint="pagefollowup",
            entity_id=page_followup_id,
            exception_message="Page followup not found",
        )

    def get_page_followup_fields(self):
        """
        Get list of valid page followup fields that can be passed with the
        :meth:`ActionKit.create_page_followup` method.

        `Returns`:
            List of page followup fields
        """

        resp = self._base_get(endpoint="pagefollowup/schema")
        return list(resp["fields"].keys())

    def create_page_followup(self, signup_page_id, url, **kwargs):
        """
        Add a page followup.

        `Args:`
            signup_page_id: int
                The signup page to associate the followup page with
            url: str
                URL of the folloup page
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
        `Returns`:
            API location of new resource
        """

        return self._base_post(
            endpoint="pagefollowup",
            exception_message="Could not create page followup",
            page=f"/rest/v1/eventsignuppage/{signup_page_id}/",
            url=url,
            **kwargs,
        )

    def get_survey_question(self, survey_question_id):
        """
        Get a survey question.

        `Args:`
            survey_question_id: int
                The survey question id of the record to get.
        `Returns`:
            Survey question json object
        """

        return self._base_get(
            endpoint="surveyquestion",
            entity_id=survey_question_id,
            exception_message="Survey question not found",
        )

    def update_survey_question(self, survey_question_id, **kwargs):
        """
        Update a survey question.

        `Args:`
            survey_question_id: int
                The id of the survey question to update
            survey_question_dict: dict
                A dictionary of fields to update for the survey question.
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
        `Returns:`
            ``None``
        """

        resp = self.conn.patch(
            self._base_endpoint("surveyquestion", survey_question_id),
            data=json.dumps(kwargs),
        )
        logger.info(f"{resp.status_code}: {survey_question_id}")

    def create_transaction(self, **kwargs):
        """
        Create a transaction.

        `Args:`
            **kwargs:
                Optional arguments and fields to pass to the client.
        `Returns:`
            Transaction json object
        """

        return self._base_post(
            endpoint="transaction",
            exception_message="Could not create transaction",
            **kwargs,
        )

    def update_transaction(self, transaction_id, **kwargs):
        """
        Update a transaction.

        `Args:`
            transaction_id: int
                The id of the transaction to update
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
        `Returns:`
            ``None``
        """

        resp = self.conn.patch(
            self._base_endpoint("transaction", transaction_id), data=json.dumps(kwargs)
        )
        logger.info(f"{resp.status_code}: {transaction_id}")

    def get_transactions(self, limit=None, **kwargs):
        """Get multiple transactions.

        `Args:`
            limit: int
                The number of transactions to return. If omitted, all transactions are returned.
            **kwargs:
                Optional arguments to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.

                Additionally, expressions to filter the data can also be provided. For addition
                info, visit `Django's docs on field lookups <https://docs.djangoproject.com/\
                en/3.1/topics/db/queries/#field-lookups>`_.

                .. code-block:: python

                    ak.get_transactions(order="order-1")
        `Returns:`
            Parsons.Table
                The transactions data.
        """
        return self.paginated_get("transaction", limit=limit, **kwargs)

    def create_generic_action(self, page, email=None, ak_id=None, **kwargs):
        """
        Post a generic action. One of ``ak_id`` or ``email`` is a required argument.

        `Args:`
            page:
                The page to post the action. The page short name.
            email:
                The email address of the user to post the action.
            ak_id:
                The action kit id of the record.
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                in the `ActionKit API Documentation <https://roboticdogs.actionkit.com/docs/\
                manual/api/rest/actionprocessing.html>`_.
        `Returns`:
            dict
                The response json
        """  # noqa: E501,E261

        if not email or ak_id:
            raise ValueError("One of email or ak_id is required.")

        return self._base_post(
            endpoint="action",
            exception_message="Could not create action.",
            email=email,
            page=page,
            return_full_json=True,
            **kwargs,
        )

    def update_import_action(self, action_id, **kwargs):
        """
        Update an import action.

        `Args:`
            action_id: int
                The action id of the import action to update
            **kwargs:
                Optional arguments and fields to pass to the client. A full list can be found
                at the /rest/v1/importaction/schema/ path on any ActionKit instance.
        `Returns:`
            ``HTTP response from the patch request``
        """

        resp = self.conn.patch(
            self._base_endpoint("importaction", action_id), data=json.dumps(kwargs)
        )
        logger.info(f"{resp.status_code}: {action_id}")

        return resp

    def bulk_upload_csv(
        self,
        csv_file,
        import_page,
        autocreate_user_fields=False,
        user_fields_only=False,
    ):
        """
        Bulk upload a csv file of new users or user updates.
        If you are uploading a table object, use bulk_upload_table instead.
        See `ActionKit User Upload Documentation <https://roboticdogs.actionkit.com/docs/manual/api/rest/uploads.html>`_
        Be careful that blank values in columns will overwrite existing data.

        If you get a 500 error, try sending a much smaller file (say, one row),
        which is more likely to return the proper 400 with a useful error message

        `Args:`
            import_page: str
                The page to post the action. The page short name.
            csv_file: str or buffer
                The csv (optionally zip'd) file path or a file buffer object
                A user_id or email column is required.
                ActionKit rejects files that are larger than 128M
            autocreate_user_fields: bool
              When True columns starting with "user_" will be uploaded as user fields.
              See the `autocreate_user_fields documentation
              <https://roboticdogs.actionkit.com/docs/manual/api/rest/uploads.html#create-a-multipart-post-request>`_.
            user_fields_only: bool
              When uploading only an email/user_id column and user_ user fields,
              ActionKit has a fast processing path.
              This doesn't work, if you upload a zipped csv though.
        `Returns`:
            dict
                success: whether upload was successful
                progress_url: an API URL to get progress on upload processing
                res: requests http response object
        """  # noqa: E501,E261

        # self.conn defaults to JSON, but this has to be form/multi-part....
        upload_client = self._conn({"accepts": "application/json"})
        if isinstance(csv_file, str):
            csv_file = open(csv_file, "rb")

        url = self._base_endpoint("upload")
        files = {"upload": csv_file}
        data = {
            "page": import_page,
            "autocreate_user_fields": int(autocreate_user_fields),
            "user_fields_only": int(user_fields_only),
        }
        with upload_client.post(url, files=files, data=data) as res:
            progress_url = res.headers.get("Location")
            rv = {
                "res": res,
                "success": res.status_code == 201,
                "id": progress_url.split("/")[-2] if progress_url else None,
                "progress_url": progress_url,
            }
            return rv

    def bulk_upload_table(
        self,
        table,
        import_page,
        autocreate_user_fields=0,
        no_overwrite_on_empty=False,
        set_only_columns=None,
    ):
        """
        Bulk upload a table of new users or user updates.
        See `ActionKit User Upload Documentation <https://roboticdogs.actionkit.com/docs/manual/api/rest/uploads.html>`_
        Be careful that blank values in columns will overwrite existing data.

        Tables with only an identifying column (user_id/email) and user_ user fields
        will be fast-processed -- this is useful for setting/updating user fields.

        .. note::
            If you get a 500 error, try sending a much smaller file (say, one row),
            which is more likely to return the proper 400 with a useful error message

        `Args:`
            import_page: str
                The page to post the action. The page short name.
            table: Table Class
                A Table of user data to bulk upload
                A user_id or email column is required.
            autocreate_user_fields: bool
                When True columns starting with "user_" will be uploaded as user fields.
                `ActionKit <https://actionkit.com/>`_.
                See the autocreate_user_fields `documentation <https://roboticdogs.actionkit.com/docs/manual/api/rest/uploads.html#create-a-multipart-post-request>`_.
            no_overwrite_on_empty: bool
                When uploading user data, ActionKit will, by default, take a blank value
                and overwrite existing data for that user.
                This can be undesirable, if the goal is to only send updates.
                Setting this to True will divide up the table into multiple upload
                batches, changing the columns uploaded based on permutations of
                empty columns.
            set_only_columns: list
                This is similar to no_overwrite_on_empty but restricts to a specific set of columns
                which, if blank, should not be overwritten.
        `Returns`:
            dict
                success: bool -- whether upload was successful (individual rows may not have been)
                results: [dict] -- This is a list of the full results.
                         progress_url and res for any results
        """  # noqa: E501,E261

        import_page = check_env.check("ACTION_KIT_IMPORTPAGE", import_page)
        upload_tables = self._split_tables_no_empties(
            table, no_overwrite_on_empty, set_only_columns
        )
        results = []
        for tbl in upload_tables:
            user_fields_only = int(
                not any([h for h in tbl.columns if h != "email" and not h.startswith("user_")])
            )
            results.append(
                self.bulk_upload_csv(
                    tbl.to_csv(),
                    import_page,
                    autocreate_user_fields=autocreate_user_fields,
                    user_fields_only=user_fields_only,
                )
            )
        return {"success": all([r["success"] for r in results]), "results": results}

    def _split_tables_no_empties(self, table, no_overwrite_on_empty, set_only_columns):
        table_groups = {}
        # uploading combo of user_id and email column should be mutually exclusive
        blank_columns_test = table.columns
        if not no_overwrite_on_empty:
            blank_columns_test = set(["user_id", "email"] + (set_only_columns or [])).intersection(
                table.columns
            )
        for row in table:
            blanks = tuple(k for k in blank_columns_test if row.get(k) in (None, ""))
            grp = table_groups.setdefault(blanks, [])
            grp.append(row)
        results = []
        for blanks, subset in table_groups.items():
            subset_table = Table(subset)
            if blanks:
                subset_table.table = subset_table.table.cutout(*blanks)
            logger.debug(f"Column Upload Blanks: {blanks}")
            logger.debug(f"Column Upload Columns: {subset_table.columns}")
            if not set(["user_id", "email"]).intersection(subset_table.columns):
                logger.warning(
                    f"Upload will fail without user_id or email. "
                    f"Rows: {subset_table.num_rows}, Columns: {subset_table.columns}"
                )
            results.append(subset_table)
        return results

    def collect_upload_errors(self, result_array):
        """
        Collect any upload errors as a list of objects from bulk_upload_table 'results' key value.
        This waits for uploads to complete, so it may take some time if you uploaded a large file.
        `Args:`
            result_array: list
                After receiving a dict back from bulk_upload_table you may want to see if there
                were any errors in the uploads.  If you call collect_upload_errors(result_array)
                it will iterate across each of the uploads fetching the final result of e.g.
                /rest/v1/uploaderror?upload=123
        `Returns`:
            [dict]
                message: str -- error message
                upload: str -- upload progress API path e.g. "/rest/v1/upload/123456/"
                id: int -- upload error record id (different than upload id)
        """
        errors = []
        for res in result_array:
            upload_id = res.get("id")
            if upload_id:
                # Pend until upload is complete
                while True:
                    upload = self._base_get(endpoint="upload", entity_id=upload_id)
                    if upload.get("is_completed"):
                        break
                    else:
                        time.sleep(1)

                # ActionKit limits length of error list returned
                # Iterate until all errors are gathered
                error_count = upload.get("has_errors")
                limit = 20

                error_pages = math.ceil(error_count / limit)
                for page in range(0, error_pages):
                    error_data = self._base_get(
                        endpoint="uploaderror",
                        params={
                            "upload": upload_id,
                            "_limit": limit,
                            "_offset": page * limit,
                        },
                    )
                    logger.debug(f"error collect result: {error_data}")
                    errors.extend(error_data.get("objects", []))

        return errors
