"""NGPVAN Activist Code Endpoints"""

from parsons.etl.table import Table
import logging
logger = logging.getLogger(__name__)


class ActivistCodes(object):
    """Class for '/activistCodes' end points.

        .. note::
            To apply or remove activist codes, use the :meth:`toggle_activist_code` method.
    """

    def __init__(self, van_connection):
        """Initialize class"""

        self.connection = van_connection

    def get_activist_codes(self):
        """
        Get activist code objects

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        url = self.connection.uri + 'activistCodes'

        tbl = Table(self.connection.api.get_request(url))
        logger.info(f'Found {tbl.num_rows} activist codes.')
        return tbl

    def get_activist_code(self, activist_code_id):
        """Get an activist code

        `Args:`
            activist_code_id : int
                The activist code id associated with the activist code.
        `Returns:`
            dict
        """

        url = self.connection.uri + f'activistCodes/{activist_code_id}'

        r = self.connection.api.get_request(url)
        logger.info(f'Found activist code {activist_code_id}.')
        return r
