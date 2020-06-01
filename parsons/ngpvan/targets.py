"""NGPVAN Target Endpoints"""

from parsons.etl.table import Table
import logging

logger = logging.getLogger(__name__)


class Targets(object):

    def __init__(self, van_connection):

        self.connection = van_connection

    def get_targets(self):
        """
        Get targets.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = Table(self.connection.get_request('targets'))
        logger.info(f'Found {tbl.num_rows} targets.')
        return tbl

    def get_target(self, target_id):
        """
        Get a single target.

        `Args:`
            target_id : int
                The target id.
        `Returns:`
            dict
                The target
        """

        r = self.connection.get_request(f'targets/{target_id}')
        logger.info(f'Found target {target_id}.')
        return r
