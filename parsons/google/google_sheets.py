import logging
import uuid

import gspread

from parsons.etl.table import Table
from parsons.google.utilities import (
    load_google_application_credentials,
    setup_google_application_credentials,
    hexavigesimal,
)

logger = logging.getLogger(__name__)


class GoogleSheets:
    """
    A connector for Google Sheets, handling data import and export.

    `Args:`
        google_keyfile_dict: dict
            A dictionary of Google Drive API credentials, parsed from JSON provided
            by the Google Developer Console. Required if env variable
            ``GOOGLE_DRIVE_CREDENTIALS`` is not populated.
        subject: string
            In order to use account impersonation, pass in the email address of the account to be
            impersonated as a string.
    """

    def __init__(self, google_keyfile_dict=None, subject=None):

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]

        env_credentials_path = str(uuid.uuid4())
        setup_google_application_credentials(
            google_keyfile_dict,
            "GOOGLE_DRIVE_CREDENTIALS",
            target_env_var_name=env_credentials_path,
        )

        credentials = load_google_application_credentials(
            env_credentials_path, scopes=scope, subject=subject
        )

        self.gspread_client = gspread.authorize(credentials)

    def _get_worksheet(self, spreadsheet_id, worksheet=0):
        # Internal method to retrieve a worksheet object.

        # Check if the worksheet is an integer, if so find the sheet by index
        if isinstance(worksheet, int):
            return self.gspread_client.open_by_key(spreadsheet_id).get_worksheet(
                worksheet
            )

        elif isinstance(worksheet, str):
            idx = self.list_worksheets(spreadsheet_id).index(worksheet)
            try:
                return self.gspread_client.open_by_key(spreadsheet_id).get_worksheet(
                    idx
                )
            except:  # noqa: E722
                raise ValueError(f"Couldn't find worksheet {worksheet}")

        else:
            raise ValueError(f"Couldn't find worksheet index or title {worksheet}")

    def list_worksheets(self, spreadsheet_id):
        """
        Return a list of worksheets in the spreadsheet.

        `Args:`
            spreadsheet_id: str
                The ID of the spreadsheet (Tip: Get this from the spreadsheet URL)
        `Returns:`
            list
                A List of worksheets order by their index
        """
        worksheets = self.gspread_client.open_by_key(spreadsheet_id).worksheets()
        return [w.title for w in worksheets]

    def get_worksheet_index(self, spreadsheet_id, title):
        """
        Get the first sheet in a Google spreadsheet with the given title. The
        title is case sensitive and the index begins with 0.

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

    def get_worksheet(self, spreadsheet_id, worksheet=0):
        """
        Create a ``parsons table`` from a sheet in a Google spreadsheet, given the sheet index.

        `Args:`
            spreadsheet_id: str
                The ID of the spreadsheet (Tip: Get this from the spreadsheet URL)
            worksheet: str or int
                The index or the title of the worksheet. The index begins with
                0.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        worksheet = self._get_worksheet(spreadsheet_id, worksheet)
        tbl = Table(worksheet.get_all_values())
        logger.info(f"Retrieved worksheet with {tbl.num_rows} rows.")
        return tbl

    def share_spreadsheet(
        self,
        spreadsheet_id,
        sharee,
        share_type="user",
        role="reader",
        notify=True,
        notify_message=None,
        with_link=False,
    ):
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
        spreadsheet.share(
            sharee,
            share_type,
            role,
            notify=notify,
            email_message=notify_message,
            with_link=with_link,
        )
        logger.info(f"Shared spreadsheet {spreadsheet_id}.")

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
        tbl = Table(spreadsheet.list_permissions())
        logger.info(f"Retrieved permissions for {spreadsheet_id} spreadsheet.")
        return tbl

    def create_spreadsheet(self, title, editor_email=None, folder_id=None):
        """
        Creates a new Google spreadsheet. Optionally shares the new doc with
        the given email address. Optionally creates the sheet in a specified folder.

        `Args:`
            title: str
                The human-readable title of the new spreadsheet
            editor_email: str (optional)
                Email address which should be given permissions on this spreadsheet.
                Tip: You may want to share this file with the service account.
            folder_id: str (optional)
                ID of the Google folder where the spreadsheet should be created.
                Tip: Get this from the folder URL.
                Anyone shared on the folder will have access to the spreadsheet.

        `Returns:`
            str
                The spreadsheet ID
        """

        spreadsheet = self.gspread_client.create(title, folder_id=folder_id)

        if editor_email:
            self.gspread_client.insert_permission(
                spreadsheet.id,
                editor_email,
                perm_type="user",
                role="writer",
            )

        logger.info(f"Created spreadsheet {spreadsheet.id}")
        return spreadsheet.id

    def delete_spreadsheet(self, spreadsheet_id):
        """
        Deletes a Google spreadsheet.

        `Args:`
            spreadsheet_id: str
                The ID of the spreadsheet (Tip: Get this from the spreadsheet URL)
        """
        self.gspread_client.del_spreadsheet(spreadsheet_id)
        logger.info(f"Deleted spreadsheet {spreadsheet_id}")

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
        logger.info("Created worksheet.")
        return sheet_count - 1

    def append_to_sheet(
        self, spreadsheet_id, table, worksheet=0, user_entered_value=False, **kwargs
    ):
        """
        Append data from a Parsons table to a Google sheet. Note that the table's columns are
        ignored, as we'll be keeping whatever header row already exists in the Google sheet.

        `Args:`
            spreadsheet_id: str
                The ID of the spreadsheet (Tip: Get this from the spreadsheet URL)
            table: obj
                Parsons table
            worksheet: str or int
                The index or the title of the worksheet. The index begins with
                0.
            user_entered_value: bool (optional)
                If True, will submit cell values as entered (required for entering formulas).
                Otherwise, values will be entered as strings or numbers only.
        """

        if not table.num_rows:
            logger.warning("No data provided to append, skipping.")
            return

        # This is in here to ensure backwards compatibility with previous versions of Parsons.
        if "sheet_index" in kwargs:
            worksheet = kwargs["sheet_index"]
            logger.warning("Argument deprecated. Use worksheet instead.")

        sheet = self._get_worksheet(spreadsheet_id, worksheet)

        # Grab the existing data, so we can figure out where to start adding new data as a batch.
        # TODO Figure out a way to do a batch append without having to read the whole sheet first.
        # Maybe use gspread's low-level batch_update().
        existing_table = self.get_worksheet(spreadsheet_id, worksheet)

        # If the existing sheet is blank, then just overwrite the table.
        if existing_table.num_rows == 0:
            return self.overwrite_sheet(
                spreadsheet_id, table, worksheet, user_entered_value
            )

        cells = []
        for row_num, row in enumerate(table.data):
            for col_num, cell in enumerate(row):
                # Add 2 to allow for the header row, and for google sheets indexing starting at 1
                sheet_row_num = existing_table.num_rows + row_num + 2
                cells.append(gspread.Cell(sheet_row_num, col_num + 1, row[col_num]))

        value_input_option = "RAW"
        if user_entered_value:
            value_input_option = "USER_ENTERED"

        # Update the data in one batch
        sheet.update_cells(cells, value_input_option=value_input_option)
        logger.info(f"Appended {table.num_rows} rows to worksheet.")

    def paste_data_in_sheet(
        self, spreadsheet_id, table, worksheet=0, header=True, startrow=0, startcol=0
    ):
        """
        Pastes data from a Parsons table to a Google sheet. Note that this may overwrite
        presently existing data. This function is useful for adding data to a subsection
        if an existing sheet that will have other existing data - contrast to
        `overwrite_sheet` (which will fully replace any existing data) and `append_to_sheet`
        (which sticks the data only after all other existing data).

        `Args:`
            spreadsheet_id: str
                The ID of the spreadsheet (Tip: Get this from the spreadsheet URL).
            table: obj
                Parsons table
            worksheet: str or int
                The index or the title of the worksheet. The index begins with 0.
            header: bool
                Whether or not the header row gets pasted with the data.
            startrow: int
                Starting row position of pasted data. Counts from 0.
            startcol: int
                Starting column position of pasted data. Counts from 0.
        """

        sheet = self._get_worksheet(spreadsheet_id, worksheet)

        number_of_columns = len(table.columns)
        number_of_rows = table.num_rows + 1 if header else table.num_rows

        if not number_of_rows or not number_of_columns:  # No data to paste
            logger.warning(
                f"No data available to paste, table size "
                f"({number_of_rows}, {number_of_columns}). Skipping."
            )
            return

        # gspread uses ranges like "C3:J7", so we need to convert to this format
        data_range = (
            hexavigesimal(startcol + 1)
            + str(startrow + 1)
            + ":"
            + hexavigesimal(startcol + number_of_columns)
            + str(startrow + number_of_rows)
        )

        # Unpack data. Hopefully this is small enough for memory
        data = [[]] * table.num_rows
        for row_num, row in enumerate(table.data):
            data[row_num] = list(row)

        if header:
            sheet.update(data_range, [table.columns] + data)
        else:
            sheet.update(data_range, data)

        logger.info(f"Pasted data to {data_range} in worksheet.")

    def overwrite_sheet(
        self, spreadsheet_id, table, worksheet=0, user_entered_value=False, **kwargs
    ):
        """
        Replace the data in a Google sheet with a Parsons table, using the table's columns as the
        first row.

        `Args:`
            spreadsheet_id: str
                The ID of the spreadsheet (Tip: Get this from the spreadsheet URL)
            table: obj
                Parsons table
            worksheet: str or int
                The index or the title of the worksheet. The index begins with
                0.
            user_entered_value: bool (optional)
                If True, will submit cell values as entered (required for entering formulas).
                Otherwise, values will be entered as strings or numbers only.
        """

        # This is in here to ensure backwards compatibility with previous versions of Parsons.
        if "sheet_index" in kwargs:
            worksheet = kwargs["sheet_index"]
            logger.warning("Argument deprecated. Use worksheet instead.")

        sheet = self._get_worksheet(spreadsheet_id, worksheet)
        sheet.clear()

        if not len(table.columns):
            logger.warning("No data provided, worksheet is empty.")
            return

        value_input_option = "RAW"
        if user_entered_value:
            value_input_option = "USER_ENTERED"

        # Add header row
        sheet.append_row(table.columns, value_input_option=value_input_option)

        if table.num_rows:
            cells = []
            for row_num, row in enumerate(table.data):
                for col_num, _ in enumerate(row):
                    # We start at row #2 to keep room for the header row we added above
                    cells.append(gspread.Cell(row_num + 2, col_num + 1, row[col_num]))

            # Update the data in one batch
            sheet.update_cells(cells, value_input_option=value_input_option)
        else:
            logger.warning("No rows provided.")

        logger.info("Overwrote worksheet.")

    def format_cells(self, spreadsheet_id, range, cell_format, worksheet=0):
        """
        Format the cells of a worksheet.

        `Args:`
            spreadsheet_id: str
                The ID of the spreadsheet (Tip: Get this from the spreadsheet URL)
            range: str
                The cell range to format. E.g. ``"A2"`` or ``"A2:B100"``
            cell_format: dict
                The formatting to apply to the range. Full options are specified in
                the GoogleSheets `API documentation <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/cells#cellformat>`_.
            worksheet: str or int
                The index or the title of the worksheet. The index begins with
                0.

        **Examples**

        .. code-block:: python

            # Set 'A4' cell's text format to bold
            gs.format_cells(sheet_id, "A4", {"textFormat": {"bold": True}}, worksheet=0)

            # Color the background of 'A2:B2' cell range yellow,
            # change horizontal alignment, text color and font size
            gs.format_cells.format(sheet_id, "A2:B2", {
                "backgroundColor": {
                    "red": 0.0,
                    "green": 0.0,
                    "blue": 0.0
                    },
                "horizontalAlignment": "CENTER",
                "textFormat": {
                    "foregroundColor": {
                        "red": 1.0,
                        "green": 1.0,
                        "blue": 0.0
                        },
                        "fontSize": 12,
                        "bold": True
                        }
                    }, worksheet=0)

        """  # noqa: E501,E261

        ws = self._get_worksheet(spreadsheet_id, worksheet)
        ws.format(range, cell_format)
        logger.info("Formatted worksheet")

    def read_sheet(self, spreadsheet_id, sheet_index=0):
        # Deprecated method v0.14 of Parsons.

        logger.warning("Deprecated method. Use get_worksheet() instead.")
        return self.get_worksheet(spreadsheet_id, sheet_index)

    def read_sheet_with_title(self, spreadsheet_id, title):
        # Deprecated method v0.14 of Parsons.

        logger.warning("Deprecated method. Use get_worksheet() instead.")
        return self.get_worksheet(spreadsheet_id, title)

    def get_sheet_index_with_title(self, spreadsheet_id, title):
        # Deprecated method v0.14 of Parsons.

        logger.warning("Deprecated method. Use get_worksheet_index   instead.")
        return self.get_worksheet_index(spreadsheet_id, title)
