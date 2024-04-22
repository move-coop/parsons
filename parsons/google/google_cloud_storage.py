import datetime
import gzip
import petl
import logging
import time
import uuid
import zipfile
from typing import Optional

import google
from google.cloud import storage, storage_transfer

from parsons.google.utilities import (
    load_google_application_credentials,
    setup_google_application_credentials,
)
from parsons.utilities import files

logger = logging.getLogger(__name__)


class GoogleCloudStorage(object):
    """
    This class requires application credentials in the form of a json. It can be passed
    in the following ways:

    * Set an environmental variable named ``GOOGLE_APPLICATION_CREDENTIALS`` with the
      local path to the credentials json.

      Example: ``GOOGLE_APPLICATION_CREDENTALS='path/to/creds.json'``

    * Pass in the path to the credentials using the ``app_creds`` argument.

    * Pass in a json string using the ``app_creds`` argument.


    `Args:`
        app_creds: str
            A credentials json string or a path to a json file. Not required
            if ``GOOGLE_APPLICATION_CREDENTIALS`` env variable set.
        project: str
            The project which the client is acting on behalf of. If not passed
            then will use the default inferred environment.
    `Returns:`
        GoogleCloudStorage Class
    """

    def __init__(self, app_creds=None, project=None):
        env_credentials_path = str(uuid.uuid4())
        setup_google_application_credentials(
            app_creds, target_env_var_name=env_credentials_path
        )
        credentials = load_google_application_credentials(env_credentials_path)
        self.project = project

        # Throws an error if you pass project=None, so adding if/else statement.
        if not self.project:
            self.client = storage.Client(credentials=credentials)
            """
            Access all methods of `google.cloud` package
            """
        else:
            self.client = storage.Client(credentials=credentials, project=self.project)

    def list_buckets(self):
        """
        Returns a list of buckets

        `Returns:`
            List of buckets
        """

        buckets = [b.name for b in self.client.list_buckets()]
        logger.info(f"Found {len(buckets)}.")
        return buckets

    def bucket_exists(self, bucket_name):
        """
        Verify that a bucket exists

        `Args:`
            bucket_name: str
                The name of the bucket
        `Returns:`
            boolean
        """

        if bucket_name in self.list_buckets():
            logger.debug(f"{bucket_name} exists.")
            return True
        else:
            logger.debug(f"{bucket_name} does not exist.")
            return False

    def get_bucket(self, bucket_name):
        """
        Returns a bucket object

        `Args:`
            bucket_name: str
                The name of bucket
        `Returns:`
            GoogleCloud Storage bucket
        """

        if self.client.lookup_bucket(bucket_name):
            bucket = self.client.get_bucket(bucket_name)
        else:
            raise google.cloud.exceptions.NotFound("Bucket not found")

        logger.debug(f"Returning {bucket_name} object")
        return bucket

    def create_bucket(self, bucket_name):
        """
        Create a bucket.

        `Args:`
            bucket_name: str
                A globally unique name for the bucket.
        `Returns:`
            ``None``
        """

        # TODO: Allow user to set all of the bucket parameters

        self.client.create_bucket(bucket_name)
        logger.info(f"Created {bucket_name} bucket.")

    def delete_bucket(self, bucket_name, delete_blobs=False):
        """
        Delete a bucket. Will fail if not empty unless ``delete_blobs`` argument
        is set to ``True``.

        `Args:`
            bucket_name: str
                The name of the bucket
            delete_blobs: boolean
                Delete blobs in the bucket, if it is not empty
        `Returns:`
            ``None``
        """

        bucket = self.get_bucket(bucket_name)
        bucket.delete(force=delete_blobs)
        logger.info(f"{bucket_name} bucket deleted.")

    def list_blobs(
        self,
        bucket_name,
        max_results=None,
        prefix=None,
        match_glob=None,
        include_file_details=False,
    ):
        """
        List all of the blobs in a bucket

        `Args:`
            bucket_name: str
                The name of the bucket
            max_results: int
                Maximum number of blobs to return
            prefix: str
                A prefix to filter files
            match_glob: str
                Filters files based on glob string. NOTE that the match_glob
                parameter runs on the full blob URI, include a preceding wildcard
                value to account for nested files (*/ for one level, **/ for n levels)
            include_file_details: bool
                If True, returns a list of `Blob` objects with accessible metadata. For
                documentation of attributes associated with `Blob` objects see
                https://cloud.google.com/python/docs/reference/storage/latest/google.cloud.storage.blob.Blob
        `Returns:`
            A list of blob names (or `Blob` objects if `include_file_details` is invoked)
        """

        blobs = self.client.list_blobs(
            bucket_name, max_results=max_results, prefix=prefix, match_glob=match_glob
        )

        if include_file_details:
            lst = [b for b in blobs]
        else:
            lst = [b.name for b in blobs]

        logger.info(f"Found {len(lst)} in {bucket_name} bucket.")

        return lst

    def blob_exists(self, bucket_name, blob_name):
        """
        Verify that a blob exists in the specified bucket

        `Args:`
            bucket_name: str
                The bucket name
            blob_name: str
                The name of the blob
        `Returns:`
            boolean
        """

        if blob_name in self.list_blobs(bucket_name):
            logger.debug(f"{blob_name} exists.")
            return True
        else:
            logger.debug(f"{blob_name} does not exist.")
            return False

    def get_blob(self, bucket_name, blob_name):
        """
        Get a blob object

        `Args`:
            bucket_name: str
                A bucket name
            blob_name: str
                A blob name
        `Returns:`
            A Google Storage blob object
        """

        bucket = self.get_bucket(bucket_name)
        blob = bucket.get_blob(blob_name)
        logger.debug(f"Got {blob_name} object from {bucket_name} bucket.")
        return blob

    def put_blob(self, bucket_name, blob_name, local_path, **kwargs):
        """
        Puts a blob (aka file) in a bucket

        `Args:`
            bucket_name:
                The name of the bucket to store the blob
            blob_name:
                The name of blob to be stored in the bucket
            local_path: str
                The local path of the file to upload
        `Returns:`
            ``None``
        """

        bucket = self.get_bucket(bucket_name)
        blob = storage.Blob(blob_name, bucket)

        with open(local_path, "rb") as f:
            blob.upload_from_file(f, **kwargs)

        logger.info(f"{blob_name} put in {bucket_name} bucket.")

    def download_blob(self, bucket_name, blob_name, local_path=None):
        """
        Gets a blob from a bucket

        `Args:`
            bucket_name: str
                The name of the bucket
            blob_name: str
                The name of the blob
            local_path: str
                The local path where the file will be downloaded. If not specified, a temporary
                file will be created and returned, and that file will be removed automatically
                when the script is done running.
        `Returns:`
            str
                The path of the downloaded file
        """

        if not local_path:
            local_path = files.create_temp_file_for_path("TEMPTHING")

        bucket = storage.Bucket(self.client, name=bucket_name)
        blob = storage.Blob(blob_name, bucket)

        logger.debug(f"Downloading {blob_name} from {bucket_name} bucket.")
        with open(local_path, "wb") as f:
            blob.download_to_file(f, client=self.client)
        logger.debug(f"{blob_name} saved to {local_path}.")

        return local_path

    def delete_blob(self, bucket_name, blob_name):
        """
        Delete a blob

        `Args:`
            bucket_name: str
                The bucket name
            blob_name: str
                The blob name
        `Returns:`
            ``None``
        """

        blob = self.get_blob(bucket_name, blob_name)
        blob.delete()
        logger.info(f"{blob_name} blob in {bucket_name} bucket deleted.")

    def upload_table(
        self, table, bucket_name, blob_name, data_type="csv", default_acl=None
    ):
        """
        Load the data from a Parsons table into a blob.

        `Args:`
            table: obj
                A :ref:`parsons-table`
            bucket_name: str
                The name of the bucket to upload the data into.
            blob_name: str
                The name of the blob to upload the data into.
            data_type: str
                The file format to use when writing the data. One of: `csv` or `json`
            default_acl:
                ACL desired for newly uploaded table

        `Returns`:
            String representation of file URI in GCS
        """
        bucket = storage.Bucket(self.client, name=bucket_name)
        blob = storage.Blob(blob_name, bucket)

        if data_type == "csv":
            # If a parsons Table is loaded from a CSV and has had no
            # transformations, the Table.table object will be a petl
            # CSVView. Once any transformations are made, the Table.table
            # becomes a different petl class
            if isinstance(table.table, petl.io.csv_py3.CSVView):
                local_file = table.table.source.filename
            else:
                local_file = table.to_csv()
            content_type = "text/csv"
        elif data_type == "json":
            local_file = table.to_json()
            content_type = "application/json"
        else:
            raise ValueError(
                f"Unknown data_type value ({data_type}): must be one of: csv or json"
            )

        try:
            blob.upload_from_filename(
                local_file,
                content_type=content_type,
                client=self.client,
                predefined_acl=default_acl,
            )
        finally:
            files.close_temp_file(local_file)

        return f"gs://{bucket_name}/{blob_name}"

    def get_url(self, bucket_name, blob_name, expires_in=60):
        """
        Generates a presigned url for a blob

        `Args:`
            bucket_name: str
                The name of the bucket
            blob_name: str
                The name of the blob
            expires_in: int
                Minutes until the url expires
        `Returns:`
            url:
                A link to download the object
        """

        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(minutes=expires_in),
            method="GET",
        )
        return url

    def copy_bucket_to_gcs(
        self,
        gcs_sink_bucket: str,
        source: str,
        source_bucket: str,
        destination_path: str = "",
        source_path: str = "",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
    ):
        """
        Creates a one-time transfer job from Amazon S3 to Google Cloud
        Storage. Copies all blobs within the bucket unless a key or prefix
        is passed.

        `Args`:
            gcs_sink_bucket (str):
                Destination for the data transfer (located in GCS)
            source (str):
                File storge vendor [gcs or s3]
            source_bucket (str):
                Source bucket name
            source_path (str):
                Path in the source system pointing to the relevant keys
                / files to sync. Must end in a '/'
            aws_access_key_id (str):
                Access key to authenticate storage transfer
            aws_secret_access_key (str):
                Secret key to authenticate storage transfer
        """
        if source not in ["gcs", "s3"]:
            raise ValueError(
                f"Blob transfer only supports gcs and s3 sources [source={source}]"
            )
        if source_path and source_path[-1] != "/":
            raise ValueError("Source path much end in a '/'")

        client = storage_transfer.StorageTransferServiceClient()

        now = datetime.datetime.utcnow()
        # Setting the start date and the end date as
        # the same time creates a one-time transfer
        one_time_schedule = {"day": now.day, "month": now.month, "year": now.year}

        if source == "gcs":
            description = f"""One time GCS to GCS Transfer
            [{source_bucket} -> {gcs_sink_bucket}] - {uuid.uuid4()}"""
        elif source == "s3":
            description = f"""One time S3 to GCS Transfer
            [{source_bucket} -> {gcs_sink_bucket}] - {uuid.uuid4()}"""

        transfer_job_config = {
            "project_id": self.project,
            "description": description,
            "status": storage_transfer.TransferJob.Status.ENABLED,
            "schedule": {
                "schedule_start_date": one_time_schedule,
                "schedule_end_date": one_time_schedule,
            },
        }

        # Setup transfer job configuration based on user imput
        if source == "s3":
            blob_storage = "S3"
            transfer_job_config["transfer_spec"] = {
                "aws_s3_data_source": {
                    "bucket_name": source_bucket,
                    "path": source_path,
                    "aws_access_key": {
                        "access_key_id": aws_access_key_id,
                        "secret_access_key": aws_secret_access_key,
                    },
                },
                "gcs_data_sink": {
                    "bucket_name": gcs_sink_bucket,
                    "path": destination_path,
                },
            }
        elif source == "gcs":
            blob_storage = "GCS"
            transfer_job_config["transfer_spec"] = {
                "gcs_data_source": {
                    "bucket_name": source_bucket,
                    "path": source_path,
                },
                "gcs_data_sink": {
                    "bucket_name": gcs_sink_bucket,
                    "path": destination_path,
                },
            }

        create_transfer_job_request = storage_transfer.CreateTransferJobRequest(
            {"transfer_job": transfer_job_config}
        )

        # Create the transfer job
        create_result = client.create_transfer_job(create_transfer_job_request)

        polling = True
        wait_time = 0
        wait_between_attempts_in_sec = 10

        # NOTE: This value defaults to an empty string until GCP
        # triggers the job internally ... we'll use this value to
        # determine whether or not the transfer has kicked off
        latest_operation_name = create_result.latest_operation_name

        while polling:
            if latest_operation_name:
                operation = client.get_operation({"name": latest_operation_name})

                if not operation.done:
                    logger.debug("Operation still running...")

                else:
                    operation_metadata = storage_transfer.TransferOperation.deserialize(
                        operation.metadata.value
                    )
                    error_output = operation_metadata.error_breakdowns
                    if len(error_output) != 0:
                        raise Exception(
                            f"""{blob_storage} to GCS Transfer Job
                            {create_result.name} failed with error: {error_output}"""
                        )
                    else:
                        logger.info(f"TransferJob: {create_result.name} succeeded.")
                        return

            else:
                logger.info("Waiting to kickoff operation...")
                get_transfer_job_request = storage_transfer.GetTransferJobRequest(
                    {"job_name": create_result.name, "project_id": self.project}
                )
                get_result = client.get_transfer_job(request=get_transfer_job_request)
                latest_operation_name = get_result.latest_operation_name

            wait_time += wait_between_attempts_in_sec
            time.sleep(wait_between_attempts_in_sec)

    def format_uri(self, bucket: str, name: str):
        """
        Represent a GCS URI as a string

        `Args`:
            bucket: str
                GCS bucket name
            name: str
                Filename in bucket

        `Returns`:
            String represetnation of URI
        """
        return f"gs://{bucket}/{name}"

    def split_uri(self, gcs_uri: str):
        """
        Split a GCS URI into a bucket and blob name

        `Args`:
            gcs_uri: str
                GCS URI

        `Returns`:
            Tuple of strings with bucket_name and blob_name
        """
        # TODO: make this more robust with regex?
        remove_protocol = gcs_uri.replace("gs://", "")
        uri_parts = remove_protocol.split("/")
        bucket_name = uri_parts[0]
        blob_name = "/".join(uri_parts[1:])
        return bucket_name, blob_name

    def unzip_blob(
        self,
        bucket_name: str,
        blob_name: str,
        compression_type: str = "gzip",
        new_filename: Optional[str] = None,
        new_file_extension: Optional[str] = None,
    ) -> str:
        """
        Downloads and decompresses a blob. The decompressed blob
        is re-uploaded with the same filename if no `new_filename`
        parameter is provided.

        `Args`:
            bucket_name: str
                GCS bucket name

            blob_name: str
                Blob name in GCS bucket

            compression_type: str
                Either `zip` or `gzip`

            new_filename: str
                If provided, replaces the existing blob name
                when the decompressed file is uploaded

            new_file_extension: str
                If provided, replaces the file extension
                when the decompressed file is uploaded

        `Returns`:
            String representation of decompressed GCS URI
        """

        compression_params = {
            "zip": {
                "file_extension": ".zip",
                "compression_function": self.__zip_decompress_and_write_to_gcs,
                "read": "r",
            },
            "gzip": {
                "file_extension": ".gz",
                "compression_function": self.__gzip_decompress_and_write_to_gcs,
            },
        }

        file_extension = compression_params[compression_type]["file_extension"]
        compression_function = compression_params[compression_type][
            "compression_function"
        ]

        compressed_filepath = self.download_blob(
            bucket_name=bucket_name, blob_name=blob_name
        )

        decompressed_filepath = compressed_filepath.replace(file_extension, "")
        decompressed_blob_name = (
            new_filename if new_filename else blob_name.replace(file_extension, "")
        )
        if new_file_extension:
            decompressed_filepath += f".{new_file_extension}"
            decompressed_blob_name += f".{new_file_extension}"

        logger.debug("Decompressing file...")
        compression_function(
            compressed_filepath=compressed_filepath,
            decompressed_filepath=decompressed_filepath,
            decompressed_blob_name=decompressed_blob_name,
            bucket_name=bucket_name,
            new_file_extension=new_file_extension,
        )

        return self.format_uri(bucket=bucket_name, name=decompressed_blob_name)

    def __gzip_decompress_and_write_to_gcs(self, **kwargs):
        """
        Handles `.gzip` decompression and streams blob contents
        to a decompressed storage object
        """

        compressed_filepath = kwargs.pop("compressed_filepath")
        decompressed_blob_name = kwargs.pop("decompressed_blob_name")
        bucket_name = kwargs.pop("bucket_name")

        with gzip.open(compressed_filepath, "rb") as f_in:
            logger.debug(
                f"Uploading uncompressed file to GCS: {decompressed_blob_name}"
            )
            bucket = self.get_bucket(bucket_name=bucket_name)
            blob = storage.Blob(name=decompressed_blob_name, bucket=bucket)
            blob.upload_from_file(file_obj=f_in, rewind=True, timeout=3600)

    def __zip_decompress_and_write_to_gcs(self, **kwargs):
        """
        Handles `.zip` decompression and streams blob contents
        to a decompressed storage object
        """

        compressed_filepath = kwargs.pop("compressed_filepath")
        decompressed_blob_name = kwargs.pop("decompressed_blob_name")
        decompressed_blob_in_archive = decompressed_blob_name.split("/")[-1]
        bucket_name = kwargs.pop("bucket_name")

        # Unzip the archive
        with zipfile.ZipFile(compressed_filepath) as path_:
            # Open the underlying file
            with path_.open(decompressed_blob_in_archive) as f_in:
                logger.debug(
                    f"Uploading uncompressed file to GCS: {decompressed_blob_name}"
                )
                bucket = self.get_bucket(bucket_name=bucket_name)
                blob = storage.Blob(name=decompressed_blob_name, bucket=bucket)
                blob.upload_from_file(file_obj=f_in, rewind=True, timeout=3600)
