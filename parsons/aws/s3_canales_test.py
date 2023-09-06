# import parsons.aws.s3
from s3 import S3

AWS_ACCESS_KEY_ID = 'AKIARJVLBM6AZYDCUQ7Y'

AWS_SECRET_ACCESS_KEY = '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'
bucket = 'tmc-internal'
s3 = S3(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

output = s3.process_s3_keys(bucket=bucket, incoming_prefix='test-incoming',
                            processing_prefix='test-processing', dest_prefix='test-dest')
print(output)
# buckets = s3.get_buckets_with_subname('actblue')
# print(buckets)
# aws_access_key_id = 'tmc-engineering-sharinef'
# aws_secret_access_key = 'cmt.cpu_xum3CNU*uyx'

# s3 = S3()
