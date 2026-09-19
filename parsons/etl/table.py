import logging
import pickle
from collections.abc import Generator, Iterator, Sequence
from enum import Enum
from pathlib import Path
from typing import Any

import petl

from parsons.etl.etl import ETL
from parsons.etl.tofrom import ToFrom
from parsons.utilities import files

logger = logging.getLogger(__name__)

DIRECT_INDEX_WARNING_COUNT = 10


class _EmptyDefault(Enum):
    """
    Default, non-mutable argument for Table().

    This is used because Table(None) should not be allowed, but we
    need a default argument that isn't the mutable [].

    See https://stackoverflow.com/a/76606310 for discussion.

    """

    token = 0


_EMPTYDEFAULT = _EmptyDefault.token


class Table(ETL, ToFrom):
    """
    Create a Parsons Table.

    Accepts one of the following:
    - A list of lists, with list[0] holding field names, and the other lists holding data
    - A list of dicts
    - A petl table

    Args:
        lst: See above for accepted list formats
        source: The original data source from which the data was pulled (optional)
        name: The name of the table (optional)

    """

    table: petl.util.base.Table

    def __init__(
        self,
        lst: list | tuple | Iterator | petl.util.base.Table | _EmptyDefault = _EMPTYDEFAULT,
        source: str | None = None,
        name: str | None = None,
    ) -> None:
        """
        Initialize a Table.

        .. admonition:: Creating an Empty Table

            Table cannot be initialized with ``Table(None)``; to create an empty table, use ``Table()``.

        .. admonition:: Creating a Table from a Generator or Iterator

            Generators are used with a temporary file cache to allow multiple passes.
            Iterators like map are converted to lists during initialization.

        Args:
            lst: Data to populate the table with
            source: The original data source from which the data was pulled (optional)
            name: The name of the table (optional)

        Raises:
            ValueError: If the Table could not be initialized due to an unrecognized data type.
            ValueError: If the resulting Table does not contain a valid petl Table.

        """
        self.source = source
        self.name = name

        # Sentinal used here to maintain the existing behavior.
        if lst is _EMPTYDEFAULT:
            self.table = petl.fromdicts([])

        elif isinstance(lst, (list, tuple)):
            # Check for empty list
            if not lst:
                self.table = petl.fromdicts([])
            else:
                first_row = lst[0]
                if isinstance(first_row, dict):
                    self.table = petl.fromdicts(lst)
                elif isinstance(first_row, (list, tuple)):
                    self.table = petl.wrap(lst)
                else:
                    err_msg = f"Could not initialize Table. Expected dict or list/tuple in first row, got {type(first_row)}."
                    raise ValueError(err_msg)

        elif isinstance(lst, petl.util.base.Table):
            self.table = lst

        elif isinstance(lst, Iterator):
            self.table = petl.fromdicts(lst if isinstance(lst, Generator) else list(lst))

        else:
            err_msg = f"Could not initialize Table from input type. Expected list, tuple, generator, or petl Table, got {type(lst)}."
            raise ValueError(err_msg)

        if not self.is_valid_table():
            err_msg = "Could not initialize Table."
            raise ValueError(err_msg)

        # Count how many times someone is indexing directly into this table, so we can warn against inefficient usage.
        self._index_count = 0

    def __repr__(self) -> str:
        """Return a string representation of the table as a list of dicts."""
        return repr(petl.dicts(self.table))

    def __iter__(self) -> Iterator[dict[str, Any]]:
        """Return an iterator of the table as a list of dicts."""
        return iter(petl.dicts(self.table))

    def __getitem__(self, index: int | str | slice) -> list | dict[str, Any]:
        """
        Return the row or column data at the given index.

        If the index is an int, return the requested row (as dict).
        If the index is a str, return the requested column (as list).
        If the index is a slice, return the requested data rows (as list)

        Raises:
            TypeError: If the index is not an int, str, or slice.

        """
        if isinstance(index, int):
            return self.row_data(index)

        if isinstance(index, str):
            return self.column_data(index)

        if isinstance(index, slice):
            tblslice = petl.rowslice(self.table, index.start, index.stop, index.step)
            return list(tblslice)

        err_msg = "You must pass a string or an index as a value."
        raise TypeError(err_msg)

    def __bool__(self) -> bool:
        """Return True if the first 5 data rows of table are not empty, False otherwise."""
        head_one = petl.head(self.table)
        return petl.nrows(head_one) > 0

    def _repr_html_(self) -> str:
        """Leverage Petl functionality to display well formatted tables in Jupyter Notebook."""
        return self.table._repr_html_()  # type: ignore[ty:unresolved-attribute]

    @property
    def num_rows(self) -> int:
        """
        Count the number of rows in the table.

        Returns:
            Number of rows in the table

        """
        return petl.nrows(self.table)

    def __len__(self) -> int:
        """Table length is equal to row count."""
        return self.num_rows

    @property
    def data(self) -> Sequence[tuple]:
        """
        Return an iterable object.

        This allows iterating over the raw data rows as tuples (without field names).

        """
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
    def first(self) -> Any:
        """
        Return the first value in the table.

        Useful for database queries that only return a single value.

        If the first value is empty (IndexError), returns ``None``.

        """
        try:
            return self.data[0][0]

        except IndexError:
            return None

    def row_data(self, row_index: int) -> dict[str, Any]:
        """
        Return a row in table.

        Calling this method excessively will log a warning advising of a more efficient alternative.

        Args:
            row_index: The index of the row to return.

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
        Return the data in the column as a list.

        Args:
            column_name: The name of the column

        Returns:
            All data in the column

        Raises:
            ValueError: If the column name is not found.

        """
        if column_name in self.columns:
            return list(self.table[column_name])

        err_msg = "Column name not found."
        raise ValueError(err_msg)

    def materialize(self) -> None:
        """
        "Materialize" a Table.

        All data is loaded into memory and all pending transformations are applied.

        Use this if petl's lazy-loading behavior is causing you problems,
        eg. if you want to read data from a file immediately.

        This method updates the current table in place.

        """
        self.table = petl.wrap(petl.tupleoftuples(self.table))

    def materialize_to_file(self, file_path: Path | str | None = None) -> str:
        """
        "Materialize" a Table directly to a file.

        Unlike the :meth:`Table.materialize` method,
        this loads the data into a local temp file without bringing it into memory.

        This method updates the current table in place.

        Args:
            file_path:
                The path to the file to materialize the table to.
                If not specified, a temporary file will be created.

        Returns:
            Path to the temporary file that now contains the table.

        """
        # Load the data in batches, and "pickle" the rows to a temp file.
        # We pickle the data rather than writing to, say, a CSV,
        # so that we maintain all the type information for each field.

        file_path = Path(file_path or files.create_temp_file())

        with file_path.open(mode="wb") as handle:
            for row in self.table:
                pickle.dump(list(row), handle)

        # Load a Table from the pickled file
        self.table = petl.frompickle(file_path)

        return str(file_path)

    def is_valid_table(self) -> bool:
        """
        Perform simple checks on a Table.

        Specifically, verifies that we have a valid petl table within the Parsons Table.

        """
        if not isinstance(self.table, petl.util.base.Table):
            return False

        try:
            self.columns  # noqa B018 useless-expression

        except StopIteration:
            return False

        return True

    def empty_column(self, column: str) -> bool:
        """
        Check if a given column is empty.

        Args:
            column: The column name

        Returns:
            ``True`` if empty and ``False`` if not empty.

        """
        return petl.nrows(petl.selectnotnone(self.table, column)) == 0
