"""NGPVAN Activist Code Endpoints"""

from parsons.etl.table import Table
import logging

logger = logging.getLogger(__name__)


class ActivistCodes(object):
    """
        .. note::
            To apply or remove activist codes, use the :meth:`toggle_activist_code` method.
    """

    def __init__(self, van_connection):

        self.connection = van_connection

    def get_activist_codes(self):
        """
        Get activist codes.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = Table(self.connection.get_request('activistCodes'))
        logger.info(f'Found {tbl.num_rows} activist codes.')
        return tbl

    def get_activist_code(self, activist_code_id):
        """
        Get an activist code.

        `Args:`
            activist_code_id : int
                The activist code id.
        `Returns:`
            dict
                The activist code
        """

        r = self.connection.get_request(f'activistCodes/{activist_code_id}')
        logger.info(f'Found activist code {activist_code_id}.')
        return r
