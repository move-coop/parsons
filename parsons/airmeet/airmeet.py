from http import HTTPStatus
from typing import Literal

from parsons.etl.table import Table
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector, _JsonType

AIRMEET_DEFAULT_URI = "https://api-gateway.airmeet.com/prod/"


class Airmeet:
    """Parsons connector for interacting with Airmeet endpoints."""

    def __init__(
        self,
        airmeet_uri: str | None = None,
        airmeet_access_key: str | None = None,
        airmeet_secret_key: str | None = None,
    ) -> None:
        """
        Instantiate the Airmeet class.

        .. admonition:: Generating Access Key and Secret Key

            See `Airmeet's Event Details API documentation
            <https://help.airmeet.com/support/solutions/articles/82000909768-1-event-details-airmeet-public-api>`__.

        Args:
            airmeet_uri:
                The URI of the Airmeet API endpoint.
                Default is ``https://api-gateway.airmeet.com/prod/``.
                You can set an ``AIRMEET_URI`` env variable
                or use this parameter when instantiating the class.
            airmeet_access_key: The Airmeet API access key.
            airmeet_secret_key: The Airmeet API secret key.

        """
        self.uri = check_env.check("AIRMEET_URI", airmeet_uri, optional=True) or AIRMEET_DEFAULT_URI
        self.client = APIConnector(self.uri)
        self.airmeet_client_key = check_env.check("AIRMEET_ACCESS_KEY", airmeet_access_key)
        self.airmeet_client_secret = check_env.check("AIRMEET_SECRET_KEY", airmeet_secret_key)
        self.client.headers = {
            "X-Airmeet-Access-Key": self.airmeet_client_key,
            "X-Airmeet-Secret-Key": self.airmeet_client_secret,
        }
        response = self.client.post_request(url="auth", success_codes=[200])
        self.token = response["token"]

        # API calls expect the token in the header.
        self.client.headers = {
            "Content-Type": "application/json",
            "X-Airmeet-Access-Token": self.token,
        }

    def _get_all_pages(self, url: str, page_size: int = 50, **kwargs) -> Table:
        """
        Get all the results from an Airmeet API url.

        Handles pagination based on the returned ``pageCount``.

        Args:
            url: The API endpoint URL for the request.
            page_size:
                The number of items to get per page.
                The max allowed varies by API call.
                For details, see `Airmeet's Event Details API documentation
                <https://help.airmeet.com/support/solutions/articles/82000909768-1-event-details-airmeet-public-api>`_.
            `**kwargs`: Additional parameters to include in the request.

        """
        kwargs["size"] = page_size

        # Initial API call to get the first page of data
        response: dict[str, _JsonType] = self.client.get_request(url=url, params=kwargs)

        # Some APIs are asynchronous and will return a 202 if the request
        # should be tried again after five minutes, because the results
        # set needs to be built.
        if "statusCode" in response and response["statusCode"] != HTTPStatus.OK:
            raise Exception(response)

        results: list[_JsonType] = response["data"]
        if "cursors" in response and response["cursors"]["pageCount"] > 1:
            cursor_after = response["cursors"]["after"]  # For getting the next set of results

            # Fetch subsequent pages if needed
            for _ in range(2, response["cursors"]["pageCount"] + 1):
                kwargs["after"] = cursor_after
                response = self.client.get_request(url=url, params=kwargs)
                results.extend(response["data"])
                cursor_after = response["cursors"]["after"]

        return Table(results)

    def list_airmeets(self) -> Table:
        """
        Get the list of Airmeets.

        The API excludes any Airmeets that are Archived (Deleted).

        """
        return self._get_all_pages(url="airmeets", page_size=500)

    def fetch_airmeet_participants(
        self,
        airmeet_id: str,
        sorting_key: Literal["name", "email", "registrationDate"] = "registrationDate",
        sorting_direction: Literal["ASC", "DESC"] = "DESC",
    ) -> Table:
        """
        Get all participants (registrations) for a specific Airmeet.

        Handles pagination based on the returned ``totalUserCount``.
        This API doesn't use cursors for paging, so we can't use :meth:`_get_all_pages` here.

        Args:
            airmeet_id: The id of the Airmeet.
            sorting_key: The key to sort the participants by.
            sorting_direction: Can be either 'ASC' or 'DESC' (the default).

        Returns:
            Participants for the Airmeet event

        """
        participants = []  # List to hold all participants
        page_size = 1000  # Maximum number of results per page

        # Initial API call to get the total user count and first page of data
        response = self.client.get_request(
            url=f"airmeet/{airmeet_id}/participants",
            params={
                "pageNumber": 1,
                "resultSize": page_size,
                "sortingKey": sorting_key,
                "sortingDirection": sorting_direction,
            },
        )
        participants.extend(response["participants"])

        # Calculate total pages needed based on totalUserCount.
        total_count = response["totalUserCount"]
        total_pages = (total_count + page_size - 1) // page_size  # This rounds up the division.

        # Fetch subsequent pages if needed.
        for page in range(2, total_pages + 1):
            response = self.client.get_request(
                url=f"airmeet/{airmeet_id}/participants",
                params={
                    "pageNumber": page,
                    "resultSize": page_size,
                    "sortingKey": sorting_key,
                    "sortingDirection": sorting_direction,
                },
            )
            participants.extend(response["participants"])

        return Table(participants)

    def fetch_airmeet_sessions(self, airmeet_id: str) -> Table:
        """
        Get the list of sessions for an Airmeet.

        Args:
            airmeet_id: The id of the Airmeet.

        Returns:
            Sessions for this Airmeet event

        """
        response = self.client.get_request(url=f"airmeet/{airmeet_id}/info")

        return Table(response["sessions"])

    def fetch_airmeet_info(
        self, airmeet_id: str, lists_to_tables: bool = False
    ) -> dict[str, _JsonType | Table]:
        """
        Get the data for an Airmeet (event).

        Includes the list of sessions, session hosts/cohosts, and various other info.

        Args:
            airmeet_id: The id of the Airmeet.
            lists_to_tables: If True, will convert any dictionary values that are lists to Tables.

        """
        request_url = f"airmeet/{airmeet_id}/info"
        response: dict[str, _JsonType | Table] = self.client.get_request(url=request_url)
        if lists_to_tables:
            for k in response:
                if isinstance(response[k], list):
                    response[k] = Table(response[k])

        return response

    def fetch_airmeet_custom_registration_fields(self, airmeet_id: str) -> Table:
        """
        Get the list of custom registration fields for an Airmeet.

        Args:
            airmeet_id: The id of the Airmeet.

        Returns:
            Custom registration fields for this Airmeet event

        """
        response = self.client.get_request(url=f"airmeet/{airmeet_id}/custom-fields")

        return Table(response["customFields"])

    def fetch_event_attendance(self, airmeet_id: str) -> Table:
        """
        Get all attendees for an Airmeet.

        Handles pagination based on the returned ``pageCount``.
        Results include attendance only from sessions with a status of
        ``FINISHED``. Maximum number of results per page = 50.

        .. admonition:: Asynchronous API

            If you get a 202 code in response, please try again after 5 minutes.

        Args:
            airmeet_id: The id of the Airmeet.

        Returns:
            Attendees for this Airmeet event

        """
        return self._get_all_pages(url=f"airmeet/{airmeet_id}/attendees", page_size=50)

    def fetch_session_attendance(self, session_id: str) -> Table:
        """
        Get all attendees for a specific Airmeet session.

        Handles pagination based on the returned ``pageCount``.
        Results are available only for sessions with a status of ``FINISHED``.
        Maximum number of results per page = 50.

        .. admonition:: Asynchronous API

            If you get a 202 code in response, please try again after 5 minutes.

        Args:
            session_id: The id of the session.

        Returns:
            Attendees for this session

        """
        return self._get_all_pages(url=f"session/{session_id}/attendees", page_size=50)

    def fetch_airmeet_booths(self, airmeet_id: str) -> Table:
        """
        Get the list of booths for a specific Airmeet by ID.

        .. warning::

            This method is untested and may not work as expected.
            Booths are available only in certain Airmeet plans.

        Args:
            airmeet_id: The id of the Airmeet.

        Returns:
            Booths for this Airmeet.
            If no data in response, returns an empty Table.

        """
        response = self.client.get_request(url=f"airmeet/{airmeet_id}/booths")

        return Table(response["booths"] or [])

    def fetch_booth_attendance(self, airmeet_id: str, booth_id: str) -> Table:
        """
        Get all attendees for a specific Airmeet booth.

        Handles pagination based on the returned ``pageCount``.
        Results are available only for events with a status of ``FINISHED``.
        Maximum number of results per page = 50.

        .. admonition:: Asynchronous API

            If you get a 202 code in response, please try again after 5 minutes.

        .. warning::

            This method is untested and may not work as expected.
            Booths are available only in certain Airmeet plans.

        Args:
            airmeet_id: The id of the Airmeet.
            booth_id: The id of the booth.

        Returns:
            Attendees for this booth

        """
        request_url = f"airmeet/{airmeet_id}/booth/{booth_id}/booth-attendance"

        return self._get_all_pages(url=request_url, page_size=50)

    def fetch_poll_responses(self, airmeet_id: str) -> Table:
        """
        Get a list of the poll responses in an Airmeet.

        Handles pagination based on the returned ``pageCount``.
        Maximum number of results per page = 50.

        Args:
            airmeet_id: The id of the Airmeet.

        Returns:
            Users who responded to the poll.
            For each user, the value for the ``polls``
            key is a list of poll questions and answers for that user.

        """
        return self._get_all_pages(url=f"airmeet/{airmeet_id}/polls", page_size=50)

    def fetch_questions_asked(self, airmeet_id: str) -> Table:
        """
        Get a list of the questions asked in an Airmeet.

        Args:
            airmeet_id: The id of the Airmeet.

        Returns:
            Users who responded to the poll.
            For each user, the value for the ``questions``
            key is a list of the questions that the user was asked.

        """
        response = self.client.get_request(url=f"airmeet/{airmeet_id}/questions")

        return Table(response["data"])

    def fetch_event_tracks(self, airmeet_id: str) -> Table:
        """
        Get a list of the tracks in a specific Airmeet by ID.

        .. warning::

            This method is untested and may not work as expected.
            Event tracks are available only in certain Airmeet plans.

        Args:
            airmeet_id: The id of the Airmeet.

        Returns:
            All matching event tracks

        """
        response = self.client.get_request(url=f"airmeet/{airmeet_id}/tracks")

        return Table(response["tracks"])

    def fetch_registration_utms(self, airmeet_id: str) -> Table:
        """
        Get all the UTM parameters captured during registration.

        Handles pagination based on the returned ``pageCount``.
        Maximum number of results per page = ?? (documentation doesn't say,
        but assume 50 like the other asynchronous APIs).

        .. admonition:: Asynchronous API

            If you get a 202 code in response, please try again after 5 minutes.

        Args:
            airmeet_id: The id of the Airmeet.

        Returns:
            UTM parameters captured during registration.

        """
        return self._get_all_pages(url=f"airmeet/{airmeet_id}/utms", page_size=50)

    def download_session_recordings(self, airmeet_id: str, session_id: str | None = None) -> Table:
        """
        Get a list of recordings for a specific Airmeet.

        Can limit results to recordings of a specific session in that Airmeet.
        The data for each recording includes a download link which is valid for 6 hours.

        .. warning::

            The API returns ``recordingsCount`` and ``totalCount``, which implies
            that the results could be paged like in :meth:`fetch_airmeet_participants`.
            The API docs don't specify if that's the case, but this method will
            need to be updated if it is.

        Args:
            airmeet_id: The id of the Airmeet.
            session_id:
                The id of the session. If provided,
                limits results to only the recording of the specified session.

        Returns:
            Session recordings

        """
        params = {}
        if session_id:
            params["sessionIds"] = session_id

        response = self.client.get_request(
            url=f"airmeet/{airmeet_id}/session-recordings", params=params
        )

        return Table(response["recordings"])

    def fetch_event_replay_attendance(
        self, airmeet_id: str, session_id: str | None = None
    ) -> Table:
        """
        Get all replay attendees for a specific Airmeet.

        Can limit results to replay attendees of a specific session in that Airmeet.
        Handles pagination based on the returned ``pageCount``.
        Results are available only for events with a status of ``FINISHED``.
        Maximum number of results per page = 50.

        .. admonition:: Asynchronous API

            If you get a 202 code in response, please try again after 5 minutes.

        Args:
            airmeet_id: The id of the Airmeet.
            session_id: Limits results to only attendees of the specified session.

        Returns:
            Event replay attendees

        """
        attendees = self._get_all_pages(
            url=f"airmeet/{airmeet_id}/event-replay-attendees", page_size=50
        )
        if session_id is not None:
            attendees = attendees.select_rows("{session_id} == '" + session_id + "'")

        return attendees
