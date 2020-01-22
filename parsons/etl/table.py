from parsons.etl.etl import ETL
from parsons.etl.tofrom import ToFrom
import petl
import logging


logger = logging.getLogger(__name__)

DIRECT_INDEX_WARNING_COUNT = 10


class Table(ETL, ToFrom):
    """
    Create a Parsons Table. Accepts one of the following:
    - A list of lists, with list[0] holding field names, and the other lists holding data
    - A list of dicts
    - A petl table

    `Args:`
        lst: list
            See above for accepted list formats
        source: str
            The original data source from which the data was pulled (optional)
        name: str
            The name of the table (optional)
    """

    def __init__(self, lst=[]):

        self.table = None

        lst_type = type(lst)

        if lst_type in [list, tuple]:

            # Check for empty list
            if not len(lst):
                self.table = petl.fromdicts([])
            else:
                row_type = type(lst[0])
                # Check for list of dicts
                if row_type == dict:
                    self.table = petl.fromdicts(lst)
                # Check for list of lists
                elif row_type in [list, tuple]:
                    self.table = petl.wrap(lst)

        else:
            # Create from a petl table
            self.table = lst

        if not self.is_valid_table():
            raise ValueError("Could not create Table")

        # Count how many times someone is indexing directly into this table, so we can warn
        # against inefficient usage.
        self._index_count = 0

    def __repr__(self):

        return repr(petl.dicts(self.table))

    def __iter__(self):

        return iter(petl.dicts(self.table))

    def __getitem__(self, index):

        if isinstance(index, int):

            return self.row_data(index)

        elif isinstance(index, str):

            return self.column_data(index)

        else:

            raise TypeError('You must pass a string or an index as a value.')

    def _repr_html_(self):
        """
        Leverage Petl functionality to display well formatted tables in Jupyter Notebook.
        """

        return self.table._repr_html_()

    @property
    def num_rows(self):
        """
        `Returns:`
            int
                Number of rows in the table
        """
        return petl.nrows(self.table)

    @property
    def data(self):
        """
        Returns an iterable object for iterating over the raw data rows as tuples
        (without field names)
        """
        return petl.data(self.table)

    @property
    def columns(self):
        """
        `Returns:`
            list
                List of the table's column names
        """
        return list(petl.header(self.table))

    @property
    def first(self):
        """
        Returns the first value in the table. Useful for database queries that only
        return a single value.
        """

        try:
            return self.data[0][0]

        # If first value is empty, return None
        except IndexError:
            return None

    def row_data(self, row_index):
        """
        Returns a row in table

        `Args:`
            row_index: int
        `Returns:`
            dict
                A dictionary of the row with the column as the key and the cell
                as the value.
        """

        self._index_count += 1
        if self._index_count >= DIRECT_INDEX_WARNING_COUNT:
            logger.warning("""
                You have indexed directly into this Table multiple times. This can be inefficient,
                as data transformations you've made will be computed _each time_ you index into the
                Table. If you are accessing many rows of data, consider switching to this style of
                iteration, which is much more efficient:
                `for row in table:`
                """)

        return petl.dicts(self.table)[row_index]

    def column_data(self, column_name):
        """
        Returns the data in the column as a list.

        `Args:`
            column_name: str
                The name of the column
        `Returns`:
            list
                A list of data in the column.
        """

        if column_name in self.columns:
            return list(self.table[column_name])

        else:
            raise ValueError('Column name not found.')

    def materialize(self):
        """
        "Materializes" a Table, meaning all data is loaded into memory and all pending
        transformations are applied.

        Use this if petl's lazy-loading behavior is causing you problems, eg. if you want to read
        data from a file immediately.
        """

        self.table = petl.wrap(petl.tupleoftuples(self.table))

    def is_valid_table(self):
        """
        Performs some simple checks on a Table. Specifically, verifies that we have a valid petl
        table within the Parsons Table.

        `Returns:`
            bool
        """

        if not self.table:
            return False

        try:
            self.columns
        except StopIteration:
            return False

        return True

    def empty_column(self, column):
        """
        Checks if a given column is empty. Returns ``True`` if empty and ``False``
        if not empty.

        `Args:`
            column: str
                The column name
        `Returns:`
            bool
        """

        if petl.nrows(petl.selectnotnone(self.table, column)) == 0:
            return True
        else:
            return False
