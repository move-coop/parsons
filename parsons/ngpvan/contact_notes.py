"""NGPVAN Contact Notes Endpoints"""

import logging

from parsons.etl.table import Table

logger = logging.getLogger(__name__)


class ContactNotes:
    def __init__(self, van_connection):
        self.connection = van_connection

    def get_contact_notes(self, van_id):
        """
        Get custom fields.

        Args:
            van_id : str
                VAN ID for the person to get notes for.

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        tbl = Table(self.connection.get_request(f"people/{van_id}/notes"))
        logger.info(f"Found {tbl.num_rows} custom fields.")
        return tbl

    def create_contact_note(
        self,
        van_id,
        text,
        is_view_restricted,
        note_category_id=None,
        contact_type_id=None,
        input_type_id=None,
        date_canvassed=None,
        result_code_id=None,
    ):
        """
        Create a contact note

        Args:
            van_id: str
                VAN ID for the person this note will be applied to.
            text: str
                The content of the note.
            is_view_restricted: bool
                Set to true if the note should be restricted only to certain users within
                the current context; set to false if the note may be viewed by any user
                in the current context.
            note_category_id: int
                Optional; if set, the note category for this note.
            contact_type_id: str
                Defaults to 82 if no value is set. This value results in a null contact type in EA.
            input_type_id: str
                Defaults to 11 if no value is set. If the value is 11,
                the input type in EA will be listed as "API"
            date_canvassed: date
                Defaults to current date if no value is set. Dates should be formatted in ISO8601 standard.
            result_code_id: str
                Defaults to 205 if no value is set. This value results in a "Contacted" result in EA.

        Returns:
            int
              The note ID.

        """
        note = {"text": text, "isViewRestricted": is_view_restricted}
        if note_category_id is not None:
            note["category"] = {"noteCategoryId": note_category_id}

        contact_history = {}

        if contact_type_id is not None:
            contact_history["contact_type_id"] = str(contact_type_id)
        if input_type_id is not None:
            contact_history["input_type_id"] = str(input_type_id)
        if date_canvassed is not None:
            contact_history["dateCanvassed"] = date_canvassed
        if result_code_id is not None:
            contact_history["result_code_id"] = str(result_code_id)

        if contact_history:
            note["contactHistory"] = contact_history

        r = self.connection.post_request(f"people/{van_id}/notes", json=note)
        logger.info(f"Contact note {r} created.")
        return r
