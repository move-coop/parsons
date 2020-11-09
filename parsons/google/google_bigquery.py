import pickle
import uuid

from google.cloud import bigquery
from google.cloud.bigquery import dbapi
from google.cloud import exceptions
import petl

from parsons.databases.table import BaseTable
from parsons.etl import Table
from parsons.google.utitities import setup_google_application_credentials
from parsons.google.google_cloud_storage import GoogleCloudStorage
from parsons.utilities import check_env
from parsons.utilities.files import create_temp_file

BIGQUERY_TYPE_MAP = {
    'str': 'STRING',
    'float': 'FLOAT',
    'int': 'INTEGER',
    'bool': 'BOOLEAN',
    'datetime.datetime': 'DATETIME',
    'datetime.date': 'DATE',
    'datetime.time': 'TIME',
    'dict': 'RECORD',
}

# Max number of rows that we query at a time, so we can avoid loading huge
# data sets into memory.
# 100k rows per batch at ~1k bytes each = ~100MB per batch.
QUERY_BATCH_SIZE = 100000


def get_table_ref(client, table_name):
    # Helper function to build a TableReference for our table
    parsed = parse_table_name(table_name)
    dataset_ref = client.dataset(parsed['dataset'])
    return dataset_ref.table(parsed['table'])


def parse_table_name(table_name):
    # Helper function to parse out the different components of a table ID
    parts = table_name.split('.')
    parts.reverse()
    parsed = {
        'project': None,
        'dataset': None,
        'table': None,
    }
    if len(parts) > 0:
        parsed['table'] = parts[0]
    if len(parts) > 1:
        parsed['dataset'] = parts[1]
    if len(parts) > 2:
        parsed['project'] = parts[2]
    return parsed


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
        app_creds: str
            A credentials json string or a path to a json file. Not required
            if ``GOOGLE_APPLICATION_CREDENTIALS`` env variable set.
        project: str
            The project which the client is acting on behalf of. If not passed
            then will use the default inferred environment.
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

        self._dbapi = dbapi

        self.dialect = 'bigquery'

    def copy(self, table_obj, table_name, if_exists='fail',
             tmp_gcs_bucket=None, gcs_client=None, job_config=None, **load_kwargs):
        """
        Copy a :ref:`parsons-table` into Google BigQuery via Google Cloud Storage.

        `Args:`
            table_obj: obj
                The Parsons Table to copy into BigQuery.
            table_name: str
                The table name to load the data into.
            if_exists: str
                If the table already exists, either ``fail``, ``append``, ``drop``
                or ``truncate`` the table.
            tmp_gcs_bucket: str
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

        table_exists = self.table_exists(table_name)

        if not job_config:
            job_config = bigquery.LoadJobConfig()

        if not job_config.schema:
            job_config.schema = self._generate_schema(table_obj)

        if not job_config.create_disposition:
            job_config.create_disposition = bigquery.CreateDisposition.CREATE_IF_NEEDED
        job_config.skip_leading_rows = 1
        job_config.source_format = bigquery.SourceFormat.CSV
        job_config.write_disposition = bigquery.WriteDisposition.WRITE_EMPTY

        if table_exists:
            if if_exists == 'fail':
                raise ValueError('Table already exists.')
            elif if_exists == 'drop':
                self.delete_table(table_name)
            elif if_exists == 'append':
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
            elif if_exists == 'truncate':
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE

        gcs_client = gcs_client or GoogleCloudStorage()
        temp_blob_name = f'{uuid.uuid4()}.csv'
        temp_blob_uri = gcs_client.upload_table(table_obj, tmp_gcs_bucket, temp_blob_name)

        # load CSV from Cloud Storage into BigQuery
        table_ref = get_table_ref(self.client, table_name)
        try:
            load_job = self.client.load_table_from_uri(
                temp_blob_uri, table_ref,
                job_config=job_config, **load_kwargs,
            )
            load_job.result()
        finally:
            gcs_client.delete_blob(tmp_gcs_bucket, temp_blob_name)

    def delete_table(self, table_name):
        """
        Delete a BigQuery table.

        `Args:`
            table_name: str
                The name of the table to delete.
        """
        table_ref = get_table_ref(self.client, table_name)
        self.client.delete_table(table_ref)

    def query(self, sql, parameters=None):
        """
        Run a BigQuery query and return the results as a Parsons table.

        To include python variables in your query, it is recommended to pass them as parameters,
        following the BigQuery style where parameters are prefixed with `@`s.
        Using the ``parameters`` argument ensures that values are escaped properly, and avoids SQL
        injection attacks.

        **Parameter Examples**

        .. code-block:: python

           name = "Beatrice O'Brady"
           sql = 'SELECT * FROM my_table WHERE name = %s'
           rs.query(sql, parameters=[name])

        .. code-block:: python

           name = "Beatrice O'Brady"
           sql = "SELECT * FROM my_table WHERE name = %(name)s"
           rs.query(sql, parameters={'name': name})

        `Args:`
            sql: str
                A valid BigTable statement
            parameters: dict
                A dictionary of query parameters for BigQuery.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """
        # get our connection and cursor
        cursor = self._dbapi.connect(self.client).cursor()

        # Run the query
        cursor.execute(sql, parameters)

        # We will use a temp file to cache the results so that they are not all living
        # in memory. We'll use pickle to serialize the results to file in order to maintain
        # the proper data types (e.g. integer).
        temp_filename = create_temp_file()

        wrote_header = False
        with open(temp_filename, 'wb') as temp_file:
            # Track whether we got data, since if we don't get any results we need to return None
            got_results = False
            while True:
                batch = cursor.fetchmany(QUERY_BATCH_SIZE)
                if len(batch) == 0:
                    break

                got_results = True

                for row in batch:
                    # Make sure we write out the header once and only once
                    if not wrote_header:
                        wrote_header = True
                        header = list(row.keys())
                        pickle.dump(header, temp_file)

                    row_data = list(row.values())
                    pickle.dump(row_data, temp_file)

        if not got_results:
            return None

        ptable = petl.frompickle(temp_filename)
        final_table = Table(ptable)

        return final_table

    def table_exists(self, table_name):
        """
        Check whether or not the Google BigQuery table exists in the specified dataset.

        `Args:`
            table_name: str
                The name of the BigQuery table to check for
        `Returns:`
            bool
                True if the table exists in the specified dataset, false otherwise
        """
        table_ref = get_table_ref(self.client, table_name)
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

    def _generate_schema(self, tbl):
        stats = tbl.get_columns_type_stats()
        fields = []
        for stat in stats:
            petl_types = stat['type']
            best_type = 'str' if 'str' in petl_types else petl_types[0]
            field_type = self._bigquery_type(best_type)
            field = bigquery.schema.SchemaField(stat['name'], field_type)
            fields.append(field)
        return fields

    @staticmethod
    def _bigquery_type(tp):
        return BIGQUERY_TYPE_MAP[tp]

    def table(self, table_name):
        # Return a MySQL table object

        return BigQueryTable(self, table_name)


class BigQueryTable(BaseTable):
    # BigQuery table object.

    def drop(self, cascade=False):
        """
        Drop the table.
        """

        self.db.delete_table(self.table)

    def truncate(self):
        """
        Truncate the table.
        """
        # BigQuery does not support truncate natively, so we will "load" an empty dataset
        # with write disposition of "truncate"
        table_ref = get_table_ref(self.db.client, self.table)
        bq_table = self.db.client.get_table(table_ref)

        # BigQuery wants the schema when we load the data, so we will grab it from the table
        job_config = bigquery.LoadJobConfig()
        job_config.schema = bq_table.schema

        empty_table = Table([])
        self.db.copy(empty_table, self.table, if_exists='truncate', job_config=job_config)
