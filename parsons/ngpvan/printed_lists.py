"""NGPVAN Saved List Endpoints"""

from parsons.etl.table import Table
import logging

logger = logging.getLogger(__name__)


class PrintedLists(object):
    def __init__(self, van_connection):

        self.connection = van_connection

    def get_printed_lists(
        self,
        generated_after=None,
        generated_before=None,
        created_by=None,
        folder_name=None,
        turf_name=None,
    ):
        """
        Get printed lists.

        `Args:`
            folder_id: int
                Filter by the id for a VAN folder. If included returns only
                the saved lists in the folder
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        params = {
            "generatedAfter": generated_after,
            "generatedBefore": generated_before,
            "createdBy": created_by,
            "folderName": folder_name,
            "turfName": turf_name,
        }

        params = {key: value for key, value in params.items() if value is not None}

        tbl = Table(self.connection.get_request("printedLists", params=params))

        logger.info(f"Found {tbl.num_rows} printed lists.")
        return tbl

    def get_printed_list(self, printed_list_number):
        """
        Returns a printed list object.

        `Args:`
            printed_list_number: int
                The printed list number
        `Returns:`
            dict
        """

        r = self.connection.get_request(f"printedLists/{printed_list_number}")
        logger.info(f"Found printed list {printed_list_number}.")
        return r
