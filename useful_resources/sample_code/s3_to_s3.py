# ### METADATA

# Connectors: S3
# Description: Gets files from source s3 bucket and moves to destination S3 bucket
# Parsons Version: unknown


# ### CONFIGURATION

# Set the configuration variables below or set environmental variables of the same name and leave
# these with empty strings.  We recommend using environmental variables if possible.

config_vars = {
    # S3 (source)
    "AWS_SOURCE_ACCESS_KEY_ID": "",
    "AWS_SOURCE_SECRET_ACCESS_KEY": "",
    # S3 (destination)
    "AWS_DESTINATION_SECRET_ACCESS_KEY": "",
    "AWS_DESTINATION_ACCESS_KEY_ID": "",
}

DESTINATION_BUCKET = None


# ### CODE

import os  # noqa: E402
from parsons import S3, utilities, logger  # noqa: E402

# Setup

for name, value in config_vars.items():  # sets variables if provided in this script
    if value.strip() != "":
        os.environ[name] = value

s3_source = S3(os.environ["AWS_SOURCE_ACCESS_KEY_ID"], os.environ["AWS_SOURCE_SECRET_ACCESS_KEY"])
s3_destination = S3(
    os.environ["AWS_DESTINATION_ACCESS_KEY_ID"],
    os.environ["AWS_DESTINATION_SECRET_ACCESS_KEY"],
)

# Let's write some code!

# Get Source Bucket Information
bucket_guide = s3_source.list_buckets()
logger.info(f"We will be getting data from {len(bucket_guide)} buckets...")

# Moving Files from Source s3 Bucket to Destination s3 Bucket
for bucket in bucket_guide:
    logger.info(f"Working on files for {bucket}...")
    keys = s3_source.list_keys(bucket)
    logger.info(f"Found {len(keys)}.")
    for key in keys:
        temp_file = s3_source.get_file(bucket, key)
        s3_destination.put_file(DESTINATION_BUCKET, key, temp_file)
        utilities.files.close_temp_file(temp_file)
