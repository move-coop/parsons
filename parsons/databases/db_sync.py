from parsons.databases.table import table_factory
import logging

logger = logging.getLogger(__name__)


class DBSync:
    """
    Sync tables between databases. Works with ``Redshift``, ``Postgres``
    and ``BigQuery`` databases.

    `Args:`
        source_db: Database connection object
            A database object.
        destination_db: Database connection object
            A database object.
        chunk_size: int
            The number of rows per transaction copy when syncing a table.
    `Returns:`
        A DBSync object.
    """

    def __init__(self, source_db, destination_db, chunk_size=500000):

        self.source_db = source_db
        self.dest_db = destination_db
        self.chunk_size = chunk_size

    def table_sync_full(self, source_table, destination_table, if_exists='drop',
                        **kwargs):
        """
        Full sync of table from a source database to a destination database.

        `Args:`
            source_table: str
                Full table path if desired (e.g. ``my_schema.my_table``)
            destination_table: str
                Full table path if desired (e.g. ``my_schema.my_table``)
            if_exists: str
                If destination table exists either ``drop`` or ``truncate``. Truncate is
                useful when there are dependent views associated with the table.
            **kwargs: args
                Optional copy arguments for destination database.
        `Returns:`
            ``None``
        """

        # Create the table objects
        source_tbl = table_factory(self.source_db, source_table)
        destination_tbl = table_factory(self.dest_db, destination_table)

        # Drop or truncate if the destination table exists
        if destination_tbl.exists:
            if if_exists == 'drop':
                destination_tbl.drop()
            elif if_exists == 'truncate':
                destination_tbl.truncate()
            else:
                raise ValueError('Invalid if_exists type. Must be drop or truncate.')

        # Copy rows in chunks
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

    def table_sync_increment(self, source_table, destination_table, primary_key, **kwargs):
        """
        Full sync of table from a source database to a destination database.

        `Args:`
            source_table: str
                Full table path if desired (e.g. ``my_schema.my_table``)
            destination_table: str
                Full table path if desired (e.g. ``my_schema.my_table``)
            if_exists: str
                If destination table exists either ``drop`` or ``truncate``. Truncate is
                useful when there are dependent views associated with the table.
            primary_key: str
                The name of the primary key or timestamp column.
            **kwargs: args
                Optional copy arguments for destination database.
        `Returns:`
            ``None``
        """

        # Create the table objects
        source_tbl = table_factory(self.source_db, source_table)
        destination_tbl = table_factory(self.dest_db, destination_table)

        # Get the max source table and destination table primary key
        source_max_pk = source_tbl.max_primary_key(primary_key)
        dest_max_pk = destination_tbl.max_primary_key(primary_key)

        # Check for a mismatch in row counts.
        if dest_max_pk > source_max_pk:
            raise ValueError('Destination DB primary key greater than source DB primary key.')

        # Do not copied if row counts are equal.
        elif dest_max_pk == source_max_pk:
            logger.info('Tables are in sync.')
            return None
            # Question: Should I check that the row counts match too?

        else:
            # Get count of rows to be copied.
            new_row_count = source_tbl.get_new_rows_count(primary_key, dest_max_pk)
            logger.info(f'Found {new_row_count} new rows in source table.')

            # Copy rows in chunks.
            copied_rows = 0
            while copied_rows < new_row_count:

                # Get a chunk
                rows = source_tbl.get_new_rows(primary_key, dest_max_pk, copied_rows, self.chunk_size)

                print (rows.num_rows)

                # Copy the chunk
                #self.dest_db.copy(rows, destination_table, if_exists='append', **kwargs)

                # Update the counter
                copied_rows += rows.num_rows

        self._row_count_verify(source_table, destination_table)

        logger.info(f'{source_table} synced: {copied_rows} total rows copied.')

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
