from requests import request
import time
from parsons.etl import Table
from parsons.utilities import check_env
import logging

logger = logging.getLogger(__name__)

CT_URI = "https://api.crowdtangle.com/"
PAGE_SIZE = 100
REQUEST_SLEEP = 10  # CT has a rather agressive 6 requests per minute rate limit.


class CrowdTangle(object):
    """
    Instantiate CrowdTangle Class

    `Args:`
        api_key: str
            A valid CrowdTangle API key. Not required if ``CROWDTANGLE_API_KEY`` env
            variable set.
    `Returns:`
        CrowdTangle Class
    """

    def __init__(self, api_key=None):

        self.api_key = check_env.check("CT_API_KEY", api_key)
        self.uri = CT_URI

    def _base_request(self, endpoint, req_type="GET", args=None):

        url = f"{self.uri}/{endpoint}"
        base_args = {"token": self.api_key, "count": PAGE_SIZE}

        # Add any args passed through to the base args
        if args is not None:
            base_args.update(args)

        r = request(req_type, url, params=base_args).json()
        json = r["result"]
        keys = list(json.keys())
        data = json[keys[0]]

        while "nextPage" in list(json["pagination"].keys()):
            logger.info(f"Retrieving {PAGE_SIZE} rows.")
            time.sleep(REQUEST_SLEEP)
            next_url = json["pagination"]["nextPage"]
            r = request(req_type, next_url).json()
            json = r["result"]
            data.extend(json[keys[0]])

        logger.info(f"Retrieved {len(data)} rows.")

        return data

    def _base_unpack(self, ParsonsTable):

        logger.debug("Working to unpack the Parsons Table...")
        logger.debug(f"Starting with {len(ParsonsTable.columns)} columns...")
        sample = ParsonsTable[0]

        col_dict = {}
        for x in ParsonsTable.columns:
            col_dict[x] = str(type(sample[x]))

        for col in col_dict:
            if col_dict[col] == "<class 'dict'>":
                ParsonsTable.unpack_dict(col)
            elif col_dict[x] == "<class 'list'>":
                ParsonsTable.unpack_list(col)

        logger.info(f"There are now {len(ParsonsTable.columns)} columns...")
        return ParsonsTable

    def _unpack(self, ParsonsTable):

        if ParsonsTable.num_rows == 0:
            return None

        first_count = len(ParsonsTable.columns)
        second_count = first_count + 1

        while second_count > first_count:
            first_count = len(ParsonsTable.columns)
            self._base_unpack(ParsonsTable)
            second_count = len(ParsonsTable.columns)

        return ParsonsTable

    def _list_to_string(self, list_arg):

        if list_arg:
            return ",".join(list_arg)
        else:
            return None

    def get_posts(
        self,
        start_date=None,
        end_date=None,
        language=None,
        list_ids=None,
        min_interations=None,
        search_term=None,
        types=None,
    ):
        """
        Return a set of posts for the given parameters.

        See the `API documentation <https://github.com/CrowdTangle/API/wiki/Posts>`_
        for more information.

        .. warning::
          Rate limit is 2 calls / minute.

        `Args:`
            start_date: str
                Filter to the earliest date at which a post could be posted.
                The time is formatted as UTC (e.g. ``yyyy-mm-ddThh:mm:ss`` or ``yyyy-mm-dd``).
            end_date: str
                Filter to the latest date at which a post could be posted.
                The time is formatted as UTC (e.g. ``yyyy-mm-ddThh:mm:ss`` or ``yyyy-mm-dd``).
            language: str
                Filter to 2-character Locale code. Some languages require more
                than two characters: Chinese (Simplified) is zh-CN and
                Chinese (Traditional) is zh-TW.
            list_ids: list
                Filter to the ids of lists or saved searches to retrieve.
            min_interactions: int
                Filter to posts with total interactions above this threshold.
            search_team: str
                Returns only posts that match this search term. For multiple terms, separate
                with commas for OR, use quotes for phrases.
            types: list
                Filter to post types including:
                * ``episode``
                * ``extra_clip``
                * ``link``
                * ``live_video``
                * ``live_video_complete``
                * ``live_video_scheduled``
                * ``native_video``
                * ``photo``
                * ``status``
                * ``trailer``
                * ``tweet``
                * ``vimeo``
                * ``vine``
                * ``youtube``

                If you want all live videos (whether currently or formerly live),
                pass include both ``live_video`` and ``live_video_complete``
                parameters.

                The ``video`` type does not mean all videos, it refers to videos
                that are not ``native_video``, ``youtube`` or ``vine``.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        args = {
            "startDate": start_date,
            "endDate": end_date,
            "language": language,
            "listIds": self._list_to_string(list_ids),
            "minInteractions": min_interations,
            "searchTerm": search_term,
            "types": types,
        }

        logger.info("Retrieving posts.")
        pt = Table(self._base_request("posts", args=args))
        logger.info(f"Retrieved {pt.num_rows} posts.")
        self._unpack(pt)
        return pt

    def get_leaderboard(self, start_date=None, end_date=None, list_ids=None, account_ids=None):
        """
        Return leaderboard data.

        See the `API documentation <https://github.com/CrowdTangle/API/wiki/Leaderboard>`_
        for more information.

        .. warning::
          Rate limit is 6 calls / minute.

        `Args:`
            start_date: str
                Filter to the earliest date at which a post could be posted.
                The time is formatted as UTC (e.g. ``yyyy-mm-ddThh:mm:ss`` or ``yyyy-mm-dd``).
            end_date: str
                Filter to the latest date at which a post could be posted.
                The time is formatted as UTC (e.g. ``yyyy-mm-ddThh:mm:ss`` or ``yyyy-mm-dd``).
            list_ids: list
                Filter to the ids of lists or saved searches to retrieve.
            account_ids: list
                A list of CrowdTangle accountIds to retrieve leaderboard data for.
                This and ``list_id`` are mutually exclusive; if both are sent, the
                ``account_ids`` value will be used.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        args = {
            "startDate": start_date,
            "endDate": end_date,
            "listIds": self._list_to_string(list_ids),
            "accountIds": self._list_to_string(account_ids),
        }

        pt = Table(self._base_request("leaderboard", args=args))
        logger.info(f"Retrieved {pt.num_rows} records from the leaderbooard.")
        self._unpack(pt)
        return pt

    def get_links(self, link, start_date=None, end_date=None, include_summary=None, platforms=None):
        """
        Return up to 100 posts based on a specific link. It is strongly recommended to
        use the ``start_date`` parameter to limit queries to relevant dates.

        See the `API documentation <https://github.com/CrowdTangle/API/wiki/Links>`_
        for more information.

        .. warning::
          Rate limit is 2 calls / minute.

        `Args:`
            link: str
                The link to filter posts to.
            start_date: str
                Filter to the earliest date at which a post could be posted.
                The time is formatted as UTC (e.g. ``yyyy-mm-ddThh:mm:ss`` or ``yyyy-mm-dd``).
            end_date: str
                Filter to the latest date at which a post could be posted.
                The time is formatted as UTC (e.g. ``yyyy-mm-ddThh:mm:ss`` or ``yyyy-mm-dd``).
            include_summary: boolean
                Adds a ``summary`` column with account statistics for each platform
                that has posted this link. It will look beyond the count
                requested to summarize across the time searched.
                Requires a value for ``start_date``.
            platforms: list
                Filter by platforms

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        args = {
            "link": link,
            "startDate": start_date,
            "endDate": end_date,
            "includeSummary": str(include_summary),
            "platforms": self._list_to_string(platforms),
        }

        logger.info("Retrieving posts based on link.")
        pt = Table(self._base_request("links", args=args))
        logger.info(f"Retrieved {pt.num_rows} links.")
        self._unpack(pt)
        return pt
