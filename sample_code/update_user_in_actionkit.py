# Civis Container Link: https://platform.civisanalytics.com/spa/#/scripts/containers/33553735
import sys
import os
import datetime
import logging
from parsons import Redshift, Table, ActionKit

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

# ActionKit Setup - this assumes a Civis Platform Customo Credential parameter called "AK"
username = os.environ['AK_USERNAME']
password = os.environ['AK_PASSWORD']
domain = os.environ['AK_DOMAIN']
ak = ActionKit(domain=domain, username=username, password=password)

# Logging

logger = logging.getLogger(__name__)
_handler = logging.StreamHandler()
_formatter = logging.Formatter('%(levelname)s %(message)s')
_handler.setFormatter(_formatter)
logger.addHandler(_handler)
logger.setLevel('INFO')

# This example involves adding a voterbase_id (the Targetsmart ID) to a user in ActionKit

timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") #timestamp to be used for log table
loaded = [['id','voterbase_id','date_updated']] #column names for log table

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
