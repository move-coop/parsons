from airtable import Airtable as client
from parsons.etl import Table
from parsons.utilities import check_env
import logging


logger = logging.getLogger(__name__)


class Airtable(object):
    """
    `Args:`
        base_key: str
            The key of the Airtable base that you will interact with.
        table_name: str
            The name of the table in the base. The table name is the equivilant of the sheet name
            in Excel or GoogleDocs.
        personal_access_token: str
            The Airtable personal access token. Not required if ``AIRTABLE_PERSONAL_ACCESS_TOKEN``
            env variable set.
    """

    def __init__(self, base_key, table_name, personal_access_token=None):

        self.personal_access_token = check_env.check(
            "AIRTABLE_PERSONAL_ACCESS_TOKEN", personal_access_token
        )
        self.client = client(base_key, table_name, self.personal_access_token)

    def get_record(self, record_id):
        """
        Returns a single record.

        `Args:`
            record_id: str
                The Airtable record id
        `Returns:`
            A dictionary of the record
        """

        return self.client.get(record_id)

    def get_records(
        self,
        fields=None,
        max_records=None,
        view=None,
        formula=None,
        sort=None,
        sample_size=None,
    ):
        """
        `Args:`
            fields: str or lst
                Only return specified column or list of columns. The column name is
                case sensitive
            max_records: int
                The maximum total number of records that will be returned.
            view: str
                If set, only the records in that view will be returned. The records will be
                sorted according to the order of the view.
            formula: str
                The formula will be evaluated for each record, and if the result
                is not 0, false, "", NaN, [], or #Error! the record will be included
                in the response.

                If combined with view, only records in that view which satisfy the
                formula will be returned. For example, to only include records where
                ``COLUMN_A`` isn't empty, pass in: ``"NOT({COLUMN_A}='')"``

                For more information see
                `Airtable Docs on formulas. <https://airtable.com/api>`_

                Usage - Text Column is not empty:

                ``airtable.get_all(formula="NOT({COLUMN_A}='')")``

                Usage - Text Column contains:

                ``airtable.get_all(formula="FIND('SomeSubText', {COLUMN_STR})=1")``

            sort: str or lst
                Specifies how the records will be ordered. If you set the view parameter, the
                returned records in that view will be sorted by these fields. If sorting by
                multiple columns, column names can be passed as a list. Sorting Direction is
                ascending by default, but can be reversed by prefixing the column name with a minus
                sign -.

                Example usage:
                ``airtable.get_records(sort=['ColumnA', '-ColumnB'])``

            sample_size: int
                Number of rows to sample before determining columns

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        if isinstance(fields, str):
            fields = [fields]
        # Raises an error if sort is None type. Thus, only adding if populated.
        kwargs = {
            "fields": fields,
            "max_records": max_records,
            "view": view,
            "formula": formula,
        }
        if sort:
            kwargs["sort"] = sort

        tbl = Table(self.client.get_all(**kwargs))

        # If the results are empty, then return an empty table.
        if "fields" not in tbl.columns:
            return Table([[]])

        unpack_dicts_kwargs = {
            "column": "fields",
            "prepend": False,
        }
        if fields:
            unpack_dicts_kwargs["keys"] = fields

        if sample_size:
            unpack_dicts_kwargs["sample_size"] = sample_size

        return tbl.unpack_dict(**unpack_dicts_kwargs)

    def insert_record(self, row):
        """
        Insert a single record into an Airtable.

        `Args:`
            row: dict
                Fields to insert. Must be dictionary with Column names as Key.
            typecast: boolean
                Automatic data conversion from string values.
        `Returns:`
            Dictionary of inserted row

        """

        resp = self.client.insert(row)
        logger.info("Record inserted")
        return resp

    def insert_records(self, table, typecast=False):
        """
        Insert multiple records into an Airtable. The columns in your Parsons table must
        exist in the Airtable. The method will attempt to map based on column name, so the
        order of the columns is irrelevant.

        `Args:`
            table: A Parsons Table or list of dicts
                Insert a Parsons table or list
            typecast: boolean
                Automatic data conversion from string values.
        `Returns:`
            List of dictionaries of inserted rows
        """
        if isinstance(table, Table):
            table = table.to_dicts()
        resp = self.client.batch_insert(table, typecast=typecast)
        logger.info(f"{len(table)} records inserted.")
        return resp

    def update_record(self, record_id, fields, typecast=False):
        """
        Updates a record by its record id. Only Fields passed are updated, the rest are left as
        is.

        `Args:`
            record_id: str
                The Airtable record id
            fields: dict
                Fields to insert. Must be dictionary with Column names as Key.
            typecast: boolean
                Automatic data conversion from string values.
        `Returns:`
            ``None``
        """

        resp = self.client.update(record_id, fields, typecast=typecast)
        logger.info(f"{record_id} updated")
        return resp
