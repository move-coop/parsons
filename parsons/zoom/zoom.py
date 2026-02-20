import datetime
import logging
import uuid
from typing import Literal

from oauthlib.oauth2.rfc6749.errors import InvalidClientError

from parsons import Table
from parsons.utilities import check_env
from parsons.utilities.oauth_api_connector import OAuth2APIConnector

logger = logging.getLogger(__name__)

ZOOM_URI = "https://api.zoom.us/v2/"
ZOOM_AUTH_CALLBACK = "https://zoom.us/oauth/token"

##########


class ZoomV1:
    def __init__(
        self,
        account_id: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
    ):
        """
        Instantiate the Zoom class.

        Args:
            account_id: str
                A valid Zoom account id. Not required if ``ZOOM_ACCOUNT_ID`` env
                variable set.
            client_id: str
                A valid Zoom client id. Not required if ``ZOOM_CLIENT_ID`` env
                variable set.
            client_secret: str
                A valid Zoom client secret. Not required if `ZOOM_CLIENT_SECRET` env
                variable set.

        """
        self.account_id = check_env.check("ZOOM_ACCOUNT_ID", account_id)
        self.client_id = check_env.check("ZOOM_CLIENT_ID", client_id)
        self.__client_secret = check_env.check("ZOOM_CLIENT_SECRET", client_secret)
        self.client = self.get_oauth_client()

    def get_oauth_client(self) -> OAuth2APIConnector:
        return OAuth2APIConnector(
            uri=ZOOM_URI,
            client_id=self.client_id,
            client_secret=self.__client_secret,
            token_url=ZOOM_AUTH_CALLBACK,
            auto_refresh_url=ZOOM_AUTH_CALLBACK,
            grant_type="account_credentials",
            authorization_kwargs={"account_id": self.account_id},
        )

    def _get_request(
        self,
        endpoint: str,
        data_key: str | None,
        params: dict[str, str] | None = None,
        **kwargs,
    ) -> Table:
        """
        TODO: Consider increasing default page size.

        Args:
            endpoint: str
                API endpoint to send GET request
            data_key: str
                Unique value to use to parse through nested data
                (akin to a primary key in response JSON)
            params: dict
                Additional request parameters, defaults to None

        Returns:
            Parsons Table of API responses

        """

        logger.warning("This version of the Zoom connector uses a deprecated pagination method.")
        logger.info("Consider switching to V2!")
        logger.info(
            "See docs for more information: https://move-coop.github.io/parsons/html/latest/zoom.html"
        )

        r = self.client.get_request(endpoint, params=params, **kwargs)
        self.client.data_key = data_key
        data = self.client.data_parse(r)

        if not params:
            params = {}

        # Return a dict or table if only one item.
        if "page_number" not in r:
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

    def __handle_nested_json(self, table: Table, column: str, version: Literal[1, 2] = 1) -> Table:
        """
        This function unpacks JSON values from Zoom's API, which are often
        objects nested in lists

        Args:
            table: parsons.Table
                Parsons Table of Zoom API responses

            column: str
                Column name of nested JSON

        Returns:
            Parsons Table

        """
        if version == 2:
            if column in table.columns:
                return Table(table.unpack_list(column=column))
            else:
                return table

        return Table(table.unpack_list(column=column)).unpack_dict(
            column=f"{column}_0", prepend_value=f"{column}_"
        )

    def __process_poll_results(self, tbl: Table) -> Table:
        """
        Unpacks nested poll results values from the Zoom reports endpoint

        Args:
            tbl: parsons.Table
                Table of poll results derived from Zoom API request

        Returns:
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

    def get_users(
        self,
        status: Literal["active", "inactive", "pending"] = "active",
        role_id: str | None = None,
    ) -> Table:
        """
        Get users.

        Args:
            status: str
                Filter by the user status. Must be one of following: ``active``,
                ``inactive``, or ``pending``.
            role_id: str
                Filter by the user role.

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        if status not in ["active", "inactive", "pending"]:
            raise ValueError("Invalid status type provided.")

        params = {"status": status, "role_id": role_id}

        tbl = self._get_request(endpoint="users", data_key="users", params=params)
        logger.info(f"Retrieved {tbl.num_rows} users.")
        return tbl

    def get_meetings(
        self,
        user_id: str,
        meeting_type: Literal[
            "scheduled", "live", "upcoming", "upcoming_meetings", "previous_meetings"
        ] = "scheduled",
        from_date: datetime.date | None = None,
        to_date: datetime.date | None = None,
    ) -> Table:
        """
        Get meetings scheduled by a user.

        Args:
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
            from_date: datetime.date or None
                Optional start date for the range of meetings to retrieve.
            to_date: datetime.date or None
                Optional end date for the range of meetings to retrieve.

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """
        params: dict[str, str] = {"type": meeting_type}
        if from_date:
            params["from"] = from_date.isoformat()
        if to_date:
            params["to"] = to_date.isoformat()

        tbl = self._get_request(f"users/{user_id}/meetings", "meetings", params=params)
        logger.info(f"Retrieved {tbl.num_rows} meetings.")
        return tbl

    def get_past_meeting(self, meeting_uuid: str) -> Table:
        """
        Get metadata regarding a past meeting.

        Args:
            meeting_id: int
                The meeting id
        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        tbl = self._get_request(f"past_meetings/{meeting_uuid}", None)
        logger.info(f"Retrieved meeting {meeting_uuid}.")
        return tbl

    def get_past_meeting_participants(self, meeting_id: int) -> Table:
        """
        Get past meeting participants.

        Args:
            meeting_id: int
                The meeting id
        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        tbl = self._get_request(f"report/meetings/{meeting_id}/participants", "participants")
        logger.info(f"Retrieved {tbl.num_rows} participants.")
        return tbl

    def get_meeting_registrants(self, meeting_id: int) -> Table:
        """
        Get meeting registrants.

        Args:
            meeting_id: int
                The meeting id
        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        tbl = self._get_request(f"meetings/{meeting_id}/registrants", "registrants")
        logger.info(f"Retrieved {tbl.num_rows} registrants.")
        return tbl

    def get_user_webinars(self, user_id: str) -> Table:
        """
        Get meeting registrants.

        Args:
            user_id: str
                The user id
        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        tbl = self._get_request(f"users/{user_id}/webinars", "webinars")
        logger.info(f"Retrieved {tbl.num_rows} webinars.")
        return tbl

    def get_past_webinar_report(self, webinar_id: str) -> dict | None:
        """
        Get past meeting participants

        Args:
            webinar_id: str
                The webinar id
        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        dic = self._get_request(endpoint=f"report/webinars/{webinar_id}", data_key=None)
        if dic:
            logger.info(f"Retrieved webinar_report for webinar: {webinar_id}.")
        return dic

    def get_past_webinar_participants(self, webinar_id: str) -> Table:
        """
        Get past meeting participants

        Args:
            webinar_id: str
                The webinar id
        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        tbl = self._get_request(f"report/webinars/{webinar_id}/participants", "participants")
        logger.info(f"Retrieved {tbl.num_rows} webinar participants.")
        return tbl

    def get_webinar_registrants(self, webinar_id: str) -> Table:
        """
        Get past meeting participants

        Args:
            webinar_id: str
                The webinar id
        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        tbl = self._get_request(f"webinars/{webinar_id}/registrants", "registrants")
        logger.info(f"Retrieved {tbl.num_rows} webinar registrants.")
        return tbl

    def get_meeting_poll_metadata(
        self, meeting_id: int, poll_id: int, version: Literal[1, 2] = 1
    ) -> Table:
        """
        Get metadata about a specific poll for a given meeting ID

        Required scopes: `meeting:read`

        Args:
            meeting_id: int
                Unique identifier for Zoom meeting
            poll_id: int
                Unique identifier for poll

        Returns:
            Parsons Table of all polling responses

        """

        endpoint = f"meetings/{meeting_id}/polls/{poll_id}"
        tbl = self._get_request(endpoint=endpoint, data_key="questions")

        if tbl.num_rows == 0:
            logger.debug(f"No poll data returned for poll ID {poll_id}")
            return tbl

        logger.info(
            f"Retrieved {tbl.num_rows} rows of metadata [meeting={meeting_id} poll={poll_id}]"
        )

        if "prompts" in tbl.columns:
            logger.info(f"Unnesting columns 'prompts' from existing table columns: {tbl.columns}")
            return self.__handle_nested_json(table=tbl, column="prompts", version=version)
        else:
            return tbl

    def get_meeting_all_polls_metadata(self, meeting_id: int, version: Literal[1, 2] = 1) -> Table:
        """
        Get metadata for all polls for a given meeting ID

        Required scopes: `meeting:read`

        Args:
            meeting_id: int
                Unique identifier for Zoom meeting

        Returns:
            Parsons Table of all polling responses

        """

        endpoint = f"meetings/{meeting_id}/polls"
        tbl = self._get_request(endpoint=endpoint, data_key="polls")

        if tbl.num_rows == 0:
            logger.debug(f"No poll data returned for meeting ID {meeting_id}")
            return tbl

        logger.info(f"Retrieved {tbl.num_rows} polls for meeting ID {meeting_id}")

        return self.__handle_nested_json(table=tbl, column="questions", version=version)

    def get_past_meeting_poll_metadata(self, meeting_id: int, version: Literal[1, 2] = 1) -> Table:
        """
        List poll metadata of a past meeting.

        Required scopes: `meeting:read`

        Args:
            meeting_id: int
                The meeting's ID or universally unique ID (UUID).

        Returns:
            Parsons Table of poll results

        """

        endpoint = f"past_meetings/{meeting_id}/polls"
        tbl = self._get_request(endpoint=endpoint, data_key="questions")

        if tbl.num_rows == 0:
            logger.debug(f"No poll data returned for meeting ID {meeting_id}")
            return tbl

        logger.info(f"Retrieved {tbl.num_rows} polls for meeting ID {meeting_id}")
        logger.info(
            f"Unnesting columns 'question_details' from existing table columns: {tbl.columns}"
        )

        return self.__handle_nested_json(table=tbl, column="question_details", version=version)

    def get_webinar_poll_metadata(
        self, webinar_id: str, poll_id: int, version: Literal[1, 2] = 1
    ) -> Table:
        """
        Get metadata for a specific poll for a given webinar ID

        Required scopes: `webinar:read`

        Args:
            webinar_id: str
                Unique identifier for Zoom webinar
            poll_id: int
                Unique identifier for poll

        Returns:
            Parsons Table of all polling responses

        """

        endpoint = f"webinars/{webinar_id}/polls/{poll_id}"
        tbl = self._get_request(endpoint=endpoint, data_key="questions")

        if tbl.num_rows == 0:
            logger.debug(f"No poll data returned for poll ID {poll_id}")
            return tbl

        logger.info(
            f"Retrieved {tbl.num_rows} rows of metadata [meeting={webinar_id} poll={poll_id}]"
        )

        return self.__handle_nested_json(table=tbl, column="prompts", version=version)

    def get_webinar_all_polls_metadata(self, webinar_id: str, version: Literal[1, 2] = 1) -> Table:
        """
        Get metadata for all polls for a given webinar ID

        Required scopes: `webinar:read`

        Args:
            webinar_id: str
                Unique identifier for Zoom webinar

        Returns:
            Parsons Table of all polling responses

        """

        endpoint = f"webinars/{webinar_id}/polls"
        tbl = self._get_request(endpoint=endpoint, data_key="polls")

        if tbl.num_rows == 0:
            logger.debug(f"No poll data returned for webinar ID {webinar_id}")
            return tbl

        logger.info(f"Retrieved {tbl.num_rows} polls for meeting ID {webinar_id}")

        return self.__handle_nested_json(table=tbl, column="questions", version=version)

    def get_past_webinar_poll_metadata(self, webinar_id: str, version: Literal[1, 2] = 1) -> Table:
        """
        Retrieves the metadata for Webinar Polls of a specific Webinar

        Required scopes: `webinar:read`

        Args:
            webinar_id: str
                The webinar's ID or universally unique ID (UUID).

        Returns:
            Parsons Table of all polling responses

        """

        endpoint = f"past_webinars/{webinar_id}/polls"
        tbl = self._get_request(endpoint=endpoint, data_key="questions")

        if tbl.num_rows == 0:
            logger.debug(f"No poll data returned for webinar ID {webinar_id}")
            return tbl

        logger.info(f"Retrieved {tbl.num_rows} polls for meeting ID {webinar_id}")

        return self.__handle_nested_json(table=tbl, column="question_details", version=version)

    def get_meeting_poll_results(self, meeting_id: int) -> Table:
        """
        Get a report of poll results for a past meeting

        Required scopes: `report:read:admin`
        """

        endpoint = f"report/meetings/{meeting_id}/polls"
        tbl = self._get_request(endpoint=endpoint, data_key="questions")

        if tbl.num_rows == 0:
            logger.debug(f"No poll data returned for meeting ID {meeting_id}")
            return tbl

        logger.info(f"Retrieved {tbl.num_rows} reults for meeting ID {meeting_id}")

        return self.__process_poll_results(tbl=tbl)

    def get_webinar_poll_results(self, webinar_id: str) -> Table:
        """
        Get a report of poll results for a past webinar

        Required scopes: `report:read:admin`
        """

        endpoint = f"report/webinars/{webinar_id}/polls"
        tbl = self._get_request(endpoint=endpoint, data_key="questions")

        if tbl.num_rows == 0:
            logger.debug(f"No poll data returned for webinar ID {webinar_id}")
            return tbl

        logger.info(f"Retrieved {tbl.num_rows} reults for webinar ID {webinar_id}")

        return self.__process_poll_results(tbl=tbl)


class ZoomV2(ZoomV1):
    """
    Version 2 implementation of a Parsons connector. Designed to involve minimal
    transformation logic and clearer naming conventions.

    Inherits the following methods from version 1:
    - get_users
    - get_meetings
    - get_past_meeting
    - get_meeting_registrants
    - get_past_webinar_report
    - get_webinar_registrants

    Overwrites the following methods from version 1:
    - get_past_meeting_participants
    - get_past_webinar_participants

    Renames/refactors the following methods (and raises error if original function called):
    - get_user_webinars
    - get_meeting_poll_metadata
    - get_meeting_all_polls_metadata
    - get_past_meeting_poll_metadata
    - get_webinar_poll_metadata
    - get_webinar_all_polls_metadata
    - get_past_webinar_poll_metadata
    - get_meeting_poll_results
    - get_webinar_poll_results

    Args:
        ZoomV1 (cls): version 1 Zoom connector class

    """

    def __init__(
        self,
        account_id: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
    ):
        super().__init__(account_id, client_id, client_secret)

    def _get_request(
        self,
        endpoint: str,
        data_key: str | None,
        params: dict[str, str] | None = None,
        **kwargs,
    ) -> Table:
        """
        Args:
            endpoint: str
                API endpoint to send GET request
            data_key: str
                Unique value to use to parse through nested data
                (akin to a primary key in response JSON)
            params: dict
                Additional request parameters, defaults to None

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        if params is None:
            params = {}
        if not params:
            params = {"page_size": 300}

        self.client.data_key = data_key
        next_page_token = ""
        has_more_pages = True
        data = []

        while has_more_pages:
            if next_page_token:
                params["next_page_token"] = next_page_token

            try:
                r = self.client.get_request(endpoint, params=params, **kwargs)
            except InvalidClientError:
                self.client = self.get_oauth_client()
                r = self.client.get_request(endpoint, params=params, **kwargs)
            parsed_resp = self.client.data_parse(r)
            if isinstance(parsed_resp, dict):
                parsed_resp = [parsed_resp]
            data.extend(parsed_resp)

            next_page_token = r.get("next_page_token")
            has_more_pages = bool(next_page_token)

        return Table(data)

    def get_webinars(self, user_id: int) -> Table:
        """
        Get webinars scheduled by or on behalf of a webinar host.

        Args:
            user_id: str
                The user id
        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        tbl = self._get_request(f"users/{user_id}/webinars", "webinars")
        logger.info(f"Retrieved {tbl.num_rows} webinars.")
        return tbl

    def get_webinar_occurrences(self, webinar_id: int) -> Table:
        """
        Get webinar occurrences for a given webinar ID.

        Args:
            webinar_id: int
                The webinar id
        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """
        tbl = self._get_request(f"webinars/{webinar_id}/", "occurrences")
        logger.info(f"Retrieved {tbl.num_rows} webinar occurrences.")
        return tbl

    def get_past_webinar_occurrences(self, webinar_id: int) -> Table:
        """
        Get past webinar occurrences for a given webinar ID.

        Args:
            webinar_id: int
                The webinar id
        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """
        tbl = self._get_request(f"past_webinars/{webinar_id}/instances", "webinars")
        tbl.add_column(column="webinar_id", value=webinar_id)
        logger.info(f"Retrieved {tbl.num_rows} webinar occurrences.")
        return tbl

    def get_user_webinars(self, user_id: str) -> AttributeError:
        return AttributeError(
            "Method get_user_webinars has been deprecated in favor of get_webinars"
        )

    def get_past_meeting_participants(self, meeting_id: int) -> Table:
        """
        Get past meeting participants.

        Args:
            meeting_id: int
                The meeting id
        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        tbl = self._get_request(f"past_meetings/{meeting_id}/participants", "participants")
        logger.info(f"Retrieved {tbl.num_rows} participants.")
        return tbl

    def get_past_webinar_participants(self, webinar_id: int) -> Table:
        """
        Get past webinar participants.

        Args:
            webinar_id: int
                The webinar id
        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        tbl = self._get_request(f"past_webinars/{webinar_id}/participants", "participants")
        logger.info(f"Retrieved {tbl.num_rows} participants.")
        return tbl

    def get_past_meeting_occurrences(self, meeting_id: int) -> Table:
        """
        Get past meeting occurrences for a given meeting ID.

        Args:
            meeting_id: int
                The meeting id
        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """
        tbl = self._get_request(f"past_meetings/{meeting_id}/instances", "meetings")
        tbl.add_column(column="meeting_id", value=meeting_id)
        logger.info(f"Retrieved {tbl.num_rows} webinar occurrences.")
        return tbl

    def get_meeting_poll(self, meeting_id: int, poll_id: str) -> Table:
        """
        Get information about a single poll for a given meeting ID.
        The returned data is identical to get_meeting_polls.

        Args:
            meeting_id: int
                Unique identifier for Zoom meeting
            poll_id: str
                Unique identifier for Zoom poll

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        endpoint = f"meetings/{meeting_id}/polls/{poll_id}"
        tbl = self._get_request(endpoint=endpoint, data_key=None)
        logger.info(f"Retrieved {tbl.num_rows} for [poll {poll_id}, meeting {meeting_id}]")
        return tbl

    def get_meeting_poll_metadata(self, meeting_id: int, poll_id: str, version: Literal[1, 2] = 1):
        raise AttributeError(
            "Method get_meeting_poll_metadata is deprecated in favor of get_meeting_poll"
        )

    def get_meeting_polls(self, meeting_id: int) -> Table:
        """
        Get information about all polls for a given meeting ID.
        The returned data is identical to get_meeting_poll but for
        all polls in the meeting.

        Args:
            meeting_id: int
                Unique identifier for Zoom meeting

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        endpoint = f"meetings/{meeting_id}/polls"
        tbl = self._get_request(endpoint=endpoint, data_key="polls")
        logger.info(f"Retrieved {tbl.num_rows} meeting polls for meeting {meeting_id}")
        return tbl

    def get_meeting_all_polls_metadata(self, meeting_id: int, version: Literal[1, 2] = 1):
        raise AttributeError(
            "Method get_meeting_all_polls_metadata is deprecated in favor of get_meeting_polls"
        )

    def get_past_meeting_poll_results(self, meeting_id: int) -> Table:
        """
        Get results for all polls for a given past meeting ID

        Args:
            meeting_id: int
                Unique identifier for Zoom meeting

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        endpoint = f"past_meetings/{meeting_id}/polls"
        tbl = self._get_request(endpoint=endpoint, data_key=None)
        logger.info(f"Retrieved {tbl.num_rows} meeting poll results")
        return tbl

    def get_past_meeting_poll_metadata(self, meeting_id: int, version: Literal[1, 2] = 1):
        raise AttributeError(
            "Method get_past_meeting_poll_metadata is deprecated in favor of get_past_meeting_poll_results"
        )

    def get_webinar_poll(self, webinar_id: int, poll_id: str) -> Table:
        """
        Get information about a single poll for a given webinar ID.
        The returned data is identical to get_webinar_polls.

        Args:
            webinar_id: int
                Unique identifier for Zoom webinar
            poll_id: str
                Unique identifier for Zoom poll

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        endpoint = f"webinars/{webinar_id}/polls/{poll_id}"
        tbl = self._get_request(endpoint=endpoint, data_key=None)
        logger.info(f"Retrieved {tbl.num_rows} for [poll {poll_id}, webinar {webinar_id}]")
        return tbl

    def get_webinar_poll_metadata(self, webinar_id, poll_id: str, version: Literal[1, 2] = 1):
        raise AttributeError(
            "Method get_webinar_poll_metadata is deprecated in favor of get_webinar_poll"
        )

    def get_webinar_polls(self, webinar_id: int) -> Table:
        """
        Get information for all polls for a given webinar ID
        The returned data is identical to get_webinar_poll but includes
        all polls in the webinar

        Args:
            webinar_id: str
                Unique identifier for Zoom webinar

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        endpoint = f"webinars/{webinar_id}/polls"
        tbl = self._get_request(endpoint=endpoint, data_key="polls")
        logger.info(f"Retrieved {tbl.num_rows} polls for webinar ID {webinar_id}")
        return tbl

    def get_webinar_all_polls_metadata(self, webinar_id: int, version: Literal[1, 2] = 1):
        raise AttributeError(
            "Method get_webinar_all_polls_metadata is deprecated in favor of get_webinar_polls"
        )

    def get_past_webinar_poll_results(self, webinar_id: int) -> Table:
        """
        Get results for all polls for a given past webinar ID

        Args:
            webinar_id: str
                Unique identifier for Zoom webinar

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        endpoint = f"past_webinars/{webinar_id}/polls"
        tbl = self._get_request(endpoint=endpoint, data_key=None)
        logger.info(f"Retrieved {tbl.num_rows} poll results for webinar ID {webinar_id}")
        return tbl

    def get_past_webinar_poll_metadata(self, webinar_id: int, version: Literal[1, 2] = 1):
        raise AttributeError(
            "Method get_past_webinar_poll_metadata is deprecated in favor of get_past_webinar_poll_results"
        )

    def get_meeting_poll_reports(self, meeting_id: int) -> Table:
        """
        Get polls reports for a given past meeting ID

        Args:
            meeting_id: str
                Unique identifier for Zoom meeting

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        endpoint = f"report/meetings/{meeting_id}/polls"
        tbl = self._get_request(endpoint=endpoint, data_key=None)
        logger.info(f"Retrieved {tbl.num_rows} poll reports for meeting ID {meeting_id}")
        return tbl

    def get_meeting_poll_results(self, meeting_id: int):
        raise AttributeError(
            "Method get_meeting_poll_results is deprecated in favor of get_meeting_poll_reports"
        )

    def get_webinar_poll_reports(self, webinar_id: int) -> Table:
        """
        Get results for all polls for a given past webinar ID

        Args:
            webinar_id: str
                Unique identifier for Zoom webinar

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        endpoint = f"report/webinars/{webinar_id}/polls"
        tbl = self._get_request(endpoint=endpoint, data_key=None)
        logger.info(f"Retrieved {tbl.num_rows} poll reports for webinar ID {webinar_id}")
        return tbl

    def get_webinar_poll_results(self, webinar_id: int):
        raise AttributeError(
            "Method get_webinar_poll_results is deprecated in favor of get_webinar_poll_reports"
        )


class Zoom:
    def __new__(
        cls,
        account_id: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        parsons_version: Literal["v1", "v2"] | None = None,
    ) -> ZoomV1:
        """
        Create and return Zoom instance base on chosen version (1 or 2)

        API Documentation: https://developers.zoom.us/docs/api/

        Args:
            account_id: str
                A valid Zoom account id. Not required if ``ZOOM_ACCOUNT_ID`` env
                variable set.
            client_id: str
                A valid Zoom client id. Not required if ``ZOOM_CLIENT_ID`` env
                variable set.
            client_secret: str
                A valid Zoom client secret. Not required if `ZOOM_CLIENT_SECRET` env
                variable set.
            parsons_version (str, optional): Parsons version of the Zoom connector. Defaults to v1.

        """
        if not parsons_version:
            parsons_version = check_env.check("ZOOM_PARSONS_VERSION", None, optional=True)
        if not parsons_version or parsons_version == "v1":
            logger.info("Consider upgrading to version 2 of the Zoom connector!")
            logger.info(
                "See docs for more information: https://move-coop.github.io/parsons/html/latest/zoom.html"
            )
            return ZoomV1(account_id=account_id, client_id=client_id, client_secret=client_secret)
        if parsons_version == "v2":
            return ZoomV2(account_id=account_id, client_id=client_id, client_secret=client_secret)
        raise ValueError(f"{parsons_version} not supported")
