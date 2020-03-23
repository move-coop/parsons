from parsons.etl.table import Table
from parsons.databases.redshift.rs_copy_table import RedshiftCopyTable
from parsons.databases.redshift.rs_create_table import RedshiftCreateTable
from parsons.databases.redshift.rs_table_utilities import RedshiftTableUtilities
from parsons.databases.redshift.rs_schema import RedshiftSchema
from parsons.databases.table import BaseTable
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
import random

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
        self.dialect = 'redshift'
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

            if self._create_table_precheck(connection, table_name, if_exists):

                # Grab the object from s3
                from parsons.aws.s3 import S3
                s3 = S3(aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key)

                local_path = s3.get_file(bucket, key)

                if data_type == 'csv':
                    tbl = Table.from_csv(local_path, delimiter=csv_delimiter)
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
                                           compression=compression, max_errors=max_errors,
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

    def copy(self, tbl, table_name, if_exists='fail', max_errors=0, distkey=None,
             sortkey=None, padding=None, statupdate=False, compupdate=True, acceptanydate=True,
             emptyasnull=True, blanksasnull=True, nullas=None, acceptinvchars=True,
             dateformat='auto', timeformat='auto', varchar_max=None, truncatecolumns=False,
             columntypes=None, specifycols=None, alter_table=False,
             aws_access_key_id=None, aws_secret_access_key=None):
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
            alter_table: boolean
                Will check if the target table varchar widths are wide enough to copy in the
                table data. If not, will attempt to alter the table to make it wide enough. This
                will not work with tables that have dependent views.
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

        # Specify the columns for a copy statement.
        if specifycols:
            cols = tbl.columns
        else:
            cols = None

        with self.connection() as connection:

            # Check to see if the table exists. If it does not or if_exists = drop, then
            # create the new table.
            if self._create_table_precheck(connection, table_name, if_exists):
                sql = self.create_statement(tbl, table_name, padding=padding,
                                            distkey=distkey, sortkey=sortkey,
                                            varchar_max=varchar_max,
                                            columntypes=columntypes)
                self.query_with_connection(sql, connection, commit=False)
                logger.info(f'{table_name} created.')

            # If alter_table is True, then alter table if the table column widths
            # are wider than the existing table.
            elif alter_table:
                self.alter_varchar_column_widths(tbl, table_name)

            # Upload the table to S3
            key = self.temp_s3_copy(tbl, aws_access_key_id=aws_access_key_id,
                                    aws_secret_access_key=aws_secret_access_key)

            try:
                # Copy to Redshift database.
                copy_args = {'max_errors': max_errors,
                             'ignoreheader': 1,
                             'statupdate': statupdate,
                             'compupdate': compupdate,
                             'acceptanydate': acceptanydate,
                             'dateformat': dateformat,
                             'timeformat': timeformat,
                             'blanksasnull': blanksasnull,
                             'nullas': nullas,
                             'emptyasnull': emptyasnull,
                             'acceptinvchars': acceptinvchars,
                             'truncatecolumns': truncatecolumns,
                             'specifycols': cols,
                             'aws_access_key_id': aws_access_key_id,
                             'aws_secret_access_key': aws_secret_access_key,
                             'compression': 'gzip'}

                # Copy from S3 to Redshift
                sql = self.copy_statement(table_name, self.s3_temp_bucket, key, **copy_args)
                self.query_with_connection(sql, connection, commit=False)
                logger.info(f'Data copied to {table_name}.')

            # Clean up the S3 bucket.
            finally:
                if key:
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

        from parsons.aws import S3
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
            primary_key: str or list
                The primary key column(s) of the target table
            vacuum: boolean
                Re-sorts rows and reclaims space in the specified table. You must be a table owner
                or super user to effectively vacuum a table, however the method will not fail
                if you lack these priviledges.
            distinct_check: boolean
                Check if the primary key column is distinct. Raise error if not.
        """

        if not self.table_exists(target_table):
            logger.info('Target table does not exist. Copying into newly \
                         created target table.')
            self.copy(table_obj, target_table)
            return None

        noise = f'{random.randrange(0, 10000):04}'[:4]
        date_stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
        # Generate a temp table like "table_tmp_20200210_1230_14212"
        staging_tbl = '{}_stg_{}_{}'.format(target_table, date_stamp, noise)

        if isinstance(primary_key, str):
            primary_keys = [primary_key]
        else:
            primary_keys = primary_key

        if distinct_check:
            primary_keys_statement = ', '.join(primary_keys)
            diff = self.query(f'''
                select (
                    select count(*)
                    from {target_table}
                ) - (
                    SELECT COUNT(*) from (
                        select distinct {primary_keys_statement}
                        from {target_table}
                    )
                ) as total_count
            ''').first
            if diff > 0:
                raise ValueError('Primary key column contains duplicate values.')

        with self.connection() as connection:

            try:

                # Copy to a staging table
                logger.info(f'Building staging table: {staging_tbl}')
                self.copy(table_obj, staging_tbl)

                staging_table_name = staging_tbl.split('.')[1]
                target_table_name = target_table.split('.')[1]

                # Delete rows
                comparisons = [
                    f'{staging_table_name}.{primary_key} = {target_table_name}.{primary_key}'
                    for primary_key in primary_keys
                ]
                where_clause = ' and '.join(comparisons)

                sql = f"""
                       DELETE FROM {target_table}
                       USING {staging_tbl}
                       WHERE {where_clause}
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

    def alter_varchar_column_widths(self, tbl, table_name):
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
        rc = {k: v['max_length'] for k, v in cols.items() if v['data_type'] == 'character varying'} # noqa: E501, E261

        # Figure out if any of the destination table varchar columns are smaller than the
        # associated Parsons table columns. If they are, then alter column types to expand
        # their width.
        for c in set(rc.keys()).intersection(set(pc.keys())):
            if rc[c] < pc[c]:
                logger.info(f'{c} not wide enough. Expanding column width.')
                self.alter_table_column_type(table_name, c, 'varchar', varchar_width=pc[c])

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
            logger.info(f'Altered {table_name} {column_name}.')

    def table(self, table_name):
        # Return a Redshift table object

        return RedshiftTable(self, table_name)


class RedshiftTable(BaseTable):
    # Redshift table object.

    pass
