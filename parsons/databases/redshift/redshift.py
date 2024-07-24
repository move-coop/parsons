from typing import List, Optional
from parsons.etl.table import Table
from parsons.databases.redshift.rs_copy_table import RedshiftCopyTable
from parsons.databases.redshift.rs_create_table import RedshiftCreateTable
from parsons.databases.redshift.rs_table_utilities import RedshiftTableUtilities
from parsons.databases.redshift.rs_schema import RedshiftSchema
from parsons.databases.table import BaseTable
from parsons.databases.alchemy import Alchemy
from parsons.utilities import files, sql_helpers
from parsons.databases.database_connector import DatabaseConnector
import psycopg2
import psycopg2.extras
import os
import logging
import json
import pickle
import petl
from contextlib import contextmanager
import datetime
import random

# Max number of rows that we query at a time, so we can avoid loading huge
# data sets into memory.
# 100k rows per batch at ~1k bytes each = ~100MB per batch.
QUERY_BATCH_SIZE = 100000

logger = logging.getLogger(__name__)


class Redshift(
    RedshiftCreateTable,
    RedshiftCopyTable,
    RedshiftTableUtilities,
    RedshiftSchema,
    Alchemy,
    DatabaseConnector,
):
    """
    A Redshift class to connect to database.

    Args:
        username: str
            Required if env variable ``REDSHIFT_USERNAME`` not populated
        password: str
            Required if env variable ``REDSHIFT_PASSWORD`` not populated
        host: str
            Required if env variable ``REDSHIFT_HOST`` not populated
        db: str
            Required if env variable ``REDSHIFT_DB`` not populated
        port: int
            Required if env variable ``REDSHIFT_PORT`` not populated. Port 5439 is typical.
        timeout: int
            Seconds to timeout if connection not established
        s3_temp_bucket: str
            Name of the S3 bucket that will be used for storing data during bulk transfers.
            Required if you intend to perform bulk data transfers (eg. the copy_s3 method),
            and env variable ``S3_TEMP_BUCKET`` is not populated.
        aws_access_key_id: str
            The default AWS access key id for copying data from S3 into Redshift
            when running copy/upsert/etc methods.
            This will default to environment variable AWS_ACCESS_KEY_ID.
        aws_secret_access_key: str
            The default AWS secret access key for copying data from S3 into Redshift
            when running copy/upsert/etc methods.
            This will default to environment variable AWS_SECRET_ACCESS_KEY.
        iam_role: str
            AWS IAM Role ARN string -- an optional, different way for credentials to
            be provided in the Redshift copy command that does not require an access key.
        use_env_token: bool
            Controls use of the ``AWS_SESSION_TOKEN`` environment variable for S3. Defaults
            to ``True``. Set to ``False`` in order to ignore the ``AWS_SESSION_TOKEN`` environment
            variable even if the ``aws_session_token`` argument was not passed in.
    """

    def __init__(
        self,
        username=None,
        password=None,
        host=None,
        db=None,
        port=None,
        timeout=10,
        s3_temp_bucket=None,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        iam_role=None,
        use_env_token=True,
    ):
        super().__init__()

        try:
            self.username = username or os.environ["REDSHIFT_USERNAME"]
            self.password = password or os.environ["REDSHIFT_PASSWORD"]
            self.host = host or os.environ["REDSHIFT_HOST"]
            self.db = db or os.environ["REDSHIFT_DB"]
            self.port = port or os.environ["REDSHIFT_PORT"]
        except KeyError as error:
            logger.error("Connection info missing. Most include as kwarg or " "env variable.")
            raise error

        self.timeout = timeout
        self.dialect = "redshift"
        self.s3_temp_bucket = s3_temp_bucket or os.environ.get("S3_TEMP_BUCKET")
        # Set prefix for temp S3 bucket paths that include subfolders
        self.s3_temp_bucket_prefix = None
        if self.s3_temp_bucket and "/" in self.s3_temp_bucket:
            split_temp_bucket_name = self.s3_temp_bucket.split("/", 1)
            self.s3_temp_bucket = split_temp_bucket_name[0]
            self.s3_temp_bucket_prefix = split_temp_bucket_name[1]
        self.use_env_token = use_env_token
        # We don't check/load the environment variables for aws_* here
        # because the logic in S3() and rs_copy_table.py does already.
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.iam_role = iam_role

    @contextmanager
    def connection(self):
        """
        Generate a Redshift connection.
        The connection is set up as a python "context manager", so it will be closed
        automatically (and all queries committed) when the connection goes out of scope.

        When using the connection, make sure to put it in a ``with`` block (necessary for
        any context manager):
        ``with rs.connection() as conn:``

        `Returns:`
            Psycopg2 ``connection`` object
        """

        # Create a psycopg2 connection and cursor
        conn = psycopg2.connect(
            user=self.username,
            password=self.password,
            host=self.host,
            dbname=self.db,
            port=self.port,
            connect_timeout=self.timeout,
        )
        try:
            yield conn

            conn.commit()
        finally:
            conn.close()

    @contextmanager
    def cursor(self, connection):
        cur = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        try:
            yield cur
        finally:
            cur.close()

    def query(self, sql: str, parameters: Optional[list] = None) -> Optional[Table]:
        """
        Execute a query against the Redshift database. Will return ``None``
        if the query returns zero rows.

        To include python variables in your query, it is recommended to pass them as parameters,
        following the `psycopg style <http://initd.org/psycopg/docs/usage.html#passing-parameters-to-sql-queries>`_.
        Using the ``parameters`` argument ensures that values are escaped properly, and avoids SQL
        injection attacks.

        **Parameter Examples**

        .. code-block:: python

            # Note that the name contains a quote, which could break your query if not escaped
            # properly.
            name = "Beatrice O'Brady"
            sql = "SELECT * FROM my_table WHERE name = %s"
            rs.query(sql, parameters=[name])

        .. code-block:: python

            names = ["Allen Smith", "Beatrice O'Brady", "Cathy Thompson"]
            placeholders = ', '.join('%s' for item in names)
            sql = f"SELECT * FROM my_table WHERE name IN ({placeholders})"
            rs.query(sql, parameters=names)

        `Args:`
            sql: str
                A valid SQL statement
            parameters: list
                A list of python variables to be converted into SQL values in your query

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.

        """  # noqa: E501

        with self.connection() as connection:
            return self.query_with_connection(sql, connection, parameters=parameters)

    def query_with_connection(self, sql, connection, parameters=None, commit=True):
        """
        Execute a query against the Redshift database, with an existing connection.
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
                Whether to commit the transaction immediately. If ``False`` the transaction will
                be committed when the connection goes out of scope and is closed (or you can
                commit manually with ``connection.commit()``).

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        # To Do: Have it return an ordered dict to return the
        #        rows in the correct order

        with self.cursor(connection) as cursor:
            if "credentials" not in sql:
                logger.debug(f"SQL Query: {sql}")
            cursor.execute(sql, parameters)

            if commit:
                connection.commit()

            # If the cursor is empty, don't cause an error
            if not cursor.description:
                logger.debug("Query returned 0 rows")
                return None

            else:
                # Fetch the data in batches, and "pickle" the rows to a temp file.
                # (We pickle rather than writing to, say, a CSV, so that we maintain
                # all the type information for each field.)

                temp_file = files.create_temp_file()

                with open(temp_file, "wb") as f:
                    # Grab the header
                    header = [i[0] for i in cursor.description]
                    pickle.dump(header, f)

                    while True:
                        batch = cursor.fetchmany(QUERY_BATCH_SIZE)
                        if not batch:
                            break

                        logger.debug(f"Fetched {len(batch)} rows.")
                        for row in batch:
                            pickle.dump(list(row), f)

                # Load a Table from the file
                final_tbl = Table(petl.frompickle(temp_file))

                logger.debug(f"Query returned {final_tbl.num_rows} rows.")
                return final_tbl

    def copy_s3(
        self,
        table_name,
        bucket,
        key,
        manifest=False,
        data_type="csv",
        csv_delimiter=",",
        compression=None,
        if_exists="fail",
        max_errors=0,
        distkey=None,
        sortkey=None,
        padding=None,
        varchar_max=None,
        statupdate=True,
        compupdate=True,
        ignoreheader=1,
        acceptanydate=True,
        dateformat="auto",
        timeformat="auto",
        emptyasnull=True,
        blanksasnull=True,
        nullas=None,
        acceptinvchars=True,
        truncatecolumns=False,
        columntypes=None,
        specifycols=None,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        bucket_region=None,
        strict_length=True,
        template_table=None,
        encoding="utf-8",
        line_delimited=False,
    ):
        """
        Copy a file from s3 to Redshift.

        `Args:`
            table_name: str
                The table name and schema (``tmc.cool_table``) to point the file.
            bucket: str
                The s3 bucket where the file or manifest is located.
            key: str
                The key of the file or manifest in the s3 bucket.
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

        with self.connection() as connection:
            if self._create_table_precheck(connection, table_name, if_exists):
                if template_table:
                    sql = f"CREATE TABLE {table_name} (LIKE {template_table})"
                else:
                    # Grab the object from s3
                    from parsons.aws.s3 import S3

                    s3 = S3(
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key,
                        use_env_token=self.use_env_token,
                    )

                    local_path = s3.get_file(bucket, key)
                    if data_type == "csv":
                        tbl = Table.from_csv(local_path, delimiter=csv_delimiter, encoding=encoding)
                    elif data_type == "json":
                        tbl = Table.from_json(local_path, line_delimited=line_delimited)
                    else:
                        raise TypeError("Invalid data type provided")

                    # Create the table
                    sql = self.create_statement(
                        tbl,
                        table_name,
                        padding=padding,
                        distkey=distkey,
                        sortkey=sortkey,
                        varchar_max=varchar_max,
                        columntypes=columntypes,
                        strict_length=strict_length,
                    )

                self.query_with_connection(sql, connection, commit=False)
                logger.info(f"{table_name} created.")

            # Copy the table
            logger.info(f"Data type is {data_type}")
            copy_sql = self.copy_statement(
                table_name,
                bucket,
                key,
                manifest=manifest,
                data_type=data_type,
                csv_delimiter=csv_delimiter,
                compression=compression,
                max_errors=max_errors,
                statupdate=statupdate,
                compupdate=compupdate,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                ignoreheader=ignoreheader,
                acceptanydate=acceptanydate,
                emptyasnull=emptyasnull,
                blanksasnull=blanksasnull,
                nullas=nullas,
                acceptinvchars=acceptinvchars,
                truncatecolumns=truncatecolumns,
                specifycols=specifycols,
                dateformat=dateformat,
                timeformat=timeformat,
                bucket_region=bucket_region,
            )

            self.query_with_connection(copy_sql, connection, commit=False)
            logger.info(f"Data copied to {table_name}.")

    def copy(
        self,
        tbl: Table,
        table_name: str,
        if_exists: str = "fail",
        max_errors: int = 0,
        distkey: Optional[str] = None,
        sortkey: Optional[str] = None,
        padding: Optional[float] = None,
        statupdate: Optional[bool] = None,
        compupdate: Optional[bool] = None,
        acceptanydate: bool = True,
        emptyasnull: bool = True,
        blanksasnull: bool = True,
        nullas: Optional[str] = None,
        acceptinvchars: bool = True,
        dateformat: str = "auto",
        timeformat: str = "auto",
        varchar_max: Optional[List[str]] = None,
        truncatecolumns: bool = False,
        columntypes: Optional[dict] = None,
        specifycols: Optional[bool] = None,
        alter_table: bool = False,
        alter_table_cascade: bool = False,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        iam_role: Optional[str] = None,  # Unused - Should we remove?
        cleanup_s3_file: bool = True,
        template_table: Optional[str] = None,
        temp_bucket_region: Optional[str] = None,
        strict_length: bool = True,
        csv_encoding: str = "utf-8",
    ):
        """
        Copy a :ref:`parsons-table` to Redshift.

        `Args:`
            tbl: obj
                A Parsons Table.
            table_name: str
                The destination table name (ex. ``my_schema.my_table``).
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
            statupate: boolean
                Governs automatic computation and refresh of optimizer statistics at the end
                of a successful COPY command. If ``True`` explicitly sets ``statupate`` to on, if
                ``False`` explicitly sets ``statupate`` to off. If ``None`` stats update only if
                the table is initially empty. Defaults to ``None``.
                See `Redshift docs <https://docs.aws.amazon.com/redshift/latest/dg/copy-parameters-data-load.html#copy-statupdate>`_
                for more details.

                .. note::
                    If STATUPDATE is used, the current user must be either the table owner or a
                    superuser.

            compupdate: boolean
                Controls whether compression encodings are automatically applied during a COPY. If
                ``True`` explicitly sets ``compupdate`` to on, if ``False`` explicitly sets
                ``compupdate`` to off. If ``None`` the COPY command only chooses compression if the
                table is initially empty. Defaults to ``None``.
                See `Redshift docs <https://docs.aws.amazon.com/redshift/latest/dg/copy-parameters-data-load.html#copy-compupdate>`_
                for more details.
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
            varchar_max: list
                A list of columns in which to set the width of the varchar column to 65,535
                characters.
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
            alter_table: boolean
                Will check if the target table varchar widths are wide enough to copy in the
                table data. If not, will attempt to alter the table to make it wide enough. This
                will not work with tables that have dependent views. To drop them, set
                ``alter_table_cascade`` to True.
            alter_table_cascade: boolean
                Will drop dependent objects when attempting to alter the table. If ``alter_table``
                is ``False``, this will be ignored.
            aws_access_key_id:
                An AWS access key granted to the bucket where the file is located. Not required
                if keys are stored as environmental variables.
            aws_secret_access_key:
                An AWS secret access key granted to the bucket where the file is located. Not
                required if keys are stored as environmental variables.
            iam_role: str
                An AWS IAM Role ARN string; an alternative credential for the COPY command
                from Redshift to S3. The IAM role must have been assigned to the Redshift
                instance and have access to the S3 bucket.
            cleanup_s3_file: boolean
                The s3 upload is removed by default on cleanup. You can set to False for debugging.
            template_table: str
                Instead of specifying columns, columntypes, and/or inference, if there
                is a pre-existing table that has the same columns/types, then use the template_table
                table name as the schema for the new table.
                Unless you set specifycols=False explicitly, a template_table will set it to True
            temp_bucket_region: str
                The AWS region that the temp bucket (specified by the TEMP_S3_BUCKET environment
                variable) is located in. This should be provided if the Redshift cluster is located
                in a different region from the temp bucket.
            strict_length: bool
                Whether or not to tightly fit the length of the table columns to the length
                of the data in ``tbl``; if ``padding`` is specified, this argument is ignored.
            csv_ecoding: str
                String encoding to use when writing the temporary CSV file that is uploaded to S3.
                Defaults to 'utf-8'.

        `Returns`
            Parsons Table or ``None``
                See :ref:`parsons-table` for output options.
        """  # noqa: E501

        # Specify the columns for a copy statement.
        if specifycols or (specifycols is None and template_table):
            cols = tbl.columns
        else:
            cols = None

        with self.connection() as connection:
            # Check to see if the table exists. If it does not or if_exists = drop, then
            # create the new table.
            if self._create_table_precheck(connection, table_name, if_exists):
                if template_table:
                    # Copy the schema from the template table
                    sql = f"CREATE TABLE {table_name} (LIKE {template_table})"
                else:
                    sql = self.create_statement(
                        tbl,
                        table_name,
                        padding=padding,
                        distkey=distkey,
                        sortkey=sortkey,
                        varchar_max=varchar_max,
                        columntypes=columntypes,
                        strict_length=strict_length,
                    )
                self.query_with_connection(sql, connection, commit=False)
                logger.info(f"{table_name} created.")

            # If alter_table is True, then alter table if the table column widths
            # are wider than the existing table.
            if alter_table:
                self.alter_varchar_column_widths(
                    tbl, table_name, drop_dependencies=alter_table_cascade
                )

            # Upload the table to S3
            key = self.temp_s3_copy(
                tbl,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                csv_encoding=csv_encoding,
            )

            try:
                # Copy to Redshift database.
                copy_args = {
                    "max_errors": max_errors,
                    "ignoreheader": 1,
                    "statupdate": statupdate,
                    "compupdate": compupdate,
                    "acceptanydate": acceptanydate,
                    "dateformat": dateformat,
                    "timeformat": timeformat,
                    "blanksasnull": blanksasnull,
                    "nullas": nullas,
                    "emptyasnull": emptyasnull,
                    "acceptinvchars": acceptinvchars,
                    "truncatecolumns": truncatecolumns,
                    "specifycols": cols,
                    "aws_access_key_id": aws_access_key_id,
                    "aws_secret_access_key": aws_secret_access_key,
                    "compression": "gzip",
                    "bucket_region": temp_bucket_region,
                }

                # Copy from S3 to Redshift
                sql = self.copy_statement(table_name, self.s3_temp_bucket, key, **copy_args)
                sql_censored = sql_helpers.redact_credentials(sql)

                logger.debug(f"Copy SQL command: {sql_censored}")
                self.query_with_connection(sql, connection, commit=False)

                logger.info(f"Data copied to {table_name}.")

            # Clean up the S3 bucket.
            finally:
                if key and cleanup_s3_file:
                    self.temp_s3_delete(key)

    def unload(
        self,
        sql,
        bucket,
        key_prefix,
        manifest=True,
        header=True,
        delimiter="|",
        compression="gzip",
        add_quotes=True,
        null_as=None,
        escape=True,
        allow_overwrite=True,
        parallel=True,
        max_file_size="6.2 GB",
        extension=None,
        aws_region=None,
        aws_access_key_id=None,
        aws_secret_access_key=None,
    ):
        """
        Unload Redshift data to S3 Bucket. This is a more efficient method than running a query
        to export data as it can export in parallel and directly into an S3 bucket. Consider
        using this for exports of 10MM or more rows.

        sql: str
            The SQL string to execute to generate the data to unload.
        bucket: str
           The destination S3 bucket
        key_prefix: str
            The prefix of the key names that will be written
        manifest: boolean
            Creates a manifest file that explicitly lists details for the data files
            that are created by the UNLOAD process.
        header: boolean
            Adds a header line containing column names at the top of each output file.
        delimiter: str
            Specificies the character used to separate fields. Defaults to '|'.
        compression: str
            One of ``gzip``, ``bzip2`` or ``None``. Unloads data to one or more compressed
            files per slice. Each resulting file is appended with a ``.gz`` or ``.bz2`` extension.
        add_quotes: boolean
            Places quotation marks around each unloaded data field, so that Amazon Redshift
            can unload data values that contain the delimiter itself.
        null_as: str
            Specifies a string that represents a null value in unload files. If this option is
            not specified, null values are unloaded as zero-length strings for delimited output.
        escape: boolean
            For CHAR and VARCHAR columns in delimited unload files, an escape character (\) is
            placed before every linefeed, carriage return, escape characters and delimiters.
        allow_overwrite: boolean
            If ``True``, will overwrite existing files, including the manifest file. If ``False``
            will fail.
        parallel: boolean
            By default, UNLOAD writes data in parallel to multiple files, according to the number
            of slices in the cluster. The default option is ON or TRUE. If PARALLEL is OFF or
            FALSE, UNLOAD writes to one or more data files serially, sorted absolutely according
            to the ORDER BY clause, if one is used.
        max_file_size: str
            The maximum size of files UNLOAD creates in Amazon S3. Specify a decimal value between
            5 MB and 6.2 GB.
        extension: str
            This extension will be added to the end of file names loaded to S3
        region: str
            The AWS Region where the target Amazon S3 bucket is located. REGION is required for
            UNLOAD to an Amazon S3 bucket that is not in the same AWS Region as the Amazon Redshift
            cluster.
        aws_access_key_id:
            An AWS access key granted to the bucket where the file is located. Not required
            if keys are stored as environmental variables.
        aws_secret_access_key:
            An AWS secret access key granted to the bucket where the file is located. Not
            required if keys are stored as environmental variables.
        """  # NOQA W605

        # The sql query is provided between single quotes, therefore single
        # quotes within the actual query must be escaped.
        # https://docs.aws.amazon.com/redshift/latest/dg/r_UNLOAD.html#unload-parameters
        sql = sql.replace("'", "''")

        statement = f"""
                     UNLOAD ('{sql}') to 's3://{bucket}/{key_prefix}' \n
                     {self.get_creds(aws_access_key_id, aws_secret_access_key)} \n
                     PARALLEL {parallel} \n
                     MAXFILESIZE {max_file_size}
                     """
        if manifest:
            statement += "MANIFEST \n"
        if header:
            statement += "HEADER \n"
        if delimiter:
            statement += f"DELIMITER as '{delimiter}' \n"
        if compression:
            statement += f"{compression.upper()} \n"
        if add_quotes:
            statement += "ADDQUOTES \n"
        if null_as:
            statement += f"NULL {null_as} \n"
        if escape:
            statement += "ESCAPE \n"
        if allow_overwrite:
            statement += "ALLOWOVERWRITE \n"
        if extension:
            statement += f"EXTENSION '{extension}' \n"
        if aws_region:
            statement += f"REGION {aws_region} \n"

        logger.info(f"Unloading data to s3://{bucket}/{key_prefix}")
        # Censor sensitive data
        statement_censored = sql_helpers.redact_credentials(statement)
        logger.debug(statement_censored)

        return self.query(statement)

    def drop_and_unload(
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
        query_end = "cascade" if cascade else ""

        self.unload(
            sql=f"select * from {rs_table}",
            bucket=bucket,
            key_prefix=f"{key}/{rs_table.replace('.', '_')}/",
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

        self.query(f"drop table if exists {rs_table} {query_end}")

        return None

    def generate_manifest(
        self,
        buckets,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        mandatory=True,
        prefix=None,
        manifest_bucket=None,
        manifest_key=None,
        path=None,
    ):
        """
        Given a list of S3 buckets, generate a manifest file (JSON format). A manifest file
        allows you to copy multiple files into a single table at once. Once the manifest is
        generated, you can pass it with the :func:`~parsons.redshift.Redshift.copy_s3` method.

        AWS keys are not required if ``AWS_ACCESS_KEY_ID`` and
        ``AWS_SECRET_ACCESS_KEY`` environmental variables set.

        `Args:`

            buckets: list or str
                A list of buckets or single bucket from which to generate manifest
            aws_access_key_id: str
                AWS access key id to access S3 bucket
            aws_secret_access_key: str
                AWS secret access key to access S3 bucket
            mandatory: boolean
                The mandatory flag indicates whether the Redshift COPY should
                terminate if the file does not exist.
            prefix: str
                Optional filter for key prefixes
            manifest_bucket: str
                Optional bucket to write manifest file.
            manifest_key: str
                Optional key name for S3 bucket to write file

        `Returns:`
            ``dict`` of manifest
        """

        from parsons.aws import S3

        s3 = S3(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            use_env_token=self.use_env_token,
        )

        # Deal with a single bucket being passed, rather than list.
        if isinstance(buckets, str):
            buckets = [buckets]

        # Generate manifest file
        manifest = {"entries": []}
        for bucket in buckets:
            # Retrieve list of files in bucket
            key_list = s3.list_keys(bucket, prefix=prefix)
            for key in key_list:
                manifest["entries"].append(
                    {"url": "/".join(["s3:/", bucket, key]), "mandatory": mandatory}
                )

        logger.info("Manifest generated.")

        # Save the file to s3 bucket if provided
        if manifest_key and manifest_bucket:
            # Dump the manifest to a temp JSON file
            manifest_path = files.create_temp_file()
            with open(manifest_path, "w") as manifest_file_obj:
                json.dump(manifest, manifest_file_obj, sort_keys=True, indent=4)

            # Upload the file to S3
            s3.put_file(manifest_bucket, manifest_key, manifest_path)

            logger.info(f"Manifest saved to s3://{manifest_bucket}/{manifest_key}")

        return manifest

    def upsert(
        self,
        table_obj,
        target_table,
        primary_key,
        vacuum=True,
        distinct_check=True,
        cleanup_temp_table=True,
        alter_table=True,
        alter_table_cascade=False,
        from_s3=False,
        distkey=None,
        sortkey=None,
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
            vacuum: boolean
                Re-sorts rows and reclaims space in the specified table. You must be a table owner
                or super user to effectively vacuum a table, however the method will not fail
                if you lack these priviledges.
            distinct_check: boolean
                Check if the primary key column is distinct. Raise error if not.
            cleanup_temp_table: boolean
                A temp table is dropped by default on cleanup. You can set to False for debugging.
            alter_table: boolean
                Set to False to avoid automatic varchar column resizing to accomodate new data
            alter_table_cascade: boolean
                Will drop dependent objects when attempting to alter the table. If ``alter_table``
                is ``False``, this will be ignored.
            from_s3: boolean
                Instead of specifying a table_obj (set the first argument to None),
                set this to True and include :func:`~parsons.databases.Redshift.copy_s3` arguments
                to upsert a pre-existing s3 file into the target_table
            distkey: str
                The column name of the distkey. If not provided, will default to ``primary_key``.
            sortkey: str or list
                The column name(s) of the sortkey. If not provided, will default to ``primary_key``.
            \**copy_args: kwargs
                See :func:`~parsons.databases.Redshift.copy` for options.
        """  # noqa: W605

        if isinstance(primary_key, str):
            primary_keys = [primary_key]
        else:
            primary_keys = primary_key

        # Set distkey and sortkey to argument or primary key. These keys will be used
        # for the staging table and, if it does not already exist, the destination table.
        distkey = distkey or primary_keys[0]
        sortkey = sortkey or primary_key

        if not self.table_exists(target_table):
            logger.info(
                "Target table does not exist. Copying into newly \
                         created target table."
            )
            self.copy(table_obj, target_table, distkey=distkey, sortkey=sortkey)
            return None

        if alter_table and table_obj:
            # Make target table column widths match incoming table, if necessary
            self.alter_varchar_column_widths(
                table_obj, target_table, drop_dependencies=alter_table_cascade
            )

        noise = f"{random.randrange(0, 10000):04}"[:4]
        date_stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        # Generate a temp table like "table_tmp_20200210_1230_14212"
        staging_tbl = "{}_stg_{}_{}".format(target_table, date_stamp, noise)

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

        with self.connection() as connection:
            try:
                # Copy to a staging table
                logger.info(f"Building staging table: {staging_tbl}")
                if "compupdate" not in copy_args:
                    # Especially with a lot of columns, compupdate=True can
                    # cause a lot of processing/analysis by Redshift before upload.
                    # Since this is a temporary table, setting compression for each
                    # column is not impactful barely impactful
                    # https://docs.aws.amazon.com/redshift/latest/dg/c_Loading_tables_auto_compress.html
                    copy_args = dict(copy_args, compupdate=False)

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
                        alter_table=False,  # We just did our own alter table above
                        distkey=distkey,
                        sortkey=sortkey,
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

                sql = f"""
                       DELETE FROM {target_table}
                       USING {staging_tbl}
                       WHERE {where_clause}
                       """
                self.query_with_connection(sql, connection, commit=False)
                logger.debug(f"Target rows deleted from {target_table}.")

                # Insert rows
                # ALTER TABLE APPEND would be more efficient, but you can't run it in a
                # transaction block. It's worth the performance hit to not commit until the
                # end.
                sql = f"""
                       INSERT INTO {target_table}
                       SELECT * FROM {staging_tbl};
                       """

                self.query_with_connection(sql, connection, commit=False)
                logger.info(f"Target rows inserted to {target_table}")

            finally:
                if cleanup_temp_table:
                    # Drop the staging table
                    self.query_with_connection(
                        f"DROP TABLE IF EXISTS {staging_tbl};", connection, commit=False
                    )
                    logger.info(f"{staging_tbl} staging table dropped.")

        # Vacuum table. You must commit when running this type of transaction.
        if vacuum:
            with self.connection() as connection:
                connection.set_session(autocommit=True)
                self.query_with_connection(f"VACUUM {target_table};", connection)
                logger.info(f"{target_table} vacuumed.")

    def drop_dependencies_for_cols(self, schema, table, cols):
        fmt_cols = ", ".join([f"'{c}'" for c in cols])
        sql_depend = f"""
            select
                distinct dependent_ns.nspname||'.'||dependent_view.relname as table_name
            from pg_depend
            join pg_rewrite
                on pg_depend.objid = pg_rewrite.oid
            join pg_class as dependent_view
                on pg_rewrite.ev_class = dependent_view.oid
            join pg_class as source_table
                on pg_depend.refobjid = source_table.oid
            join pg_attribute
                on pg_depend.refobjid = pg_attribute.attrelid
                and pg_depend.refobjsubid = pg_attribute.attnum
            join pg_namespace dependent_ns
                on dependent_ns.oid = dependent_view.relnamespace
            join pg_namespace source_ns on source_ns.oid = source_table.relnamespace
            where
                source_ns.nspname = '{schema}'
                and source_table.relname = '{table}'
                and pg_attribute.attname in ({fmt_cols})
            ;
        """

        with self.connection() as connection:
            connection.set_session(autocommit=True)
            tbl = self.query_with_connection(sql_depend, connection)
            dropped_views = [row["table_name"] for row in tbl]
            if dropped_views:
                sql_drop = "\n".join([f"drop view {view} CASCADE;" for view in dropped_views])
                tbl = self.query_with_connection(sql_drop, connection)
                logger.info(f"Dropped the following views: {dropped_views}")

        return tbl

    def alter_varchar_column_widths(self, tbl, table_name, drop_dependencies=False):
        """
        Alter the width of a varchar columns in a Redshift table to match the widths
        of a Parsons table. The columns are matched by column name and not their
        index.

        `Args:`
            tbl: obj
                A Parsons table
            table_name:
                The target table name (e.g. ``my_schema.my_table``)
        `Returns:`
            ``None``
        """

        # Make the Parsons table column names match valid Redshift names
        tbl.table = petl.setheader(tbl.table, self.column_name_validate(tbl.columns))

        # Create a list of column names and max width for string values.
        pc = {c: tbl.get_column_max_width(c) for c in tbl.columns}

        # Determine the max width of the varchar columns in the Redshift table
        s, t = self.split_full_table_name(table_name)
        cols = self.get_columns(s, t)
        rc = {
            k: v["max_length"] for k, v in cols.items() if v["data_type"] == "character varying"
        }  # noqa: E501, E261

        # Figure out if any of the destination table varchar columns are smaller than the
        # associated Parsons table columns. If they are, then alter column types to expand
        # their width.
        for c in set(rc.keys()).intersection(set(pc.keys())):
            if rc[c] < pc[c] and rc[c] != 65535:
                logger.info(f"{c} not wide enough. Expanding column width.")
                # If requested size is larger than Redshift will allow,
                # automatically set to Redshift's max varchar width
                new_size = 65535
                if pc[c] < new_size:
                    new_size = pc[c]
                if drop_dependencies:
                    self.drop_dependencies_for_cols(s, t, [c])
                self.alter_table_column_type(table_name, c, "varchar", varchar_width=new_size)

    def alter_table_column_type(self, table_name, column_name, data_type, varchar_width=None):
        """
        Alter a column type of an existing table.

        table_name: str
            The table name (ex. ``my_schema.my_table``).
        column_name: str
            The target column name
        data_type: str
            A valid Redshift data type to alter the table to.
        varchar_width:
            The new width of the column if of type varchar.
        """

        sql = f"ALTER TABLE {table_name} ALTER COLUMN {column_name} TYPE {data_type}"

        if varchar_width:
            sql += f"({varchar_width})"

        with self.connection() as connection:
            connection.set_session(autocommit=True)
            self.query_with_connection(sql, connection)
            logger.info(f"Altered {table_name} {column_name}.")

    def table(self, table_name):
        # Return a Redshift table object

        return RedshiftTable(self, table_name)


class RedshiftTable(BaseTable):
    # Redshift table object.

    pass
