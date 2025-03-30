
import pandas as pd

from parsons.utilities import files


class ToFrom(object):
    def __init__(self, data):
        self.data = data

    def to_dataframe(self, index=None, exclude=None, columns=None, coerce_float=False):
        """
        Outputs table as a Pandas DataFrame.

        `Args:`
            index: str, list
                Field of array to use as the index.
            exclude: list
                Columns or fields to exclude.
            columns: list
                Column names to use.
        `Returns:`
            dataframe
                Pandas DataFrame object.
        """
        df = self.data.copy()
        if exclude:
            df = df.drop(columns=exclude)
        if columns:
            df = df[columns]
        if index:
            df.set_index(index, inplace=True)
        return df

    def to_html(self, local_path=None, **kwargs):
        """
        Outputs table to HTML.

        `Args:`
            local_path: str
                The path to write the HTML locally.
            **kwargs: dict
                Additional arguments for pandas.DataFrame.to_html.
        `Returns:`
            str
                The path of the new file.
        """
        if not local_path:
            local_path = files.create_temp_file(suffix=".html")
        self.data.to_html(local_path, **kwargs)
        return local_path

    def to_csv(self, local_path=None, **kwargs):
        """
        Outputs table to a CSV.

        `Args:`
            local_path: str
                The path to write the CSV locally.
            **kwargs: dict
                Additional arguments for pandas.DataFrame.to_csv.
        `Returns:`
            str
                The path of the new file.
        """
        if not local_path:
            local_path = files.create_temp_file(suffix=".csv")
        self.data.to_csv(local_path, index=False, **kwargs)
        return local_path

    def append_csv(self, local_path, **kwargs):
        """
        Appends table to an existing CSV.

        `Args:`
            local_path: str
                The local path of an existing CSV file.
            **kwargs: dict
                Additional arguments for pandas.DataFrame.to_csv.
        `Returns:`
            str
                The path of the file.
        """
        self.data.to_csv(local_path, mode="a", header=False, index=False, **kwargs)
        return local_path

    def to_dicts(self):
        """
        Output table as a list of dicts.

        `Returns:`
            list
        """
        return self.data.to_dict(orient="records")

    @classmethod
    def from_csv(cls, local_path, **kwargs):
        """
        Create a `parsons table` object from a CSV file.

        `Args:`
            local_path: str
                A CSV formatted local path.
            **kwargs: dict
                Additional arguments for pandas.read_csv.
        `Returns:`
            Parsons Table
        """
        return cls(pd.read_csv(local_path, **kwargs))

    @classmethod
    def from_columns(cls, cols, header=None):
        """
        Create a `parsons table` from a list of lists organized as columns.

        `Args:`
            cols: list
                A list of lists organized as columns.
            header: list
                List of column names.
        `Returns:`
            Parsons Table
        """
        data = {header[i]: col for i, col in enumerate(cols)} if header else {f"col_{i}": col for i, col in enumerate(cols)}
        return cls(pd.DataFrame(data))

    @classmethod
    def from_json(cls, local_path, **kwargs):
        """
        Create a `parsons table` from a JSON file.

        `Args:`
            local_path: str
                A JSON formatted local path.
            **kwargs: dict
                Additional arguments for pandas.read_json.
        `Returns:`
            Parsons Table
        """
        return cls(pd.read_json(local_path, **kwargs))

    @classmethod
    def from_html(cls, local_path, **kwargs):
        """
        Create a `parsons table` from an HTML file.

        `Args:`
            local_path: str
                A HTML formatted local path.
            **kwargs: dict
                Additional arguments for pandas.read_html.
        `Returns:`
            Parsons Table
        """
        return cls(pd.read_html(local_path, **kwargs)[0])