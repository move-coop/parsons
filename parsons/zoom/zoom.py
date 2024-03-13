from parsons.utilities import check_env
from parsons.utilities.oauth_api_connector import OAuth2APIConnector
from parsons import Table
import logging
import uuid

logger = logging.getLogger(__name__)

ZOOM_URI = "https://api.zoom.us/v2/"
ZOOM_AUTH_CALLBACK = "https://zoom.us/oauth/token"

##########


class Zoom:
    """
    Instantiate the Zoom class.

    `Args:`
        api_key: str
            A valid Zoom api key. Not required if ``ZOOM_API_KEY`` env
            variable set.
        api_secret: str
            A valid Zoom api secret. Not required if ``ZOOM_API_SECRET`` env
            variable set.
    """

    def __init__(self, account_id=None, client_id=None, client_secret=None):
        self.account_id = check_env.check("ZOOM_ACCOUNT_ID", account_id)
        self.client_id = check_env.check("ZOOM_CLIENT_ID", client_id)
        self.__client_secret = check_env.check("ZOOM_CLIENT_SECRET", client_secret)

        self.client = OAuth2APIConnector(
            uri=ZOOM_URI,
            client_id=self.client_id,
            client_secret=self.__client_secret,
            token_url=ZOOM_AUTH_CALLBACK,
            auto_refresh_url=ZOOM_AUTH_CALLBACK,
            grant_type="account_credentials",
            authorization_kwargs={"account_id": self.account_id},
        )

    def _get_request(self, endpoint, data_key, params=None, **kwargs):
        """
        TODO: Consider increasing default page size.

        `Args`:
            endpoint: str
                API endpoint to send GET request
            data_key: str
                Unique value to use to parse through nested data
                (akin to a primary key in response JSON)
            params: dict
                Additional request parameters, defaults to None

        `Returns`:
            Parsons Table of API responses
        """

        r = self.client.get_request(endpoint, params=params, **kwargs)
        self.client.data_key = data_key
        data = self.client.data_parse(r)

        if not params:
            params = {}

        # Return a dict or table if only one item.
        if "page_number" not in r.keys():
            if isinstance(data, dict):
                return data
            if isinstance(data, list):
                return Table(data)

        # Else iterate through the pages and return a Table
        else:
            while r["page_number"] < r["page_count"]:
                params["page_number"] = int(r["page_number"]) + 1
                r = self.client.get_request(endpoint, params=params, **kwargs)
                data.extend(self.client.data_parse(r))
            return Table(data)

    def __handle_nested_json(self, table: Table, column: str) -> Table:
        """
        This function unpacks JSON values from Zoom's API, which are often
        objects nested in lists

        `Args`:
            table: parsons.Table
                Parsons Table of Zoom API responses

            column: str
                Column name of nested JSON

        `Returns`:
            Parsons Table
        """

        return Table(table.unpack_list(column=column)).unpack_dict(
            column=f"{column}_0", prepend_value=f"{column}_"
        )

    def __process_poll_results(self, tbl: Table) -> Table:
        """
        Unpacks nested poll results values from the Zoom reports endpoint

        `Args`:
            tbl: parsons.Table
                Table of poll results derived from Zoom API request

        `Returns`:
            Parsons Table
        """
        if tbl.num_rows == 0:
            return tbl

        # Add surrogate key
        tbl.add_column("poll_taker_id", lambda _: str(uuid.uuid4()))

        # Unpack values
        tbl = tbl.unpack_nested_columns_as_rows(
            "question_details", key="poll_taker_id", expand_original=True
        )

        # Remove extraneous columns
        tbl.remove_column("poll_taker_id")
        tbl.remove_column("question_details")

        # Unpack question values
        tbl = tbl.unpack_dict("question_details_value", include_original=True, prepend=False)

        # Remove column from API response
        tbl.remove_column("question_details_value")
        tbl.remove_column("uid")

        return tbl

    def get_users(self, status="active", role_id=None):
        """
        Get users.

        `Args:`
            status: str
                Filter by the user status. Must be one of following: ``active``,
                ``inactive``, or ``pending``.
            role_id: str
                Filter by the user role.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        if status not in ["active", "inactive", "pending"]:
            raise ValueError("Invalid status type provided.")

        params = {"status": status, "role_id": role_id}

        tbl = self._get_request("users", "users", params=params)
        logger.info(f"Retrieved {tbl.num_rows} users.")
        return tbl

    def get_meetings(self, user_id, meeting_type="scheduled"):
        """
        Get meetings scheduled by a user.

        `Args:`
            user_id: str
                A user id or email address of the meeting host.
            meeting_type: str

                .. list-table::
                    :widths: 25 50
                    :header-rows: 1

                    * - Type
                      - Notes
                    * - ``scheduled``
                      - This includes all valid past meetings, live meetings and upcoming
                        scheduled meetings. It is the equivalent to the combined list of
                        "Previous Meetings" and "Upcoming Meetings" displayed in the user's
                        Meetings page.
                    * - ``live``
                      - All the ongoing meetings.
                    * - ``upcoming``
                      - All upcoming meetings including live meetings.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = self._get_request(f"users/{user_id}/meetings", "meetings")
        logger.info(f"Retrieved {tbl.num_rows} meetings.")
        return tbl

    def get_past_meeting(self, meeting_uuid):
        """
        Get metadata regarding a past meeting.

        `Args:`
            meeting_id: int
                The meeting id
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = self._get_request(f"past_meetings/{meeting_uuid}", None)
        logger.info(f"Retrieved meeting {meeting_uuid}.")
        return tbl

    def get_past_meeting_participants(self, meeting_id):
        """
        Get past meeting participants.

        `Args:`
            meeting_id: int
                The meeting id
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = self._get_request(f"report/meetings/{meeting_id}/participants", "participants")
        logger.info(f"Retrieved {tbl.num_rows} participants.")
        return tbl

    def get_meeting_registrants(self, meeting_id):
        """
        Get meeting registrants.

        `Args:`
            meeting_id: int
                The meeting id
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = self._get_request(f"meetings/{meeting_id}/registrants", "registrants")
        logger.info(f"Retrieved {tbl.num_rows} registrants.")
        return tbl

    def get_user_webinars(self, user_id):
        """
        Get meeting registrants.

        `Args:`
            user_id: str
                The user id
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = self._get_request(f"users/{user_id}/webinars", "webinars")
        logger.info(f"Retrieved {tbl.num_rows} webinars.")
        return tbl

    def get_past_webinar_participants(self, webinar_id):
        """
        Get past meeting participants

        `Args:`
            webinar_id: str
                The webinar id
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = self._get_request(f"report/webinars/{webinar_id}/participants", "participants")
        logger.info(f"Retrieved {tbl.num_rows} webinar participants.")
        return tbl

    def get_webinar_registrants(self, webinar_id):
        """
        Get past meeting participants

        `Args:`
            webinar_id: str
                The webinar id
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = self._get_request(f"webinars/{webinar_id}/registrants", "registrants")
        logger.info(f"Retrieved {tbl.num_rows} webinar registrants.")
        return tbl

    def get_meeting_poll_metadata(self, meeting_id, poll_id) -> Table:
        """
        Get metadata about a specific poll for a given meeting ID

        Required scopes: `meeting:read`

        `Args`:
            meeting_id: int
                Unique identifier for Zoom meeting
            poll_id: int
                Unique identifier for poll

        `Returns`:
            Parsons Table of all polling responses
        """

        endpoint = f"meetings/{meeting_id}/polls/{poll_id}"
        tbl = self._get_request(endpoint=endpoint, data_key="questions")

        if isinstance(tbl, dict):
            logger.debug(f"No poll data returned for poll ID {poll_id}")
            return Table(tbl)

        logger.info(
            f"Retrieved {tbl.num_rows} rows of metadata [meeting={meeting_id} poll={poll_id}]"
        )

        return self.__handle_nested_json(table=tbl, column="prompts")

    def get_meeting_all_polls_metadata(self, meeting_id) -> Table:
        """
        Get metadata for all polls for a given meeting ID

        Required scopes: `meeting:read`

        `Args`:
            meeting_id: int
                Unique identifier for Zoom meeting

        `Returns`:
            Parsons Table of all polling responses
        """

        endpoint = f"meetings/{meeting_id}/polls"
        tbl = self._get_request(endpoint=endpoint, data_key="polls")

        if isinstance(tbl, dict):
            logger.debug(f"No poll data returned for meeting ID {meeting_id}")
            return Table(tbl)

        logger.info(f"Retrieved {tbl.num_rows} polls for meeting ID {meeting_id}")

        return self.__handle_nested_json(table=tbl, column="questions")

    def get_past_meeting_poll_metadata(self, meeting_id) -> Table:
        """
        List poll metadata of a past meeting.

        Required scopes: `meeting:read`

        `Args`:
            meeting_id: int
                The meeting's ID or universally unique ID (UUID).

        `Returns`:
            Parsons Table of poll results
        """

        endpoint = f"past_meetings/{meeting_id}/polls"
        tbl = self._get_request(endpoint=endpoint, data_key="questions")

        if isinstance(tbl, dict):
            logger.debug(f"No poll data returned for meeting ID {meeting_id}")
            return Table(tbl)

        logger.info(f"Retrieved {tbl.num_rows} polls for meeting ID {meeting_id}")

        return self.__handle_nested_json(table=tbl, column="prompts")

    def get_webinar_poll_metadata(self, webinar_id, poll_id) -> Table:
        """
        Get metadata for a specific poll for a given webinar ID

        Required scopes: `webinar:read`

        `Args`:
            webinar_id: str
                Unique identifier for Zoom webinar
            poll_id: int
                Unique identifier for poll

        `Returns`:
            Parsons Table of all polling responses
        """

        endpoint = f"webinars/{webinar_id}/polls/{poll_id}"
        tbl = self._get_request(endpoint=endpoint, data_key="questions")

        if isinstance(tbl, dict):
            logger.debug(f"No poll data returned for poll ID {poll_id}")
            return Table(tbl)

        logger.info(
            f"Retrieved {tbl.num_rows} rows of metadata [meeting={webinar_id} poll={poll_id}]"
        )

        return self.__handle_nested_json(table=tbl, column="prompts")

    def get_webinar_all_polls_metadata(self, webinar_id) -> Table:
        """
        Get metadata for all polls for a given webinar ID

        Required scopes: `webinar:read`

        `Args`:
            webinar_id: str
                Unique identifier for Zoom webinar

        `Returns`:
            Parsons Table of all polling responses
        """

        endpoint = f"webinars/{webinar_id}/polls"
        tbl = self._get_request(endpoint=endpoint, data_key="polls")

        if isinstance(tbl, dict):
            logger.debug(f"No poll data returned for webinar ID {webinar_id}")
            return Table(tbl)

        logger.info(f"Retrieved {tbl.num_rows} polls for meeting ID {webinar_id}")

        return self.__handle_nested_json(table=tbl, column="questions")

    def get_past_webinar_poll_metadata(self, webinar_id) -> Table:
        """
        Retrieves the metadata for Webinar Polls of a specific Webinar

        Required scopes: `webinar:read`

        `Args`:
            webinar_id: str
                The webinar's ID or universally unique ID (UUID).

        `Returns`:
            Parsons Table of all polling responses
        """

        endpoint = f"past_webinars/{webinar_id}/polls"
        tbl = self._get_request(endpoint=endpoint, data_key="questions")

        if isinstance(tbl, dict):
            logger.debug(f"No poll data returned for webinar ID {webinar_id}")
            return Table(tbl)

        logger.info(f"Retrieved {tbl.num_rows} polls for meeting ID {webinar_id}")

        return self.__handle_nested_json(table=tbl, column="prompts")

    def get_meeting_poll_results(self, meeting_id) -> Table:
        """
        Get a report of poll results for a past meeting

        Required scopes: `report:read:admin`
        """

        endpoint = f"report/meetings/{meeting_id}/polls"
        tbl = self._get_request(endpoint=endpoint, data_key="questions")

        if isinstance(tbl, dict):
            logger.debug(f"No poll data returned for meeting ID {meeting_id}")
            return Table(tbl)

        logger.info(f"Retrieved {tbl.num_rows} reults for meeting ID {meeting_id}")

        return self.__process_poll_results(tbl=tbl)

    def get_webinar_poll_results(self, webinar_id) -> Table:
        """
        Get a report of poll results for a past webinar

        Required scopes: `report:read:admin`
        """

        endpoint = f"report/webinars/{webinar_id}/polls"
        tbl = self._get_request(endpoint=endpoint, data_key="questions")

        if isinstance(tbl, dict):
            logger.debug(f"No poll data returned for webinar ID {webinar_id}")
            return Table(tbl)

        logger.info(f"Retrieved {tbl.num_rows} reults for webinar ID {webinar_id}")

        return self.__process_poll_results(tbl=tbl)
