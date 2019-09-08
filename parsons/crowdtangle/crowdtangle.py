from requests import request
import time
from parsons import Table
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

        self.api_key = check_env.check('CT_API_KEY', api_key)
        self.uri = CT_URI

    def base_request(self, endpoint, req_type='GET', args=None):
        # Internal Request Method

        url = f'{self.uri}/{endpoint}'
        base_args = {'token': self.api_key,
                     'count': PAGE_SIZE}

        # Add any args passed through to the base args
        if args is not None:
            base_args.update(args)

        r = request(req_type, url, params=base_args).json()
        json = r['result']
        keys = list(json.keys())
        data = json[keys[0]]

        while 'nextPage' in list(json['pagination'].keys()):
            logger.info(f"Retrieving {PAGE_SIZE} rows.")
            time.sleep(REQUEST_SLEEP)
            next_url = json['pagination']['nextPage']
            r = request(req_type, next_url).json()
            json = r['result']
            data.extend(json[keys[0]])

        logger.info(f"Retrieved {len(data)} rows.")

        return data

    def base_unpack(self, ParsonsTable):
        # Unpack base request

        logger.debug("Working to unpack the Parsons Table...")
        logger.debug(f'Starting with {len(ParsonsTable.columns)} columns...')
        sample = ParsonsTable[0]

        col_dict = {}
        for x in ParsonsTable.columns:
            col_dict[x] = str(type(sample[x]))

        for col in col_dict:
            if col_dict[col] == "<class 'dict'>":
                ParsonsTable.unpack_dict(col)
            elif col_dict[x] == "<class 'list'>":
                ParsonsTable.unpack_list(col)

        logger.info(f'There are now {len(ParsonsTable.columns)} columns...')
        return ParsonsTable

    def unpack(self, ParsonsTable):

        if ParsonsTable.num_rows == 0:
            return None

        first_count = len(ParsonsTable.columns)
        second_count = first_count + 1

        while second_count > first_count:
            first_count = len(ParsonsTable.columns)
            self.base_unpack(ParsonsTable)
            second_count = len(ParsonsTable.columns)

        return ParsonsTable

    def get_posts(self, start_date=None, end_date=None, language=None, list_ids=None,
                  min_interations=None, search_term=None, types=None):

        """
        Return advocates (person records).

        `Args:`
            start_date: Format is “yyyy-mm-ddThh:mm:ss”
                The earliest date at which a post could be posted. Time zone is UTC.
            end_date: Format is “yyyy-mm-ddThh:mm:ss”
              The latest date at which a post could be posted. Time zone is UTC.
            language: str
                2-character Locale code
                Exceptions: Some languages require more than two characters: Chinese
                (Simplified) is zh-CN and Chinese (Traditional) is zh-TW.
            list_ids: comma separated
                The IDs of lists or saved searches to retrieve.
                These can be separated by commas to include multiple lists.
            min_interactions: int
                If set, will exclude posts with total interactions below this threshold.
            search_team: str
                Returns only posts that match this search term. For multiple terms, separate
                with commas for OR, use quotes for phrases.
            types: str
                episode, extra_clip, link, live_video, live_video_complete,
                live_video_scheduled, native_video, photo, status, trailer,
                tweet, video, vine, youtube	The types of post to include.
                These can be separated by commas to include multiple types.
                If you want all live videos (whether currently or formerly live),
                be sure to include both live_video and live_video_complete.
                The "video" type does not mean all videos, it refers to videos
                that aren't native_video, youtube or vine (e.g. a video on Vimeo).

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        args = {'startDate': start_date,
                'endDate': end_date,
                'language': language,
                'listIds': list_ids,
                'minInteractions': min_interations,
                'searchTerm': search_term,
                'types': types}

        logger.info("Retrieving posts.")
        pt = Table(self.base_request('posts', args=args))
        logger.info(f'Retrieved {pt.num_rows} posts.')
        self.unpack(pt)
        return pt

    def get_leaderboard(self, start_date=None, end_date=None, list_ids=None, account_ids=None):

        """
        Return advocates (person records).

        `Args:`
            start_date: Format is “yyyy-mm-ddThh:mm:ss”
                The earliest date at which a post could be posted. Time zone is UTC.
            end_date: Format is “yyyy-mm-ddThh:mm:ss”
              The latest date at which a post could be posted. Time zone is UTC.
            list_ids: comma separated
                The IDs of lists or saved searches to retrieve.
                These can be separated by commas to include multiple lists.
            account_ids: comma separated
                A list of CrowdTangle accountIds to retrieve leaderboard data for.
                These should be provided comma-separated. This and listId are mutually
                exclusive; if both are sent, accountIds will be preferred.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        args = {'startDate': start_date,
                'endDate': end_date,
                'listIds': list_ids,
                'accountIds': account_ids}

        pt = Table(self.base_request('leaderboard', args=args))
        logger.info(f'Retrieved {pt.num_rows} records from the leaderbooard.')
        self.unpack(pt)
        return pt

    def get_links(self, link, start_date=None, end_date=None, include_summary=None,
                  platforms=None):

        """
        Return posts based on a specific link.

        `Args:`
            link: string
                The link to query by
            start_date: Format is “yyyy-mm-ddThh:mm:ss”
                The earliest date at which a post could be posted. Time zone is UTC.
            end_date: Format is “yyyy-mm-ddThh:mm:ss”
              The latest date at which a post could be posted. Time zone is UTC.
            include_summary: 'true','false'
                Adds a "summary" section with AccountStatistics for each platform
                that has posted this link. It will look beyond the count
                requested to summarize across the time searched.
                Requires a value for startDate.
            platforms: comma separated
                The platforms from which to retrieve links. This value can be comma-separated.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        args = {'link': link,
                'startDate': start_date,
                'endDate': end_date,
                'includeSummary': include_summary,
                'platforms': platforms}

        logger.info("Retrieving posts based on link")
        pt = Table(self.base_request('links', args=args))
        logger.info(f'Retrieved {pt.num_rows} links.')
        self.unpack(pt)
        return pt
