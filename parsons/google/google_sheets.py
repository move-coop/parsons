import os
import json
import logging

from parsons.etl.table import Table

import gspread
from oauth2client.service_account import ServiceAccountCredentials

logger = logging.getLogger(__name__)


class GoogleSheets:
    """
    A connector for Google Sheets, handling data import and export.

    `Args:`
        google_keyfile_dict: dict
            A dictionary of Google Drive API credentials, parsed from JSON provided
            by the Google Developer Console. Required if env variable
            ``GOOGLE_DRIVE_CREDENTIALS`` is not populated.
    """

    def __init__(self, google_keyfile_dict=None):

        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive',
            ]

        self.google_keyfile_dict = google_keyfile_dict

        if google_keyfile_dict is None:
            try:
                keyfile_json = os.environ['GOOGLE_DRIVE_CREDENTIALS']
            except KeyError as error:
                logger.error("Google credentials missing. Must be specified as an env var or kwarg")
                raise error

            self.google_keyfile_dict = json.loads(keyfile_json)
        else:
            self.google_keyfile_dict = google_keyfile_dict

        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            self.google_keyfile_dict, scope
            )
        self.gspread_client = gspread.authorize(credentials)

    def _get_sheet(self, spreadsheet_id, sheet_index=0):
        return self.gspread_client.open_by_key(spreadsheet_id).get_worksheet(sheet_index)

    def get_sheet_index_with_title(self, spreadsheet_id, title):
        """
        Get the first sheet in a Google spreadsheet with the given title.

        `Args:`
            spreadsheet_id: str
                The ID of the spreadsheet (Tip: Get this from the spreadsheet URL)
            title: str
                The sheet title

        `Returns:`
            str
                The sheet index
        """

        sheets = self.gspread_client.open_by_key(spreadsheet_id).worksheets()
        for index, sheet in enumerate(sheets):
            if sheet.title == title:
                return index
        raise ValueError(f"Couldn't find sheet with title {title}")

    def read_sheet(self, spreadsheet_id, sheet_index=0):
        """
        Create a ``parsons table`` from a sheet in a Google spreadsheet, given the sheet index.

        `Args:`
            spreadsheet_id: str
                The ID of the spreadsheet (Tip: Get this from the spreadsheet URL)
            sheet_index: int (optional)
                The index of the desired worksheet (Index begins at 0).

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        sheet = self._get_sheet(spreadsheet_id, sheet_index)
        records = sheet.get_all_values()

        return Table(records)

    def read_sheet_with_title(self, spreadsheet_id, title):
        """
        Create a ```parsons table``` from a sheet in Google spreadsheet, given the sheet title.

        `Args:`
            spreadsheet_id: str
                The ID of the spreadsheet (Tip: Get this from the spreadsheet URL)
            title: str
                The sheet title

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        index = self.get_sheet_index_with_title(spreadsheet_id, title)
        return self.read_sheet(spreadsheet_id, index)

    def share_spreadsheet(self, spreadsheet_id, sharee, share_type='user', role='reader',
                          notify=True, notify_message=None, with_link=False):
        """
        Share a spreadsheet with a user, group of users, domain and/or the public.

        `Args:`
            spreadsheet_id: str
                The ID of the spreadsheet (Tip: Get this from the spreadsheet URL)
            sharee: str
                User or group e-mail address, domain name to share the spreadsheet
                with. To share publicly, set sharee value to ``None``.
            share_type: str
                The sharee type. Allowed values are: ``user``, ``group``, ``domain``,
                ``anyone``.
            role: str
                The primary role for this user. Allowed values are: ``owner``,
                ``writer``, ``reader``.
            notify: boolean
                Whether to send an email to the target user/domain.
            email_message: str
                The email to be sent if notify kwarg set to True.
            with_link: boolean
                Whether a link is required for this permission.
        """

        spreadsheet = self.gspread_client.open_by_key(spreadsheet_id)
        spreadsheet.share(sharee, share_type, role, notify=notify,
                          email_message=notify_message, with_link=with_link)

    def get_spreadsheet_permissions(self, spreadsheet_id):
        """
        List the permissioned users and groups for a spreadsheet.

        `Args:`
            spreadsheet_id: str
                The ID of the spreadsheet (Tip: Get this from the spreadsheet URL)
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        spreadsheet = self.gspread_client.open_by_key(spreadsheet_id)
        return Table(spreadsheet.list_permissions())

    def create_spreadsheet(self, title, editor_email=None):
        """
        Create a Google spreadsheet from a Parsons table. Optionally shares the new doc with
        the given email address.

        `Args:`
            title: str
                The human-readable title of the new spreadsheet
            editor_email: str (optional)
                Email address which should be given permissions on this spreadsheet

        `Returns:`
            str
                The spreadsheet ID
        """

        spreadsheet = self.gspread_client.create(title)

        if editor_email:
            self.gspread_client.insert_permission(
                spreadsheet.id,
                editor_email,
                perm_type='user',
                role='writer',
            )

        return spreadsheet.id

    def delete_spreadsheet(self, spreadsheet_id):
        """
        Deletes a Google spreadsheet.

        `Args:`
            spreadsheet_id: str
                The ID of the spreadsheet (Tip: Get this from the spreadsheet URL)
        """
        self.gspread_client.del_spreadsheet(spreadsheet_id)

    def add_sheet(self, spreadsheet_id, title=None, rows=100, cols=25):
        """
        Adds a sheet to a Google spreadsheet.

        `Args:`
            spreadsheet_id: str
                The ID of the spreadsheet (Tip: Get this from the spreadsheet URL)
            rows: int
                Number of rows
            cols
                Number of cols

        `Returns:`
            str
                The sheet index
        """
        spreadsheet = self.gspread_client.open_by_key(spreadsheet_id)
        spreadsheet.add_worksheet(title, rows, cols)
        sheet_count = len(spreadsheet.worksheets())
        return (sheet_count-1)

    def append_to_sheet(self, spreadsheet_id, table, sheet_index=0, user_entered_value=False):
        """
        Append data from a Parsons table to a Google sheet. Note that the table's columns are
        ignored, as we'll be keeping whatever header row already exists in the Google sheet.

        `Args:`
            spreadsheet_id: str
                The ID of the spreadsheet (Tip: Get this from the spreadsheet URL)
            table: obj
                Parsons table
            sheet_index: int (optional)
                The index of the desired worksheet
            user_entered_value: bool (optional)
                If True, will submit cell values as entered (required for entering formulas).
                Otherwise, values will be entered as strings or numbers only.
        """

        sheet = self._get_sheet(spreadsheet_id, sheet_index)

        # Grab the existing data, so we can figure out where to start adding new data as a batch.
        # TODO Figure out a way to do a batch append without having to read the whole sheet first.
        # Maybe use gspread's low-level batch_update().
        existing_table = self.read_sheet(spreadsheet_id, sheet_index)

        # If the existing sheet is blank, then just overwrite the table.
        if existing_table.num_rows == 0:
            return self.overwrite_sheet(spreadsheet_id, table, sheet_index, user_entered_value)

        cells = []
        for row_num, row in enumerate(table.data):
            for col_num, cell in enumerate(row):
                # Add 2 to allow for the header row, and for google sheets indexing starting at 1
                sheet_row_num = existing_table.num_rows + row_num + 2
                cells.append(gspread.Cell(sheet_row_num, col_num + 1, row[col_num]))

        value_input_option = 'RAW'
        if user_entered_value:
            value_input_option = 'USER_ENTERED'

        # Update the data in one batch
        sheet.update_cells(cells, value_input_option=value_input_option)

    def overwrite_sheet(self, spreadsheet_id, table, sheet_index=0, user_entered_value=False):
        """
        Replace the data in a Google sheet with a Parsons table, using the table's columns as the
        first row.

        `Args:`
            spreadsheet_id: str
                The ID of the spreadsheet (Tip: Get this from the spreadsheet URL)
            table: obj
                Parsons table
            sheet_index: int (optional)
                The index of the desired worksheet
            user_entered_value: bool (optional)
                If True, will submit cell values as entered (required for entering formulas).
                Otherwise, values will be entered as strings or numbers only.
        """

        sheet = self._get_sheet(spreadsheet_id, sheet_index)
        sheet.clear()

        value_input_option = 'RAW'
        if user_entered_value:
            value_input_option = 'USER_ENTERED'

        # Add header row
        sheet.append_row(table.columns, value_input_option=value_input_option)

        cells = []
        for row_num, row in enumerate(table.data):
            for col_num, cell in enumerate(row):
                # We start at row #2 to keep room for the header row we added above
                cells.append(gspread.Cell(row_num + 2, col_num + 1, row[col_num]))

        # Update the data in one batch
        sheet.update_cells(cells, value_input_option=value_input_option)
