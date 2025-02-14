# This script runs a query against a MySQL database and saves the results to a Google Sheet.

import logging
import time

from gspread.exceptions import APIError

from parsons import GoogleSheets, MySQL

logger = logging.getLogger(__name__)
_handler = logging.StreamHandler()
_formatter = logging.Formatter("%(levelname)s %(message)s")
_handler.setFormatter(_formatter)
logger.addHandler(_handler)
logger.setLevel("INFO")

# To use the MySQL connector, set the environment variables:
# MYSQL_USERNAME
# MYSQL_PASSWORD
# MYSQL_HOST
# MYSQL_DB
# MYSQL_PORT
# To use the Google Sheets connector, set the GOOGLE_DRIVE_CREDENTIALS environment variable.
# More on environmental variables:
# https://move-coop.github.io/parsons/html/use_cases/contribute_use_cases.html#sensitive-information

# Instantiate classes
mysql = MySQL()
gsheets = GoogleSheets()

# Configuration Variables
# FOLDER_ID is the ID of the Google Drive folder the Google Sheets workbook will be created.
FOLDER_ID = "enter_id_here"
# TITLE is the name of the Google Sheets workbook the script will create.
TITLE = "sheet_title_here"
# TAB_LABEL is the name of the tab where your query results will appear in Google Sheets.
TAB_LABEL = "tab_label_here"
# QUERY is the SQL query we will run against the MYSQL database.
QUERY = """-- Enter SQL here"""


# Function to add data to spreadsheet tab.
# There is a limit to the number of calls per minute,
# so we use request_count to set a maximum number of tries
def try_overwrite(table, request_count, sheet_id, tab_index):
    try:
        gsheets.overwrite_sheet(sheet_id, table, worksheet=tab_index, user_entered_value=False)

    except APIError as e:
        print(f"trying to overwrite {tab_index} for the {request_count}th time")
        if request_count > 60:
            raise APIError(e)
        time.sleep(80)
        request_count += 1
        try_overwrite(table, request_count, sheet_id, tab_index)


def main():
    logger.info(f"Creating Google Sheets workbook called '{TITLE}'")

    try:
        new_sheet = gsheets.create_spreadsheet(title=TITLE, editor_email=None, folder_id=FOLDER_ID)
        # If successful new_sheet will be the spreadsheet's ID in a string
        if isinstance(new_sheet, str):
            logger.info(f"Successfully created sheet {TITLE}!")
        # If we do not get a string back from the create_spreadsheet call
        # then something went wrong. Print the response.
        else:
            logger.info(f"create_spreadsheet did not return a sheet ID. Issue: {str(new_sheet)}")

    # If we get an error when trying to create the spreadsheet we print the error.
    except Exception as e:
        logger.info(f"There was a problem creating the Google Sheets workbook! Error: {str(e)}")

    logger.info("Querying MYSQL database...")
    query_results = mysql.query(QUERY)

    logger.info(f"Querying complete. Preparing to load data into Google Sheets tab {TAB_LABEL}")
    query_results.convert_columns_to_str()
    request_count = 0
    tab_index = gsheets.add_sheet(new_sheet, title=TAB_LABEL)
    try_overwrite(query_results, request_count, sheet_id=new_sheet, tab_index=tab_index)
    logger.info(f"Load into Google Sheets for tab {TAB_LABEL} complete!")


if __name__ == "__main__":
    main()
