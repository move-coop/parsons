# ### METADATA

# Connectors: Redshift, VAN
# Description: Gets activist codes stored in redshift and applies to users in Van
# Parsons Version: unknown


# ### CONFIGURATION

# Set the configuration variables below or set environmental variables of the
# same name and leave these
# with empty strings.  We recommend using environmental variables if possible.

config_vars = {
    # Redshift
    "REDSHIFT_PORT": "",
    "REDSHIFT_DB": "",
    "REDSHIFT_HOST": "",
    "REDSHIFT_CREDENTIAL_USERNAME": "",
    "REDSHIFT_CREDENTIAL_PASSWORD": "",
    # Van
    "VAN_PASSWORD": "",
    "VAN_DB_NAME": "",
}


# ### CODE

from parsons import Table, Redshift, VAN  # noqa E402
from parsons import logger  # noqa E402
import os  # noqa E402

# Setup

for name, value in config_vars.items():  # sets variables if provided in this script
    if value.strip() != "":
        os.environ[name] = value

rs = Redshift()  # just create Redshift() - VAN connector is created dynamically below

# Create dictionary of VAN states and API keys from multiline Civis credential

myv_states = {x.split(",")[0]: x.split(",")[1] for x in os.environ["VAN_PASSWORD"].split("\r\n")}
myv_keys = {k: VAN(api_key=v, db=os.environ["VAN_DB_NAME"]) for k, v in myv_states.items()}

# Create simple set of states for insertion into SQL
states = "','".join(list(myv_keys))

# SQL to pull those needing Activist Code
sql = f"""
SELECT vb_smartvan_id
    , vb_vf_source_state
    , hash
    , activist_code_id
FROM schema.table
WHERE vb_vf_source_state IN ({states})
"""

records = rs.query(sql)

logger.info(f"Applying Activist Codes to {str(records.num_rows)} records...")

# Apply codes segmented by state (different API Keys)
for state, key in myv_keys.items():
    state_set = records.select_rows(lambda row: row.vb_vf_source_state == state)
    if len(state_set) > 0:
        logger.info(f"Applying {str(len(state_set))} Activist Codes in {state}...")
        for vanid in state_set:
            # TODO: row undefined, select row form record?
            row = None
            key.toggle_activist_code(row["vb_smartvan_id"], row["activist_code_id"], "apply")
