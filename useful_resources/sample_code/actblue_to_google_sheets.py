# ### METADATA

# Connectors: ActBlue, GoogleSheets
# Description: Get information about contributions from ActBlue and put in a new Google Sheet

# ### CONFIGURATION

# Set the configuration variables below or set environmental variables of the same name and leave
# these with empty strings.  We recommend using environmental variables if possible.

config_vars = {
    # Connector 1:
    "ACTBLUE_CLIENT_UUID": "",  # see https://secure.actblue.com/docs/csv_api#authentication
    "ACTBLUE_CLIENT_SECRET": "",  # see https://secure.actblue.com/docs/csv_api#authentication
    # Connector 2:
    # Visit https://console.developers.google.com to create a Service Account and download its
    # credentials in a json file. Provide the path to that file for this configuration.
    "GOOGLE_DRIVE_CREDENTIALS": "",
}


# ### CODE

# Setup

import os  # noqa E402

os.environ["PARSONS_SKIP_IMPORT_ALL"] = "1"

from parsons import logger  # noqa E402
from parsons.actblue import ActBlue  # noqa E402
from parsons.google.google_sheets import GoogleSheets  # noqa E402

# if variables specified above, sets them as environmental variables
for name, value in config_vars.items():
    if value.strip() != "":
        os.environ[name] = value

actblue = ActBlue()
google_sheets = GoogleSheets()

# Code

# Step 1: Specify name and permissions for the new Google Sheet
# A new spreadsheet with this name will be created, even if another spreadsheet with this name
# already exists. The Google Sheets connector will create the new spreadsheet, with 0 rows, and
# then overwrite the empty spreadsheet with your data. This script will not overwrite or update
# existing Google Sheets.
spreadsheet_name = "Contributions - January"

# This script will create a Google Sheet with Restriced permissions -- only people specifically
# added can open it. The account specifed in the Google credentials file will be the owner of
# the new spreadsheet. If you created a Service Account, the Service Account will be the owner.
# In this case, to receive a link to the spreadsheet and editor permissions, you must provide
# your email address. Once the sheet has been created you may add user permissions in Google Sheets.
editor_email = ""
if not editor_email:
    raise ValueError("editor_email is required to enable access to the new Google Sheet")

# Step 2: Specify what contribution data you want from ActBlue
date_range_start = "2022-01-01"  # Start of date range to withdraw contribution data (inclusive).
date_range_end = "2022-02-01"  # End of date range to withdraw contribution data (exclusive).
csv_type = "paid_contributions"
# csv_type options:
#     'paid_contributions':
#         contains paid, non-refunded contributions to the entity (campaign or organization) you
#         created the credential for, during the specified date range
#     'refunded_contributions':
#         contributions to your entity that were refunded, during the specified date range
#     'managed_form_contributions':
#         contributions made through any form that is managed by your entity, during the specified
#         date range - including contributions to other entities via that form if it is a tandem
#         form.

# Step 3: Retrieve data from ActBlue and hold it in a Parsons Table.
contribution_data = actblue.get_contributions(csv_type, date_range_start, date_range_end)

# Step 4: Create a spreadsheet on Google Sheets
sheet_id = google_sheets.create_spreadsheet(spreadsheet_name, editor_email=editor_email)
logger.info(f"Created a spreadsheet named {spreadsheet_name}.")

# Step 5: Send data from the Parsons Table to the Google Sheets spreadsheet
google_sheets.append_to_sheet(sheet_id, contribution_data)
logger.info("Completed transfer of data to Google Sheets.")
logger.info(f"Google will email {editor_email} with a link to the new Google Sheet.")
