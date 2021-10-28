import google
from google.cloud import storage
from parsons.google.utitities import setup_google_application_credentials
from parsons.utilities import files
import datetime
import logging

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

        setup_google_application_credentials(app_creds)

        # Throws an error if you pass project=None, so adding if/else statement.
        if not project:
            self.client = storage.Client()
            """
            Access all methods of `google.cloud` package
            """
        else:
            self.client = storage.Client(project=project)

    def list_buckets(self):
        """
        Returns a list of buckets

        `Returns:`
            List of buckets
        """

        buckets = [b.name for b in self.client.list_buckets()]
        logger.info(f'Found {len(buckets)}.')
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
            logger.info(f'{bucket_name} exists.')
            return True
        else:
            logger.info(f'{bucket_name} does not exist.')
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
            raise google.cloud.exceptions.NotFound('Bucket not found')

        logger.info(f'Returning {bucket_name} object')
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

        # To Do: Allow user to set all of the bucket parameters

        self.client.create_bucket(bucket_name)
        logger.info(f'Created {bucket_name} bucket.')

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
        logger.info(f'{bucket_name} bucket deleted.')

    def list_blobs(self, bucket_name, max_results=None, prefix=None):
        """
        List all of the blobs in a bucket

        `Args:`
            bucket_name: str
                The name of the bucket
            max_results: int
                TBD
            prefix_filter: str
                A prefix to filter files
        `Returns:`
            A list of blob names
        """

        blobs = self.client.list_blobs(bucket_name, max_results=max_results, prefix=prefix)
        lst = [b.name for b in blobs]
        logger.info(f'Found {len(lst)} in {bucket_name} bucket.')

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
            logger.info(f'{blob_name} exists.')
            return True
        else:
            logger.info(f'{blob_name} does not exist.')
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
        logger.debug(f'Got {blob_name} object from {bucket_name} bucket.')
        return blob

    def put_blob(self, bucket_name, blob_name, local_path):
        """
        Puts a blob (aka file) in a bucket

        `Args:`
            blob_name:
                The name of blob to be stored in the bucket
            bucket_name:
                The name of the bucket to store the blob
            local_path: str
                The local path of the file to upload
        `Returns:`
            ``None``
        """

        bucket = self.get_bucket(bucket_name)
        blob = storage.Blob(blob_name, bucket)

        with open(local_path, "rb") as f:
            blob.upload_from_file(f)

        logger.info(f'{blob_name} put in {bucket_name} bucket.')

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
            local_path = files.create_temp_file_for_path('TEMPTHING')

        bucket = storage.Bucket(self.client, name=bucket_name)
        blob = storage.Blob(blob_name, bucket)

        logger.info(f'Downloading {blob_name} from {bucket_name} bucket.')
        with open(local_path, 'wb') as f:
            blob.download_to_file(f, client=self.client)
        logger.info(f'{blob_name} saved to {local_path}.')

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
        logger.info(f'{blob_name} blob in {bucket_name} bucket deleted.')

    def upload_table(self, table, bucket_name, blob_name, data_type='csv', default_acl=None):
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
        """
        bucket = storage.Bucket(self.client, name=bucket_name)
        blob = storage.Blob(blob_name, bucket)

        if data_type == 'csv':
            local_file = table.to_csv()
            content_type = 'text/csv'
        elif data_type == 'json':
            local_file = table.to_json()
            content_type = 'application/json'
        else:
            raise ValueError(f'Unknown data_type value ({data_type}): must be one of: csv or json')

        try:
            blob.upload_from_filename(local_file, content_type=content_type, client=self.client,
                                      predefined_acl=default_acl)
        finally:
            files.close_temp_file(local_file)

        return f'gs://{bucket_name}/{blob_name}'

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
        url = blob.generate_signed_url(version="v4",
                                       expiration=datetime.timedelta(minutes=expires_in),
                                       method="GET")
        return url
