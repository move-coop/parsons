import datetime
import json
import logging
import pickle
import random
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Literal

import google
import petl
from google.api_core import exceptions
from google.cloud import bigquery
from google.cloud.bigquery import dbapi, job
from google.cloud.bigquery.job import ExtractJobConfig, LoadJobConfig, QueryJobConfig
from google.oauth2.credentials import Credentials

from parsons import Table
from parsons.databases.database_connector import DatabaseConnector
from parsons.databases.table import BaseTable
from parsons.google.google_cloud_storage import GoogleCloudStorage
from parsons.google.utilities import (
    load_google_application_credentials,
    setup_google_application_credentials,
)
from parsons.utilities import check_env
from parsons.utilities.files import create_temp_file

logger = logging.getLogger(__name__)

BIGQUERY_TYPE_MAP = {
    "str": "STRING",
    "float": "FLOAT",
    "int": "INTEGER",
    "bool": "BOOLEAN",
    "datetime": "DATETIME",
    "date": "DATE",
    "time": "TIME",
    "NoneType": "STRING",
    "UUID": "STRING",
    "timestamp": "TIMESTAMP",
    "Decimal": "FLOAT",
}

# Max number of rows that we query at a time, so we can avoid loading huge
# data sets into memory.
# 100k rows per batch at ~1k bytes each = ~100MB per batch.
QUERY_BATCH_SIZE = 100000


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

    Args:
        schema_definition: list
        This function expects a list of dictionaries in the following format:

        .. code-block:: python

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

    Returns:
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
        client_options: dict
            A dictionary containing any requested client options. Defaults to the required
            scopes for making API calls against External tables stored in Google Drive.
            Can be set to None if these permissions are not desired
        gcs_temp_bucket: str
            Name of the GCS bucket that will be used for storing data during bulk transfers.
            Required if you intend to perform bulk data transfers (eg. the copy_from_gcs method),
            and env variable ``GCS_TEMP_BUCKET`` is not populated.

    """

    def __init__(
        self,
        app_creds: str | dict | Credentials | None = None,
        project=None,
        location=None,
        client_options: dict | None = None,
        tmp_gcs_bucket: str | None = None,
    ):
        if client_options is None:
            client_options = {
                "scopes": [
                    "https://www.googleapis.com/auth/drive",
                    "https://www.googleapis.com/auth/bigquery",
                    "https://www.googleapis.com/auth/cloud-platform",
                ]
            }
        self.app_creds = app_creds

        if isinstance(app_creds, Credentials):
            self.credentials = app_creds
        else:
            self.env_credential_path = str(uuid.uuid4())
            setup_google_application_credentials(
                app_creds, target_env_var_name=self.env_credential_path
            )
            self.credentials = load_google_application_credentials(self.env_credential_path)

        self.project = project
        self.location = location
        self.client_options = client_options
        self.tmp_gcs_bucket = tmp_gcs_bucket

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

        Returns:
            `google.cloud.bigquery.client.Client`

        """
        if not self._client:
            # Create a BigQuery client to use to make the query
            self._client = bigquery.Client(
                project=self.project,
                location=self.location,
                client_options=self.client_options,
                credentials=self.credentials,
            )

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

        Yields:
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
        parameters: list | dict | None = None,
        return_values: bool = True,
        job_config: QueryJobConfig | None = None,
    ) -> Table | None:
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

        Args:
            sql: str
                A valid BigTable statement
            parameters: dict
                A dictionary of query parameters for BigQuery.
            job_config: QueryJobConfig or None
                An optional QueryJobConfig object for custom behavior. See https://cloud.google.com/python/docs/reference/bigquery/latest#google.cloud.bigquery.job.QueryJobConfig

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        with self.connection() as connection:
            return self.query_with_connection(
                sql,
                connection,
                parameters=parameters,
                return_values=return_values,
                job_config=job_config,
            )

    def query_with_connection(
        self,
        sql,
        connection,
        parameters=None,
        commit=True,
        return_values: bool = True,
        job_config: QueryJobConfig | None = None,
    ):
        """
        Execute a query against the BigQuery database, with an existing connection.
        Useful for batching queries together. Will return ``None`` if the query
        returns zero rows.

        Args:
            sql: str
                A valid SQL statement
            connection: obj
                A connection object obtained from ``redshift.connection()``
            parameters: list
                A list of python variables to be converted into SQL values in your query
            commit: boolean
                Must be true. BigQuery
            job_config: QueryJobConfig or None
                An optional QueryJobConfig object for custom behavior. See https://cloud.google.com/python/docs/reference/bigquery/latest#google.cloud.bigquery.job.QueryJobConfig

        Returns:
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
            cursor.execute(sql, parameters, job_config=job_config)

            if not return_values:
                return None

            # This applies when running a SQL statement without any return value
            # e.g. when creating a view or a table
            # This does not apply when 0 rows are returned
            if not cursor.description:
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

    def get_job(
        self, job_id: str, **job_kwargs
    ) -> job.LoadJob | job.CopyJob | job.ExtractJob | job.QueryJob | job.UnknownJob:
        """
        Fetch a job

        Args:
            job_id: str
                ID of job to fetch
            location: str
                Location where the job was run
            `**job_kwargs`: kwargs
                Other arguments to pass to the underlying get_job
                call on the BigQuery client.

        """
        return self.client.get_job(job_id=job_id, **job_kwargs)

    def copy_from_gcs(
        self,
        gcs_blob_uri: str,
        table_name: str,
        if_exists: Literal["append", "drop", "truncate", "fail"] = "fail",
        max_errors: int = 0,
        data_type: Literal["csv", "json"] = "csv",
        csv_delimiter: str = ",",
        ignoreheader: int = 1,
        nullas: str | None = None,
        allow_quoted_newlines: bool = True,
        allow_jagged_rows: bool = True,
        quote: str | None = None,
        schema: list[dict] | None = None,
        job_config: LoadJobConfig | None = None,
        force_unzip_blobs: bool = False,
        compression_type: str = "gzip",
        new_file_extension: str = "csv",
        template_table: str | None = None,
        max_timeout: int = 21600,
        source_column_match: str | None = None,
        **load_kwargs,
    ):
        """
        Copy a csv saved in Google Cloud Storage into Google BigQuery.

        Args:
            gcs_blob_uri: str
                The GoogleCloudStorage URI referencing the file to be copied.
            table_name: str
                The table name to load the data into. Will be used to generate load schema
                if no custom schema or template table are supplied and the if_exists is
                set to "truncate" or "append".
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

                .. code-block:: python

                    schema = [
                        {"name": "column_name", "type": STRING},
                        {"name": "another_column_name", "type": INT}
                    ]

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
            template_table: str
                Table name to be used as the load schema. Load operation wil use the same
                columns and data types as the template table.
            max_timeout: int
                The maximum number of seconds to wait for a request before the job fails.
            `**load_kwargs`: kwargs
                Other arguments to pass to the underlying load_table_from_uri
                call on the BigQuery client.

        """
        self._validate_copy_inputs(
            if_exists=if_exists,
            data_type=data_type,
            accepted_data_types=[
                "csv",
                "json",
                "parquet",
                "datastore_backup",
                "newline_delimited_json",
                "avro",
                "orc",
            ],
        )

        job_config = self._process_job_config(
            job_config=job_config,
            destination_table_name=table_name,
            if_exists=if_exists,
            max_errors=max_errors,
            data_type=data_type,
            csv_delimiter=csv_delimiter,
            ignoreheader=ignoreheader,
            nullas=nullas,
            allow_quoted_newlines=allow_quoted_newlines,
            allow_jagged_rows=allow_jagged_rows,
            quote=quote,
            custom_schema=schema,
            template_table=template_table,
            source_column_match=source_column_match,
        )

        # load CSV from Cloud Storage into BigQuery
        table_ref = self.get_table_ref(table_name=table_name)

        try:
            if force_unzip_blobs:
                return self.copy_large_compressed_file_from_gcs(
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
                    max_timeout=max_timeout,
                )
            else:
                return self._load_table_from_uri(
                    source_uris=gcs_blob_uri,
                    destination=table_ref,
                    job_config=job_config,
                    max_timeout=max_timeout,
                    **load_kwargs,
                )
        except exceptions.BadRequest as e:
            if "one of the files is larger than the maximum allowed size." in str(e):
                logger.debug(
                    f"{gcs_blob_uri.split('/')[-1]} exceeds max size ... \
                    running decompression function..."
                )

                return self.copy_large_compressed_file_from_gcs(
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
                    max_timeout=max_timeout,
                )
            elif "Schema has no field" in str(e):
                logger.debug(f"{gcs_blob_uri.split('/')[-1]} is empty, skipping file")
                return "Empty file"

            else:
                raise e

        except exceptions.DeadlineExceeded as e:
            logger.error(f"Max timeout exceeded for {gcs_blob_uri.split('/')[-1]}")
            raise e

    def copy_large_compressed_file_from_gcs(
        self,
        gcs_blob_uri: str,
        table_name: str,
        if_exists: Literal["append", "drop", "truncate", "fail"] = "fail",
        max_errors: int = 0,
        data_type: Literal["csv", "json"] = "csv",
        csv_delimiter: str = ",",
        ignoreheader: int = 1,
        nullas: str | None = None,
        allow_quoted_newlines: bool = True,
        allow_jagged_rows: bool = True,
        quote: str | None = None,
        schema: list[dict] | None = None,
        job_config: LoadJobConfig | None = None,
        compression_type: str = "gzip",
        new_file_extension: str = "csv",
        template_table: str | None = None,
        max_timeout: int = 21600,
        **load_kwargs,
    ):
        """
        Copy a compressed CSV file that exceeds the maximum size in Google Cloud Storage
        into Google BigQuery.

        Args:
            gcs_blob_uri: str
                The GoogleCloudStorage URI referencing the file to be copied.
            table_name: str
                The table name to load the data into. Will be used to generate load schema
                if no custom schema or template table are supplied and the if_exists is
                set to "truncate" or "append".
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

                .. code-block:: python

                    schema = [
                        {"name": "column_name", "type": STRING},
                        {"name": "another_column_name", "type": INT}
                    ]

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
            template_table: str
                Table name to be used as the load schema. Load operation wil use the same
                columns and data types as the template table.
            max_timeout: int
                The maximum number of seconds to wait for a request before the job fails.
            `**load_kwargs`: kwargs
                Other arguments to pass to the underlying load_table_from_uri call on the BigQuery
                client.

        """

        self._validate_copy_inputs(
            if_exists=if_exists,
            data_type=data_type,
            accepted_data_types=["csv", "newline_delimited_json"],
        )

        job_config = self._process_job_config(
            job_config=job_config,
            destination_table_name=table_name,
            if_exists=if_exists,
            max_errors=max_errors,
            data_type=data_type,
            csv_delimiter=csv_delimiter,
            ignoreheader=ignoreheader,
            nullas=nullas,
            allow_quoted_newlines=allow_quoted_newlines,
            allow_jagged_rows=allow_jagged_rows,
            quote=quote,
            custom_schema=schema,
            template_table=template_table,
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

            logger.debug(f"Loading uncompressed uri into BigQuery {uncompressed_gcs_uri}...")
            table_ref = self.get_table_ref(table_name=table_name)
            return self._load_table_from_uri(
                source_uris=uncompressed_gcs_uri,
                destination=table_ref,
                job_config=job_config,
                max_timeout=max_timeout,
                **load_kwargs,
            )

        finally:
            if uncompressed_gcs_uri:
                new_bucket_name, new_blob_name = gcs.split_uri(gcs_uri=uncompressed_gcs_uri)
                gcs.delete_blob(new_bucket_name, new_blob_name)
                logger.debug("Successfully dropped uncompressed blob")

    def copy_s3(
        self,
        table_name,
        bucket,
        key,
        if_exists: Literal["append", "drop", "truncate", "fail"] = "fail",
        max_errors: int = 0,
        data_type: Literal["csv", "json"] = "csv",
        csv_delimiter: str = ",",
        ignoreheader: int = 1,
        nullas: str | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        gcs_client: GoogleCloudStorage | None = None,
        tmp_gcs_bucket: str | None = None,
        template_table: str | None = None,
        job_config: LoadJobConfig | None = None,
        max_timeout: int = 21600,
        **load_kwargs,
    ):
        """
        Copy a file from s3 to BigQuery.

        Args:
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
                into BigQuery. Required if `GCS_TEMP_BUCKET` is not specified or set on
                the class instance.
            template_table: str
                Table name to be used as the load schema. Load operation wil use the same
                columns and data types as the template table.
            job_config: object
                A LoadJobConfig object to provide to the underlying call to load_table_from_uri
                on the BigQuery client. The function will create its own if not provided. Note
                if there are any conflicts between the job_config and other parameters, the
                job_config values are preferred.
            max_timeout: int
                The maximum number of seconds to wait for a request before the job fails.

        `Returns`
            Parsons Table or ``None``
                See :ref:`parsons-table` for output options.

        """

        # copy from S3 to GCS
        tmp_gcs_bucket = (
            tmp_gcs_bucket
            or self.tmp_gcs_bucket
            or check_env.check("GCS_TEMP_BUCKET", tmp_gcs_bucket)
        )
        gcs_client = gcs_client or GoogleCloudStorage()
        temp_blob_uri = gcs_client.copy_s3_to_gcs(
            aws_source_bucket=bucket,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            gcs_sink_bucket=tmp_gcs_bucket,
            aws_s3_key=key,
        )
        temp_blob_name = key
        temp_blob_uri = gcs_client.format_uri(bucket=tmp_gcs_bucket, name=temp_blob_name)

        # load CSV from Cloud Storage into BigQuery
        try:
            return self.copy_from_gcs(
                gcs_blob_uri=temp_blob_uri,
                table_name=table_name,
                if_exists=if_exists,
                max_errors=max_errors,
                data_type=data_type,
                csv_delimiter=csv_delimiter,
                ignoreheader=ignoreheader,
                nullas=nullas,
                job_config=job_config,
                template_table=template_table,
                max_timeout=max_timeout,
                **load_kwargs,
            )
        finally:
            gcs_client.delete_blob(tmp_gcs_bucket, temp_blob_name)

    def copy_direct(
        self,
        tbl: Table,
        table_name: str,
        if_exists: Literal["append", "drop", "truncate", "fail"] = "fail",
        max_errors: int = 0,
        job_config: LoadJobConfig | None = None,
        template_table: str | None = None,
        ignoreheader: int = 1,
        nullas: str | None = None,
        allow_quoted_newlines: bool = True,
        allow_jagged_rows: bool = True,
        quote: str | None = None,
        schema: list[dict] | None = None,
        max_timeout: int = 21600,
        convert_dict_list_columns_to_json: bool = True,
        **load_kwargs,
    ):
        """
        Copy a :ref:`parsons-table` into Google BigQuery
        directly. This will work well for smaller data. For larger
        data, use the :meth:`copy` method which stages the upload through CloudStorage.

        Args:
            tbl: obj
                The Parsons Table to copy into BigQuery.
            table_name: str
                The table name to load the data into. Will be used to generate load schema
                if no custom schema or template table are supplied and if_exists is
                set to "truncate" or "append".
            if_exists: str
                If the table already exists, either ``fail``, ``append``, ``drop``
                or ``truncate`` the table.
            max_errors: int
                The maximum number of rows that can error and be skipped before
                the job fails.
            job_config: object
                A LoadJobConfig object to provide to the underlying call to load_table_from_uri
                on the BigQuery client. The function will create its own if not provided.
            template_table: str
                Table name to be used as the load schema. Load operation wil use the same
                columns and data types as the template table.
            max_timeout: int
                The maximum number of seconds to wait for a request before the job fails.
            convert_dict_list_columns_to_json: bool
                If set to True, will convert any dict or list columns (which cannot by default be successfully loaded to BigQuery to JSON strings)
            `**load_kwargs`: kwargs
                Arguments to pass to the underlying load_table_from_uri call on the BigQuery
                client.

        """

        if convert_dict_list_columns_to_json:
            tbl = self._stringify_records(tbl)

        job_config = self._prepare_local_upload_job(
            tbl,
            table_name,
            if_exists,
            max_errors,
            job_config,
            template_table,
            ignoreheader,
            nullas,
            allow_quoted_newlines,
            allow_jagged_rows,
            quote,
            schema,
        )

        tmpfile_path = tbl.to_csv()
        with Path(tmpfile_path).open(mode="rb") as tmpfile:
            load_job = self.client.load_table_from_file(
                tmpfile,
                destination=self.get_table_ref(table_name=table_name),
                job_config=job_config,
            )

            try:
                load_job.result(timeout=max_timeout)
                return load_job
            except exceptions.BadRequest as e:
                for idx, error_ in enumerate(load_job.errors):
                    if idx == 0:
                        logger.error("* Load job failed. Enumerating errors collection below:")
                    logger.error(f"** Error collection - index {idx}:")
                    logger.error(error_)

                raise e

    def copy(
        self,
        tbl: Table,
        table_name: str,
        if_exists: Literal["append", "drop", "truncate", "fail"] = "fail",
        max_errors: int = 0,
        tmp_gcs_bucket: str | None = None,
        temp_blob_name: str | None = None,
        gcs_client: GoogleCloudStorage | None = None,
        job_config: LoadJobConfig | None = None,
        template_table: str | None = None,
        ignoreheader: int = 1,
        nullas: str | None = None,
        allow_quoted_newlines: bool = True,
        allow_jagged_rows: bool = True,
        quote: str | None = None,
        schema: list[dict] | None = None,
        max_timeout: int = 21600,
        convert_dict_list_columns_to_json: bool = True,
        keep_gcs_file: bool = False,
        **load_kwargs,
    ):
        """
        Copy a :ref:`parsons-table` into Google BigQuery via Google Cloud Storage.

        Args:
            tbl: obj
                The Parsons Table to copy into BigQuery.
            table_name: str
                The table name to load the data into. Will be used to generate load schema
                if no custom schema or template table are supplied and if_exists is
                set to "truncate" or "append".
            if_exists: str
                If the table already exists, either ``fail``, ``append``, ``drop``
                or ``truncate`` the table.
            max_errors: int
                The maximum number of rows that can error and be skipped before
                the job fails.
            tmp_gcs_bucket: str
                The name of the Google Cloud Storage bucket to use to stage the data to load
                into BigQuery. Required if `GCS_TEMP_BUCKET` is not specified or set on
                the class instance.
            gcs_client: object
                The GoogleCloudStorage Connector to use for loading data into Google Cloud Storage.
            job_config: object
                A LoadJobConfig object to provide to the underlying call to load_table_from_uri
                on the BigQuery client. The function will create its own if not provided.
            template_table: str
                Table name to be used as the load schema. Load operation wil use the same
                columns and data types as the template table.
            max_timeout: int
                The maximum number of seconds to wait for a request before the job fails.
            convert_dict_list_columns_to_json: bool
                If set to True, will convert any dict or list columns (which cannot by default be successfully loaded to BigQuery to JSON strings)
            `**load_kwargs`: kwargs
                Arguments to pass to the underlying load_table_from_uri call on the BigQuery
                client.

        """
        data_type = "csv"
        tmp_gcs_bucket = (
            tmp_gcs_bucket
            or self.tmp_gcs_bucket
            or check_env.check("GCS_TEMP_BUCKET", tmp_gcs_bucket)
        )
        if not tmp_gcs_bucket:
            raise ValueError(
                "Must set GCS_TEMP_BUCKET environment variable or pass in tmp_gcs_bucket parameter. If you have smaller data, you can use the `copy_direct` method to upload the data without needing to use CloudStorage. This alternate method will not work well with larger data."
            )

        if convert_dict_list_columns_to_json:
            tbl = self._stringify_records(tbl)

        job_config = self._prepare_local_upload_job(
            tbl,
            table_name,
            if_exists,
            max_errors,
            job_config,
            template_table,
            ignoreheader,
            nullas,
            allow_quoted_newlines,
            allow_jagged_rows,
            quote,
            schema,
        )

        gcs_client = gcs_client or GoogleCloudStorage(app_creds=self.app_creds)
        temp_blob_name = temp_blob_name if temp_blob_name else f"{uuid.uuid4()}.{data_type}"
        temp_blob_uri = gcs_client.upload_table(tbl, tmp_gcs_bucket, temp_blob_name)

        # load CSV from Cloud Storage into BigQuery
        try:
            self._load_table_from_uri(
                source_uris=temp_blob_uri,
                destination=self.get_table_ref(table_name=table_name),
                job_config=job_config,
                max_timeout=max_timeout,
                **load_kwargs,
            )
        finally:
            if not keep_gcs_file:
                gcs_client.delete_blob(tmp_gcs_bucket, temp_blob_name)

    def _stringify_records(self, tbl):
        # Convert dict columns to JSON strings
        for field in tbl.get_columns_type_stats():
            if "dict" in field["type"] or "list" in field["type"]:
                new_petl = tbl.table.addfield(
                    field["name"] + "_replace",
                    lambda row, field=field: json.dumps(row[field["name"]]),
                )
                new_tbl = Table(new_petl)
                new_tbl.remove_column(field["name"])
                new_tbl.rename_column(field["name"] + "_replace", field["name"])
                new_tbl.materialize()
                tbl = new_tbl

        return tbl

    def _prepare_local_upload_job(
        self,
        tbl,
        table_name,
        if_exists,
        max_errors,
        job_config,
        template_table,
        ignoreheader,
        nullas,
        allow_quoted_newlines,
        allow_jagged_rows,
        quote,
        schema,
    ):
        data_type = "csv"

        self._validate_copy_inputs(
            if_exists=if_exists, data_type=data_type, accepted_data_types=["csv"]
        )

        # If our source table is loaded from CSV with no transformations
        # The original source file will be directly loaded to GCS
        # We may need to pass along a custom delimiter to BigQuery
        # Otherwise we use the default comma
        if isinstance(tbl.table, petl.io.csv_py3.CSVView):
            csv_delimiter = tbl.table.csvargs.get("delimiter", ",")
        else:
            csv_delimiter = ","

        job_config = self._process_job_config(
            job_config=job_config,
            destination_table_name=table_name,
            if_exists=if_exists,
            max_errors=max_errors,
            data_type=data_type,
            template_table=template_table,
            parsons_table=tbl,
            ignoreheader=ignoreheader,
            nullas=nullas,
            allow_quoted_newlines=allow_quoted_newlines,
            allow_jagged_rows=allow_jagged_rows,
            quote=quote,
            custom_schema=schema,
            csv_delimiter=csv_delimiter,
        )

        # Reorder schema to match table to ensure compatibility
        schema = []
        for column in tbl.columns:
            try:
                schema_row = [i for i in job_config.schema if i.name.lower() == column.lower()][0]
            except IndexError as e:
                raise IndexError(
                    f"Column found in Table that was not found in schema: {column}"
                ) from e
            schema.append(schema_row)
        job_config.schema = schema

        return job_config

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

        Args:
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
        r"""
        Preform an upsert on an existing table. An upsert is a function in which rows
        in a table are updated and inserted at the same time.

        Args:
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
            `**copy_args`: kwargs
                See :func:`~parsons.databases.bigquery.BigQuery.copy` for options.

        """
        if not self.table_exists(target_table):
            logger.info(
                "Target table does not exist. Copying into newly \
                         created target table."
            )

            self.copy(table_obj, target_table)
            return None

        primary_keys = [primary_key] if isinstance(primary_key, str) else primary_key

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

        # Delete rows
        comparisons = [
            f"`{staging_tbl}`.{primary_key} = `{target_table}`.{primary_key}"
            for primary_key in primary_keys
        ]
        where_clause = " and ".join(comparisons)

        queries = [
            f"""
                DELETE FROM `{target_table}`
                WHERE EXISTS
                (SELECT * FROM `{staging_tbl}`
                WHERE {where_clause})
                """,
            f"""
                INSERT INTO `{target_table}`
                SELECT * FROM `{staging_tbl}`
                """,
        ]

        try:
            return self.query_with_transaction(queries=queries)
        finally:
            if cleanup_temp_table:
                logger.info(f"Deleting staging table: {staging_tbl}")
                self.query(f"DROP TABLE IF EXISTS {staging_tbl}", return_values=False)

    def delete_table(self, table_name):
        """
        Delete a BigQuery table.

        Args:
            table_name: str
                The name of the table to delete.

        """
        table_ref = self.get_table_ref(table_name=table_name)
        self.client.delete_table(table_ref)

    def table_exists(self, table_name: str) -> bool:
        """
        Check whether or not the Google BigQuery table exists in the specified dataset.

        Args:
            table_name: str
                The name of the BigQuery table to check for
        Returns:
            bool
                True if the table exists in the specified dataset, false otherwise

        """
        table_ref = self.get_table_ref(table_name=table_name)
        try:
            self.client.get_table(table_ref)
        except exceptions.NotFound:
            return False

        return True

    def get_tables(self, schema, table_name: str | None = None):
        """
        List the tables in a schema including metadata.

        Args:
            schema: str
                Filter by a schema
            table_name: str
                Filter by a table name
        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        logger.debug("Retrieving tables info.")
        sql = f"select * from {schema}.INFORMATION_SCHEMA.TABLES"
        if table_name:
            sql += f" where table_name = '{table_name}'"
        return self.query(sql)

    def get_views(self, schema, view: str | None = None):
        """
        List views.

        Args:
            schema: str
                Filter by a schema
            view: str
                Filter by a table name
        Returns:
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

        Args:
            schema: str
                The schema name
            table_name: str
                The table name

        Returns:
            A dictionary mapping column name to a dictionary with extra info. The
            keys of the dictionary are ordered just liked the columns in the table.
            The extra info is a dict with format

        """

        base_query = f"""
        SELECT
            *
        FROM `{schema}.INFORMATION_SCHEMA.COLUMNS`
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

        Args:
            schema: str
                The schema name
            table_name: str
                The table name

        Returns:
            A list of column names

        """

        table_ref = self.client.get_table(table=f"{schema}.{table_name}")

        return [schema_ref.name for schema_ref in table_ref.schema]

    def get_row_count(self, schema: str, table_name: str) -> int:
        """
        Gets the row count for a BigQuery materialization.

        Caution: This method uses SELECT COUNT(*) which can be expensive for large tables,
        especially those with many columns. This is because BigQuery scans all table data
        to perform the count, even though only the row count is returned.

        Args:
            schema: str
                The schema name
            table_name: str
                The table name

        Returns:
            Row count of the target table

        """

        sql = f"SELECT COUNT(*) AS row_count FROM `{schema}.{table_name}`"
        result = self.query(sql=sql)

        return result["row_count"][0]

    def get_table_ref(self, table_name):
        # Helper function to build a TableReference for our table
        parsed = parse_table_name(table_name)
        dataset_ref = self.client.dataset(parsed["dataset"])
        return dataset_ref.table(parsed["table"])

    def _get_job_config_schema(
        self,
        job_config: LoadJobConfig,
        destination_table_name: str,
        if_exists: Literal["append", "drop", "truncate", "fail"],
        parsons_table: Table | None = None,
        custom_schema: list | None = None,
        template_table: str | None = None,
    ) -> list[bigquery.SchemaField] | None:
        # if job.schema already set in job_config, do nothing
        if job_config.schema:
            return job_config.schema
        # if schema specified by user, convert to schema type and use that
        if custom_schema:
            return map_column_headers_to_schema_field(custom_schema)
        # if template_table specified by user, use that
        # otherwise, if loading into existing table, infer destination table as template table
        if not template_table and if_exists in ("append", "truncate"):
            template_table = destination_table_name
        # if template_table set, use it to set the load schema
        if template_table:
            try:
                bigquery_table = self.client.get_table(template_table)
                return bigquery_table.schema
            except google.api_core.exceptions.NotFound:
                logger.warning(
                    f"template_table '{template_table}' not found. Unable to set schema."
                )
        # if load is coming from a Parsons table, use that to generate schema
        if parsons_table:
            return self._generate_schema_from_parsons_table(parsons_table)

        return None

    def _generate_schema_from_parsons_table(self, tbl):
        """BigQuery schema generation based on contents of Parsons table.

        Not usually necessary to use this. BigQuery is able to
        natively autodetect schema formats.
        """
        stats = tbl.get_columns_type_stats()
        fields = []
        for stat in stats:
            petl_types = stat["type"]

            # Prefer 'str' if included
            # Otherwise choose first type that isn't "NoneType"
            # Otherwise choose NoneType
            not_none_petl_types = [i for i in petl_types if i != "NoneType"]
            if "str" in petl_types:
                best_type = "str"
            elif ("int" in petl_types) and ("float" in petl_types):
                best_type = "float"
            elif not_none_petl_types:
                best_type = not_none_petl_types[0]
            else:
                best_type = "NoneType"

            # Python datetimes may be datetime or timestamp in BigQuery
            # BigQuery datetimes have no timezone, timestamps do
            if best_type == "datetime":
                for value in petl.util.base.values(tbl.table, stat["name"]):
                    if isinstance(value, datetime.datetime) and value.tzinfo:
                        best_type = "timestamp"

            try:
                field_type = self._bigquery_type(best_type)
            except KeyError as e:
                raise KeyError(
                    "Column type not supported for load to BigQuery. "
                    "Consider converting to another type. "
                    f"[type={best_type}]"
                ) from e
            field = bigquery.schema.SchemaField(stat["name"], field_type)
            fields.append(field)
        return fields

    def _process_job_config(
        self,
        destination_table_name: str,
        if_exists: Literal["append", "drop", "truncate", "fail"],
        max_errors: int,
        data_type: Literal["csv", "json"],
        csv_delimiter: str | None = ",",
        ignoreheader: int | None = 1,
        nullas: str | None = None,
        allow_quoted_newlines: bool | None = None,
        allow_jagged_rows: bool | None = None,
        quote: str | None = None,
        job_config: LoadJobConfig | None = None,
        custom_schema: list | None = None,
        template_table: str | None = None,
        parsons_table: Table | None = None,
        source_column_match: str | None = None,
    ) -> LoadJobConfig:
        """
        Internal function to neatly process a user-supplied job configuration object.
        As a convention, if both the job_config and keyword arguments specify a value,
        we defer to the job_config.

        Args:
            job_config: `LoadJobConfig`
                Optionally supplied GCS `LoadJobConfig` object

        Returns:
            A `LoadJobConfig` object

        """

        if not job_config:
            job_config = bigquery.LoadJobConfig()

        job_config.schema = self._get_job_config_schema(
            job_config=job_config,
            destination_table_name=destination_table_name,
            if_exists=if_exists,
            parsons_table=parsons_table,
            custom_schema=custom_schema,
            template_table=template_table,
        )
        if not job_config.schema:
            job_config.autodetect = True

        if not job_config.create_disposition:
            job_config.create_disposition = bigquery.CreateDisposition.CREATE_IF_NEEDED

        if not job_config.max_bad_records:
            job_config.max_bad_records = max_errors

        if not job_config.skip_leading_rows and data_type == "csv":
            job_config.skip_leading_rows = ignoreheader

        if not job_config.source_format:
            data_type_mappings = {
                "csv": bigquery.SourceFormat.CSV,
                "parquet": bigquery.SourceFormat.PARQUET,
                "datastore_backup": bigquery.SourceFormat.DATASTORE_BACKUP,
                "json": bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
                "avro": bigquery.SourceFormat.AVRO,
                "orc": bigquery.SourceFormat.ORC,
            }
            job_config.source_format = data_type_mappings[data_type]

        if not job_config.source_column_match:
            job_config.source_column_match = source_column_match

        if not job_config.field_delimiter:
            if data_type == "csv":
                job_config.field_delimiter = csv_delimiter
            if nullas:
                job_config.null_marker = nullas

        destination_table_exists = self.table_exists(destination_table_name)
        if not job_config.write_disposition:
            if if_exists == "append":
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
            elif if_exists == "truncate":
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
            elif destination_table_exists and if_exists == "fail":
                raise Exception("Table already exists.")
            elif if_exists == "drop" and destination_table_exists:
                self.delete_table(destination_table_name)
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_EMPTY
            else:
                job_config.write_disposition = bigquery.WriteDisposition.WRITE_EMPTY

        if not job_config.allow_quoted_newlines and allow_quoted_newlines is not None:
            job_config.allow_quoted_newlines = allow_quoted_newlines

        if data_type == "csv" and allow_jagged_rows is not None:
            job_config.allow_jagged_rows = allow_jagged_rows

        if not job_config.quote_character and quote is not None:
            job_config.quote_character = quote

        return job_config

    def _fetch_query_results(self, cursor) -> Table:
        # We will use a temp file to cache the results so that they are not all living
        # in memory. We'll use pickle to serialize the results to file in order to maintain
        # the proper data types (e.g. integer).
        temp_filename = create_temp_file()

        with Path(temp_filename).open(mode="wb") as temp_file:
            header = [i[0] for i in cursor.description]
            pickle.dump(header, temp_file)

            while True:
                batch = cursor.fetchmany(QUERY_BATCH_SIZE)
                if len(batch) == 0:
                    break

                for row in batch:
                    row_data = list(row.values())
                    pickle.dump(row_data, temp_file)

        ptable = petl.frompickle(temp_filename)
        return Table(ptable)

    def _validate_copy_inputs(
        self,
        if_exists: Literal["append", "drop", "truncate", "fail"],
        data_type: Literal["csv", "json"],
        accepted_data_types: list[str],
    ):
        if if_exists not in ["fail", "truncate", "append", "drop"]:
            raise ValueError(
                f"Unexpected value for if_exists: {if_exists}, must be one of "
                '"append", "drop", "truncate", or "fail"'
            )

        if data_type not in accepted_data_types:
            raise ValueError(f"Only supports {accepted_data_types} files [data_type = {data_type}]")

    def _load_table_from_uri(
        self, source_uris, destination, job_config, max_timeout, **load_kwargs
    ):
        load_job = self.client.load_table_from_uri(
            source_uris=source_uris,
            destination=destination,
            job_config=job_config,
            **load_kwargs,
        )

        try:
            load_job.result(timeout=max_timeout)
            return load_job
        except exceptions.BadRequest as e:
            for idx, error_ in enumerate(load_job.errors):
                if idx == 0:
                    logger.error("* Load job failed. Enumerating errors collection below:")
                logger.error(f"** Error collection - index {idx}:")
                logger.error(error_)

            raise e

    @staticmethod
    def _bigquery_type(tp):
        return BIGQUERY_TYPE_MAP[tp]

    def table(self, table_name):
        # Return a MySQL table object

        return BigQueryTable(self, table_name)

    def extract(
        self,
        dataset: str,
        table_name: str,
        gcs_bucket: str,
        gcs_blob_name: str,
        project: str | None = None,
        gzip: bool = False,
        location: str = "US",
        destination_file_format: str = "CSV",
        field_delimiter: str = ",",
        compression: str | None = None,
        job_config: ExtractJobConfig = None,
        wait_for_job_to_complete: bool = True,
        **export_kwargs,
    ) -> None:
        """
        Extracts a BigQuery table to a Google Cloud Storage bucket.

        Args:
            dataset: str
                The BigQuery dataset containing the table.
            table_name: str
                The name of the table to extract.
            gcs_bucket: str
                The GCS bucket where the table will be exported.
            gcs_blob_name: str
                The name of the blob in the GCS bucket.
            project: Optional[str]
                The Google Cloud project ID.
                If not provided, the default project of the client is used.
            gzip: bool
                If True, the exported file will be compressed using GZIP.
                Defaults to False.

        """
        if not job_config:
            logger.info("Using default job config as none was provided...")
            job_config = ExtractJobConfig(
                destination_format=destination_file_format,
                compression=compression,
                field_delimiter=field_delimiter,
            )
        source = f"{dataset}.{table_name}"
        gs_destination = f"gs://{gcs_bucket}/{gcs_blob_name}"
        compression = "GZIP" if gzip else compression
        logger.info(f"Project (parsons): {project}")
        extract_job = self.client.extract_table(
            source=source,
            destination_uris=gs_destination,
            location=location,
            job_config=job_config,
            project=project,
            **export_kwargs,
        )
        if wait_for_job_to_complete:
            extract_job.result()
            logger.info(f"Finished exporting query result to {gs_destination}.")

        return extract_job

    def copy_between_projects(
        self,
        source_project,
        source_dataset,
        source_table,
        destination_project,
        destination_dataset,
        destination_table,
        if_dataset_not_exists="fail",
        if_table_exists="fail",
    ):
        """
        Copy a table from one project to another. Fails if the source or target project
            does not exist.
        If the target dataset does not exist, fhe flag if_dataset_not_exists controls behavior.
            It defaults to 'fail'; set it to 'create' if it's ok to create it.
        If the target table exists, the flag if_table_exists controls behavior.
            It defaults to 'fail'; set it to 'overwrite' if it's ok to overwrite an existing table.

        Args:
            source_project: str
                Name of source project
            source_dataset: str
                Name of source dataset
            source_table: str
                Name of source table
            destination_project: str
                Name of destination project
            destination_dataset: str
                Name of destination dataset
            destination_table: str
                Name of destination table
            if_dataset_not_exists: str
                Action if dataset doesn't exist {'fail','create'}
            if_table_exists: str
                Action if table exists {'fail', 'overwrite'}

        """

        from google.cloud import bigquery
        from google.cloud.exceptions import NotFound

        destination_table_id = (
            destination_project + "." + destination_dataset + "." + destination_table
        )
        source_table_id = source_project + "." + source_dataset + "." + source_table
        dataset_id = destination_project + "." + destination_dataset

        # check if destination dataset exists
        try:
            self.client.get_dataset(dataset_id)  # Make an API request.
            # if it exists: continue; if not, check to see if it's ok to create it
        except NotFound:
            # if it doesn't exist: check if it's ok to create it
            if if_dataset_not_exists == "create":  # create a new dataset in the destination
                dataset = bigquery.Dataset(dataset_id)
                dataset = self.client.create_dataset(dataset, timeout=30)
            else:  # if it doesn't exist and it's not ok to create it, fail
                logger.error("BigQuery copy failed")
                logger.error(
                    f"Dataset {destination_dataset} does not exist and if_dataset_not_exists set to {if_dataset_not_exists}"
                )

        job_config = bigquery.CopyJobConfig()

        # check if destination table exists
        try:
            self.client.get_table(destination_table_id)
            if if_table_exists == "overwrite":  # if it exists
                job_config = bigquery.CopyJobConfig()
                job_config.write_disposition = "WRITE_TRUNCATE"
                job = self.client.copy_table(
                    source_table_id,
                    destination_table_id,
                    location="US",
                    job_config=job_config,
                )
                result = job.result()
            else:
                logger.error(
                    f"BigQuery copy failed, Table {destination_table} exists and if_table_exists set to {if_table_exists}"
                )

        except NotFound:
            # destination table doesn't exist, so we can create one
            job = self.client.copy_table(
                source_table_id,
                destination_table_id,
                location="US",
                job_config=job_config,
            )
            result = job.result()
            logger.info(result)


class BigQueryTable(BaseTable):
    """BigQuery table object."""

    def drop(self, cascade=False):
        """Drop the table."""

        self.db.delete_table(self.table)

    def truncate(self):
        """Truncate the table."""

        self.db.query(f"TRUNCATE TABLE {self.table}")
