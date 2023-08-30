import re
import boto3
from botocore.client import ClientError
from parsons.databases.redshift.redshift import Redshift
from parsons.utilities import files
import logging
import os
import random
import datetime

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
                if (
                    date_modified_before
                    and not key["LastModified"] < date_modified_before
                ):
                    continue

                if (
                    date_modified_after
                    and not key["LastModified"] > date_modified_after
                ):
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

    def put_file(
        self, bucket, key, local_path, acl="bucket-owner-full-control", **kwargs
    ):
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

        self.client.upload_file(
            local_path, bucket, key, ExtraArgs={"ACL": acl, **kwargs}
        )

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
            self.client.copy(
                copy_source, destination_bucket, dest_key, ExtraArgs=kwargs
            )
            if remove_original:
                try:
                    self.remove_file(origin_bucket, origin_key)
                except Exception as e:
                    logger.error("Failed to delete original key: " + str(e))

            if public_read:
                object_acl = self.s3.ObjectAcl(destination_bucket, destination_key)
                object_acl.put(ACL="public-read")

        logger.info(f"Finished syncing {len(key_list)} keys")

    def get_buckets_type(self, regex):
        """
        Grabs a type of bucket based on naming convention.

        `Args:`
            regex: str
                This will most commonly be 'member' or 'vendor'

        `Returns:`
            list
                list of buckets

        """

        all_buckets = self.list_buckets()
        buckets = [x for x in all_buckets if regex in x.split('-')]

        return buckets

    def s3_to_redshift(
        self,
        bucket,
        key,
        rs_table,
        if_exists="truncate",
        delimiter="tab",
        errors=10,
        truncate_columns=True,
    ):
        """
        Moves a tab-delimited file from s3 to Redshift.

        `Args:`

            bucket: str
                S3 bucket

            key: str
                S3 key

            rs_table: str
                Redshift table. This MUST EXIST already.

            if_exists: str
                options are: "drop", "append", "truncate", "fail"

            delimiter: str
                options are "tab" and "pipe"

            errors: int
                the amount of errors you are willing to accept

            truncatecolumns: bool
                if you want to truncate long running text

        Returns:
            None
        """

        rs = Redshift()

        if ".zip" in key:
            raise Exception(".zip files won't work with copy. We need unzipped or GZIP.")

        full_key = f"s3://{bucket}/{key}"
        logger.info(f"Starting download of {full_key}...")
        zip = "gzip" if ".gz" in key else ""

        if delimiter == "tab":
            delimiter_line = "delimiter '\t'"
        elif delimiter == "pipe":
            delimiter_line = "CSV delimiter '|'"
        elif delimiter == "comma":
            delimiter_line = "CSV"
        else:
            raise Exception("ERROR: Your options here are tab, pipe, or comma.")

        if truncate_columns:
            truncate = "TRUNCATECOLUMNS"
        else:
            truncate = ""

        if rs.table_exists(rs_table):
            if if_exists == "fail":
                raise Exception("Table already exists, and you said fail. Maybe try drop?")
            elif if_exists in ["drop", "truncate"]:
                copy_query = f"truncate {rs_table};"
                copy_table = rs_table
                copy_query_end = None
            elif if_exists == "append":
                copy_table = f"{rs_table}_temp"
                copy_query = f"drop table if exists {copy_table}; create table {copy_table} (like {rs_table});"
                copy_query_end = f"insert into {rs_table} (select * from {copy_table})"
            else:
                raise Exception(
                    "You chose an option that is not 'fail','truncate','append', or 'drop'."
                )
            copy_query += f"""
                -- Load the data
                copy {copy_table} from '{full_key}'
                credentials 'aws_access_key_id={self.aws_access_key_id};aws_secret_access_key={self.aws_secret_access_key}'
                emptyasnull
                blanksasnull
                ignoreheader 1
                {delimiter_line}
                acceptinvchars
                {zip}
                maxerror {errors}
                COMPUPDATE true
                {truncate}
                ;
            """
            logger.info(f"copying from s3 into {copy_table}...")
            rs.query(copy_query)

            if copy_query_end:
                logger.info(f"inserting {copy_table} into {rs_table}...")
                rs.query(copy_query_end)
                rs.query(f"drop table if exists {copy_table};")

        else:
            raise Exception("ERROR: You need to have a table already created to copy into.")

        return None

    def drop_and_save(
        self,
        rs_table,
        bucket,
        key,
        cascade=True,
        manifest=True,
        header=True,
        delimiter="|",
        compression="gzip",
        add_quotes=True,
        escape=True,
        allow_overwrite=True,
        parallel=True,
        max_file_size="6.2 GB",
        aws_region=None,
    ):
        """
        Unload data to s3, and then drop Redshift table

        Args:
            rs_table: str
                Redshift table.

            bucket: str
                S3 bucket

            key: str
                S3 key prefix ahead of table name

            cascade: bool
                whether to drop cascade

            ***unload params

        Returns:
            None
        """

        rs = Redshift()

        query_end = "cascade" if cascade else ""

        rs.unload(
            sql=f"select * from {rs_table}",
            bucket=bucket,
            key_prefix=f"{key}/{rs_table.replace('.','_')}/",
            manifest=manifest,
            header=header,
            delimiter=delimiter,
            compression=compression,
            add_quotes=add_quotes,
            escape=escape,
            allow_overwrite=allow_overwrite,
            parallel=parallel,
            max_file_size=max_file_size,
            aws_region=aws_region,
        )

        rs.query(f"drop table if exists {rs_table} {query_end}")

        return None

    def process_s3_keys(
        s3,
        bucket,
        incoming_prefix,
        processing_prefix,
        dest_prefix,
        extension=None,
        key_limit=None,
        key_offset=0,
    ):
        """
        Process the keys in an S3 bucket under a specific prefix.

        `Args:`
            s3: object
                The S3 connector to use.
            incoming_prefix: str
                The prefix to use to search for keys to process.
            processing_prefix:  str
                The prefix to put files under as they are being processed.
            dest_prefix: str
                The S3 prefix where the files should be put after processing.
            extension: str
                `Optional:` The extension of files to look for
            key_limit: int
                `Optional:` The max number of keys to process; if not specified, will process
                all keys
            key_offset: int
                `Optional:` The offset from the first key found to start processing from; if not
                specified, defaults to the first key
        `Return:`
            A list of the final location of all processed keys.
        """
        logger.info("Moving any keys from previous runs back to incoming")
        merged_regex = re.compile(f"^{processing_prefix}/\\d+/(.+)$")

        previous_keys = s3.list_keys(bucket, processing_prefix)
        logger.info("Found %d keys left over from previous runs", len(previous_keys))

        for key in previous_keys:
            match = merged_regex.match(key)
            if match:
                remainder = match.group(1)
                destination = f"{incoming_prefix}/{remainder}"
                logger.info("Moving %s back to %s", key, destination)
                s3.transfer_bucket(bucket, key, bucket, destination, remove_original=True)
            else:
                logger.warning("Could not match processing key to expected regex: %s", key)

        all_keys = s3.list_keys(bucket, incoming_prefix, suffix=extension)

        if key_limit:
            all_keys = all_keys[key_offset: key_offset + key_limit]

        job_id = f"{random.randrange(0, 100000):06}"
        random_processing_prefix = f"{processing_prefix}/{job_id}"

        logger.info(
            "Found %s keys in bucket %s under prefix %s with suffix %s",
            len(all_keys),
            bucket,
            incoming_prefix,
            extension,
        )

        moved_keys = []
        for from_key in all_keys:
            dest_key = from_key.replace(incoming_prefix, random_processing_prefix)
            s3.transfer_bucket(bucket, from_key, bucket, dest_key)
            s3.remove_file(bucket, from_key)
            moved_keys.append(dest_key)

        for key in moved_keys:
            yield key

        date = datetime.datetime.now()
        date_string = date.strftime("%Y%m%d")
        dated_dest_prefix = f"{dest_prefix}/{date_string}"

        final_keys = []
        for from_key in moved_keys:
            dest_key = from_key.replace(random_processing_prefix, dated_dest_prefix)
            s3.transfer_bucket(bucket, from_key, bucket, dest_key)
            s3.remove_file(bucket, from_key)
            final_keys.append(dest_key)

        return final_keys
