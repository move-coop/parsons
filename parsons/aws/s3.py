import re
import boto3
from botocore.client import ClientError

from parsons.utilities import files
import logging
import os

logger = logging.getLogger(__name__)


class AWSConnection(object):
    def __init__(
        self,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        aws_session_token=None,
        use_env_token=True,
    ):
        # Order of operations for searching for keys:
        #   1. Look for keys passed as kwargs
        #   2. Look for env variables
        #   3. Look for aws config file
        # Boto3 handles 2 & 3, but should handle 1 on it's own. Not sure
        # why that's not working.

        if aws_access_key_id and aws_secret_access_key:
            # The AWS session token isn't needed most of the time, so we'll check
            # for the env variable here instead of requiring it to be passed
            # whenever the aws_access_key_id and aws_secret_access_key are passed.

            if aws_session_token is None and use_env_token:
                aws_session_token = os.getenv("AWS_SESSION_TOKEN")

            self.session = boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_session_token=aws_session_token,
            )

        else:
            self.session = boto3.Session()


class S3(object):
    """
    Instantiate the S3 class.

    `Args:`
        aws_access_key_id: str
            The AWS access key id. Not required if the ``AWS_ACCESS_KEY_ID`` env variable
            is set.
        aws_secret_access_key: str
            The AWS secret access key. Not required if the ``AWS_SECRET_ACCESS_KEY`` env
            variable is set.
        aws_session_token: str
            The AWS session token. Optional. Can also be stored in the ``AWS_SESSION_TOKEN``
            env variable. Used for accessing S3 with temporary credentials.
        use_env_token: boolean
            Controls use of the ``AWS_SESSION_TOKEN`` environment variable. Defaults
            to ``True``. Set to ``False`` in order to ignore the ``AWS_SESSION_TOKEN`` environment
            variable even if the ``aws_session_token`` argument was not passed in.

    `Returns:`
        S3 class.
    """

    def __init__(
        self,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        aws_session_token=None,
        use_env_token=True,
    ):
        self.aws = AWSConnection(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            use_env_token=use_env_token,
        )

        self.s3 = self.aws.session.resource("s3")
        """Boto3 API Session Resource object. Use for more advanced boto3 features."""

        self.client = self.s3.meta.client
        """Boto3 API Session client object. Use for more advanced boto3 features."""

    def list_buckets(self):
        """
        List all buckets to which you have access.

        `Returns:`
            list
        """

        return [bucket.name for bucket in self.s3.buckets.all()]

    def bucket_exists(self, bucket):
        """
        Determine if a bucket exists and you have access to it.

        `Args:`
            bucket: str
                The bucket name
        `Returns:`
            boolean
                ``True`` if the bucket exists and ``False`` if not.
        """

        try:
            # If we can list the keys, the bucket definitely exists. We do this check since
            # it will account for buckets that live on other AWS accounts and that we
            # have access to.
            self.list_keys(bucket)
            return True
        except Exception:
            pass

        return bucket in self.list_buckets()

    def list_keys(
        self,
        bucket,
        prefix=None,
        suffix=None,
        regex=None,
        date_modified_before=None,
        date_modified_after=None,
        **kwargs,
    ):
        """
        List the keys in a bucket, along with extra info about each one.

        `Args:`
            bucket: str
                The bucket name
            prefix: str
                Limits the response to keys that begin with the specified prefix.
            suffix: str
                Limits the response to keys that end with specified suffix
            regex: str
                Limits the reponse to keys that match a regex pattern
            date_modified_before: datetime.datetime
                Limits the response to keys with date modified before
            date_modified_after: datetime.datetime
                Limits the response to keys with date modified after
            kwargs:
                Additional arguments for the S3 API call. See `AWS ListObjectsV2 documentation
                <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.list_objects_v2>`_
                for more info.
        `Returns:`
            dict
                Dict mapping the keys to info about each key. The info includes 'LastModified',
                'Size', and 'Owner'.
        """

        keys_dict = dict()
        logger.debug(f"Fetching keys in {bucket} bucket")

        continuation_token = None

        while True:
            args = {"Bucket": bucket}

            if prefix:
                args["Prefix"] = prefix

            if continuation_token:
                args["ContinuationToken"] = continuation_token

            args.update(kwargs)

            try:
                resp = self.client.list_objects_v2(**args)

            except ClientError as e:
                error_message = """Unable to list bucket objects!
                This may be due to a lack of permission on the requested
                bucket. Double-check that you have sufficient READ permissions
                on the bucket you've requested. If you only have permissions for
                keys within a specific prefix, make sure you include a trailing '/' in
                in prefix."""

                logger.error(error_message)

                raise e

            for key in resp.get("Contents", []):
                # Match suffix
                if suffix and not key["Key"].endswith(suffix):
                    continue

                # Regex matching
                if regex and not bool(re.search(regex, key["Key"])):
                    continue

                # Match timestamp parsing
                if date_modified_before and not key["LastModified"] < date_modified_before:
                    continue

                if date_modified_after and not key["LastModified"] > date_modified_after:
                    continue

                # Convert date to iso string
                key["LastModified"] = key["LastModified"].isoformat()

                # Add to output dict
                keys_dict[key.get("Key")] = key

            # If more than 1000 results, continue with token
            if resp.get("NextContinuationToken"):
                continuation_token = resp["NextContinuationToken"]

            else:
                break

        logger.debug(f"Retrieved {len(keys_dict)} keys")

        return keys_dict

    def key_exists(self, bucket, key):
        """
        Determine if a key exists in a bucket.

        `Args:`
            bucket: str
                The bucket name
            key: str
                The object key
        `Returns:`
            boolean
                ``True`` if key exists and ``False`` if not.
        """

        key_count = len(self.list_keys(bucket, prefix=key))

        if key_count > 0:
            logger.debug(f"Found {key} in {bucket}.")
            return True
        else:
            logger.debug(f"Did not find {key} in {bucket}.")
            return False

    def create_bucket(self, bucket):
        """
        Create an s3 bucket.

        .. warning::
            S3 has a limit on the number of buckets you can create in an AWS account, and
            that limit is fairly low (typically 100). If you are creating buckets frequently,
            you may be mis-using S3, and should consider using the same bucket for multiple tasks.
            There is no limit on the number of objects in a bucket.
            See `AWS bucket restrictions
            <https://docs.aws.amazon.com/AmazonS3/latest/dev/BucketRestrictions.html>`_ for more
            info.

        .. warning::
            S3 bucket names are *globally* unique. So when creating a new bucket,
            the name can't collide with any existing bucket names. If the provided name does
            collide, you'll see errors like `IllegalLocationConstraintException` or
            `BucketAlreadyExists`.

        `Args:`
            bucket: str
                The name of the bucket to create
        `Returns:`
            ``None``
        """

        self.client.create_bucket(Bucket=bucket)

    def put_file(self, bucket, key, local_path, acl="bucket-owner-full-control", **kwargs):
        """
        Uploads an object to an S3 bucket

        `Args:`
            bucket: str
                The bucket name
            key: str
                The object key
            local_path: str
                The local path of the file to upload
            acl: str
                The S3 permissions on the file
            kwargs:
                Additional arguments for the S3 API call. See `AWS Put Object documentation
                <https://docs.aws.amazon.com/AmazonS3/latest/API/RESTObjectPUT.html>`_ for more
                info.
        """

        self.client.upload_file(local_path, bucket, key, ExtraArgs={"ACL": acl, **kwargs})

    def remove_file(self, bucket, key):
        """
        Deletes an object from an S3 bucket

        `Args:`
            bucket: str
                The bucket name
            key: str
                The object key
        `Returns:`
            ``None``
        """

        self.client.delete_object(Bucket=bucket, Key=key)

    def get_file(self, bucket, key, local_path=None, **kwargs):
        """
        Download an object from S3 to a local file

        `Args:`
            local_path: str
                The local path where the file will be downloaded. If not specified, a temporary
                file will be created and returned, and that file will be removed automatically
                when the script is done running.
            bucket: str
                The bucket name
            key: str
                The object key
            kwargs:
                Additional arguments for the S3 API call. See `AWS download_file documentation
                <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.download_file>`_
                for more info.

        `Returns:`
            str
                The path of the new file
        """

        if not local_path:
            local_path = files.create_temp_file_for_path(key)

        self.s3.Object(bucket, key).download_file(local_path, ExtraArgs=kwargs)

        return local_path

    def get_url(self, bucket, key, expires_in=3600):
        """
        Generates a presigned url for an s3 object.

        `Args:`
            bucket: str
                The bucket name
            key: str
                The object name
            expires_in: int
                The time, in seconds, until the url expires
        `Returns:`
            Url:
                A link to download the object
        """

        return self.client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires_in,
        )

    def transfer_bucket(
        self,
        origin_bucket,
        origin_key,
        destination_bucket,
        destination_key=None,
        suffix=None,
        regex=None,
        date_modified_before=None,
        date_modified_after=None,
        public_read=False,
        remove_original=False,
        **kwargs,
    ):
        """
        Transfer files between s3 buckets

        `Args:`
            origin_bucket: str
                The origin bucket
            origin_key: str
                The origin file or prefix
            destination_bucket: str
                The destination bucket
            destination_key: str
                If `None` then will retain the `origin key`. If set to prefix will move all
                to new prefix
            suffix: str
                Limits the response to keys that end with specified suffix
            regex: str
                Limits the reponse to keys that match a regex pattern
            date_modified_before: datetime.datetime
                Limits the response to keys with date modified before
            date_modified_after: datetime.datetime
                Limits the response to keys with date modified after
            public_read: bool
                If the keys should be set to `public-read`
            remove_original: bool
                If the original keys should be removed after transfer
            kwargs:
                Additional arguments for the S3 API call. See `AWS download_file docs
                <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.copy>`_
                for more info.
        `Returns:`
            ``None``
        """

        # If prefix, get all files for the prefix
        if origin_key.endswith("/"):
            resp = self.list_keys(
                origin_bucket,
                prefix=origin_key,
                suffix=suffix,
                regex=regex,
                date_modified_before=date_modified_before,
                date_modified_after=date_modified_after,
            )
            key_list = [value["Key"] for value in resp.values()]
        else:
            key_list = [origin_key]

        for key in key_list:
            # If destination_key is prefix, replace
            if destination_key and destination_key.endswith("/"):
                dest_key = key.replace(origin_key, destination_key)

            # If single destination, use destination key
            elif destination_key:
                dest_key = destination_key

            # Else use key from original source
            else:
                dest_key = key

            copy_source = {"Bucket": origin_bucket, "Key": key}
            self.client.copy(copy_source, destination_bucket, dest_key, ExtraArgs=kwargs)
            if remove_original:
                try:
                    self.remove_file(origin_bucket, origin_key)
                except Exception as e:
                    logger.error("Failed to delete original key: " + str(e))

            if public_read:
                object_acl = self.s3.ObjectAcl(destination_bucket, destination_key)
                object_acl.put(ACL="public-read")

        logger.info(f"Finished syncing {len(key_list)} keys")

    def get_buckets_with_subname(self, bucket_subname):
        """
        Grabs a type of bucket based on naming convention.

        `Args:`
            subname: str
                This will most commonly be a 'vendor'

        `Returns:`
            list
                list of buckets

        """

        all_buckets = self.list_buckets()
        buckets = [x for x in all_buckets if bucket_subname in x.split("-")]

        return buckets
