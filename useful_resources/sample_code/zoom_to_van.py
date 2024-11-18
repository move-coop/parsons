# ### METADATA

# Connectors: Zoom, VAN
# Description: Adds Zoom attendees to VAN and applies an activist code.

# ### CONFIGURATION

# Set the configuration variables below or set environmental variables of the same name and
# leave these with empty strings.  We recommend using environmental variables if possible.

config_vars = {
    # Zoom Authentication
    "ZOOM_API_KEY": "",
    "ZOOM_API_SECRET": "",
    # Van Authentication
    "VAN_API_KEY": "",
}

VAN_DB = "MyCampaign"  # one of: MyMembers, EveryAction, MyCampaign (not MyVoters)
ACTIVIST_CODE_NAME = ""  # name of VAN activist code, which must be created manually in VAN
ZOOM_MEETING_ID = ""
MINIMUM_DURATION = 0  # filters out Zoom participants who stayed for less than minimum duration

# ### CODE

# Setup

import os  # noqa: E402
from parsons import VAN, Zoom  # noqa: E402

# if variables specified above, sets them as environmental variables
for name, value in config_vars.items():
    if value.strip() != "":
        os.environ[name] = value

# Code

zoom = Zoom()
van = VAN(db=VAN_DB)

# Gets participants from Zoom meeting
participants = zoom.get_past_meeting_participants(ZOOM_MEETING_ID)
filtered_participants = participants.select_rows(lambda row: row.duration > MINIMUM_DURATION)

# Coalesce the columns into something VAN expects
column_map = {
    "first_name": ["fn", "first", "firstname", "first name"],
    "last_name": ["ln", "last", "lastname", "last name"],
    "date_of_birth": ["dob", "date of birth", "birthday"],
    "email": ["email address", "email_address"],
    "street_number": ["street number", "street no.", "street no", "street #"],
    "street_name": ["street name", "street"],
    "phone": ["phone_number", "phone #", "phone_#", "phone no.", "phone no"],
    "zip": ["zip5", "zipcode", "zip code"],
}
filtered_participants.map_and_coalesce_columns(column_map)

# Gets activist code id given code name
activist_code_id = None
for code in van.get_activist_codes():
    if code["name"] == ACTIVIST_CODE_NAME:
        activist_code_id = code["activistCodeId"]

for participant in filtered_participants:
    # generates list of parameters from matched columns, only inlcudes if row has data for column
    params = {col: participant[col] for col in column_map.keys() if participant[col]}

    van_person = van.upsert_person(**params)  # updates if it finds a match, or inserts new user

    if activist_code_id:
        van.apply_activist_code(
            id=van_person["vanId"], activist_code_id=activist_code_id, id_type="vanid"
        )
