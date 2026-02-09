"""NGPVAN Activist Code Endpoints"""

import logging

from parsons.etl.table import Table
from parsons.ngpvan.utilities import action_parse

logger = logging.getLogger(__name__)


class ActivistCodes:
    def __init__(self, van_connection):
        self.connection = van_connection

    def get_activist_codes(self):
        """
        Get activist codes.

        Returns:
            Table: See :ref:`parsons-table` for output options.

        """
        tbl = Table(self.connection.get_request("activistCodes"))
        logger.info(f"Found {tbl.num_rows} activist codes.")
        return tbl

    def get_activist_code(self, activist_code_id):
        """
        Get an activist code.

        Args:
            activist_code_id (int): The activist code id.

        Returns:
            dict: The activist code.

        """
        r = self.connection.get_request(f"activistCodes/{activist_code_id}")
        logger.info(f"Found activist code {activist_code_id}.")
        return r

    def toggle_activist_code(
        self, id, activist_code_id, action, id_type="vanid", omit_contact=True
    ):
        # Internal method to apply/remove activist codes. Was previously a public method,
        # but for the sake of simplicity, breaking out into two public  methods.

        response = {
            "activistCodeId": activist_code_id,
            "action": action_parse(action),
            "type": "activistCode",
            "omitActivistCodeContactHistory": omit_contact,
        }

        r = self.apply_response(id, response, id_type, omit_contact=omit_contact)

        logger.info(
            f"{id_type.upper()} {id} {action.capitalize()} " + f"activist code {activist_code_id}"
        )

        return r

    def apply_activist_code(self, id, activist_code_id, id_type="vanid", omit_contact=True):
        """
        Apply an activist code to or from a person.

        Args:
            id (str): A valid person id.
            activist_code_id (int): A valid activist code id.
            id_type (str, optional): A known person identifier type available on this VAN instance such as
                ``dwid``. Defaults to "vanid".
            omit_contact (bool, optional): If set to false the contact history will be updated with a contact
                attempt. Defaults to True.

        """
        return self.toggle_activist_code(
            id, activist_code_id, "Apply", id_type=id_type, omit_contact=omit_contact
        )

    def remove_activist_code(self, id, activist_code_id, id_type="vanid") -> None:
        """
        Remove an activist code to or from a person.

        Args:
            id (str): A valid person id.
            activist_code_id (int): A valid activist code id.
            id_type (str, optional): A known person identifier type available on this VAN instance such as
                ``dwid``. Defaults to "vanid".

        """
        return self.toggle_activist_code(id, activist_code_id, "Remove", id_type=id_type)
