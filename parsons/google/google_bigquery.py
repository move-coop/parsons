from google.cloud import bigquery
from google.cloud import exceptions
from parsons.etl import Table
from parsons.google.utitities import setup_google_application_credentials
from parsons.google.google_cloud_storage import GoogleCloudStorage
from parsons.utilities import check_env
from parsons.utilities.files import create_temp_file
import petl
import pickle
import uuid


class GoogleBigQuery:
    """
    Class for querying BigQuery table and returning the data as Parsons tables.

    This class requires application credentials in the form of a json. It can be passed
    in the following ways:

    * Set an environmental variable named ``GOOGLE_APPLICATION_CREDENTIALS`` with the
      local path to the credentials json.

      Example: ``GOOGLE_APPLICATION_CREDENTALS='path/to/creds.json'``

    * Pass in the path to the credentials using the ``app_creds`` argument.

    * Pass in a json string using the ``app_creds`` argument.

    Args:
        project_id: str
            The project which the client is acting on behalf of. If not passed
            then will use the default inferred environment.
        app_creds: str
            A credentials json string or a path to a json file. Not required
            if ``GOOGLE_APPLICATION_CREDENTIALS`` env variable set.
        location: str
            Default geographic location for tables
    """

    def __init__(self, app_creds=None, project=None, location=None):
        self.app_creds = app_creds

        setup_google_application_credentials(app_creds)

        self.project = project
        self.location = location

        # We will not create the client until we need to use it, since creating the client
        # without valid GOOGLE_APPLICATION_CREDENTIALS raises an exception.
        # This attribute will be used to hold the client once we have created it.
        self._client = None

        self.dialect = 'bigquery'

    def copy(self, table_obj, dataset_name, table_name, if_exists='fail',
             tmp_gcs_bucket=None, gcs_client=None, job_config=None, **load_kwargs):
        """
        Copy a :ref:`parsons-table` into Google BigQuery via Google Cloud Storage.

        `Args:`
            table_obj: obj
                The Parsons Table to copy into BigQuery.
            dataset_name: str
                The dataset name to load the data into.
            table_name: str
                The table name to load the data into.
            if_exists: str
                If the table already exists, either ``fail``, ``append``, ``drop``
                or ``truncate`` the table.
            temp_gcs_bucket: str
                The name of the Google Cloud Storage bucket to use to stage the data to load
                into BigQuery. Required if `GCS_TEMP_BUCKET` is not specified.
            gcs_client: object
                The GoogleCloudStorage Connector to use for loading data into Google Cloud Storage.
            job_config: object
                A LoadJobConfig object to provide to the underlying call to load_table_from_uri
                on the BigQuery client. The function will create its own if not provided.
            **load_kwargs: kwargs
                Arguments to pass to the underlying load_table_from_uri call on the BigQuery
                client.
        """
        tmp_gcs_bucket = check_env.check('GCS_TEMP_BUCKET', tmp_gcs_bucket)

        if if_exists not in ['fail', 'truncate', 'append', 'drop']:
            raise ValueError(f'Unexpected value for if_exists: {if_exists}, must be one of '
                             '"append", "drop", "truncate", or "fail"')

        table_exists = self.table_exists(dataset_name, table_name)

        if not job_config:
            job_config = bigquery.LoadJobConfig()
            job_config.autodetect = True

        job_config.skip_leading_rows = 1
        job_config.source_format = bigquery.SourceFormat.CSV
        job_config.write_disposition = bigquery.WriteDisposition.WRITE_EMPTY
        job_config.create_disposition = bigquery.CreateDisposition.CREATE_IF_NEEDED

        dataset_ref = self.client.dataset(dataset_name)

        if table_exists:
            if if_exists == 'fail':
                raise ValueError('Table already exists.')
            elif if_exists == 'drop':
                self.delete_table(dataset_name, table_name)
            elif if_exists == 'append':
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
            elif if_exists == 'truncate':
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE

        gcs_client = gcs_client or GoogleCloudStorage()
        temp_blob_name = f'{uuid.uuid4()}.csv'
        temp_blob_uri = gcs_client.upload_table(table_obj, tmp_gcs_bucket, temp_blob_name)

        # load CSV from Cloud Storage into BigQuery
        try:
            load_job = self.client.load_table_from_uri(
                temp_blob_uri, dataset_ref.table(table_name),
                job_config=job_config, **load_kwargs,
            )
            load_job.result()
        finally:
            gcs_client.delete_blob(tmp_gcs_bucket, temp_blob_name)

    def delete_table(self, dataset_name, table_name):
        """
        Delete a BigQuery table.

        `Args:`
            dataset_name: str
                The name of the dataset that the table lives in.
            table_name: str
                The name of the table to delete.
        """
        dataset_ref = self.client.dataset(dataset_name)
        table_ref = dataset_ref.table(table_name)
        self.client.delete_table(table_ref)

    def query(self, sql):
        """
        Run a BigQuery query and return the results as a Parsons table.

        `Args:`
            sql: str
                A valid BigTable statement

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """
        # Run the query
        query_job = self.client.query(sql)

        # We will use a temp file to cache the results so that they are not all living
        # in memory. We'll use pickle to serialize the results to file in order to maintain
        # the proper data types (e.g. integer).
        temp_filename = create_temp_file()

        wrote_header = False
        with open(temp_filename, 'wb') as temp_file:
            results = query_job.result()

            # If there are no results, just return None
            if results.total_rows == 0:
                return None

            for row in results:
                # Make sure we write out the header once and only once
                if not wrote_header:
                    wrote_header = True
                    header = list(row.keys())
                    pickle.dump(header, temp_file)

                row_data = list(row.values())
                pickle.dump(row_data, temp_file)

        ptable = petl.frompickle(temp_filename)
        final_table = Table(ptable)

        return final_table

    def table_exists(self, dataset_name, table_name):
        """
        Check whether or not the Google BigQuery table exists in the specified dataset.

        `Args:`
            dataset_name: str
                The name of the BigQuery dataset to check in
            table_name: str
                The name of the BigQuery table to check for
        `Returns:`
            bool
                True if the table exists in the specified dataset, false otherwise
        """
        dataset = self.client.dataset(dataset_name)
        table_ref = dataset.table(table_name)
        try:
            self.client.get_table(table_ref)
        except exceptions.NotFound:
            return False

        return True

    @property
    def client(self):
        """
        Get the Google BigQuery client to use for making queries.

        `Returns:`
            `google.cloud.bigquery.client.Client`
        """
        if not self._client:
            # Create a BigQuery client to use to make the query
            self._client = bigquery.Client(project=self.project, location=self.location)

        return self._client
