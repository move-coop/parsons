from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector
from parsons import Table
import logging
import jwt
import datetime

logger = logging.getLogger(__name__)

ZOOM_URI = 'https://api.zoom.us/v2/'


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

    def __init__(self, api_key=None, api_secret=None):

        self.api_key = check_env.check('ZOOM_API_KEY', api_key)
        self.api_secret = check_env.check('ZOOM_API_SECRET', api_secret)
        self.client = APIConnector(ZOOM_URI)

    def refresh_header_token(self):
        # Generate a token that is valid for 30 seconds and update header. Full documentation
        # on JWT generation using Zoom API: https://marketplace.zoom.us/docs/guides/auth/jwt

        payload = {"iss": self.api_key, "exp": int(datetime.datetime.now().timestamp() + 30)}
        token = jwt.encode(payload, self.api_secret, algorithm='HS256')
        self.client.headers = {'authorization': f"Bearer {token}",
                               'content-type': "application/json"}

    def _get_request(self, endpoint, data_key, params=None, **kwargs):
        # To Do: Consider increasing default page size.

        self.refresh_header_token()
        r = self.client.get_request(endpoint, params=params, **kwargs)
        self.client.data_key = data_key
        data = self.client.data_parse(r)

        if not params:
            params = {}

        # Return a dict or table if only one item.
        if 'page_number' not in r.keys():
            if isinstance(data, dict):
                return data
            if isinstance(data, list):
                return Table(data)

        # Else iterate through the pages and return a Table
        else:
            while r['page_number'] < r['page_count']:
                params['page_number'] = int(r['page_number']) + 1
                r = self.client.get_request(endpoint, params=params, **kwargs)
                data.extend(self.client.data_parse(r))
            return Table(data)

    def get_users(self, status='active', role_id=None):
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

        if status not in ['active', 'inactive', 'pending']:
            raise ValueError('Invalid status type provided.')

        params = {'status': status,
                  'role_id': role_id}

        tbl = self._get_request('users', 'users', params=params)
        logger.info(f'Retrieved {tbl.num_rows} users.')
        return tbl

    def get_meetings(self, user_id, meeting_type='scheduled'):
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

        tbl = self._get_request(f'users/{user_id}/meetings', 'meetings')
        logger.info(f'Retrieved {tbl.num_rows} meetings.')
        return tbl

    def get_past_meeting(self, meeting_uuid):
        """
        Get metadata regarding a past meeting.

        `Args:`
            meeting_id: str
                The meeting id
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = self._get_request(f'past_meetings/{meeting_uuid}', None)
        logger.info(f'Retrieved meeting {meeting_uuid}.')
        return tbl

    def get_past_meeting_participants(self, meeting_id):
        """
        Get past meeting participants.

        `Args:`
            meeting_id: str
                The meeting id
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = self._get_request(f'report/meetings/{meeting_id}/participants', 'participants')
        logger.info(f'Retrieved {tbl.num_rows} participants.')
        return tbl

    def get_meeting_registrants(self, meeting_id):
        """
        Get meeting registrants.

        `Args:`
            meeting_id: str
                The meeting id
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = self._get_request(f'meetings/{meeting_id}/registrants', 'registrants')
        logger.info(f'Retrieved {tbl.num_rows} registrants.')
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

        tbl = self._get_request(f'users/{user_id}/webinars', 'webinars')
        logger.info(f'Retrieved {tbl.num_rows} webinars.')
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

        tbl = self._get_request(f'report/webinars/{webinar_id}/participants', 'participants')
        logger.info(f'Retrieved {tbl.num_rows} webinar participants.')
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

        tbl = self._get_request(f'webinars/{webinar_id}/registrants', 'registrants')
        logger.info(f'Retrieved {tbl.num_rows} webinar registrants.')
        return tbl
