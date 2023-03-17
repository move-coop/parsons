from parsons.etl.table import Table
import logging

logger = logging.getLogger(__name__)


class CustomFields:
    def __init__(self, van_connection):

        self.connection = van_connection

    def get_custom_fields(self, field_type="contacts"):
        """
        Get custom fields.

        `Args:`
            field_type : str
                Filter by custom field group type. Must be one of ``contacts`` or
                ``contributions``.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        params = {"customFieldsGroupType": field_type.capitalize()}

        tbl = Table(self.connection.get_request("customFields", params=params))
        logger.info(f"Found {tbl.num_rows} custom fields.")
        return tbl

    def get_custom_fields_values(self, field_type="contacts"):
        """
        Get custom field values as a long table.

        `Args:`
            field_type : str
                Filter by custom field group type. Must be one of ``contacts`` or
                ``contributions``.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = self.get_custom_fields()

        # Some custom fields do no have associated values. If this is the case then
        # we should return an empty Table, but with the expected columns.
        if tbl.get_column_types("availableValues") == ["NoneType"]:
            logger.info("Found 0 custom field values.")
            return Table(
                [
                    {
                        "customFieldId": None,
                        "id": None,
                        "name": None,
                        "parentValueId": None,
                    }
                ]
            )

        else:
            logger.info(f"Found {tbl.num_rows} custom field values.")
            return tbl.long_table("customFieldId", "availableValues", prepend=False)

    def get_custom_field(self, custom_field_id):
        """
        Get a custom field.

        `Args:`
            custom_field_id: int
                A valid custom field id.
        `Returns:`
            A json.
        """

        r = self.connection.get_request(f"customFields/{custom_field_id}")
        logger.info(f"Found custom field {custom_field_id}.")
        return r
