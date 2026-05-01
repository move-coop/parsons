import logging
import pickle
from collections.abc import Generator, Iterator
from enum import Enum
from pathlib import Path
from typing import Literal

import petl

from parsons.etl.etl import ETL
from parsons.etl.tofrom import ToFrom
from parsons.utilities import files

logger = logging.getLogger(__name__)

DIRECT_INDEX_WARNING_COUNT = 10


class _EmptyDefault(Enum):
    """Default argument for Table()

    This is used because Table(None) should not be allowed, but we
    need a default argument that isn't the mutable []

    See https://stackoverflow.com/a/76606310 for discussion.
    """

    token = 0


_EMPTYDEFAULT = _EmptyDefault.token


class Table(ETL, ToFrom):
    """
    Create a Parsons Table.

    Args:
        lst: Data to be converted into a Table.
        source: The original data source from which the data was pulled.
        name: The name of the table.

    Raises:
        ValueError: If Table could not be initialized from the input data

    """

    def __init__(
        self,
        lst: list[list]
        | list[dict]
        | tuple
        | Iterator
        | petl.Table
        | Literal[_EmptyDefault.token] = _EMPTYDEFAULT,
        source: str | None = None,
        name: str | None = None,
    ) -> None:
        self.table = None
        self.source = source
        self.name = name

        # Normally we would use None as the default argument here
        # Instead of using None, we use a sentinal
        # This allows us to maintain the existing behavior
        # This is allowed: Table()
        # This should fail: Table(None)
        if lst is _EMPTYDEFAULT:
            self.table = petl.fromdicts([])

        elif isinstance(lst, (list, tuple)):
            # Check for empty list
            if not lst:
                self.table = petl.fromdicts([])
            else:
                first_row = lst[0]
                # Check for list of dicts
                if isinstance(first_row, dict):
                    self.table = petl.fromdicts(lst)
                # Check for list of lists
                elif isinstance(first_row, (list, tuple)):
                    self.table = petl.wrap(lst)
                else:
                    err_msg = f"Could not initialize Table. Expected dict or list/tuple in first row, got {type(first_row)}."
                    raise ValueError(err_msg)

        elif isinstance(lst, petl.Table):
            # Create from a petl table
            self.table = lst

        elif isinstance(lst, Iterator):
            # petl.fromdicts handles generators by using a temporary file cache
            # to allow multiple passes over the data.
            # unfortunately iterators like map don't work with this so we convert them to lists
            self.table = petl.fromdicts(lst if isinstance(lst, Generator) else list(lst))

        else:
            err_msg = f"Could not initialize Table from input type. Expected list, tuple, generator, or petl Table, got {type(lst)}."
            raise ValueError(err_msg)

        if not self.is_valid_table():
            err_msg = "Could not initialize Table."
            raise ValueError(err_msg)

        # Count how many times someone is indexing directly into this table, so we can warn
        # against inefficient usage.
        self._index_count = 0

    def __repr__(self) -> str:
        return repr(petl.dicts(self.table))

    def __iter__(self) -> Iterator:
        return iter(petl.dicts(self.table))

    def __getitem__(self, index) -> list | dict:
        if isinstance(index, int):
            return self.row_data(index)

        elif isinstance(index, str):
            return self.column_data(index)

        elif isinstance(index, slice):
            tblslice = petl.rowslice(self.table, index.start, index.stop, index.step)
            return list(tblslice)

        else:
            raise TypeError("You must pass a string or an index as a value.")

    def __bool__(self) -> bool:
        # Try to get a single row from our table
        head_one = petl.head(self.table)

        # See if our single row is empty
        return petl.nrows(head_one) > 0

    def _repr_html_(self):
        """Leverage Petl functionality to display well formatted tables in Jupyter Notebook."""
        return self.table._repr_html_()

    @property
    def num_rows(self) -> int:
        """
        Count the number of rows in the table.

        Returns:
            Number of rows in the table

        """
        return petl.nrows(self.table)

    def __len__(self):
        return self.num_rows

    @property
    def data(self) -> petl.util.base.DataView:
        """Returns an iterable object for iterating over the raw data rows as tuples (without field names)."""
        return petl.data(self.table)

    @property
    def columns(self) -> list[str]:
        """
        List the table's column names.

        Returns:
            List of the table's column names

        """
        return list(petl.header(self.table))

    @property
    def first(self):
        """
        Returns the first value in the table.

        Useful for database queries that only return a single value.
        """
        try:
            return self.data[0][0]

        # If first value is empty, return None
        except IndexError:
            return None

    def row_data(self, row_index: int) -> petl.util.base.DictsView:
        """
        Returns a row in table

        Returns:
            A dictionary of the row with the column as the key and the cell as the value.

        """
        self._index_count += 1
        if self._index_count >= DIRECT_INDEX_WARNING_COUNT:
            logger.warning(
                """
                You have indexed directly into this Table multiple times. This can be inefficient,
                as data transformations you've made will be computed _each time_ you index into the
                Table. If you are accessing many rows of data, consider switching to this style of
                iteration, which is much more efficient:
                `for row in table:`
                """
            )

        return petl.dicts(self.table)[row_index]

    def column_data(self, column_name: str) -> list:
        """
        Returns the data in the column as a list.

        Args:
            column_name: The name of the column

        Returns:
            A list of data in the column.

        """
        if column_name in self.columns:
            return list(self.table[column_name])

        else:
            raise ValueError("Column name not found.")

    def materialize(self) -> None:
        """
        "Materializes" a Table, meaning all data is loaded into memory and all pending
        transformations are applied.

        Use this if petl's lazy-loading behavior is causing you problems, eg. if you want to read
        data from a file immediately.
        """
        self.table = petl.wrap(petl.tupleoftuples(self.table))

    def materialize_to_file(self, file_path: Path | str | None = None) -> str:
        """
        "Materializes" a Table, meaning all pending transformations are applied.

        Unlike the original materialize function, this method does not bring the data into memory,
        but instead loads the data into a local temp file.

        This method updates the current table in place.

        Args:
            file_path:
                The path to the file to materialize the table to.
                If not specified, a temp file will be created.

        Returns:
            Path to the temp file that now contains the table

        """
        # Load the data in batches, and "pickle" the rows to a temp file.
        # (We pickle rather than writing to, say, a CSV, so that we maintain
        # all the type information for each field.)

        file_path = Path(file_path or files.create_temp_file())

        with file_path.open(mode="wb") as handle:
            for row in self.table:
                pickle.dump(list(row), handle)

        # Load a Table from the file
        self.table = petl.frompickle(str(file_path))

        return str(file_path)

    def is_valid_table(self) -> bool:
        """
        Performs some simple checks on a Table.

        Specifically, verifies that we have a valid petl table within the Parsons Table.

        """
        if not isinstance(self.table, petl.Table):
            return False

        try:
            self.columns  # noqa B018 useless-expression
        except StopIteration:
            return False

        return True

    def empty_column(self, column: str) -> bool:
        """
        Checks if a given column is empty.

        Args:
            column: The column name

        Returns:
            ``True`` if empty and ``False`` if not empty.

        """
        return petl.nrows(petl.selectnotnone(self.table, column)) == 0
