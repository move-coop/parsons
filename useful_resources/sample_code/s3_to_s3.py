### METADATA

# Connectors: S3
# Description: Gets files from vendor s3 bucket and moves to own S3 bucket


### CONFIGURATION

# Set the configuration variables below or set environmental variables of the same name and leave these
# with empty strings.  We recommend using environmental variables if possible.

config_vars = {
        # S3 (source) (note: this assumes a Civis Platform parameter called "AWS")
        "S3_TEMP_BUCKET": "",
        "AWS_ACCESS_KEY_ID": "",
        "AWS_SECRET_ACCESS_KEY": "",
        # S3 (vendor) (note: this assumes a Civis Platform parameter called "AWS_VENDOR")
        'AWS_VENDOR_SECRET_ACCESS_KEY': "",
        'AWS_VENDOR_ACCESS_KEY_ID': ""
}

DESTINATION_BUCKET = None    


### CODE

import os
import logging
from parsons import Redshift, S3, utilities

# Setup 

for name, value in config_vars.items():    # sets variables if provided in this script
    if value.strip() != "":
        os.environ[name] = value

s3 = S3()
s3_vendor = S3(os.environ['AWS_VENDOR_ACCESS_KEY_ID'], os.environ['AWS_VENDOR_SECRET_ACCESS_KEY'])

# Logging

logger = logging.getLogger(__name__)
_handler = logging.StreamHandler()
_formatter = logging.Formatter('%(levelname)s %(message)s')
_handler.setFormatter(_formatter)
logger.addHandler(_handler)
logger.setLevel('INFO')

# Let's write some code!

# Get Vendor Bucket Information
bucket_guide = s3_vendor.list_buckets()
logger.info(f"We will be getting data from {len(bucket_guide)} buckets...")

# Moving Files from Vendor s3 Bucket to Destination s3 Bucket
for bucket in bucket_guide:

    logger.info(f"Working on files for {bucket}...")
    keys = s3_vendor.list_keys(bucket)
    logger.info(f"Found {len(keys)}.")
    for key in keys:
        temp_file = s3_vendor.get_file(bucket, key)
        tmc_key = f"vendor_exports/{bucket}/{key}"
        s3.put_file(DESTINATION_BUCKET, tmc_key, temp_file)
        utilities.files.close_temp_file(temp_file)
