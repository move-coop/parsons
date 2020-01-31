import os
import logging
from parsons import utilities
from parsons.aws import S3
from parsons.databases.redshift import Redshift

# Redshift setup - this assumes a Civis Platform parameter called "REDSHIFT"

set_env_var(os.environ['REDSHIFT_PORT'])
set_env_var(os.environ['REDSHIFT_DB'])
set_env_var(os.environ['REDSHIFT_HOST'])
set_env_var(os.environ['REDSHIFT_CREDENTIAL_USERNAME'])
set_env_var(os.environ['REDSHIFT_CREDENTIAL_PASSWORD'])
rs = Redshift()

# AWS setup - this assumes a Civis Platform parameter called "AWS"

set_env_var('S3_TEMP_BUCKET', 'parsons-tmc')
set_env_var('AWS_ACCESS_KEY_ID', os.environ['AWS_USERNAME'])
set_env_var('AWS_SECRET_ACCESS_KEY', os.environ['AWS_PASSWORD'])
s3 = S3()

# 2nd AWS setup - this assumes a Civis Platform parameter called "AWS_VENDOR"
s3_vendor = S3(os.environ['AWS_VENDOR_ACCESS_KEY_ID'],
            os.environ['AWS_VENDOR_SECRET_ACCESS_KEY'])

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

# Define Destination Bucket
dest_bucket = 'tmc-data'

# Moving Files from Vendor s3 Bucket to Destination s3 Bucket
for bucket in bucket_guide:

    logger.info(f"Working on files for {bucket}...")
    keys = s3_vendor.list_keys(bucket)
    logger.info(f"Found {len(keys)}.")
    for key in keys:
        temp_file = s3_vendor.get_file(bucket, key)
        tmc_key = f"vendor_exports/{bucket}/{key}"
        s3.put_file(dest_bucket, tmc_key, temp_file)
        utilities.files.close_temp_file(temp_file)
