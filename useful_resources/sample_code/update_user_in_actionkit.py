# ### METADATA

# Connectors: Redshift, ActionKit
# Description: Adds a voterbase_id (the Targetsmart ID) to users in ActionKit
# Parsons Version: unknown


# ### CONFIGURATION

# Set the configuration variables below or set environmental variables of the same name and leave
# these with empty strings.  We recommend using environmental variables if possible.

config_vars = {
    # Redshift
    "REDSHIFT_PORT": "",
    "REDSHIFT_DB": "",
    "REDSHIFT_HOST": "",
    "REDSHIFT_CREDENTIAL_USERNAME": "",
    "REDSHIFT_CREDENTIAL_PASSWORD": "",
    # ActionKit
    "AK_USERNAME": "",
    "AK_PASSWORD": "",
    "AK_DOMAIN": "",
}

# ### CODE

import os  # noqa: E402
import datetime  # noqa: E402
from parsons import Redshift, Table, ActionKit, logger  # noqa: E402

# Setup

for name, value in config_vars.items():  # sets variables if provided in this script
    if value.strip() != "":
        os.environ[name] = value

rs = Redshift()
ak = ActionKit()

# This example involves adding a voterbase_id (the Targetsmart ID) to a user in ActionKit

# timestamp to be used for log table
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

loaded = [["id", "voterbase_id", "date_updated"]]  # column names for log table

source_table = "schema.table"  # this is the table with the information I'm pushing to ActionKit

# this is where we will log every user id that gets marked with a voterbase_id
log_table = "schema.table"

logger.info("Running query to get matches...")
query = """
    select distinct id, voterbase_id
    from {source_table}
    left join {log_table} using (id, voterbase_id)
    where voterbase_id is not null and date_updated is null
    """

source_data = rs.query(query)

if source_data.num_rows > 0:
    logger.info(f"Will be updating voterbase_id for {source_data.num_rows}...")
    for row in source_data:
        user = ak.get_user(user_id=row["id"])
        user_dict = {"fields": {"vb_voterbase_id": row["voterbase_id"]}}
        update_user = ak.update_user(user_id=row["id"], **user_dict)
        user = ak.get_user(user_id=row["id"])
        if user["fields"]["vb_voterbase_id"] == row["voterbase_id"]:
            loaded.append([row["id"], row["voterbase_id"], timestamp])

    logger.info("Done with loop! Loading into log table...")
    Table(loaded).to_redshift(log_table, if_exists="append")

else:
    logger.info("No one to update today...")
