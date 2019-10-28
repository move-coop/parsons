from parsons import Table, Redshift, VAN
import logging
import os

# Redshift setup - this assumes a Civis Platform parameter called "REDSHIFT"

set_env_var(os.environ['REDSHIFT_PORT'])
set_env_var(os.environ['REDSHIFT_DB'])
set_env_var(os.environ['REDSHIFT_HOST'])
set_env_var(os.environ['REDSHIFT_CREDENTIAL_USERNAME'])
set_env_var(os.environ['REDSHIFT_CREDENTIAL_PASSWORD'])
rs = Redshift()

# AWS setup - this assumes a Civis Platform parameter called "AWS"

set_env_var('S3_TEMP_BUCKET', 'parsons-tmc')
set_env_var('AWS_ACCESS_KEY_ID', os.environ['AWS_ACCESS_KEY_ID'])
set_env_var('AWS_SECRET_ACCESS_KEY', os.environ['AWS_SECRET_ACCESS_KEY'])
s3 = S3()

# Logging

logger = logging.getLogger(__name__)
_handler = logging.StreamHandler()
_formatter = logging.Formatter('%(levelname)s %(message)s')
_handler.setFormatter(_formatter)
logger.addHandler(_handler)
logger.setLevel('INFO')

# Create dictionary of VAN states and API keys from multiline Civis credential

myv_states = {x.split(",")[0]: x.split(",")[1] for x in os.environ['VAN_PASSWORD'].split("\r\n")}
myv_keys = {k: VAN(api_key=v, db='MyVoters') for k,v in myv_states.items()}

# Create simple set of states for insertion into SQL
states = "','".join([s for s in myv_keys])

# SQL to pull those needing Activist Code
sql = f"""
SELECT vb_smartvan_id
    , vb_vf_source_state
    , hash
    , activist_code_id
FROM schema.table
"""

records = rs.query(sql)

logger.info(f"Applying Activist Codes to {str(records.num_rows)} records...")

# Apply codes segmented by state (different API Keys)
for state, key in myv_keys.items():
    state_set = records.select_rows(lambda row: row.vb_vf_source_state == state)
    if len(state_set) > 0:
      logger.info(f"Applying {str(len(state_set))} Activist Codes in {state}...")
      for vanid in state_set:
          key.toggle_activist_code(row['vb_smartvan_id'], row['activist_code_id'], 'apply')
