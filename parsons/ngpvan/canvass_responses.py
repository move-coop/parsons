"""NGPVAN Canvass Responses Endpoints"""

from parsons.etl.table import Table
import logging

logger = logging.getLogger(__name__)


class CanvassResponses(object):
    def __init__(self, van_connection):

        self.connection = van_connection

    def get_canvass_responses_contact_types(self):
        """
        Get canvass response contact types.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = Table(self.connection.get_request("canvassResponses/contactTypes"))
        logger.info(f"Found {tbl.num_rows} canvass response contact types.")
        return tbl

    def get_canvass_responses_input_types(self):
        """
        Get canvass response input types.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = Table(self.connection.get_request("canvassResponses/inputTypes"))
        logger.info(f"Found {tbl.num_rows} canvass response input types.")
        return tbl

    def get_canvass_responses_result_codes(self):
        """
        Get canvass response result codes.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = Table(self.connection.get_request("canvassResponses/resultCodes"))
        logger.info(f"Found {tbl.num_rows} canvass response result codes.")
        return tbl
