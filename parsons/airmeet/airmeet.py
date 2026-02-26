from typing import Literal

from parsons.etl.table import Table
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector

AIRMEET_DEFAULT_URI = "https://api-gateway.airmeet.com/prod/"


class Airmeet:
    """
    Instantiate class.

    Args:
            airmeet_uri: string
                The URI of the Airmeet API endpoint. Not required. The default
                is https://api-gateway.airmeet.com/prod/. You can set an
                ``AIRMEET_URI`` env variable or use this parameter when
                instantiating the class.
            airmeet_access_key: string
                The Airmeet API access key.
            airmeet_secret_key: string
                The Airmeet API secret key.

        For instructions on how to generate an access key and secret key set,
        see `Airmeet's Event Details API documentation
        <https://help.airmeet.com/support/solutions/articles/82000909768-1-event-details-airmeet-public-api>`_.

    """

    def __init__(self, airmeet_uri=None, airmeet_access_key=None, airmeet_secret_key=None):
        """
        Authenticate with the Airmeet API and update the connection headers
        with the access token.

        Args:
            airmeet_uri: string
                The Airmeet API endpoint.
            airmeet_access_key: string
                The Airmeet API access key.
            airmeet_secret_key: string
                The Airmeet API secret key.

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

    def _get_all_pages(self, url, page_size=50, **kwargs) -> Table:
        """
        Get all the results from an Airmeet API url, handling pagination based
        on the returned pageCount.

        Args:
            page_size: 50
                The number of items to get per page. The max allowed varies by
                API call. For details, see `Airmeet's Event Details API
                documentation
                <https://help.airmeet.com/support/solutions/articles/82000909768-1-event-details-airmeet-public-api>`_.
            `**kwargs`:
                Additional parameters to include in the request.

        """
        results = []
        cursor_after = ""  # For getting the next set of results
        kwargs["size"] = page_size

        # Initial API call to get the first page of data
        response = self.client.get_request(url=url, params=kwargs)

        # Some APIs are asynchronous and will return a 202 if the request
        # should be tried again after five minutes, because the results
        # set needs to be built.
        if "statusCode" in response and response["statusCode"] != 200:
            raise Exception(response)
        else:
            results.extend(response["data"])

            if "cursors" in response and response["cursors"]["pageCount"] > 1:
                cursor_after = response["cursors"]["after"]

                # Fetch subsequent pages if needed
                for _ in range(2, response["cursors"]["pageCount"] + 1):
                    kwargs["after"] = cursor_after
                    response = self.client.get_request(url=url, params=kwargs)
                    results.extend(response["data"])
                    cursor_after = response["cursors"]["after"]

        return Table(results)

    def list_airmeets(self) -> Table:
        """
        Get the list of Airmeets. The API excludes any Airmeets that are
        Archived (Deleted).

        Returns:
            Parsons.Table
                List of Airmeets

        """
        return self._get_all_pages(url="airmeets", page_size=500)

    def fetch_airmeet_participants(
        self,
        airmeet_id,
        sorting_key: Literal["name", "email", "registrationDate"] = "registrationDate",
        sorting_direction: Literal["ASC", "DESC"] = "DESC",
    ) -> Table:
        """
        Get all participants (registrations) for a specific Airmeet, handling
        pagination based on the returned totalUserCount. This API doesn't use
        cursors for paging, so we can't use _get_all_pages() here.

        Args:
            airmeet_id: string
                The id of the Airmeet.
            sorting_key: string
                The key to sort the participants by. Can be 'name', 'email', or
                'registrationDate' (the default).
            sorting_direction: string
                Can be either 'ASC' or 'DESC' (the default).

        Returns:
            Parsons.Table
                List of participants for the Airmeet event

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

    def fetch_airmeet_sessions(self, airmeet_id) -> Table:
        """
        Get the list of sessions for an Airmeet.

        Args:
            airmeet_id: string
                The id of the Airmeet.

        Returns:
            Parsons.Table
                List of sessions for this Airmeet event

        """
        response = self.client.get_request(url=f"airmeet/{airmeet_id}/info")
        return Table(response["sessions"])

    def fetch_airmeet_info(self, airmeet_id, lists_to_tables=False):
        """
        Get the data for an Airmeet (event), which include the list of
        sessions, session hosts/cohosts, and various other info.

        Args:
            airmeet_id: string
                The id of the Airmeet.
            lists_to_tables: bool
                If True, will convert any dictionary values that are lists
                to Tables.

        Returns:
            Dict containing the Airmeet data

        """
        response = self.client.get_request(url=f"airmeet/{airmeet_id}/info")
        if lists_to_tables:
            for k in response:
                if isinstance(response[k], list):
                    response[k] = Table(response[k])
        return response

    def fetch_airmeet_custom_registration_fields(self, airmeet_id) -> Table:
        """
        Get the list of custom registration fields for an Airmeet.

        Args:
            airmeet_id: string
                The id of the Airmeet.

        Returns:
            Parsons.Table
                List of custom registration fields for this Airmeet event

        """
        response = self.client.get_request(url=f"airmeet/{airmeet_id}/custom-fields")
        return Table(response["customFields"])

    def fetch_event_attendance(self, airmeet_id) -> Table:
        """
        Get all attendees for an Airmeet, handling pagination based on the
        returned pageCount.

        Results include attendance only from sessions with a status of
        `FINISHED`. Maximum number of results per page = 50.

        "This is an Asynchronous API. If you get a 202 code in response,
        please try again after 5 minutes."

        Args:
            airmeet_id: string
                The id of the Airmeet.

        Returns:
            Parsons.Table
                List of attendees for this Airmeet event

        """
        return self._get_all_pages(url=f"airmeet/{airmeet_id}/attendees", page_size=50)

    def fetch_session_attendance(self, session_id) -> Table:
        """
        Get all attendees for a specific Airmeet session, handling pagination
        based on the returned pageCount.

        Results are available only for sessions with a status of `FINISHED`.
        Maximum number of results per page = 50.

        "This is an Asynchronous API. If you get a 202 code in response,
        please try again after 5 minutes."

        Args:
            session_id: string
                The id of the session.

        Returns:
            Parsons.Table
                List of attendees for this session

        """
        return self._get_all_pages(url=f"session/{session_id}/attendees", page_size=50)

    def fetch_airmeet_booths(self, airmeet_id) -> Table:
        """
        Get the list of booths for a specific Airmeet by ID.

        `CAUTION: This method is untested. Booths are available only in
        certain Airmeet plans.`

        Args:
            airmeet_id: string
                The id of the Airmeet.

        Returns:
            Parsons.Table
                List of booths for this Airmeet

        """
        response = self.client.get_request(url=f"airmeet/{airmeet_id}/booths")
        return Table(response["booths"] or [])

    def fetch_booth_attendance(self, airmeet_id, booth_id) -> Table:
        """
        Get all attendees for a specific Airmeet booth, handling pagination
        based on the returned pageCount.

        Results are available only for events with a status of `FINISHED`.
        Maximum number of results per page = 50.

        "This is an Asynchronous API. If you get a 202 code in response,
        please try again after 5 minutes."

        `CAUTION: This method is untested. Booths are available only in
        certain Airmeet plans.`

        Args:
            airmeet_id: string
                The id of the Airmeet.
            booth_id: string
                The id of the booth.

        Returns:
            Parsons.Table
                List of attendees for this booth

        """
        return self._get_all_pages(
            url=f"airmeet/{airmeet_id}/booth/{booth_id}/booth-attendance", page_size=50
        )

    def fetch_poll_responses(self, airmeet_id) -> Table:
        """
        Get a list of the poll responses in an Airmeet, handling pagination
        based on the returned pageCount.

        Maximum number of results per page = 50.

        Args:
            airmeet_id: string
                The id of the Airmeet.

        Returns:
            Parsons.Table
                List of users. For each user, the value for the "polls"
                key is a list of poll questions and answers for that user.

        """
        return self._get_all_pages(url=f"airmeet/{airmeet_id}/polls", page_size=50)

    def fetch_questions_asked(self, airmeet_id) -> Table:
        """
        Get a list of the questions asked in an Airmeet.

        Args:
            airmeet_id: string
                The id of the Airmeet.

        Returns:
            Parsons.Table
                List of users. For each user, the value for the "questions"
                key is a list of that user's questions.

        """
        response = self.client.get_request(url=f"airmeet/{airmeet_id}/questions")
        return Table(response["data"])

    def fetch_event_tracks(self, airmeet_id) -> Table:
        """
        Get a list of the tracks in a specific Airmeet by ID.

        `CAUTION: This method is untested. Event tracks are available only in
        certain Airmeet plans.`

        Args:
            airmeet_id: string
                The id of the Airmeet.

        Returns:
            Parsons.Table
                List of event tracks

        """
        response = self.client.get_request(url=f"airmeet/{airmeet_id}/tracks")
        return Table(response["tracks"])

    def fetch_registration_utms(self, airmeet_id) -> Table:
        """
        Get all the UTM parameters captured during registration, handling
        pagination based on the returned pageCount.

        Maximum number of results per page = ?? (documentation doesn't say,
        but assume 50 like the other asynchronous APIs).

        "This is an Asynchronous API. If you get a 202 code in response,
        please try again after 5 minutes."

        Args:
            airmeet_id: string
                The id of the Airmeet.

        Returns:
            Parsons.Table
                List of UTM parameters captured during registration

        """
        return self._get_all_pages(url=f"airmeet/{airmeet_id}/utms", page_size=50)

    def download_session_recordings(self, airmeet_id, session_id=None) -> Table:
        """
        Get a list of recordings for a specific Airmeet (and optionally a
        specific session in that Airmeet). The data for each recording
        includes a download link which is valid for 6 hours.

        The API returns "recordingsCount" and "totalCount", which implies
        that the results could be paged like in fetch_airmeet_participants().
        The API docs don't specify if that's the case, but this method will
        need to be updated if it is.

        Args:
            airmeet_id: string
                The id of the Airmeet.
            session_id: string
                (optional) If provided, limits results to only the recording
                of the specified session.

        Returns:
            Parsons.Table
                List of session recordings

        """
        kwargs = {}
        if session_id:
            kwargs["sessionIds"] = session_id
        response = self.client.get_request(url=f"airmeet/{airmeet_id}/session-recordings", **kwargs)
        return Table(response["recordings"])

    def fetch_event_replay_attendance(self, airmeet_id, session_id=None) -> Table:
        """
        Get all replay attendees for a specific Airmeet (and optionally a
        specific session in that Airmeet), handling pagination based on the
        returned pageCount.

        Results are available only for events with a status of `FINISHED`.
        Maximum number of results per page = 50.

        "This is an Asynchronous API. If you get a 202 code in response,
        please try again after 5 minutes."

        Args:
            airmeet_id: string
                The id of the Airmeet.
            session_id: string
                (optional) If provided, limits results to only attendees of
                the specified session.

        Returns:
            Parsons.Table
                List of event replay attendees

        """
        attendees = self._get_all_pages(
            url=f"airmeet/{airmeet_id}/event-replay-attendees", page_size=50
        )
        if session_id is not None:
            attendees = attendees.select_rows("{session_id} == '" + session_id + "'")
        return attendees
