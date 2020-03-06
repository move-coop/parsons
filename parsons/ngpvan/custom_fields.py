from parsons.etl.table import Table
import logging

logger = logging.getLogger(__name__)


class CustomFields():

    def __init__(self, van_connection):

        self.connection = van_connection

    def get_custom_fields(self):
        """
        Get custom fields.

        `Args:`
            name : str
                Filter by name of code.
            supported_entities: str
                Filter by supported entities.
            parent_code_id: str
                Filter by parent code id.
            code_type: str
                Filter by code type.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        params = {}

        tbl = Table(self.connection.get_request('customFields', params=params))
        logger.info(f'Found {tbl.num_rows} custom fields.')
        return tbl

    def get_custom_field(self, custom_field_id):
        """
        Get a custom field.

        `Args:`
            custom_field_id: int
                A valid custom field id.
        `Returns:`
            A json.
        """

        url = self.connection.uri + f'customFields/{custom_field_id}'

        r = self.connection.request(url)
        logger.debug(r)
        logger.info(f'Found custom field {custom_field_id}.')

        return r
