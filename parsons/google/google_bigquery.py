import pickle
from typing import Optional, Union, List
import uuid
import logging
import datetime
import random

from google.cloud import bigquery
from google.cloud.bigquery import dbapi
from google.cloud.bigquery.job import LoadJobConfig
from google.cloud import exceptions
import petl
from contextlib import contextmanager

from parsons.databases.table import BaseTable
from parsons.databases.database_connector import DatabaseConnector
from parsons.etl import Table
from parsons.google.utitities import setup_google_application_credentials
from parsons.google.google_cloud_storage import GoogleCloudStorage
from parsons.utilities import check_env
from parsons.utilities.files import create_temp_file

logger = logging.getLogger(__name__)

BIGQUERY_TYPE_MAP = {
    "str": "STRING",
    "float": "FLOAT",
    "int": "INTEGER",
    "bool": "BOOLEAN",
    "datetime.datetime": "DATETIME",
    "datetime.date": "DATE",
    "datetime.time": "TIME",
    "dict": "RECORD",
    "NoneType": "STRING",
    "UUID": "STRING",
    "datetime": "DATETIME",
}

# Max number of rows that we query at a time, so we can avoid loading huge
# data sets into memory.
# 100k rows per batch at ~1k bytes each = ~100MB per batch.
QUERY_BATCH_SIZE = 100000


def get_table_ref(client, table_name):
    # Helper function to build a TableReference for our table
    parsed = parse_table_name(table_name)
    dataset_ref = client.dataset(parsed["dataset"])
    return dataset_ref.table(parsed["table"])


def parse_table_name(table_name):
    # Helper function to parse out the different components of a table ID
    parts = table_name.split(".")
    parts.reverse()
    parsed = {
        "project": None,
        "dataset": None,
        "table": None,
    }
    if len(parts) > 0:
        parsed["table"] = parts[0]
    if len(parts) > 1:
        parsed["dataset"] = parts[1]
    if len(parts) > 2:
        parsed["project"] = parts[2]
    return parsed


def ends_with_semicolon(query: str) -> str:
    query = query.strip()
    if query[-1] == ";":
        return query
    return query + ";"


def map_column_headers_to_schema_field(schema_definition: list) -> list:
    """
    Loops through a list of dictionaries and instantiates
    google.cloud.bigquery.SchemaField objects. Useful docs
    from Google's API can be found here:
        https://cloud.google.com/python/docs/reference/bigquery/latest/google.cloud.bigquery.schema.SchemaField

    `Args`:
        schema_definition: list
        This function expects a list of dictionaries in the following format:

        ```
        schema_definition = [
            {
                "name": column_name,
                "field_type": [INTEGER, STRING, FLOAT, etc.]
            },
            {
                "name": column_name,
                "field_type": [INTEGER, STRING, FLOAT, etc.],
                "mode": "REQUIRED"
            },
            {
                "name": column_name,
                "field_type": [INTEGER, STRING, FLOAT, etc.],
                "default_value_expression": CURRENT_TIMESTAMP()
            }
        ]
        ```

    `Returns`:
        List of instantiated `SchemaField` objects
    """

    # TODO - Better way to test for this
    if isinstance(schema_definition[0], bigquery.SchemaField):
        logger.debug("User supplied list of SchemaField objects")
        return schema_definition

    return [bigquery.SchemaField(**x) for x in schema_definition]


class GoogleBigQuery(DatabaseConnector):
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

        self.dialect = "bigquery"

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

    @contextmanager
    def connection(self):
        """
        Generate a BigQuery connection.
        The connection is set up as a python "context manager", so it will be closed
        automatically when the connection goes out of scope. Note that the BigQuery
        API uses jobs to run database operations and, as such, simply has a no-op for
        a "commit" function.

        If you would like to manage transactions, please use multi-statement queries
        as [outlined here](https://cloud.google.com/bigquery/docs/transactions)
        or utilize the `query_with_transaction` method on this class.

        When using the connection, make sure to put it in a ``with`` block (necessary for
        any context manager):
        ``with bq.connection() as conn:``

        `Returns:`
            Google BigQuery ``connection`` object
        """
        conn = self._dbapi.connect(self.client)
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def cursor(self, connection):
        cur = connection.cursor()
        try:
            yield cur
        finally:
            cur.close()

    def query(
        self,
        sql: str,
        parameters: Optional[Union[list, dict]] = None,
        return_values: bool = True,
    ) -> Optional[Table]:
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

        with self.connection() as connection:
            return self.query_with_connection(
                sql, connection, parameters=parameters, return_values=return_values
            )

    def query_with_connection(
        self, sql, connection, parameters=None, commit=True, return_values: bool = True
    ):
        """
        Execute a query against the BigQuery database, with an existing connection.
        Useful for batching queries together. Will return ``None`` if the query
        returns zero rows.

        `Args:`
            sql: str
                A valid SQL statement
            connection: obj
                A connection object obtained from ``redshift.connection()``
            parameters: list
                A list of python variables to be converted into SQL values in your query
            commit: boolean
                Must be true. BigQuery

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        if not commit:
            raise ValueError(
                """
                BigQuery implementation uses an API client which always auto-commits.
                If you wish to wrap multiple queries in a transaction, use
                Mulit-Statement transactions within a single query as outlined
                here: https://cloud.google.com/bigquery/docs/transactions or use the
                `query_with_transaction` method on the BigQuery connector.
            """
            )

        # get our connection and cursor
        with self.cursor(connection) as cursor:
            # Run the query
            cursor.execute(sql, parameters)

            if not return_values:
                return None

            final_table = self._fetch_query_results(cursor=cursor)

            return final_table

    def query_with_transaction(self, queries, parameters=None):
        queries_with_semicolons = [ends_with_semicolon(q) for q in queries]
        queries_on_newlines = "\n".join(queries_with_semicolons)
        queries_wrapped = f"""
        BEGIN
            BEGIN TRANSACTION;
            {queries_on_newlines}
            COMMIT TRANSACTION;
        END;
        """
        self.query(sql=queries_wrapped, parameters=parameters, return_values=False)

    def copy_from_gcs(
        self,
        gcs_blob_uri: str,
        table_name: str,
        if_exists: str = "fail",
        max_errors: int = 0,
        data_type: str = "csv",
        csv_delimiter: str = ",",
        ignoreheader: int = 1,
        nullas: Optional[str] = None,
        allow_quoted_newlines: bool = True,
        allow_jagged_rows: bool = True,
        quote: Optional[str] = None,
        schema: Optional[List[dict]] = None,
        job_config: Optional[LoadJobConfig] = None,
        force_unzip_blobs: bool = False,
        compression_type: str = "gzip",
        new_file_extension: str = "csv",
        **load_kwargs,
    ):
        """
        Copy a csv saved in Google Cloud Storage into Google BigQuery.

        `Args:`
            gcs_blob_uri: str
                The GoogleCloudStorage URI referencing the file to be copied.
            table_name: str
                The table name to load the data into.
            if_exists: str
                If the table already exists, either ``fail``, ``append``, ``drop``
                or ``truncate`` the table. This maps to `write_disposition` in the
                `LoadJobConfig` class.
            max_errors: int
                The maximum number of rows that can error and be skipped before
                the job fails. This maps to `max_bad_records` in the `LoadJobConfig` class.
            data_type: str
                Denotes whether target file is a JSON or CSV
            csv_delimiter: str
                Character used to separate values in the target file
            ignoreheader: int
                Treats the specified number_rows as a file header and doesn't load them
            nullas: str
                Loads fields that match null_string as NULL, where null_string can be any string
            allow_quoted_newlines: bool
                If True, detects quoted new line characters within a CSV field and does
                not interpret the quoted new line character as a row boundary
            allow_jagged_rows: bool
                Allow missing trailing optional columns (CSV only).
            quote: str
                The value that is used to quote data sections in a CSV file.
                BigQuery converts the string to ISO-8859-1 encoding, and then uses the first byte of
                the encoded string to split the data in its raw, binary state.
            schema: list
                BigQuery expects a list of dictionaries in the following format
                ```
                schema = [
                    {"name": "column_name", "type": STRING},
                    {"name": "another_column_name", "type": INT}
                ]
                ```
            job_config: object
                A LoadJobConfig object to provide to the underlying call to load_table_from_uri
                on the BigQuery client. The function will create its own if not provided. Note
                if there are any conflicts between the job_config and other parameters, the
                job_config values are preferred.
            force_unzip_blobs: bool
                If True, target blobs will be unzipped before being loaded to BigQuery.
            compression_type: str
                Accepts `zip` or `gzip` values to differentially unzip a compressed
                blob in cloud storage.
            new_file_extension: str
                Provides a file extension if a blob is decompressed and rewritten
                to cloud storage.
            **load_kwargs: kwargs
                Other arguments to pass to the underlying load_table_from_uri
                call on the BigQuery client.
        """
        if if_exists not in ["fail", "truncate", "append", "drop"]:
            raise ValueError(
                f"Unexpected value for if_exists: {if_exists}, must be one of "
                '"append", "drop", "truncate", or "fail"'
            )
        if data_type not in ["csv", "json"]:
            raise ValueError(
                f"Only supports csv or json files [data_type = {data_type}]"
            )

        table_exists = self.table_exists(table_name)

        job_config = self._process_job_config(
            job_config=job_config,
            table_exists=table_exists,
            table_name=table_name,
            if_exists=if_exists,
            max_errors=max_errors,
            data_type=data_type,
            csv_delimiter=csv_delimiter,
            ignoreheader=ignoreheader,
            nullas=nullas,
            allow_quoted_newlines=allow_quoted_newlines,
            allow_jagged_rows=allow_jagged_rows,
            quote=quote,
            schema=schema,
        )

        # load CSV from Cloud Storage into BigQuery
        table_ref = get_table_ref(self.client, table_name)

        try:
            if force_unzip_blobs:
                self.copy_large_compressed_file_from_gcs(
                    gcs_blob_uri=gcs_blob_uri,
                    table_name=table_name,
                    if_exists=if_exists,
                    max_errors=max_errors,
                    data_type=data_type,
                    csv_delimiter=csv_delimiter,
                    ignoreheader=ignoreheader,
                    nullas=nullas,
                    allow_quoted_newlines=allow_quoted_newlines,
                    quote=quote,
                    schema=schema,
                    job_config=job_config,
                    compression_type=compression_type,
                    new_file_extension=new_file_extension,
                )
            else:
                load_job = self.client.load_table_from_uri(
                    source_uris=gcs_blob_uri,
                    destination=table_ref,
                    job_config=job_config,
                    **load_kwargs,
                )
                load_job.result()
        except exceptions.BadRequest as e:
            if "one of the files is larger than the maximum allowed size." in str(e):
                logger.debug(
                    f"{gcs_blob_uri.split('/')[-1]} exceeds max size ... \
                    running decompression function..."
                )

                self.copy_large_compressed_file_from_gcs(
                    gcs_blob_uri=gcs_blob_uri,
                    table_name=table_name,
                    if_exists=if_exists,
                    max_errors=max_errors,
                    data_type=data_type,
                    csv_delimiter=csv_delimiter,
                    ignoreheader=ignoreheader,
                    nullas=nullas,
                    allow_quoted_newlines=allow_quoted_newlines,
                    quote=quote,
                    schema=schema,
                    job_config=job_config,
                    compression_type=compression_type,
                    new_file_extension=new_file_extension,
                )
            elif "Schema has no field" in str(e):
                logger.debug(f"{gcs_blob_uri.split('/')[-1]} is empty, skipping file")
                return "Empty file"

            elif "encountered too many errors, giving up" in str(e):
                # TODO - Is this TOO verbose?
                logger.error(f"Max errors exceeded for {gcs_blob_uri.split('/')[-1]}")

                for error_ in load_job.errors:
                    logger.error(error_)

                raise e

            else:
                raise e

    def copy_large_compressed_file_from_gcs(
        self,
        gcs_blob_uri: str,
        table_name: str,
        if_exists: str = "fail",
        max_errors: int = 0,
        data_type: str = "csv",
        csv_delimiter: str = ",",
        ignoreheader: int = 1,
        nullas: Optional[str] = None,
        allow_quoted_newlines: bool = True,
        allow_jagged_rows: bool = True,
        quote: Optional[str] = None,
        schema: Optional[List[dict]] = None,
        job_config: Optional[LoadJobConfig] = None,
        compression_type: str = "gzip",
        new_file_extension: str = "csv",
        **load_kwargs,
    ):
        """
        Copy a compressed CSV file that exceeds the maximum size in Google Cloud Storage
        into Google BigQuery.

        `Args:`
            gcs_blob_uri: str
                The GoogleCloudStorage URI referencing the file to be copied.
            table_name: str
                The table name to load the data into.
            if_exists: str
                If the table already exists, either ``fail``, ``append``, ``drop``
                or ``truncate`` the table. This maps to `write_disposition` in the
                `LoadJobConfig` class.
            max_errors: int
                The maximum number of rows that can error and be skipped before
                the job fails. This maps to `max_bad_records` in the `LoadJobConfig` class.
            data_type: str
                Denotes whether target file is a JSON or CSV
            csv_delimiter: str
                Character used to separate values in the target file
            ignoreheader: int
                Treats the specified number_rows as a file header and doesn't load them
            nullas: str
                Loads fields that match null_string as NULL, where null_string can be any string
            allow_quoted_newlines: bool
                If True, detects quoted new line characters within a CSV field
                and does not interpret the quoted new line character as a row boundary
            allow_jagged_rows: bool
                Allow missing trailing optional columns (CSV only).
            quote: str
                The value that is used to quote data sections in a CSV file.
                BigQuery converts the string to ISO-8859-1 encoding, and then uses the first byte of
                the encoded string to split the data in its raw, binary state.
            schema: list
                BigQuery expects a list of dictionaries in the following format
                ```
                schema = [
                    {"name": "column_name", "type": STRING},
                    {"name": "another_column_name", "type": INT}
                ]
                ```
            job_config: object
                A LoadJobConfig object to provide to the underlying call to load_table_from_uri
                on the BigQuery client. The function will create its own if not provided. Note
                if there are any conflicts between the job_config and other parameters, the
                job_config values are preferred.
            compression_type: str
                Accepts `zip` or `gzip` values to differentially unzip a compressed
                blob in cloud storage.
            new_file_extension: str
                Provides a file extension if a blob is decompressed and rewritten to cloud storage.
            **load_kwargs: kwargs
                Other arguments to pass to the underlying load_table_from_uri call on the BigQuery
                client.
        """

        if if_exists not in ["fail", "truncate", "append", "drop"]:
            raise ValueError(
                f"Unexpected value for if_exists: {if_exists}, must be one of "
                '"append", "drop", "truncate", or "fail"'
            )
        if data_type not in ["csv", "json"]:
            raise ValueError(
                f"Only supports csv or json files [data_type = {data_type}]"
            )

        table_exists = self.table_exists(table_name)

        job_config = self._process_job_config(
            job_config=job_config,
            table_exists=table_exists,
            table_name=table_name,
            if_exists=if_exists,
            max_errors=max_errors,
            data_type=data_type,
            csv_delimiter=csv_delimiter,
            ignoreheader=ignoreheader,
            nullas=nullas,
            allow_quoted_newlines=allow_quoted_newlines,
            allow_jagged_rows=allow_jagged_rows,
            quote=quote,
            schema=schema,
        )

        # TODO - See if this inheritance is happening in other places
        gcs = GoogleCloudStorage(app_creds=self.app_creds, project=self.project)
        old_bucket_name, old_blob_name = gcs.split_uri(gcs_uri=gcs_blob_uri)

        uncompressed_gcs_uri = None

        try:
            logger.debug("Unzipping large file")
            uncompressed_gcs_uri = gcs.unzip_blob(
                bucket_name=old_bucket_name,
                blob_name=old_blob_name,
                new_file_extension=new_file_extension,
                compression_type=compression_type,
            )

            logger.debug(
                f"Loading uncompressed uri into BigQuery {uncompressed_gcs_uri}..."
            )
            table_ref = get_table_ref(self.client, table_name)
            load_job = self.client.load_table_from_uri(
                source_uris=uncompressed_gcs_uri,
                destination=table_ref,
                job_config=job_config,
                **load_kwargs,
            )
            load_job.result()
        finally:
            if uncompressed_gcs_uri:
                new_bucket_name, new_blob_name = gcs.split_uri(
                    gcs_uri=uncompressed_gcs_uri
                )
                gcs.delete_blob(new_bucket_name, new_blob_name)
                logger.debug("Successfully dropped uncompressed blob")

    def copy_s3(
        self,
        table_name,
        bucket,
        key,
        if_exists: str = "fail",
        max_errors: int = 0,
        data_type: str = "csv",
        csv_delimiter: str = ",",
        ignoreheader: int = 1,
        nullas: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        gcs_client: Optional[GoogleCloudStorage] = None,
        tmp_gcs_bucket: Optional[str] = None,
        job_config: Optional[LoadJobConfig] = None,
        **load_kwargs,
    ):
        """
        Copy a file from s3 to BigQuery.

        `Args:`
            table_name: str
                The table name and schema (``tmc.cool_table``) to point the file.
            bucket: str
                The s3 bucket where the file or manifest is located.
            key: str
                The key of the file or manifest in the s3 bucket.
            if_exists: str
                If the table already exists, either ``fail``, ``append``, ``drop``
                or ``truncate`` the table.
            max_errors: int
                The maximum number of rows that can error and be skipped before
                the job fails.
            data_type: str
                The data type of the file. Only ``csv`` supported currently.
            csv_delimiter: str
                The delimiter of the ``csv``. Only relevant if data_type is ``csv``.
            ignoreheader: int
                The number of header rows to skip. Ignored if data_type is ``json``.
            nullas: str
                Loads fields that match string as NULL
            aws_access_key_id:
                An AWS access key granted to the bucket where the file is located. Not required
                if keys are stored as environmental variables.
            aws_secret_access_key:
                An AWS secret access key granted to the bucket where the file is located. Not
                required if keys are stored as environmental variables.
            gcs_client: object
                The GoogleCloudStorage Connector to use for loading data into Google Cloud Storage.
            tmp_gcs_bucket: str
                The name of the Google Cloud Storage bucket to use to stage the data to load
                into BigQuery. Required if `GCS_TEMP_BUCKET` is not specified.
            job_config: object
                A LoadJobConfig object to provide to the underlying call to load_table_from_uri
                on the BigQuery client. The function will create its own if not provided. Note
                if there are any conflicts between the job_config and other parameters, the
                job_config values are preferred.

        `Returns`
            Parsons Table or ``None``
                See :ref:`parsons-table` for output options.
        """

        # copy from S3 to GCS
        tmp_gcs_bucket = check_env.check("GCS_TEMP_BUCKET", tmp_gcs_bucket)
        gcs_client = gcs_client or GoogleCloudStorage()
        temp_blob_uri = gcs_client.copy_s3_to_gcs(
            aws_source_bucket=bucket,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            gcs_sink_bucket=tmp_gcs_bucket,
            aws_s3_key=key,
        )
        temp_blob_name = key
        temp_blob_uri = gcs_client.format_uri(
            bucket=tmp_gcs_bucket, name=temp_blob_name
        )

        # load CSV from Cloud Storage into BigQuery
        try:
            self.copy_from_gcs(
                gcs_blob_uri=temp_blob_uri,
                table_name=table_name,
                if_exists=if_exists,
                max_errors=max_errors,
                data_type=data_type,
                csv_delimiter=csv_delimiter,
                ignoreheader=ignoreheader,
                nullas=nullas,
                job_config=job_config,
                **load_kwargs,
            )
        finally:
            gcs_client.delete_blob(tmp_gcs_bucket, temp_blob_name)

    def copy(
        self,
        tbl: Table,
        table_name: str,
        if_exists: str = "fail",
        max_errors: int = 0,
        tmp_gcs_bucket: Optional[str] = None,
        gcs_client: Optional[GoogleCloudStorage] = None,
        job_config: Optional[LoadJobConfig] = None,
        **load_kwargs,
    ):
        """
        Copy a :ref:`parsons-table` into Google BigQuery via Google Cloud Storage.

        `Args:`
            tbl: obj
                The Parsons Table to copy into BigQuery.
            table_name: str
                The table name to load the data into.
            if_exists: str
                If the table already exists, either ``fail``, ``append``, ``drop``
                or ``truncate`` the table.
            max_errors: int
                The maximum number of rows that can error and be skipped before
                the job fails.
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
        tmp_gcs_bucket = check_env.check("GCS_TEMP_BUCKET", tmp_gcs_bucket)

        # if not job_config:
        job_config = bigquery.LoadJobConfig()
        if not job_config.schema:
            job_config.schema = self._generate_schema_from_parsons_table(tbl)

        gcs_client = gcs_client or GoogleCloudStorage()
        temp_blob_name = f"{uuid.uuid4()}.csv"
        temp_blob_uri = gcs_client.upload_table(tbl, tmp_gcs_bucket, temp_blob_name)

        # load CSV from Cloud Storage into BigQuery
        try:
            self.copy_from_gcs(
                gcs_blob_uri=temp_blob_uri,
                table_name=table_name,
                if_exists=if_exists,
                max_errors=max_errors,
                job_config=job_config,
                **load_kwargs,
            )
        finally:
            gcs_client.delete_blob(tmp_gcs_bucket, temp_blob_name)

    def duplicate_table(
        self,
        source_table,
        destination_table,
        if_exists="fail",
        drop_source_table=False,
    ):
        """
        Create a copy of an existing table (or subset of rows) in a new
        table.

        `Args:`
            source_table: str
                Name of existing schema and table (e.g. ``myschema.oldtable``)
            destination_table: str
                Name of destination schema and table (e.g. ``myschema.newtable``)
            if_exists: str
                If the table already exists, either ``fail``, ``replace``, or
                ``ignore`` the operation.
            drop_source_table: boolean
                Drop the source table
        """
        if if_exists not in ["fail", "replace", "ignore"]:
            raise ValueError("Invalid value for `if_exists` argument")
        if if_exists == "fail" and self.table_exists(destination_table):
            raise ValueError("Table already exists.")

        table__replace_clause = "OR REPLACE " if if_exists == "replace" else ""
        table__exists_clause = " IF NOT EXISTS" if if_exists == "ignore" else ""

        query = f"""
            CREATE {table__replace_clause}TABLE{table__exists_clause}
            {destination_table}
            CLONE {source_table}
        """
        self.query(sql=query, return_values=False)
        if drop_source_table:
            self.delete_table(table_name=source_table)

    def upsert(
        self,
        table_obj,
        target_table,
        primary_key,
        distinct_check=True,
        cleanup_temp_table=True,
        from_s3=False,
        **copy_args,
    ):
        """
        Preform an upsert on an existing table. An upsert is a function in which rows
        in a table are updated and inserted at the same time.

        `Args:`
            table_obj: obj
                A Parsons table object
            target_table: str
                The schema and table name to upsert
            primary_key: str or list
                The primary key column(s) of the target table
            distinct_check: boolean
                Check if the primary key column is distinct. Raise error if not.
            cleanup_temp_table: boolean
                A temp table is dropped by default on cleanup. You can set to False for debugging.
            from_s3: boolean
                Instead of specifying a table_obj (set the first argument to None),
                set this to True and include :func:`~parsons.databases.bigquery.Bigquery.copy_s3`
                arguments to upsert a pre-existing s3 file into the target_table
            \**copy_args: kwargs
                See :func:`~parsons.databases.bigquery.BigQuery.copy` for options.
        """  # noqa: W605
        if not self.table_exists(target_table):
            logger.info(
                "Target table does not exist. Copying into newly \
                         created target table."
            )

            self.copy(table_obj, target_table)
            return None

        if isinstance(primary_key, str):
            primary_keys = [primary_key]
        else:
            primary_keys = primary_key

        if distinct_check:
            primary_keys_statement = ", ".join(primary_keys)
            diff = self.query(
                f"""
                select (
                    select count(*)
                    from {target_table}
                ) - (
                    SELECT COUNT(*) from (
                        select distinct {primary_keys_statement}
                        from {target_table}
                    )
                ) as total_count
            """
            ).first
            if diff > 0:
                raise ValueError("Primary key column contains duplicate values.")

        noise = f"{random.randrange(0, 10000):04}"[:4]
        date_stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        # Generate a temp table like "table_tmp_20200210_1230_14212"
        staging_tbl = f"{target_table}_stg_{date_stamp}_{noise}"

        # Copy to a staging table
        logger.info(f"Building staging table: {staging_tbl}")

        if from_s3:
            if table_obj is not None:
                raise ValueError(
                    "upsert(... from_s3=True) requires the first argument (table_obj)"
                    " to be None. from_s3 and table_obj are mutually exclusive."
                )
            self.copy_s3(staging_tbl, template_table=target_table, **copy_args)

        else:
            self.copy(
                tbl=table_obj,
                table_name=staging_tbl,
                template_table=target_table,
                **copy_args,
            )

        staging_table_name = staging_tbl.split(".")[1]
        target_table_name = target_table.split(".")[1]

        # Delete rows
        comparisons = [
            f"{staging_table_name}.{primary_key} = {target_table_name}.{primary_key}"
            for primary_key in primary_keys
        ]
        where_clause = " and ".join(comparisons)

        queries = [
            f"""
                DELETE FROM {target_table}
                USING {staging_tbl}
                WHERE {where_clause}
                """,
            f"""
                INSERT INTO {target_table}
                SELECT * FROM {staging_tbl}
                """,
        ]

        if cleanup_temp_table:
            # Drop the staging table
            queries.append(f"DROP TABLE IF EXISTS {staging_tbl}")

        return self.query_with_transaction(queries=queries)

    def delete_table(self, table_name):
        """
        Delete a BigQuery table.

        `Args:`
            table_name: str
                The name of the table to delete.
        """
        table_ref = get_table_ref(self.client, table_name)
        self.client.delete_table(table_ref)

    def table_exists(self, table_name: str) -> bool:
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

    def get_tables(self, schema, table_name: Optional[str] = None):
        """
        List the tables in a schema including metadata.

        Args:
            schema: str
                Filter by a schema
            table_name: str
                Filter by a table name
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        logger.debug("Retrieving tables info.")
        sql = f"select * from {schema}.INFORMATION_SCHEMA.TABLES"
        if table_name:
            sql += f" where table_name = '{table_name}'"
        return self.query(sql)

    def get_views(self, schema, view: Optional[str] = None):
        """
        List views.

        Args:
            schema: str
                Filter by a schema
            view: str
                Filter by a table name
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        logger.debug("Retrieving views info.")
        sql = f"""
              select
                table_schema as schema_name,
                table_name as view_name,
                view_definition
              from {schema}.INFORMATION_SCHEMA.VIEWS
              """
        if view:
            sql += f" where table_name = '{view}'"
        return self.query(sql)

    def get_columns(self, schema: str, table_name: str):
        """
        Gets the column names (and other column metadata) for a table. If you
        need just the column names run ``get_columns_list()``, as it is faster.

        `Args:`
            schema: str
                The schema name
            table_name: str
                The table name

        `Returns:`
            A dictionary mapping column name to a dictionary with extra info. The
            keys of the dictionary are ordered just liked the columns in the table.
            The extra info is a dict with format
        """

        base_query = f"""
        SELECT
            *
        FROM `{self.project}.{schema}.INFORMATION_SCHEMA.COLUMNS`
        WHERE
            table_name = '{table_name}'
        """

        logger.debug(base_query)

        return {
            row["column_name"]: {
                "data_type": row["data_type"],
                "is_nullable": row["is_nullable"],
                "is_updatable": row["is_updatable"],
                "is_partioning_column": row["is_partitioning_column"],
                "rounding_mode": row["rounding_mode"],
            }
            for row in self.query(base_query)
        }

    def get_columns_list(self, schema: str, table_name: str) -> list:
        """
        Gets the column names for a table.

        `Args:`
            schema: str
                The schema name
            table_name: str
                The table name

        `Returns:`
            A list of column names
        """

        first_row = self.query(f"SELECT * FROM {schema}.{table_name} LIMIT 1;")

        return [x for x in first_row.columns]

    def get_row_count(self, schema: str, table_name: str) -> int:
        """
        Gets the row count for a BigQuery materialization.

        `Args`:
            schema: str
                The schema name
            table_name: str
                The table name

        `Returns:`
            Row count of the target table
        """

        sql = f"SELECT COUNT(*) AS row_count FROM `{schema}.{table_name}`"
        result = self.query(sql=sql)

        return result["row_count"][0]

    def _generate_schema_from_parsons_table(self, tbl):
        stats = tbl.get_columns_type_stats()
        fields = []
        for stat in stats:
            petl_types = stat["type"]
            best_type = "str" if "str" in petl_types else petl_types[0]
            field_type = self._bigquery_type(best_type)
            field = bigquery.schema.SchemaField(stat["name"], field_type)
            fields.append(field)
        return fields

    def _process_job_config(
        self, job_config: Optional[LoadJobConfig] = None, **kwargs
    ) -> LoadJobConfig:
        """
        Internal function to neatly process a user-supplied job configuration object.
        As a convention, if both the job_config and keyword arguments specify a value,
        we defer to the job_config.

        `Args`:
            job_config: `LoadJobConfig`
                Optionally supplied GCS `LoadJobConfig` object

        `Returns`:
            A `LoadJobConfig` object
        """

        if not job_config:
            job_config = bigquery.LoadJobConfig()

        if not job_config.schema:
            if kwargs["schema"]:
                logger.debug("Using user-supplied schema definition...")
                job_config.schema = map_column_headers_to_schema_field(kwargs["schema"])
                job_config.autodetect = False
            else:
                logger.debug("Autodetecting schema definition...")
                job_config.autodetect = True

        if not job_config.create_disposition:
            job_config.create_disposition = bigquery.CreateDisposition.CREATE_IF_NEEDED

        if not job_config.max_bad_records:
            job_config.max_bad_records = kwargs["max_errors"]

        if not job_config.skip_leading_rows and kwargs["data_type"] == "csv":
            job_config.skip_leading_rows = kwargs["ignoreheader"]

        if not job_config.source_format:
            job_config.source_format = (
                bigquery.SourceFormat.CSV
                if kwargs["data_type"] == "csv"
                else bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
            )

        if not job_config.field_delimiter:
            if kwargs["data_type"] == "csv":
                job_config.field_delimiter = kwargs["csv_delimiter"]
            if kwargs["nullas"]:
                job_config.null_marker = kwargs["nullas"]

        if not job_config.write_disposition:
            if kwargs["if_exists"] == "append":
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
            elif kwargs["if_exists"] == "truncate":
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
            elif kwargs["table_exists"] and kwargs["if_exists"] == "fail":
                raise Exception("Table already exists.")
            elif kwargs["if_exists"] == "drop" and kwargs["table_exists"]:
                self.delete_table(kwargs["table_name"])
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_EMPTY
            else:
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_EMPTY

        if not job_config.allow_quoted_newlines:
            job_config.allow_quoted_newlines = kwargs["allow_quoted_newlines"]

        if kwargs["data_type"] == "csv" and kwargs["allow_jagged_rows"]:
            job_config.allow_jagged_rows = kwargs["allow_jagged_rows"]
        else:
            job_config.allow_jagged_rows = True

        if not job_config.quote_character and kwargs["quote"]:
            job_config.quote_character = kwargs["quote"]

        return job_config

    def _fetch_query_results(self, cursor) -> Table:
        # We will use a temp file to cache the results so that they are not all living
        # in memory. We'll use pickle to serialize the results to file in order to maintain
        # the proper data types (e.g. integer).
        temp_filename = create_temp_file()

        wrote_header = False
        with open(temp_filename, "wb") as temp_file:
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
        return Table(ptable)

    @staticmethod
    def _bigquery_type(tp):
        return BIGQUERY_TYPE_MAP[tp]

    def table(self, table_name):
        # Return a MySQL table object

        return BigQueryTable(self, table_name)


class BigQueryTable(BaseTable):
    """BigQuery table object."""

    def drop(self, cascade=False):
        """
        Drop the table.
        """

        self.db.delete_table(self.table)

    def truncate(self):
        """
        Truncate the table.
        """

        self.db.query(f"TRUNCATE TABLE {self.table}")
