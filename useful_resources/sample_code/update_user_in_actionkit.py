### METADATA

# Connectors: Redshift, ActionKit
# Description: Adds a voterbase_id (the Targetsmart ID) to users in ActionKit


### CONFIGURATION

# Set the configuration variables below or set environmental variables of the same name and leave these
# with empty strings.  We recommend using environmental variables if possible.

config_vars = {
    # Redshift  (note: this assumes a Civis Platform parameter called "REDSHIFT")
    "REDSHIFT_PORT": "",
    "REDSHIFT_DB": "",
    "REDSHIFT_HOST": "",
    "REDSHIFT_CREDENTIAL_USERNAME": "",
    "REDSHIFT_CREDENTIAL_PASSWORD": "",
    # ActionKit  (note: this assumes a Civis Platform Customo Credential parameter called "AK")
    "AK_USERNAME": "",
    "AK_PASSWORD": "",
    "AK_DOMAIN": ""
}

### CODE

# Civis Container Link: https://platform.civisanalytics.com/spa/#/scripts/containers/33553735

import sys, os, datetime, logging
from parsons import Redshift, Table, ActionKit

# Setup

for name, value in config_vars.items():    # sets variables if provided in this script
    if value.strip() != "":
        os.environ[name] = value

rs = Redshift()
ak = ActionKit()

# Logging

logger = logging.getLogger(__name__)
_handler = logging.StreamHandler()
_formatter = logging.Formatter('%(levelname)s %(message)s')
_handler.setFormatter(_formatter)
logger.addHandler(_handler)
logger.setLevel('INFO')

# This example involves adding a voterbase_id (the Targetsmart ID) to a user in ActionKit

timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") # timestamp to be used for log table
loaded = [['id','voterbase_id','date_updated']] # column names for log table

source_table = 'schema.table' # this is the table with the information I'm pushing to ActionKit
log_table = 'schema.table' # this is where we will log every user id that gets marked with a voterbase_id

logger.info("Running query to get matches...")
query = '''
    select distinct id, voterbase_id
    from {source_table}
    left join {log_table} using (id, voterbase_id)
    where voterbase_id is not null and date_updated is null
    '''

source_data = rs.query(query)

if source_data.num_rows > 0:
    logger.info(f"Will be updating voterbase_id for {source_data.num_rows}...")
    for row in source_data:
        user = ak.get_user(user_id=row['id'])
        user_dict = {"fields": {"vb_voterbase_id": row['voterbase_id']}}
        update_user = ak.update_user(user_id=row['id'], **user_dict)
        user = ak.get_user(user_id=row['id'])
        if user['fields']['vb_voterbase_id'] == row['voterbase_id']:
            loaded.append([row['id'], row['voterbase_id'],timestamp])

    logger.info("Done with loop! Loading into log table...")
    Table(loaded).to_redshift(log_table,if_exists='append')

else:
    logger.info(f"No one to update today...")
