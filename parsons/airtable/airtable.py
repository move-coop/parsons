from pyairtable import Api as client
from parsons.etl import Table
from parsons.utilities import check_env
import logging


logger = logging.getLogger(__name__)


class Airtable(object):
    """
    `Args:`
        base_key: str
            The key/ID of the Airtable base that you will interact with, typically
            prefixed with `app`.
        table_name: str
            The name or key/ID of the table in the base. The table name is the
            equivalent of the sheet name in Excel or GoogleDocs. The ID can be
            found in the URL and is typically prefixed with `tbl`.
        personal_access_token: str
            The Airtable personal access token. Not required if ``AIRTABLE_PERSONAL_ACCESS_TOKEN``
            env variable set.
    """

    def __init__(self, base_key, table_name, personal_access_token=None):

        self.personal_access_token = check_env.check(
            "AIRTABLE_PERSONAL_ACCESS_TOKEN", personal_access_token
        )
        self.client = client(self.personal_access_token).table(base_key, table_name)

    def get_record(self, record_id):
        """
        Returns a single record.

        `Args:`
            record_id: str
                The Airtable record `id`
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

        tbl = Table(self.client.all(**kwargs))

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

    def insert_record(self, row, typecast=False):
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

        resp = self.client.create(row, typecast=typecast)
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

        resp = self.client.batch_create(table, typecast=typecast)
        logger.info(f"{len(table)} records inserted.")
        return resp

    def update_record(self, record_id, fields, typecast=False, replace=False):
        """
        Updates a record by its record `id`. Only Fields passed are updated, the rest are left as
        is.

        `Args:`
            record_id: str
                The Airtable record `id`
            fields: dict
                Fields to insert. Must be dictionary with Column names as Key.
            typecast: boolean
                Automatic data conversion from string values.
            replace: boolean
                Only provided fields are updated. If `True`, record is replaced in its
                entirety by provided fields; if a field is not included its value
                will bet set to null.
        `Returns:`
            Dictionary of updated row
        """

        resp = self.client.update(record_id, fields, typecast=typecast, replace=replace)
        logger.info(f"{record_id} updated")
        return resp

    def update_records(self, table, typecast=False, replace=False):
        """
        Update multiple records into an Airtable. The columns in your Parsons table must
        exist in the Airtable, and the record `id` column must be present. The method
        will attempt to map based on column name, so the order of the columns is irrelevant.

        `Args:`
            table: A Parsons Table or list of dicts
                Insert a Parsons table or list. Record must contain the record `id` column
                and columns containing the fields to update
            typecast: boolean
                Automatic data conversion from string values.
            replace: boolean
                Only provided fields are updated. If `True`, record is replaced in its
                entirety by provided fields; if a field is not included its value
                will bet set to null.
        `Returns:`
            List of dicts of updated records
        """

        # the update/upsert API call expects a dict/object shape of:
        # { id: string, fields: { column_name: value, ... } }
        # the map_update_fields helper will convert the flat table field
        # columns/keys into this nested structure
        table = list(map(map_update_fields, table))

        resp = self.client.batch_update(table, typecast=typecast, replace=replace)
        logger.info(f"{len(resp)} records updated.")
        return resp

    def upsert_records(self, table, key_fields=None, typecast=False, replace=False):
        """
        Update and/or create records, either using `id` (if included) or using a set of
        fields (`key_fields`) to look for matches. The columns in your Parsons table must
        exist in the Airtable. The method will attempt to map based on column name,
        so the order of the columns is irrelevant.

        `Args:`
            table: A Parsons Table or list of dicts
                Parsons table or list with records to upsert. Records must contain the record
                `id` column or the column(s) defined in `key_fields`.
            key_fields: list of str
              List of field names that Airtable should use to match records in the input
              with existing records.
            typecast: boolean
                Automatic data conversion from string values.
            replace: boolean
                Only provided fields are updated. If `True`, record is replaced in its
                entirety by provided fields; if a field is not included its value
                will bet set to null.
        `Returns:`
            Dictionary containing:
                - `updated_records`: list of updated record `id`s
                - `created_records`: list of created records `id`s
                - `records`: list of records
        """

        # the update/upsert API call expects a dict/object shape of:
        # { id: string, fields: { column_name: value, ... } }
        # the map_update_fields helper will convert the flat table field
        # columns/keys into this nested structure
        table = list(map(map_update_fields, table))

        resp = self.client.batch_upsert(table, key_fields, typecast=typecast, replace=replace)

        updated_records = resp["updatedRecords"]
        created_records = resp["createdRecords"]

        logger.info(
            f"{len(updated_records)} records updated, {len(created_records)} records created."
        )

        return {
            "records": resp["records"],
            "updated_records": updated_records,
            "created_records": created_records,
        }

    def delete_record(self, record_id):
        """
        Deletes a record by its record `id`.

        `Args:`
            record_id: str
                The Airtable record `id`
        `Returns:`
            Dictionary of record `id` and `deleted` status
        """

        resp = self.client.delete(record_id)
        logger.info(f"{record_id} updated")
        return resp

    def delete_records(self, table):
        """
        Delete multiple records from an Airtable.

        `Args:`
            table: A Parsons Table or list containing the record `id`s to delete.
        `Returns:`
            List of dicts with record `id` and `deleted` status
        """

        if isinstance(table, Table):
            table = table.to_dicts()

        # the API expects a list of ids which this method can accept directly;
        # otherwise if a table or list of dicts containing the `id` key/column
        # is provided then map the ids into the expected list of id strings.

        if any(isinstance(row, dict) for row in table):
            table = list(map(lambda row: row["id"], table))

        resp = self.client.batch_delete(table)
        logger.info(f"{len(table)} records deleted.")
        return resp


def map_update_fields(record):
    record_id = record.get("id")
    if "id" in record:
        del record["id"]
        return {"id": record_id, "fields": record}

    return {"fields": record}
