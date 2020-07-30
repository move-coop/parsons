import logging

import boxsdk

from parsons.etl.table import Table
from parsons.utilities.check_env import check as check_env

logger = logging.getLogger(__name__)


class Box(object):
    """
    Box is a file storage provider.
    `Args:`
        client_id: str
            Box client (account) id -- probably a 16-char alphanumeric.
            Not required if ``BOX_CLIENT_ID`` env variable is set.
        client_secret: str
            Box private key -- probably a 32-char alphanumeric.
            Not required if ``BOX_CLIENT_SECRET`` env variable is set.
        access_token: str
            Box developer access token -- probably a 32-char alphanumeric.
            Note that this is only valid for developer use only, and should not
            be used when creating and maintaining access for typical users.
            Not required if ''BOX_ACCESS_TOKEN'' env variable is set.
    `Returns:`
        Box class
    """

    def __init__(self, client_id=None, client_secret=None, access_token=None):
        client_id = check_env('BOX_CLIENT_ID', client_id)
        client_secret = check_env('BOX_CLIENT_SECRET', client_secret)
        access_token = check_env('BOX_ACCESS_TOKEN', access_token)

        oauth = boxsdk.OAuth2(
            client_id=client_id,
            client_secret=client_secret,
            access_token = access_token
        )
        self.client = boxsdk.Client(oauth)

    def get_file(self, file_name=None):