### METADATA

# Connectors: Redshift, S3
# Description: Moves files from S3 to Reshift


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
    # S3  (note: this assumes a Civis Platform parameter called "AWS")
    "S3_TEMP_BUCKET": "",
    "AWS_ACCESS_KEY_ID": "",
    "AWS_SECRET_ACCESS_KEY": "",
    "BUCKET": ""    # FIXME: how does this differ from S3_TEMP_BUCKET?
}


### CODE

import os, logging
from parsons import Redshift, S3, utilities

# Setup

for name, value in config_vars.items():    # sets variables if provided in this script
    if value.strip() != "":
        os.environ[name] = value

rs = Redshift()
s3 = S3()

# Logging

logger = logging.getLogger(__name__)
_handler = logging.StreamHandler()
_formatter = logging.Formatter('%(levelname)s %(message)s')
_handler.setFormatter(_formatter)
logger.addHandler(_handler)
logger.setLevel('INFO')

# Code

bucket = os.environ['BUCKET']
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
        utilities.files.close_temp_file(file)
