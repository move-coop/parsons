from parsons import Redshift, S3, Table
import os

# Redshift setup - this assumes a Civis Platform parameter called "REDSHIFT"

set_env_var(os.environ['REDSHIFT_PORT'])
set_env_var(os.environ['REDSHIFT_DB'])
set_env_var(os.environ['REDSHIFT_HOST'])
set_env_var(os.environ['REDSHIFT_CREDENTIAL_USERNAME'])
set_env_var(os.environ['REDSHIFT_CREDENTIAL_PASSWORD'])

# AWS setup - this assumes a Civis Platform parameter called "AWS

set_env_var('S3_TEMP_BUCKET', 'parsons-tmc')
set_env_var('AWS_ACCESS_KEY_ID', os.environ['AWS_USERNAME'])
set_env_var('AWS_SECRET_ACCESS_KEY', os.environ['AWS_PASSWORD'])

# Other parameter setup based on Civis Platform

query = os.environ['QUERY']
bucket = os.environ['S3_BUCKET']
key = os.environ['S3_KEY']

# Logging 

logger = logging.getLogger(__name__)
_handler = logging.StreamHandler()
_formatter = logging.Formatter('%(levelname)s %(message)s')
_handler.setFormatter(_formatter)
logger.addHandler(_handler)
logger.setLevel('INFO')

# Let's run some code...

rs = Redshift()
s3 = S3()

if s3.bucket_exists(bucket):
    logger.info(f"{bucket} exists and we have access...")
    file = rs.query(query)
    file.to_s3_csv(bucket,key,aws_access_key_id,aws_secret_access_key)
    logger.info(f"{key} successfully loaded to {bucket}...")
else:
    logger.info(f"{bucket} does not exist or you do not have permission to access it.")
