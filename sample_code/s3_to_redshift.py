import os
import logging
from parsons import Redshift, S3, utilities

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


bucket = os.environ['BUCKET']
schema = os.environ['SCHEMA']

keys = s3.list_keys(bucket)
files = keys.keys()

if len(keys) == 0:
    logger.info("No files to sync today!")
else:
    logger.info(f"Pulling {str(len(files))} files down from s3...")
    for x in files:
        file = s3.get_file(bucket, x)
        table = Table.from_csv(file, encoding="ISO-8859-1")
        table_name = f"schema.{x.replace('.csv', '')}"
        try:
            table.to_redshift(table_name, if_exists='truncate')
        except:
            table.to_redshift(table_name, if_exists='drop')
