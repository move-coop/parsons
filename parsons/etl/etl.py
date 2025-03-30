import logging

logger = logging.getLogger(__name__)

class ETL(object):
    def __init__(self, data):
        self.data = data

    def head(self, n=5):
        """
        Return the first n rows of the table.

        `Args:`
            n: int
                The number of rows to return. Defaults to 5.
        `Returns:`
            `Parsons Table`
        """
        self.data = self.data.head(n)
        return self

    def tail(self, n=5):
        """
        Return the last n rows of the table.

        `Args:`
            n: int
                The number of rows to return. Defaults to 5.
        `Returns:`
            `Parsons Table`
        """
        self.data = self.data.tail(n)
        return self

    def add_column(self, column, value=None, if_exists="fail"):
        """
        Add a column to your table.

        `Args:`
            column: str
                Name of column to add.
            value:
                A fixed or calculated value.
            if_exists: str (options: 'fail', 'replace')
                If set to `replace`, this function will overwrite the column if it already exists.
        `Returns:`
            `Parsons Table` and also updates self.
        """
        if column in self.data.columns:
            if if_exists == "replace":
                self.data[column] = value if not callable(value) else self.data.apply(value, axis=1)
            else:
                raise ValueError(f"Column {column} already exists")
        else:
            self.data[column] = value if not callable(value) else self.data.apply(value, axis=1)
        return self

    def remove_column(self, *columns):
        """
        Remove a column from your table.

        `Args:`
            *columns: str
                Column names.
        `Returns:`
            `Parsons Table` and also updates self.
        """
        self.data.drop(columns=list(columns), inplace=True)
        return self

    def rename_column(self, column_name, new_column_name):
        """
        Rename a column.

        `Args:`
            column_name: str
                The current column name.
            new_column_name: str
                The new column name.
        `Returns:`
            `Parsons Table` and also updates self.
        """
        if new_column_name in self.data.columns:
            raise ValueError(f"Column {new_column_name} already exists")
        self.data.rename(columns={column_name: new_column_name}, inplace=True)
        return self

    def rename_columns(self, column_map):
        """
        Rename multiple columns.

        `Args:`
            column_map: dict
                A dictionary of columns and new names.
        `Returns:`
            `Parsons Table` and also updates self.
        """
        self.data.rename(columns=column_map, inplace=True)
        return self

    def fill_column(self, column_name, fill_value):
        """
        Fill a column in a table.

        `Args:`
            column_name: str
                The column to fill.
            fill_value:
                A fixed or calculated value.
        `Returns:`
            `Parsons Table` and also updates self.
        """
        self.data[column_name] = fill_value if not callable(fill_value) else self.data.apply(fill_value, axis=1)
        return self

    def fillna_column(self, column_name, fill_value):
        """
        Fill None values in a column in a table.

        `Args:`
            column_name: str
                The column to fill.
            fill_value:
                A fixed or calculated value.
        `Returns:`
            `Parsons Table` and also updates self.
        """
        self.data[column_name].fillna(fill_value, inplace=True)
        return self

    def move_column(self, column, index):
        """
        Move a column to a new position.

        `Args:`
            column: str
                The column name to move.
            index: int
                The new index for the column.
        `Returns:`
            `Parsons Table` and also updates self.
        """
        cols = list(self.data.columns)
        cols.insert(index, cols.pop(cols.index(column)))
        self.data = self.data[cols]
        return self

    def convert_column(self, column, func):
        """
        Transform values in a column via a function.

        `Args:`
            column: str
                The column to transform.
            func: callable
                The function to apply to the column.
        `Returns:`
            `Parsons Table` and also updates self.
        """
        self.data[column] = self.data[column].apply(func)
        return self

    def coalesce_columns(self, dest_column, source_columns, remove_source_columns=True):
        """
        Coalesces values from one or more source columns into a destination column.

        `Args:`
            dest_column: str
                Name of destination column.
            source_columns: list
                List of source column names.
            remove_source_columns: bool
                Whether to remove the source columns after the coalesce.
        `Returns:`
            `Parsons Table` and also updates self.
        """
        self.data[dest_column] = self.data[source_columns].bfill(axis=1).iloc[:, 0]
        if remove_source_columns:
            self.data.drop(columns=source_columns, inplace=True)
        return self

    def sort(self, columns=None, ascending=True):
        """
        Sort the rows of the table.

        `Args:`
            columns: list or str
                Column(s) to sort by.
            ascending: bool
                Sort in ascending order. Defaults to True.
        `Returns:`
            `Parsons Table` and also updates self.
        """
        self.data.sort_values(by=columns, ascending=ascending, inplace=True)
        return self
