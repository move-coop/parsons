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
    if query[-1] == ';':
        return query
    return query + ';'


class BigQuery(DatabaseConnector):
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
    def connection(self):  # TODO: Is this worth doing given the transaction thing?
        """
        Generate a BigQuery connection.
        The connection is set up as a python "context manager", so it will be closed
        automatically when the connection goes out of scope. Note that the BigQuery
        API uses jobs to run database operations and, as such, simply has a no-op for
        a "commit" function. If you would like to manage transactions, please use
        multi-statement queries as [outlined here](https://cloud.google.com/bigquery/docs/transactions)

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
                BigQuery implementation uses an API client which always auto-commits. If you wish to wrap
                multiple queries in a transaction, use Mulit-Statement transactions within a single query
                as outlined here: https://cloud.google.com/bigquery/docs/transactions
            """
            )

        # get our connection and cursor
        with self.cursor(connection) as cursor:
            # Run the query
            cursor.execute(sql, parameters)

            if not return_values:
                return None

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
            final_table = Table(ptable)

            return final_table

    def query_with_transaction(self, queries, parameters=None):
        queries_with_semicolons = [ends_with_semicolon(q) for q in queries]
        queries_on_newlines = '\n'.join(queries_with_semicolons)
        queries_wrapped = f"""
        BEGIN
            BEGIN TRANSACTION;
            
            {queries_on_newlines}

            COMMIT TRANSACTION;

            EXCEPTION WHEN ERROR THEN
            -- Roll back the transaction inside the exception handler.
            SELECT @@error.message;
            ROLLBACK TRANSACTION;
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
        nullas: str = None,
        allow_quoted_newlines: bool = True,
        job_config: Optional[LoadJobConfig] = None,
        **load_kwargs,
    ):
        """
        Copy a csv saved in Google Cloud Storage into Google BigQuery.

        `Args:` TODO: note what it maps to in the job config
            gcs_blob_uri: str
                The GoogleCloudStorage URI referencing the file to be copied.
            table_name: str
                The table name to load the data into.
            if_exists: str
                If the table already exists, either ``fail``, ``append``, ``drop``
                or ``truncate`` the table.
            max_errors: int
                The maximum number of rows that can error and be skipped before
                the job fails.
            job_config: object
                A LoadJobConfig object to provide to the underlying call to load_table_from_uri
                on the BigQuery client. The function will create its own if not provided. Note
                if there are any conflicts between the job_config and other parameters, the
                job_config values are preferred.
            **load_kwargs: kwargs
                Arguments to pass to the underlying load_table_from_uri call on the BigQuery
                client.
        """
        if if_exists not in ["fail", "truncate", "append", "drop"]:
            raise ValueError(
                f"Unexpected value for if_exists: {if_exists}, must be one of "
                '"append", "drop", "truncate", or "fail"'
            )
        if data_type not in ['csv', 'json']:
            raise ValueError(f"Only supports csv or json files [data_type = {data_type}]")

        table_exists = self.table_exists(table_name)

        # TODO: fix this nonsense (or at least wrap in fn)
        if not job_config:
            job_config = bigquery.LoadJobConfig()
        if not job_config.schema:
            job_config.autodetect = True
        if not job_config.create_disposition:
            job_config.create_disposition = bigquery.CreateDisposition.CREATE_IF_NEEDED
        if not job_config.max_bad_records:
            job_config.max_bad_records = max_errors
        if not job_config.skip_leading_rows:
            job_config.skip_leading_rows = ignoreheader
        if not job_config.source_format:
            job_config.source_format = bigquery.SourceFormat.CSV if data_type == 'csv' else bigquery.SourceFormat.JSON
        if not job_config.field_delimiter:
            if data_type == 'csv':
                job_config.field_delimiter = csv_delimiter
            if nullas:
                job_config.null_marker = nullas
        if not job_config.write_disposition:
            if table_exists:
                if if_exists == "fail":
                    raise ValueError("Table already exists.")
                elif if_exists == "drop":
                    self.delete_table(table_name)
                    job_config.write_disposition = bigquery.WriteDisposition.WRITE_EMPTY
                elif if_exists == "append":
                    job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
                elif if_exists == "truncate":
                    job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
        if not job_config.allow_quoted_newlines:
            job_config.allow_quoted_newlines = allow_quoted_newlines

        # load CSV from Cloud Storage into BigQuery
        table_ref = get_table_ref(self.client, table_name)

        load_job = self.client.load_table_from_uri(
            source_uris=gcs_blob_uri,
            destination=table_ref,
            job_config=job_config,
            **load_kwargs,
        )

        load_job.result()

        # TODO: return anything?

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
        nullas: str = None,
        aws_access_key_id=None,
        aws_secret_access_key=None,
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
            gcs_client: object
                The GoogleCloudStorage Connector to use for loading data into Google Cloud Storage.
            tmp_gcs_bucket: str
                The name of the Google Cloud Storage bucket to use to stage the data to load
                into BigQuery. Required if `GCS_TEMP_BUCKET` is not specified.
            manifest: str
                If using a manifest
            data_type: str
                The data type of the file. Only ``csv`` supported currently.
            csv_delimiter: str
                The delimiter of the ``csv``. Only relevant if data_type is ``csv``.
            compression: str
                If specified (``gzip``), will attempt to decompress the file.
            if_exists: str
                If the table already exists, either ``fail``, ``append``, ``drop``
                or ``truncate`` the table.
            max_errors: int
                The maximum number of rows that can error and be skipped before
                the job fails.
            distkey: str
                The column name of the distkey
            sortkey: str
                The column name of the sortkey
            padding: float
                A percentage padding to add to varchar columns if creating a new table. This is
                helpful to add a buffer for future copies in which the data might be wider.
            varchar_max: list
                A list of columns in which to set the width of the varchar column to 65,535
                characters.
            statupate: boolean
                Governs automatic computation and refresh of optimizer statistics at the end
                of a successful COPY command.
            compupdate: boolean
                Controls whether compression encodings are automatically applied during a COPY.
            ignore_header: int
                The number of header rows to skip. Ignored if data_type is ``json``.
            acceptanydate: boolean
                Allows any date format, including invalid formats such as 00/00/00 00:00:00, to be
                loaded without generating an error.
            emptyasnull: boolean
                Indicates that Amazon Redshift should load empty char and varchar fields
                as ``NULL``.
            blanksasnull: boolean
                Loads blank varchar fields, which consist of only white space characters,
                as ``NULL``.
            nullas: str
                Loads fields that match string as NULL
            acceptinvchars: boolean
                Enables loading of data into VARCHAR columns even if the data contains
                invalid UTF-8 characters.
            dateformat: str
                Set the date format. Defaults to ``auto``.
            timeformat: str
                Set the time format. Defaults to ``auto``.
            truncatecolumns: boolean
                If the table already exists, truncates data in columns to the appropriate number
                of characters so that it fits the column specification. Applies only to columns
                with a VARCHAR or CHAR data type, and rows 4 MB or less in size.
            columntypes: dict
                Optional map of column name to redshift column type, overriding the usual type
                inference. You only specify the columns you want to override, eg.
                ``columntypes={'phone': 'varchar(12)', 'age': 'int'})``.
            specifycols: boolean
                Adds a column list to the Redshift `COPY` command, allowing for the source table
                in an append to have the columnns out of order, and to have fewer columns with any
                leftover target table columns filled in with the `DEFAULT` value.

                This will fail if all of the source table's columns do not match a column in the
                target table. This will also fail if the target table has an `IDENTITY`
                column and that column name is among the source table's columns.
            aws_access_key_id:
                An AWS access key granted to the bucket where the file is located. Not required
                if keys are stored as environmental variables.
            aws_secret_access_key:
                An AWS secret access key granted to the bucket where the file is located. Not
                required if keys are stored as environmental variables.
            bucket_region: str
                The AWS region that the bucket is located in. This should be provided if the
                Redshift cluster is located in a different region from the temp bucket.
            strict_length: bool
                If the database table needs to be created, strict_length determines whether
                the created table's column sizes will be sized to exactly fit the current data,
                or if their size will be rounded up to account for future values being larger
                then the current dataset. defaults to ``True``; this argument is ignored if
                ``padding`` is specified
            template_table: str
                Instead of specifying columns, columntypes, and/or inference, if there
                is a pre-existing table that has the same columns/types, then use the template_table
                table name as the schema for the new table.

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

        `Args:` TODO: check these docs
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
                tbl=tbl,
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
                If the table already exists, either ``fail``, ``replace``, or ``ignore`` the operation.
            drop_source_table: boolean
                Drop the source table
        """
        if if_exists not in ["fail", "replace", "ignore"]:
            raise ValueError("Invalid value for `if_exists` argument")
        if if_exists == "fail" and self.table_exists(destination_table):
            raise ValueError("Table already exists.")

        query = f"""
            CREATE {'OR REPLACE ' if if_exists == 'replace' else ''}TABLE{' IF NOT EXISTS' if if_exists == 'ignore' else ''}
            {destination_table}
            CLONE {source_table}
        """
        if drop_source_table:
            query = self._wrap_queries_in_transaction(
                queries=[query, f"DROP TABLE {source_table}"]
            )

        return self.query(query)

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
                set this to True and include :func:`~parsons.databases.Redshift.copy_s3` arguments
                to upsert a pre-existing s3 file into the target_table
            \**copy_args: kwargs
                See :func:`~parsons.databases.Redshift.copy` for options.
        """  # noqa: W605
        if not self.table_exists(target_table):
            logger.info(
                "Target table does not exist. Copying into newly \
                         created target table."
            )
            self.copy(table_obj, target_table, distkey=distkey, sortkey=sortkey)
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
                table_obj,
                staging_tbl,
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

        transaction_query = self._wrap_queries_in_transaction(queries=queries)

        return self.query(transaction_query)

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

    def get_tables(self, schema, table_name=None):
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

        logger.info("Retrieving tables info.")
        sql = f"select * from {schema}.INFORMATION_SCHEMA.TABLES"
        if table_name:
            sql += f" where table_name = '{table_name}'"
        return self.query(sql)

    def get_views(self, schema, view=None):
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

        logger.info("Retrieving views info.")
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

    def _wrap_queries_in_transaction(self, queries: List[str]):
        joined_queries = queries.join("; \n")
        wrapped_queries = f"""
            BEGIN
                BEGIN TRANSACTION;
                {joined_queries}

            EXCEPTION WHEN ERROR THEN
                -- Roll back the transaction inside the exception handler.
                SELECT @@error.message;
                ROLLBACK TRANSACTION;
            END;
        """
        return wrapped_queries

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

    def _generate_schema_from_gcs(self, gcs_blob_uri):
        # TODO: need to implement this?
        # if so, consider using GoogleCloudStorage class
        # downloading blob as local file
        # converting local file to Parsons table
        # using the _generate_schema_from_parsons_table function
        return None

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
        self.db.copy(
            empty_table, self.table, if_exists="truncate", job_config=job_config
        )
