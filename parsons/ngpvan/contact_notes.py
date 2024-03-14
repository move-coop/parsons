"""NGPVAN Contact Notes Endpoints"""

from parsons.etl.table import Table
import logging

logger = logging.getLogger(__name__)


class ContactNotes(object):
    def __init__(self, van_connection):
        self.connection = van_connection

    def get_contact_notes(self, van_id):
        """
        Get custom fields.

        `Args:`
            van_id : str
                VAN ID for the person to get notes for.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = Table(self.connection.get_request(f"people/{van_id}/notes"))
        logger.info(f"Found {tbl.num_rows} custom fields.")
        return tbl

    def create_contact_note(self, van_id, text, is_view_restricted, note_category_id=None):
        """
        Create a contact note

        `Args:`
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
        `Returns:`
            int
              The note ID.
        """
        note = {"text": text, "isViewRestricted": is_view_restricted}
        if note_category_id is not None:
            note["category"] = {"noteCategoryId": note_category_id}

        r = self.connection.post_request(f"people/{van_id}/notes", json=note)
        logger.info(f"Contact note {r} created.")
        return r
