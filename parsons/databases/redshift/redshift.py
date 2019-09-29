from parsons.etl.table import Table
from parsons.databases.redshift.rs_copy_table import RedshiftCopyTable
from parsons.databases.redshift.rs_create_table import RedshiftCreateTable
from parsons.databases.redshift.rs_table_utilities import RedshiftTableUtilities
from parsons.databases.redshift.rs_schema import RedshiftSchema
from parsons.utilities import files
import psycopg2
import psycopg2.extras
import os
import logging
import json
import pickle
import petl
from contextlib import contextmanager
import datetime

# Max number of rows that we query at a time, so we can avoid loading huge
# data sets into memory.
# 100k rows per batch at ~1k bytes each = ~100MB per batch.
QUERY_BATCH_SIZE = 100000

logger = logging.getLogger(__name__)


class Redshift(RedshiftCreateTable, RedshiftCopyTable, RedshiftTableUtilities, RedshiftSchema):
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
    """

    def __init__(self, username=None, password=None, host=None, db=None, port=None,
                 timeout=10, s3_temp_bucket=None):

        try:
            self.username = username or os.environ['REDSHIFT_USERNAME']
            self.password = password or os.environ['REDSHIFT_PASSWORD']
            self.host = host or os.environ['REDSHIFT_HOST']
            self.db = db or os.environ['REDSHIFT_DB']
            self.port = port or os.environ['REDSHIFT_PORT']
        except KeyError as error:
            logger.error("Connection info missing. Most include as kwarg or "
                         "env variable.")
            raise error

        self.timeout = timeout
        # Petl needs this to create tables
        self.dialect = 'postgresql'

        self.s3_temp_bucket = s3_temp_bucket or os.environ.get('S3_TEMP_BUCKET')

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
            Psycopg2 `connection` object
        """

        # Create a psycopg2 connection and cursor
        conn = psycopg2.connect(user=self.username, password=self.password,
                                host=self.host, dbname=self.db, port=self.port,
                                connect_timeout=self.timeout)
        yield conn

        conn.commit()
        conn.close()

    @contextmanager
    def cursor(self, connection):
        cur = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        yield cur
        cur.close()

    def query(self, sql, parameters=None):
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

            logger.debug(f'SQL Query: {sql}')
            cursor.execute(sql, parameters)

            if commit:
                connection.commit()

            # If the cursor is empty, don't cause an error
            if not cursor.description:
                logger.debug('Query returned 0 rows')
                return None

            else:

                # Fetch the data in batches, and "pickle" the rows to a temp file.
                # (We pickle rather than writing to, say, a CSV, so that we maintain
                # all the type information for each field.)

                temp_file = files.create_temp_file()

                with open(temp_file, 'wb') as f:
                    # Grab the header
                    header = [i[0] for i in cursor.description]
                    pickle.dump(header, f)

                    while True:
                        batch = cursor.fetchmany(QUERY_BATCH_SIZE)
                        if not batch:
                            break

                        logger.debug(f'Fetched {len(batch)} rows.')
                        for row in batch:
                            pickle.dump(list(row), f)

                # Load a Table from the file
                final_tbl = Table(petl.frompickle(temp_file))

                logger.debug(f'Query returned {final_tbl.num_rows} rows.')
                return final_tbl

    def copy_s3(self, table_name, bucket, key, manifest=False, data_type='csv',
                csv_delimiter=',', compression=None, if_exists='fail', max_errors=0,
                distkey=None, sortkey=None, padding=None, varchar_max=None,
                statupdate=True, compupdate=True, ignoreheader=1, acceptanydate=True,
                dateformat='auto', timeformat='auto', emptyasnull=True,
                blanksasnull=True, nullas=None, acceptinvchars=True, truncatecolumns=False,
                columntypes=None, specifycols=None,
                aws_access_key_id=None, aws_secret_access_key=None):
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
        `Returns`
            Parsons Table or ``None``
                See :ref:`parsons-table` for output options.
        """

        with self.connection() as connection:
            should_create = self._create_table_precheck(connection, table_name, if_exists)

            if should_create:
                # Grab the object from s3
                from parsons.aws.s3 import S3
                s3 = S3(aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key)

                local_path = s3.get_file(bucket, key)

                if data_type == 'csv':
                    tbl = Table.from_csv(local_path)
                else:
                    raise TypeError("Invalid data type provided")

                # Create the table
                sql = self.create_statement(tbl, table_name, padding=padding,
                                            distkey=distkey, sortkey=sortkey,
                                            varchar_max=varchar_max,
                                            columntypes=columntypes)

                self.query_with_connection(sql, connection, commit=False)
                logger.info(f'{table_name} created.')

            # Copy the table
            copy_sql = self.copy_statement(table_name, bucket, key, manifest=manifest,
                                           data_type=data_type, csv_delimiter=csv_delimiter,
                                           compression=compression,
                                           max_errors=max_errors,
                                           statupdate=statupdate, compupdate=compupdate,
                                           aws_access_key_id=aws_access_key_id,
                                           aws_secret_access_key=aws_secret_access_key,
                                           ignoreheader=ignoreheader, acceptanydate=acceptanydate,
                                           emptyasnull=emptyasnull, blanksasnull=blanksasnull,
                                           nullas=nullas, acceptinvchars=acceptinvchars,
                                           truncatecolumns=truncatecolumns,
                                           specifycols=specifycols,
                                           dateformat=dateformat, timeformat=timeformat)

            self.query_with_connection(copy_sql, connection, commit=False)
            logger.info(f'Data copied to {table_name}.')

    def copy(self, table_obj, table_name, if_exists='fail', max_errors=0, distkey=None,
             sortkey=None, padding=None, statupdate=False, compupdate=True, acceptanydate=True,
             emptyasnull=True, blanksasnull=True, nullas=None, acceptinvchars=True,
             dateformat='auto', timeformat='auto', varchar_max=None, truncatecolumns=False,
             columntypes=None, specifycols=False,
             aws_access_key_id=None, aws_secret_access_key=None):
        """
        Copy a :ref:`parsons-table` to Redshift.

        `Args:`
            table_obj: obj
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
            varchar_max: list
                A list of columns in which to set the width of the varchar column to 65,535
                characters.
            statupate: boolean
                Governs automatic computation and refresh of optimizer statistics at the end
                of a successful COPY command.
            compupdate: boolean
                Controls whether compression encodings are automatically applied during a COPY.
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
        `Returns`
            Parsons Table or ``None``
                See :ref:`parsons-table` for output options.
        """

        # To Do:
        # Auto split big files to copy more quickly
        # Consider a json for better stability

        key = self.temp_s3_copy(table_obj)

        cols = None
        if specifycols:
            cols = table_obj.columns

        try:

            self.copy_s3(table_name, self.s3_temp_bucket, key,
                         if_exists=if_exists, max_errors=max_errors,
                         distkey=distkey, sortkey=sortkey, padding=padding, ignoreheader=1,
                         varchar_max=varchar_max, statupdate=statupdate, compupdate=compupdate,
                         acceptanydate=acceptanydate, dateformat=dateformat, timeformat=timeformat,
                         blanksasnull=blanksasnull, nullas=nullas, emptyasnull=emptyasnull,
                         acceptinvchars=acceptinvchars, truncatecolumns=truncatecolumns,
                         columntypes=columntypes, specifycols=cols,
                         aws_access_key_id=aws_access_key_id,
                         aws_secret_access_key=aws_secret_access_key, compression='gzip')

        finally:

            self.temp_s3_delete(key)

    def unload(self, sql, bucket, key_prefix, manifest=True, header=True, compression='gzip',
               add_quotes=True, null_as=None, escape=True, allow_overwrite=True,
               parallel=True, max_file_size='6.2 GB', aws_region=None,
               aws_access_key_id=None, aws_secret_access_key=None):
        """
        Unload Redshift data to S3 Bucket. This is a more efficient method than running a query
        to export data as it can export in parallel and directly into an S3 bucket. Consider
        using this for exports of 10MM or more rows.

        sql: str
            The SQL string to execute to generate the data to unload.
        buckey: str
           The destination S3 bucket
        key_prefix: str
            The prefix of the key names that will be written
        manifest: boolean
            Creates a manifest file that explicitly lists details for the data files
            that are created by the UNLOAD process.
        header: boolean
            Adds a header line containing column names at the top of each output file.
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
        if compression:
            statement += f"{compression.upper()} \n"
        if add_quotes:
            statement += "ADDQUOTES \n"
        if null_as:
            statement += f"NULL {null_as} \n"
        if escape:
            statement += "ESCAPE \n"
        if allow_overwrite:
            statement += "ALLOWOVERWRITE"
        if aws_region:
            statement += f"REGION {aws_region}"

        logger.info(f'Unloading data to s3://{bucket}/{key_prefix}')
        logger.debug(statement)

        return self.query(statement)

    def generate_manifest(self, buckets, aws_access_key_id=None, aws_secret_access_key=None,
                          mandatory=True, prefix=None, manifest_bucket=None, manifest_key=None,
                          path=None):
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

        from parsons import S3
        s3 = S3(aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key)

        # Deal with a single bucket being passed, rather than list.
        if isinstance(buckets, str):
            buckets = [buckets]

        # Generate manifest file
        manifest = {'entries': []}
        for bucket in buckets:

            # Retrieve list of files in bucket
            key_list = s3.list_keys(bucket, prefix=prefix)
            for key in key_list:
                manifest['entries'].append({
                    'url': '/'.join(['s3:/', bucket, key]),
                    'mandatory': mandatory
                })

        logger.info('Manifest generated.')

        # Save the file to s3 bucket if provided
        if manifest_key and manifest_bucket:
            # Dump the manifest to a temp JSON file
            manifest_path = files.create_temp_file()
            with open(manifest_path, 'w') as manifest_file_obj:
                json.dump(manifest, manifest_file_obj, sort_keys=True, indent=4)

            # Upload the file to S3
            s3.put_file(manifest_bucket, manifest_key, manifest_path)

            logger.info(f'Manifest saved to s3://{manifest_bucket}/{manifest_key}')

        return manifest

    def upsert(self, table_obj, target_table, primary_key, vacuum=True, distinct_check=True):
        """
        Preform an upsert on an existing table. An upsert is a function in which records
        in a table are updated and inserted at the same time. Unlike other SQL databases,
        it does not exist natively in Redshift.

        `Args:`
            table_obj: obj
                A Parsons table object
            target_table: str
                The schema and table name to upsert
            primary_key: str
                The primary key column of the target table
            vacuum: boolean
                Re-sorts rows and reclaims space in the specified table. You must be a table owner
                or super user to effectively vacuum a table, however the method will not fail
                if you lack these priviledges.
            distinct_check: boolean
                Check if the primary key column is distinct. Raise error if not.
        """

        staging_tbl = '{}_{}'.format(target_table, datetime.datetime.now().strftime('%Y%m%d_%M%S'))

        if distinct_check:
            sql = f'SELECT COUNT(*)-COUNT(DISTINCT {primary_key}) C FROM {target_table};'
            if self.query(sql)[0]['c'] > 0:
                raise ValueError('Primary key column contains duplicate values.')

        with self.connection() as connection:

            # Copy to a staging table
            logger.info(f'Building staging table: {staging_tbl}')
            self.copy(table_obj, staging_tbl)

            try:
                # Delete rows
                staging_primary_key = f"{staging_tbl.split('.')[1]}.{primary_key}"
                target_primary_key = f"{target_table.split('.')[1]}.{primary_key}"
                sql = f"""
                       DELETE FROM {target_table}
                       USING {staging_tbl}
                       WHERE {staging_primary_key} = {target_primary_key}
                       """
                self.query_with_connection(sql, connection, commit=False)
                logger.info(f'Target rows deleted from {target_table}.')

                # Insert rows
                # ALTER TABLE APPEND would be more efficient, but you can't run it in a
                # transaction block. It's worth the performance hit to not commit until the
                # end.
                sql = f"""
                       INSERT INTO {target_table}
                       SELECT * FROM {staging_tbl};
                       """

                self.query_with_connection(sql, connection, commit=False)
                logger.info(f'Target rows inserted to {target_table}')

            finally:

                # Drop the staging table
                self.query_with_connection(f"DROP TABLE IF EXISTS {staging_tbl};",
                                           connection, commit=False)
                logger.info(f'{staging_tbl} staging table dropped.')

        # Vacuum table. You must commit when running this type of transaction.
        if vacuum:
            with self.connection() as connection:
                connection.set_session(autocommit=True)
                self.query_with_connection(f'VACUUM {target_table};', connection)
                logger.info(f'{target_table} vacuumed.')
