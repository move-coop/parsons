import logging

logger = logging.getLogger(__name__)


class DBSync:
    """
    Sync tables between databases. Works with ``Postgres``, ``Redshift``, ``MySQL``
    databases.

    `Args:`
        source_db: Database connection object
            A database object.
        destination_db: Database connection object
            A database object.
        chunk_size: int
            The number of rows per transaction copy when syncing a table. The
            default value is 100,000 rows.
    `Returns:`
        A DBSync object.
    """

    def __init__(self, source_db, destination_db, chunk_size=100000):

        self.source_db = source_db
        self.dest_db = destination_db
        self.chunk_size = chunk_size

    def table_sync_full(self, source_table, destination_table, if_exists='drop',
                        **kwargs):
        """
        Full sync of table from a source database to a destination database. This will
        wipe all data from the destination table.

        `Args:`
            source_table: str
                Full table path (e.g. ``my_schema.my_table``)
            destination_table: str
                Full table path (e.g. ``my_schema.my_table``)
            if_exists: str
                If destination table exists either ``drop`` or ``truncate``. Truncate is
                useful when there are dependent views associated with the table.
            **kwargs: args
                Optional copy arguments for destination database.
        `Returns:`
            ``None``
        """

        # Create the table objects
        source_tbl = self.source_db.table(source_table)
        destination_tbl = self.dest_db.table(destination_table)

        logger.info(f'Syncing full table data from {source_table} to {destination_table}')

        # Drop or truncate if the destination table exists
        if destination_tbl.exists:
            if if_exists == 'drop':
                destination_tbl.drop()
            elif if_exists == 'truncate':
                self._check_column_match(source_tbl, destination_tbl)
                destination_tbl.truncate()
            else:
                raise ValueError('Invalid if_exists argument. Must be drop or truncate.')

        # If the source table contains 0 rows, do not attempt to copy the table.
        if source_tbl.num_rows == 0:
            logger.info('Source table contains 0 rows')
            return None

        # Copy rows in chunks.
        copied_rows = 0
        while copied_rows < source_tbl.num_rows:

            # Get a chunk
            rows = source_tbl.get_rows(offset=copied_rows, chunk_size=self.chunk_size)

            # Copy the chunk
            self.dest_db.copy(rows, destination_table, if_exists='append', **kwargs)

            # Update counter
            copied_rows += rows.num_rows

        logger.info(f'{source_table} synced: {copied_rows} total rows copied.')

        self._row_count_verify(source_tbl, destination_tbl)

    def table_sync_incremental(self, source_table, destination_table, primary_key,
                               distinct_check=True, **kwargs):
        """
        Incremental sync of table from a source database to a destination database
        using an incremental primary key.

        `Args:`
            source_table: str
                Full table path (e.g. ``my_schema.my_table``)
            destination_table: str
                Full table path (e.g. ``my_schema.my_table``)
            if_exists: str
                If destination table exists either ``drop`` or ``truncate``. Truncate is
                useful when there are dependent views associated with the table.
            primary_key: str
                The name of the primary key. This must be the same for the source and
                destination table.
            distinct_check: bool
                Check that the source table primary key is distinct prior to running the
                sync. If it is not, an error will be raised.
            **kwargs: args
                Optional copy arguments for destination database.
        `Returns:`
            ``None``
        """

        # Create the table objects
        source_tbl = self.source_db.table(source_table)
        destination_tbl = self.dest_db.table(destination_table)

        # Check that the destination table exists. If it does not, then run a
        # full sync instead.
        if not destination_tbl.exists:
            self.table_sync_full(source_table, destination_table)

        # If the source table contains 0 rows, do not attempt to copy the table.
        if source_tbl.num_rows == 0:
            logger.info('Source table contains 0 rows')
            return None

        # Check that the source table primary key is distinct
        if distinct_check and not source_tbl.distinct_primary_key(primary_key):
            raise ValueError('{primary_key} is not distinct in source table.')

        # Get the max source table and destination table primary key
        source_max_pk = source_tbl.max_primary_key(primary_key)
        dest_max_pk = destination_tbl.max_primary_key(primary_key)

        # Check for a mismatch in row counts; if dest_max_pk is None, or destination is empty
        # and we don't have to worry about this check.
        if dest_max_pk is not None and dest_max_pk > source_max_pk:
            raise ValueError('Destination DB primary key greater than source DB primary key.')

        # Do not copied if row counts are equal.
        elif dest_max_pk == source_max_pk:
            logger.info('Tables are in sync.')
            return None

        else:
            # Get count of rows to be copied.
            if dest_max_pk is not None:
                new_row_count = source_tbl.get_new_rows_count(primary_key, dest_max_pk)
            else:
                new_row_count = source_tbl.num_rows

            logger.info(f'Found {new_row_count} new rows in source table.')

            copied_rows = 0
            # Copy rows in chunks.
            while True:
                # Get a chunk
                rows = source_tbl.get_new_rows(primary_key=primary_key,
                                               cutoff_value=dest_max_pk,
                                               offset=copied_rows,
                                               chunk_size=self.chunk_size)

                row_count = rows.num_rows if rows else 0
                if row_count == 0:
                    break

                # Copy the chunk
                self.dest_db.copy(rows, destination_table, if_exists='append', **kwargs)

                # Update the counter
                copied_rows += row_count

        self._row_count_verify(source_tbl, destination_tbl)

        logger.info(f'{source_table} synced to {destination_table}.')

    def _row_count_verify(self, source_table_obj, destination_table_obj):
        """
        Ensure the the rows of the source table and the destination table match
        """

        source_row_count = source_table_obj.num_rows
        dest_row_count = destination_table_obj.num_rows

        if source_row_count != dest_row_count:
            logger.warning((f'Table count mismatch. Source table contains {source_row_count}.',
                           f' Destination table contains {dest_row_count}.'))
            return False

        logger.info('Source and destination table row counts match.')
        return True

    def _check_column_match(self, source_table_obj, destination_table_obj):
        """
        Ensure that the columns from each table match
        """

        if source_table_obj.columns != destination_table_obj.columns:
            raise ValueError("""Destination table columns do not match source table columns.
                             Consider dropping destination table and running a full sync.""")
