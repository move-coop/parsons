import logging

import pandas as pd

from parsons.etl.etl import ETL
from parsons.etl.tofrom import ToFrom
from parsons.utilities import files

logger = logging.getLogger(__name__)


class Table(ETL, ToFrom):
    """
    Create a Parsons Table. Accepts one of the following:
    - A pandas DataFrame
    - A list of dicts

    `Args:`
        data: list of dicts, pandas DataFrame, or None
            The data to initialize the table with.
    """

    def __init__(self, data=None):
        if isinstance(data, pd.DataFrame):
            self.data = data
        elif isinstance(data, list):
            self.data = pd.DataFrame(data)
        elif data is None:
            self.data = pd.DataFrame()
        else:
            raise ValueError("Unsupported data type for Table initialization.")

    @classmethod
    def from_csv(cls, file_path, **kwargs):
        """
        Load a Table from a CSV file.

        `Args:`
            file_path: str
                The path to the CSV file.
            **kwargs: dict
                Additional arguments to pass to pandas.read_csv.
        `Returns:`
            Table
        """
        return cls(pd.read_csv(file_path, **kwargs))

    def to_csv(self, file_path, **kwargs):
        """
        Save the Table to a CSV file.

        `Args:`
            file_path: str
                The path to save the CSV file.
            **kwargs: dict
                Additional arguments to pass to pandas.to_csv.
        """
        self.data.to_csv(file_path, index=False, **kwargs)

    def add_column(self, column_name, func):
        """
        Add a new column to the Table.

        `Args:`
            column_name: str
                The name of the new column.
            func: callable
                A function to generate values for the new column.
        """
        self.data[column_name] = self.data.apply(func, axis=1)

    def remove_column(self, column_name):
        """
        Remove a column from the Table.

        `Args:`
            column_name: str
                The name of the column to remove.
        """
        self.data.drop(columns=[column_name], inplace=True)

    def to_dataframe(self):
        """
        Return the underlying pandas DataFrame.

        `Returns:`
            pandas.DataFrame
        """
        return self.data

    @property
    def num_rows(self):
        """
        Get the number of rows in the Table.

        `Returns:`
            int
        """
        return len(self.data)

    @property
    def columns(self):
        """
        Get the column names of the Table.

        `Returns:`
            list
        """
        return self.data.columns.tolist()

    def __repr__(self):
        return repr(self.data)

    def __iter__(self):
        return iter(self.data.to_dict(orient="records"))

    def __getitem__(self, index):
        if isinstance(index, int):
            return self.data.iloc[index].to_dict()
        elif isinstance(index, str):
            return self.data[index].tolist()
        elif isinstance(index, slice):
            return self.data.iloc[index].to_dict(orient="records")
        else:
            raise TypeError("You must pass a string or an index as a value.")

    def __bool__(self):
        return not self.data.empty

    def materialize(self):
        """
        "Materializes" a Table, meaning all data is loaded into memory.

        Use this if lazy-loading behavior is causing you problems.
        """
        self.data = self.data.copy()

    def materialize_to_file(self, file_path=None):
        """
        "Materializes" a Table, meaning all data is loaded into memory.

        Unlike the original materialize function, this method does not bring the data into memory,
        but instead saves the data into a local temp file.

        `Args:`
            file_path: str
                The path to the file to materialize the table to; if not specified, a temp file
                will be created.
        `Returns:`
            str
                Path to the temp file that now contains the table
        """
        file_path = file_path or files.create_temp_file()
        self.to_csv(file_path)
        return file_path

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
        if column not in self.columns:
            raise ValueError("Column name not found.")
        return self.data[column].isnull().all()
