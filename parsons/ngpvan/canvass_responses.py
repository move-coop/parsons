"""NGPVAN Canvass Responses Endpoints"""

import logging

from parsons.etl.table import Table

logger = logging.getLogger(__name__)


class CanvassResponses:
    def __init__(self, van_connection):
        self.connection = van_connection

    def get_canvass_responses_contact_types(self):
        """
        Get canvass response contact types.

        Returns:
            Table
                See :ref:`Table` for output options.

        """
        tbl = Table(self.connection.get_request("canvassResponses/contactTypes"))
        logger.info("Found %s canvass response contact types.", tbl.num_rows)
        return tbl

    def get_canvass_responses_input_types(self):
        """
        Get canvass response input types.

        Returns:
            Table
                See :ref:`Table` for output options.

        """
        tbl = Table(self.connection.get_request("canvassResponses/inputTypes"))
        logger.info("Found %s canvass response input types.", tbl.num_rows)
        return tbl

    def get_canvass_responses_result_codes(self) -> Table:
        """
        Get canvass response result codes.

        Returns:
            See :ref:`Table` for output options.

        """
        tbl = Table(self.connection.get_request("canvassResponses/resultCodes"))
        logger.info("Found %s canvass response result codes.", tbl.num_rows)

        return tbl
