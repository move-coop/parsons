import requests
from requests.auth import HTTPBasicAuth
from parsons.etl import Table
from parsons.utilities import check_env
import logging

logger = logging.getLogger(__name__)

PHONE2ACTION_URI = 'https://api.phone2action.com/2.0/'


class Phone2Action(object):
    """
    Instantiate Phone2Action Class

    `Args:`
        app_id: str
            The Phone2Action provided application id. Not required if ``PHONE2ACTION_APP_ID``
            env variable set.
        app_key: str
            The Phone2Action provided application key. Not required if ``PHONE2ACTION_APP_KEY``
            env variable set.
    `Returns:`
        Phone2Action Class
    """

    def __init__(self, app_id=None, app_key=None):

        self.app_id = check_env.check('PHONE2ACTION_APP_ID', app_id)
        self.app_key = check_env.check('PHONE2ACTION_APP_KEY', app_key)
        self.auth = HTTPBasicAuth(self.app_id, self.app_key)
        self.uri = PHONE2ACTION_URI

    def _request(self, url, args=None):
        # Internal request method

        r = requests.get(url, auth=self.auth, params=args)
        r.raise_for_status()
        return r

    def _paginate_request(self, url, args=None, page=None):
        # Internal pagination method

        if page is not None:
            args['page'] = page

        r = self._request(url, args=args)

        json = r.json()['data']

        if page is not None:
            return json

        # If count of items is less than the total allowed per page, paginate
        while r.json()['pagination']['count'] == r.json()['pagination']['per_page']:

            r = self._request(r.json()['pagination']['next_url'], args)
            json.extend(r.json()['data'])

        return json

    def get_advocates(self, state=None, campaign_id=None, updated_since=None, page=None):
        """
        Return advocates (person records).

        If no page is specified, the method will automatically paginate through the available
        advocates.

        `Args:`
            state: str
                Filter by US postal abbreviation for a state
                or territory e.g., "CA" "NY" or "DC"
            campaign_id: int
                Filter to specific campaign
            updated_since: str
                Fetch all advocates updated since UTC date time provided
                using (ex. '2014-01-05 23:59:43')
            page: int
                Page number of data to fetch; if this is specified, call will only return one
                page.
        `Returns:`
            A dict of parsons tables:
                * emails
                * phones
                * memberships
                * tags
                * ids
                * fields
                * advocates
        """

        url = self.uri + 'advocates'

        args = {'state': state,
                'campaignid': campaign_id,
                'updatedSince': updated_since}

        logger.info('Retrieving advocates...')
        json = self._paginate_request(url, args=args, page=page)

        return self._advocates_tables(Table(json))

    def _advocates_tables(self, tbl):
        # Convert the advocates nested table into multiple tables

        tbls = {
            'advocates': tbl,
            'emails': Table(),
            'phones': Table(),
            'memberships': Table(),
            'tags': Table(),
            'ids': Table(),
            'fields': Table(),
        }

        if not tbl:
            return tbls

        logger.info(f'Retrieved {tbl.num_rows} advocates...')

        # Unpack all of the single objects
        # The Phone2Action API docs says that created_at and updated_at are dictionaries, but
        # the data returned from the server is a ISO8601 timestamp. - EHS, 05/21/2020
        for c in ['address', 'districts']:
            tbl.unpack_dict(c)

        # Unpack all of the arrays
        child_tables = [child for child in tbls.keys() if child != 'advocates']
        for c in child_tables:
            tbls[c] = tbl.long_table(['id'], c, key_rename={'id': 'advocate_id'})

        return tbls

    def get_campaigns(self, state=None, zip=None, include_generic=False, include_private=False,
                      include_content=True):
        """
        Returns a list of campaigns

        `Args:`
            state: str
                Filter by US postal abbreviation for a state or territory e.g., "CA" "NY" or "DC"
            zip: int
                Filter by 5 digit zip code
            include_generic: boolean
                When filtering by state or ZIP code, include unrestricted campaigns
            include_private: boolean
                If true, will include private campaigns in results
            include_content: boolean
                If true, include campaign content fields, which may vary. This may cause
                sync errors.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """
        url = self.uri + 'campaigns'

        args = {'state': state,
                'zip': zip,
                'includeGeneric': str(include_generic),
                'includePrivate': str(include_private)
                }

        tbl = Table(self._request(url, args=args).json())
        tbl.unpack_dict('updated_at')
        if include_content:
            tbl.unpack_dict('content')

        return tbl
