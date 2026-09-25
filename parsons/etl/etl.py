from __future__ import annotations

import hashlib
import logging
from typing import TYPE_CHECKING, Any, Literal, TypedDict, overload

import petl
from typing_extensions import Self

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator, Sequence

    from parsons import Table


logger = logging.getLogger(__name__)


class ETL:
    """ETL Methods for parsons Tables."""

    table: petl.util.base.Table
    columns: list[str]
    num_rows: int
    __iter__: Callable[[], Iterator[dict[str, Any]]]
    __getitem__: Callable[[int | str | slice], list | dict[str, Any]]

    def __init__(self) -> None:
        """Initialize the instance."""

    def head(self, n: int = 5) -> Self:
        """Return the first `n` rows of the table."""
        self.table = petl.head(self.table, n)

        return self

    def tail(self, n: int = 5) -> Self:
        """Return the last `n` rows of the table."""
        self.table = petl.tail(self.table, n)

        return self

    def add_column(
        self,
        column: str,
        value: Any | None = None,
        index: int | None = None,
        if_exists: Literal["fail", "replace"] = "fail",
    ) -> Self:
        """
        Add a column to your table.

        Args:
            column: Name of column to add
            value: A fixed or calculated value
            index: The position of the new column in the table
            if_exists:
                If ``replace``, this function will call :meth:`fill_column`
                if the column already exists, rather than raising a :exc:`ValueError`.

        Raises:
            ValueError: If the column already exists and ``if_exists`` is not ``replace``

        """
        if column in self.columns:
            if if_exists == "replace":
                self.fill_column(column, value)

                return self

            err_msg = f"Column {column} already exists"
            raise ValueError(err_msg)

        self.table = petl.addfield(self.table, column, value, index)

        return self

    def remove_column(self, *columns: str) -> Self:
        """
        Remove a column from your table.

        Args:
            `*columns`: Column names

        """
        self.table = petl.cutout(self.table, *columns)

        return self

    def rename_column(self, column_name: str, new_column_name: str) -> Self:
        """
        Rename an existing column.

        Args:
            column_name: The current column name
            new_column_name: The new column name

        Raises:
            ValueError: If the new column name already exists

        """
        if new_column_name in self.columns:
            err_msg = f"Column {new_column_name} already exists"
            raise ValueError(err_msg)

        self.table = petl.rename(self.table, column_name, new_column_name)

        return self

    def rename_columns(self, column_map: dict[str, str]) -> Self:
        """
        Rename multiple columns.

        Args:
            column_map:
                Old and new column names

                .. code-block:: python

                    {
                        'old_name': 'new_name',
                        'old_name2': 'new_name2',
                    }

        Raises:
            KeyError: If the old column name does not exist
            ValueError: If the new column name already exists

        """
        for old_name, new_name in column_map.items():
            if old_name not in self.columns:
                err_msg = f"Column name {old_name} does not exist"
                raise KeyError(err_msg)

            if new_name in self.columns:
                err_msg = f"Column name {new_name} already exists"
                raise ValueError(err_msg)

        self.table = petl.rename(self.table, column_map)

        return self

    def fill_column(self, column_name: str, fill_value: Any) -> Self:
        """
        Fill all values of a column in a table.

        Args:
            column_name: The column to fill
            fill_value: A fixed or calculated value

        """
        if callable(fill_value):
            self.table = petl.convert(
                self.table, column_name, lambda _, r: fill_value(r), pass_row=True
            )
        else:
            self.table = petl.update(self.table, column_name, fill_value)

        return self

    def fillna_column(self, column_name: str, fill_value: Any) -> Self:
        """
        Fill only ``None`` values of a column in a table.

        Args:
            column_name: The column to fill
            fill_value: A fixed or calculated value

        """
        if callable(fill_value):
            self.table = petl.convert(
                self.table,
                column_name,
                lambda _, r: fill_value(r),
                where=lambda r: r[column_name] is None,
                pass_row=True,
            )
        else:
            self.table = petl.update(
                self.table,
                column_name,
                fill_value,
                where=lambda r: r[column_name] is None,
            )

        return self

    def move_column(self, column: str, index: int) -> Self:
        """
        Move a column to a new index position.

        Args:
            column: The column name to move
            index: The new index for the column

        """
        self.table = petl.movefield(self.table, column, index)

        return self

    def convert_column(
        self, column: str | Iterable[str], updater: Callable | str | dict[Any, Any], *args, **kwargs
    ) -> Self:
        """
        Transform values under one or more fields.

        Transformation is possible via arbitrary functions, method invocations or dictionary translations.

        This leverages :func:`petl.convert`. Example usage can be found
        `here <https://petl.readthedocs.io/latest/transform.html#petl.transform.conversions.convert>`__.

        Args:
            column: Column(s) to convert (name, iterable)
            updater: Update via Callable, method name, dict translation, or variable to process the update
            `*args`: Additional positional arguments to pass to :func:`petl.convert`
            `**kwargs`: Additional keyword arguments to pass to :func:`petl.convert`

        """
        self.table = petl.convert(self.table, column, updater, *args, **kwargs)

        return self

    def get_column_max_width(self, column: str) -> int:
        """
        Return the maximum width of the column.

        Args:
            column: The column name

        """
        column_max_width = 0

        for v in petl.values(self.table, column):
            column_val_width = len(str(v).encode("utf-8"))
            column_max_width = max(column_max_width, column_val_width)

        return column_max_width

    def convert_columns_to_str(self) -> Self:
        """
        Convert all non-string or mixed columns strings.

        Can be very useful for comparison operations.

        """
        if self.num_rows == 0:
            return self

        cols = self.get_columns_type_stats()

        def str_or_empty(x: Any) -> str:
            return "" if x is None else str(x)

        for col in cols:
            # If there's more than one type (or no types), convert to str
            # Also if there is one type and it's not str, convert to str
            if len(col["type"]) != 1 or col["type"][0] != "str":
                self.convert_column(col["name"], str_or_empty)

        return self

    def coalesce_columns(
        self, dest_column: str, source_columns: Sequence[str], remove_source_columns: bool = True
    ) -> Self:
        """
        Coalesces values from one or more source columns into a destination column.

        The first non-empty value will be used.
        If the destination column doesn't exist, it will be added.

        Args:
            dest_column: Name of destination column
            source_columns: List of source column names
            remove_source_columns:
                Whether to remove the source columns after the coalesce.
                If the destination column is also one of the source columns, it will not be removed.

        """
        if dest_column in self.columns:

            def convert_fn(value, row: dict[str, Any]) -> Any:
                for source_col in source_columns:
                    if column_value := row.get(source_col):
                        return column_value

                return None

            logger.debug("Coalescing %s into %s", source_columns, dest_column)
            self.convert_column(dest_column, convert_fn, pass_row=True)

        else:

            def add_fn(row: dict[str, Any]) -> Any:
                for source_col in source_columns:
                    if column_value := row.get(source_col):
                        return column_value

                return None

            logger.debug("Creating new column %s from %s", dest_column, source_columns)
            self.add_column(dest_column, add_fn)

        if remove_source_columns:
            for source_col in source_columns:
                if source_col != dest_column:
                    self.remove_column(source_col)

        return self

    def map_columns(self, column_map: dict[str, Sequence[str]], exact_match: bool = True) -> Self:
        """
        Standardize column names based on multiple possible values.

        Helpful when your input table might have multiple / unknown column names.

        .. code-block:: python

            tbl = [
                {'fn': 'Jane'},
                {'lastname': 'Doe'},
                {'dob': '1980-01-01'}
            ]

            column_map = {
                'first_name': ['fn', 'first', 'firstname'],
                'last_name': ['ln', 'last', 'lastname'],
                'date_of_birth': ['dob', 'birthday']
            }

            tbl.map_columns(column_map)
            print (tbl)
            >> {{'first_name': 'Jane', 'last_name': 'Doe', 'date_of_birth': '1908-01-01'}}

        Args:
            column_map: A dictionary of columns and possible values that map to it
            exact_match:
                If ``True``, will only map if an exact match.
                If ``False``, will ignore case, spaces and underscores.

        """
        for col in self.columns:
            column_name = col.lower().replace("_", "").replace(" ", "") if not exact_match else col

            for new_column_name, possible_old_names in column_map.items():
                for old_column_name in possible_old_names:
                    if column_name == old_column_name:
                        self.rename_column(col, new_column_name)

        return self

    def map_and_coalesce_columns(self, column_map: dict[str, Sequence[str]]) -> Self:
        """
        Coalesce columns based on multiple possible values.

        The columns in the map do not need to be in your table,
        so you can create a map with all possibilities.

        The coalesce will occur in the order that the columns are listed,
        unless the destination column name already exists in the table,
        in which case that value will be preferenced.

        Helpful when your input table might have multiple / unknown column names.

        .. code-block:: python

            tbl = [
                {'first': None},
                {'fn': 'Jane'},
                {'lastname': 'Doe'},
                {'dob': '1980-01-01'}
            ]

            column_map = {
                'first_name': ['fn', 'first', 'firstname'],
                'last_name': ['ln', 'last', 'lastname'],
                'date_of_birth': ['dob', 'birthday']
            }

            tbl.map_and_coalesce_columns(column_map)

            print (tbl)
            >> {{'first_name': 'Jane', 'last_name': 'Doe', 'date_of_birth': '1908-01-01'}}

        Args:
            column_map: A dictionary of columns and possible values that map to it

        """
        for new_column_name, possible_old_names in column_map.items():
            # If the column in the mapping dict isn't actually in the table,
            # remove it from the list of columns to coalesce.
            coalesce_list = [item for item in possible_old_names if item in self.columns]

            # If the key from the mapping dict already exists in the table,
            # rename it so it can be coalesced with other possible columns.
            if new_column_name in self.columns:
                self.rename_column(new_column_name, f"{new_column_name}_temp")
                coalesce_list.insert(0, f"{new_column_name}_temp")

            # Coalesce columns
            self.coalesce_columns(new_column_name, coalesce_list, remove_source_columns=True)

        return self

    def get_column_types(self, column: str) -> list[str]:
        """
        Return a list of python types found in a given column.

        Args:
            column: Name of the column to analyze

        """
        return list(petl.typeset(self.table, column))

    def get_columns_type_stats(self) -> list[ColumnTypes]:
        """
        Return descriptive stats for all columns.

        Returns:
            A list of dicts, each containing a column ``name`` and a ``type`` list.

        """
        column_types: list[ColumnTypes] = [
            {"name": col, "type": self.get_column_types(col)} for col in self.columns
        ]
        return column_types

    def convert_table(self, updater: Callable | str | dict[Any, Any], *args, **kwargs) -> Self:
        """
        Transform all cells in a table.

        Useful for cleaning fields and data hygiene functions such as regex.

        Transformation is possible via arbitrary functions, method invocations or dictionary translations.

        This leverages :func:`petl.convert`. Example usage can be found
        `here <https://petl.readthedocs.io/latest/transform.html#petl.transform.conversions.convert>`__.

        Args:
            updater: Update via Callable, method name, dict translation, or variable to process the update
            `*args`: Additional positional arguments to pass to :func:`petl.convert`
            `**kwargs`: Additional keyword arguments to pass to :func:`petl.convert`

        """
        self.convert_column(self.columns, updater, *args, **kwargs)

        return self

    def unpack_dict(
        self,
        column: str,
        keys: list | None = None,
        include_original: bool = False,
        sample_size: int = 5000,
        missing: str | None = None,
        prepend: bool = True,
        prepend_value: str | None = None,
    ) -> Self:
        """
        Unpack dictionary values from one column into separate columns.

        Args:
            column: The column name to unpack
            keys:
                The dict keys in the column to unpack.
                If ``None``, will unpack all.
            include_original: Whether to retain original column after unpacking
            sample_size: Number of rows to sample before determining columns
            missing: If a value is missing, fill with this value
            prepend:
                Prepend the column name of the unpacked values.
                Useful for avoiding duplicate column names.
            prepend_value:
                Value to prepend new columns if ``prepend=True``.
                If ``None``, will set to column name.

        """
        if prepend:
            self.table = petl.convert(
                self.table, column, lambda v: self._prepend_dict(v, prepend_value or column)
            )

        self.table = petl.unpackdict(
            self.table,
            column,
            keys=keys,
            includeoriginal=include_original,
            samplesize=sample_size,
            missing=missing,
        )

        return self

    @overload
    def unpack_list(
        self,
        column: str,
        include_original: bool = False,
        missing: str | None = None,
        replace: Literal[True] = ...,
        max_columns: int | None = None,
    ) -> None: ...

    @overload
    def unpack_list(
        self,
        column: str,
        include_original: bool = False,
        missing: str | None = None,
        replace: Literal[False] = False,
        max_columns: int | None = None,
    ) -> Table: ...

    def unpack_list(
        self,
        column: str,
        include_original: bool = False,
        missing: str | None = None,
        replace: bool = False,
        max_columns: int | None = None,
    ) -> Table | None:
        """
        Unpack list values from one column into separate, numbered columns.

        .. code-block:: python

            # Begin with a list in column
            json = [{
                'id': '5421',
                'name': 'Jane Green',
                'phones': ['512-699-3334', '512-222-5478']
            }]

            tbl = Table(json)
            print (tbl)
            >>> {'id': '5421', 'name': 'Jane Green', 'phones': ['512-699-3334', '512-222-5478']}

            tbl.unpack_list('phones', replace=True)
            print (tbl)
            >>> {'id': '5421', 'name': 'Jane Green', 'phones_0': '512-699-3334', 'phones_1': '512-222-5478'}

        Args:
            column: The column name to unpack
            include_original: Retain original column after unpacking
            sample_size: Number of rows to sample before determining columns
            missing: If a value is missing, fill it with this value
            replace: Return new table or update existing
            max_columns: The maximum number of columns to unpack

        """
        # Convert all column values to list to avoid unpack errors
        self.table = petl.convert(
            self.table, column, lambda v: [v] if not isinstance(v, list) else v
        )

        # Find the max number of values in list for all rows
        col_count = 0
        for row in self.cut(column):
            col_count = max(col_count, len(row[column]))

        # If max columns provided, set max columns
        if col_count > 0 and max_columns:
            col_count = max_columns

        # Create new column names "COL_01, COL_02"
        new_cols = []
        for i in range(col_count):
            new_cols.append(column + "_" + str(i))

        tbl = petl.unpack(
            self.table,
            column,
            new_cols,
            include_original=include_original,
            missing=missing,
        )

        if replace:
            self.table = tbl
            return None

        return tbl

    def unpack_nested_columns_as_rows(
        self, column: str, key: str = "id", expand_original: bool | int = False
    ) -> Table:
        """
        Unpack list or dict values from one column into separate rows.

        Not recommended for JSON columns (i.e. lists of dicts),
        but can handle columns with any mix of types. Makes use of :func:`petl.melt`.

        Args:
            column: The column name to unpack
            key: The column to use as a key when unpacking. Defaults to ``id``.
            expand_original:
                If int: Add to original unless the max added per key is above the given number
                If ``True``: Add resulting unpacked rows (with all other columns) to original
                If ``False`` (default): Return unpacked rows (with `key` column only) as standalone
                In all cases, packed list and dict rows are removed from the original.

        Returns:
            If `expand_original` is not ``False``, original table with packed rows replaced by unpacked rows.
            Otherwise, standalone table with key column and unpacked values only

        """
        if isinstance(expand_original, int) and expand_original is not True:
            lengths = {len(row[column]) for row in self if isinstance(row[column], (dict, list))}
            max_len = sorted(lengths, reverse=True)[0]
            if max_len > expand_original:
                expand_original = False

        if expand_original:
            # Include all columns and filter out other non-dict types in table_list
            table = self
            table_list = table.select_rows(lambda row: isinstance(row[column], list))

        else:
            # Otherwise, include only key and column, but keep all non-dict types in table_list
            table = self.cut(key, column)
            table_list = table.select_rows(lambda row: not isinstance(row[column], dict))

        # All the columns other than column to ignore while melting
        ignore_cols = table.columns
        ignore_cols.remove(column)

        # Unpack lists as separate columns
        table_list.unpack_list(column, replace=True)

        # Rename the columns to retain only the number
        for col in table_list.columns:
            if f"{column}_" in col:
                table_list.rename_column(col, col.replace(f"{column}_", ""))

        # Filter dicts and unpack as separate columns
        table_dict = table.select_rows(lambda row: isinstance(row[column], dict))
        table_dict.unpack_dict(column, prepend=False)

        from parsons import Table

        # Use melt to pivot both sets of columns into their own Tables and clean out None values
        melted_list = Table(petl.melt(table_list.table, ignore_cols))
        melted_dict = Table(petl.melt(table_dict.table, ignore_cols))

        melted_list.remove_null_rows("value")
        melted_dict.remove_null_rows("value")

        melted_list.rename_column("variable", column)
        melted_dict.rename_column("variable", column)

        # Combine the list and dict Tables
        melted_list.concat(melted_dict)

        if expand_original:
            # Add unpacked rows to the original table (minus packed rows)
            orig = self.select_rows(lambda row: not isinstance(row[column], (dict, list)))
            orig.concat(melted_list)
            # Add unique id column by hashing all the other fields
            if "uid" not in self.columns:
                orig.add_column(
                    "uid",
                    lambda row: hashlib.md5(
                        str.encode("".join(str(x) for x in row)), usedforsecurity=False
                    ).hexdigest(),
                )
                orig.move_column("uid", 0)

            # Rename value column in case this is done again to this Table
            orig.rename_column("value", f"{column}_value")

            # Keep column next to column_value
            orig.move_column(column, -1)
            output = orig

        else:
            orig = self.remove_column(column)
            # Add unique id column by hashing all the other fields
            melted_list.add_column(
                "uid",
                lambda row: hashlib.md5(
                    str.encode("".join(str(x) for x in row)), usedforsecurity=False
                ).hexdigest(),
            )
            melted_list.move_column("uid", 0)
            output = melted_list

        self.table = orig.table
        return output

    def long_table(
        self,
        key: Sequence[str],
        column: str,
        key_rename: dict[str, str] | None = None,
        retain_original: bool = False,
        prepend: bool = True,
        prepend_value: str | None = None,
    ) -> Table:
        """
        Create a new long parsons table from a column, including the foreign key.

        .. code-block:: python

            # Begin with nested dicts in a column
            json = [
                {
                    'id': '5421',
                    'name': 'Jane Green',
                    'emails': [
                        {'home': 'jane@gmail.com'},
                        {'work': 'jane@mywork.com'}
                    ]
                }
            ]
            tbl = Table(json)
            print (tbl)
            >>> {'id': '5421', 'name': 'Jane Green', 'emails': [{'home': 'jane@gmail.com'}, {'work': 'jane@mywork.com'}]}
            >>> {'id': '5421', 'name': 'Jane Green', 'emails': [{'home': 'jane@gmail.com'}, {'work': 'jane@mywork.com'}]}

            # Create skinny table of just the nested dicts
            email_skinny = tbl.long_table(['id'], 'emails')

            print (email_skinny)
            >>> {'id': '5421', 'emails_home': 'jane@gmail.com', 'emails_work': None}
            >>> {'id': '5421', 'emails_home': None, 'emails_work': 'jane@mywork.com'}

        Args:
            key: The columns to retain in the long table (e.g. foreign keys)
            column: The column name to make long
            key_rename:
                The new name for the foreign key to better identify it. For
                example, you might want to rename ``id`` to ``person_id``.
                Ex. ``{'KEY_NAME': 'NEW_KEY_NAME'}``
            retain_original: Retain the original column from the source table.
            prepend:
                Prepend the column name of the unpacked values.
                Useful for avoiding duplicate column names.
            prepend_value:
                Value to prepend new columns if `prepend` is ``True``.
                If ``None``, will set to column name.

        """
        if type(key) is str:
            key = [key]

        lt = self.cut(*key, column)  # Create a table of key and column
        lt.unpack_list(column, replace=True)  # Unpack the list
        lt.table = petl.melt(lt.table, key)  # Melt into a long table
        lt = lt.cut(*key, "value")  # Get rid of column names created in unpack
        lt.rename_column("value", column)  # Rename 'value' to old column name
        lt.remove_null_rows(column)  # Remove null values

        # If a new key name is specified, rename
        if key_rename:
            for k, v in key_rename.items():
                lt.rename_column(k, v)

        # If there is a nested dict in the column, unpack it
        if lt.num_rows > 0 and isinstance(lt.table[column][0], dict):
            lt.unpack_dict(column, prepend=prepend, prepend_value=prepend_value)

        if not retain_original:
            self.remove_column(column)

        return lt

    def cut(self, *columns: str) -> Table:
        """
        Return the selected columns as a new Table.

        Args:
            `*columns`: Columns in the parsons table

        """
        from parsons import Table

        return Table(petl.cut(self.table, *columns))

    def select_rows(self, *filters: Callable | str) -> Table:
        """
        Select specific rows from a Parsons table based on the passed filters.

        Example filters:

        .. code-block:: python
            :caption: The filter can be structured in different ways

            tbl = Table(
                [
                    ['foo', 'bar', 'baz'],
                    ['c', 4, 9.3],
                    ['a', 2, 88.2],
                    ['b', 1, 23.3]
                ]
            )

            # Lambda Function
            tbl2 = tbl.select_rows(lambda row: row.foo == 'a' and row.baz > 88.1)
            tbl2
            >>> {'foo': 'a', 'bar': 2, 'baz': 88.1}

            # Expression String
            tbl3 = tbl.select_rows("{foo} == 'a' and {baz} > 88.1")
            tbl3
            >>> {'foo': 'a', 'bar': 2, 'baz': 88.1}

        Args:
            `*filters`: Callable | str

        """
        from parsons import Table

        return Table(petl.select(self.table, *filters))

    def remove_null_rows(
        self, columns: str | Sequence[str], null_value: int | float | str | None = None
    ) -> Self:
        """
        Remove rows if the values in a column are ``None``.

        If multiple columns are passed as list,
        all rows with null values in any of the passed columns will be removed.

        Args:
            columns: The column or columns to analyze
            null_value: The null value

        """
        if isinstance(columns, str):
            columns = [columns]

        for col in columns:
            self.table = petl.selectisnot(self.table, col, null_value)

        return self

    def _prepend_dict(self, dict_obj: dict[str, Any], prepend: str) -> dict[str, Any]:
        """Rename dict keys by adding a prefix."""
        return {prepend + "_" + old_key: dict_val for old_key, dict_val in dict_obj.items()}

    def stack(self, *tables: Table, missing: Any | None = None) -> None:
        """
        Stack Parsons tables on top of one another.

        Similar to :meth:`concat`, except no attempt is made to align fields from different tables.

        Args:
            tables: A single table, multiple tables, or a list/tuple of tables.
            missing: The value to use when padding missing values

        """
        actual_tables = (
            tables[0] if len(tables) == 1 and isinstance(tables[0], (list, tuple)) else tables
        )
        petl_tables = [tbl.table for tbl in actual_tables]

        self.table = petl.stack(self.table, *petl_tables, missing=missing)

    def concat(self, *tables: Table, missing: Any | None = None) -> None:
        """
        Concatenates one or more tables onto this one.

        Note that the tables do not need to share exactly the same fields.
        Any missing fields will be padded with ``None``, or whatever is provided via the `missing` keyword argument.

        Args:
            tables: A single table, multiple tables, or a list/tuple of tables.
            missing: The value to use when padding missing values

        """
        actual_tables = (
            tables[0] if len(tables) == 1 and isinstance(tables[0], (list, tuple)) else tables
        )
        petl_tables = [tbl.table for tbl in actual_tables]

        self.table = petl.cat(self.table, *petl_tables, missing=missing)

    def chunk(self, rows: int) -> list[Table]:
        """
        Divides a Parsons table into smaller tables of a specified row count.

        If the table cannot be divided evenly, then the final table will only include the remainder.

        Args:
            rows: The number of rows of each new Parsons table

        """
        from parsons import Table

        return [
            Table(petl.rowslice(self.table, i, i + rows)) for i in range(0, self.num_rows, rows)
        ]

    @staticmethod
    def get_normalized_column_name(column_name: str) -> str:
        """Return a column name with whitespace and non-alphanumeric characters removed, and everything lowercased."""
        column_name = column_name.lower().strip()
        return "".join(c for c in column_name if c.isalnum())

    def match_columns(
        self,
        desired_columns: Sequence[str],
        fuzzy_match: bool = True,
        if_extra_columns: Literal["remove", "ignore", "fail"] = "remove",
        if_missing_columns: Literal["add", "ignore", "fail"] = "add",
    ) -> Self:
        """
        Change the column names and ordering in this Table to match a list of desired column names.

        Args:
            desired_columns: Ordered list of desired column names
            fuzzy_match:
                Whether to normalize column names when matching against the desired column names,
                removing whitespace and non-alphanumeric characters, and lowercasing everything.
                Eg. With this flag set, ``FIRST NAME`` would match ``first_name``.
                If the Table has two columns that normalize to the same string (eg. ``FIRST NAME``
                and ``first_name``), the latter will be considered an extra column.
            if_extra_columns:
                If the Table has columns that don't match any desired columns, either ``remove``
                them, ``ignore`` them, or ``fail`` (raising an error).
            if_missing_columns:
                If the Table is missing some of the desired columns, either ``add`` them (with a
                value of ``None``), ``ignore`` them, or ``fail`` (raising an error).

        """
        from parsons import Table

        normalize_fn = Table.get_normalized_column_name if fuzzy_match else (lambda s: s)

        # Create a mapping of our "normalized" name to the original column name
        current_columns_normalized = {normalize_fn(col): col for col in reversed(self.columns)}

        # Track any columns we need to add to our current table from our desired columns
        columns_to_add = []
        # We are going to do a "cut" later to trim our table and re-order the columns, but
        # we won't have renamed our columns yet, so we need to remember their un-normalized form
        cut_columns = []
        # We are going to also rename our columns AFTER we cut, so we want to remember their normalized names
        final_header = []

        # Loop through the columns we want to see in our final table
        for desired_column in desired_columns:
            normalized_desired = normalize_fn(desired_column)
            # Try to find our desired column in our Table
            if normalized_desired not in current_columns_normalized:
                # If we can't find our desired column in our current columns, then it's "missing"
                if if_missing_columns == "fail":
                    # If our missing strategy is to fail, raise an exception
                    err_msg = f"Table is missing column {desired_column}"
                    raise TypeError(err_msg)

                if if_missing_columns == "add":
                    # We have to add to our table
                    columns_to_add.append(desired_column)
                    # We will need to remember this column when we cut down to desired columns
                    cut_columns.append(desired_column)
                    # This will be in the final table
                    final_header.append(desired_column)

                elif if_missing_columns != "ignore":
                    # If it's not ignore, add, or fail, then it's not a valid strategy
                    err_msg = (
                        f"Invalid option {if_missing_columns} for argument `if_missing_columns`"
                    )
                    raise TypeError(err_msg)

            else:
                # We have found this in our current columns, so take it out of our list to search
                current_column = current_columns_normalized.pop(normalized_desired)
                # Add the column to our intermediate table as the old column name
                cut_columns.append(current_column)
                # Add to our final header list as the "desired" name
                final_header.append(desired_column)

        # Look for any "extra" columns from our current table that aren't in our desired columns
        for current_column in current_columns_normalized.values():
            if if_extra_columns == "fail":
                err_msg = f"Table has extra column {current_column}"
                raise TypeError(err_msg)

            if if_extra_columns == "ignore":
                # If we're ignoring our extra columns, we should keep them
                # by adding them to our intermediate and final columns list
                cut_columns.append(current_column)
                final_header.append(current_column)

            elif if_extra_columns != "remove":
                # If it's not ``ignore``, ``add``, or ``fail``, then it's not a valid strategy
                err_msg = f"Invalid option {if_extra_columns} for argument `if_extra_columns`"
                raise TypeError(err_msg)

        # Add any columns we need to add
        for column in columns_to_add:
            self.table = petl.addfield(self.table, column, None)

        # Cut down to just the columns we care about
        self.table = petl.cut(self.table, *cut_columns)

        # Rename any columns
        self.table = petl.setheader(self.table, final_header)

        return self

    def reduce_rows(
        self,
        columns: Sequence[str],
        reduce_func: Callable[[Sequence[str], Sequence[Any]], Sequence[Any]],
        headers: Sequence[str],
        presorted: bool = False,
        **kwargs,
    ) -> Self:
        r"""
        Group rows by a column or columns, then reduce the groups to a single row.

        For example, the output from the query to get a table's definition is
        returned as one component per row. The `reduce_rows` method can be used
        to reduce all those to a single row containg the entire query.

        Based on the `rowreduce petl function <https://petl.readthedocs.io/en/stable/transform.html#petl.transform.reductions.rowreduce>`__.

        .. code-block:: python

            ddl = rs.query(sql_to_get_table_ddl)

        .. table:: ddl.table

            +--------------+--------------+----------------------------------------------------+
            | schemaname   | tablename    | ddl                                                |
            +==============+==============+====================================================+
            | 'db_scratch' | 'state_fips' | '--DROP TABLE db_scratch.state_fips;'              |
            +--------------+--------------+----------------------------------------------------+
            | 'db_scratch' | 'state_fips' | 'CREATE TABLE IF NOT EXISTS db_scratch.state_fips' |
            +--------------+--------------+----------------------------------------------------+
            | 'db_scratch' | 'state_fips' | '('                                                |
            +--------------+--------------+----------------------------------------------------+
            | 'db_scratch' | 'state_fips' | '\\tstate VARCHAR(1024)   ENCODE RAW'              |
            +--------------+--------------+----------------------------------------------------+
            | 'db_scratch' | 'state_fips' | '\\t,stusab VARCHAR(1024)   ENCODE RAW'            |
            +--------------+--------------+----------------------------------------------------+

        .. code-block:: python

            reducer_fn = lambda cols, rows: [
                f"{cols[0]}.{cols[1]}",
                r"\n".join([row[2] for row in rows])
            ]

            ddl.reduce_rows(
                ['schemaname', 'tablename'],
                reducer_fn,
                ['tablename', 'ddl'],
                presorted=True
            )

        .. table:: ddl.table

            +-------------------------+-------------------------------------------------------------------------+
            | tablename               | ddl                                                                     |
            +=========================+=========================================================================+
            | 'db_scratch.state_fips' | '--DROP TABLE db_scratch.state_fips;\\nCREATE TABLE IF NOT EXISTS       |
            |                         | db_scratch.state_fips\\n(\\n\\tstate VARCHAR(1024)   ENCODE RAW\\n\\t   |
            |                         | ,db_scratch.state_fips\\n(\\n\\tstate VARCHAR(1024)   ENCODE RAW        |
            |                         | \\n\\t,stusab VARCHAR(1024)   ENCODE RAW\\n\\t,state_name               |
            |                         | VARCHAR(1024)   ENCODE RAW\\n\\t,statens VARCHAR(1024)   ENCODE         |
            |                         | RAW\\n)\\nDISTSTYLE EVEN\\n;'                                           |
            +-------------------------+-------------------------------------------------------------------------+

        Args:
            columns: The column(s) by which to group the rows.
            reduce_func:
                The function by which to reduce the rows.
                Should take the 2 arguments, the columns list
                and the rows list and return a list.
                ``reducer(columns: Sequence[str], rows: Sequence[Any]) -> Sequence[Any]:``
            headers:
                The list of headers for modified table.
                The length of `headers` should match the length of the
                list returned by the reduce function.
            presorted: If false, the row will be sorted.
            `**kwargs`: Extra options to pass to :func:`petl.rowreduce`

        """
        self.table = petl.rowreduce(
            self.table,
            columns,
            reduce_func,
            header=headers,
            presorted=presorted,
            **kwargs,
        )

        return self

    def sort(
        self, columns: Sequence[str] | str | None = None, reverse: bool = False, **kwargs
    ) -> Self:
        """
        Sort the rows a table.

        Args:
            sort_columns:
                Sort by a single column or a list of column.
                If ``None``, will sort columns from left to right.
            reverse: Sort rows in reverse order.
            `**kwargs`: Extra options to pass to :func:`petl.sort`

        """
        self.table = petl.sort(self.table, key=columns, reverse=reverse, **kwargs)

        return self

    def set_header(self, new_header: Sequence[str]) -> Self:
        """
        Replace the header row of the table.

        Args:
            new_header: List of new header column names

        """
        self.table = petl.setheader(self.table, new_header)

        return self

    def use_petl(self, petl_method: str, *args, **kwargs) -> Table:
        """
        Call a petl function on the current table.

        This convenience method exposes the petl functions to the current
        Table. This is useful in cases where one might need a ``petl`` function
        that has not yet been implemented for :ref:`Table`.

        For more information on available petl functions,
        see the `transform <https://petl.readthedocs.io/latest/transform.html>`_
        and `util <https://petl.readthedocs.io/latest/util.html>`_ documentation.

        .. code-block:: python

            tbl = Table(
                [
                    ['col1', 'col2'],
                    ['# this is a comment row'],
                    ['a', 1],
                    ['#this is another comment', 'this is also ignored'],
                    ['b', 2]
                ]
            )
            tbl.use_petl('skipcomments', '#', update_table=True)

            >>> {'col1': 'a', 'col2': 1}
            >>> {'col1': 'b', 'col2': 2}

        .. table:: tbl.table

            +------+------+
            | col1 | col2 |
            +======+======+
            | 'a'  |    1 |
            +------+------+
            | 'b'  |    2 |
            +------+------+

        Args:
            petl_method: The name of the ``petl`` function to call
            `*args`: Any
                The arguements to pass to the petl function.
            `**kwargs`: Any
                The keyword arguements to pass to the petl function.
                update_table (bool) -- If ``True``, updates the :ref:`Table`. Defaults to ``False``.
                to_petl (bool) -- If ``True``, returns a petl table, otherwise a :ref:`Table`. Defaults to ``False``.

        """
        update_table = kwargs.pop("update_table", False)
        to_petl = kwargs.pop("to_petl", False)

        if update_table:
            self.table = getattr(petl, petl_method)(self.table, *args, **kwargs)

        if to_petl:
            return getattr(petl, petl_method)(self.table, *args, **kwargs)

        from parsons import Table

        return Table(getattr(petl, petl_method)(self.table, *args, **kwargs))

    def deduplicate(self, keys: str | Sequence[str] | None = None, presorted: bool = False) -> Self:
        """
        Deduplicate table.

        All keys specified in the ``keys`` argument are considered
        when deduplicating, not each key individually. For example,
        if ``keys=['a', 'b']``, the method will not remove a record unless
        it's identical to another record in both columns ``a`` and ``b``.

        .. table:: tbl.table

            +---+---+
            | a | b |
            +===+===+
            | 1 | 3 |
            +---+---+
            | 1 | 2 |
            +---+---+
            | 1 | 2 |
            +---+---+
            | 2 | 3 |
            +---+---+

        .. code-block:: python
            :caption: Remove all subsequent rows with {'a': 1}

            tbl = Table([['a', 'b'], [1, 3], [1, 2], [1, 2], [2, 3]])
            tbl.deduplicate('a')

        .. table:: tbl.table

            +---+---+
            | a | b |
            +===+===+
            | 1 | 3 |
            +---+---+
            | 2 | 3 |
            +---+---+

        .. code-block:: python
            :caption: Remove all subsequent rows with {'a': 1} and {'b': 3}

            tbl = Table([['a', 'b'], [1, 3], [1, 2], [1, 2], [2, 3]])
            tbl.deduplicate(['a', 'b'])

            # Table is deduplicated on both ('a', 'b'), so as (1, 2) was placed
            # before (1, 3) second instance of {'a': 1} or {'b': 3} was not removed.

        .. table:: tbl.table

            +---+---+
            | a | b |
            +===+===+
            | 1 | 2 |
            +---+---+
            | 1 | 3 |
            +---+---+
            | 2 | 3 |
            +---+---+

        .. code-block:: python
            :caption: Remove all subsequent rows with {'a': 1} and then all with {'b': 3}

            tbl = Table([['a', 'b'], [1, 3], [1, 2], [1, 2], [2, 3]]) # reset
            tbl.deduplicate('a').deduplicate('b')

        .. table:: tbl.table

            +---+---+
            | a | b |
            +===+===+
            | 1 | 3 |
            +---+---+

        .. code-block:: python
            :caption: The order of deduplication matters

            tbl = Table([['a', 'b'], [1, 3], [1, 2], [1, 2], [2, 3]]) # reset
            tbl.deduplicate('b').deduplicate('a')

        .. table:: tbl.table

            +---+---+
            | a | b |
            +===+===+
            | 1 | 2 |
            +---+---+

        Args:
            keys: keys to deduplicate (and optionally sort) on.
            presorted: If ``False``, the row will also be sorted.

        """
        self.table = petl.transform.dedup.distinct(self.table, key=keys, presorted=presorted)

        return self


class ColumnTypes(TypedDict):
    """A dict representing the name and types of a column."""

    name: str
    type: list[str]
