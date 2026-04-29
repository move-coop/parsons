import logging
from typing import Any

from pyairtable import Api as client
from pyairtable.api.types import RecordDeletedDict, RecordDict

from parsons import Table
from parsons.utilities import check_env

logger = logging.getLogger(__name__)


class Airtable:
    """
    Args:
        base_key:
            The key/ID of the Airtable base that you will interact with,
            typically prefixed with ``app``.
        table_name:
            The name or key/ID of the table in the base.
            The table name is the equivalent of the sheet name in Excel or Google Docs.
            The ID can be found in the URL and is typically prefixed with ``tbl``.
        personal_access_token:
            The Airtable personal access token.
            Not required if ``AIRTABLE_PERSONAL_ACCESS_TOKEN`` env variable set.

    """

    def __init__(
        self, base_key: str, table_name: str, personal_access_token: str | None = None
    ) -> None:
        self.personal_access_token = check_env.check(
            "AIRTABLE_PERSONAL_ACCESS_TOKEN", personal_access_token
        )
        self.client = client(self.personal_access_token).table(base_key, table_name)

    def get_record(self, record_id: str) -> RecordDict:
        """
        Returns a single record.

        Args:
            record_id: The Airtable record `id`

        """

        return self.client.get(record_id)

    def get_records(
        self,
        fields: str | list[str] | None = None,
        max_records: int | None = None,
        view: str | None = None,
        formula: str | None = None,
        sort: str | list[str] | None = None,
        sample_size: int | None = None,
    ) -> Table:
        """
        Args:
            fields:
                Only return specified column or list of columns.
                The column name is case sensitive
            max_records: The maximum total number of records that will be returned.
            view:
                If set, only the records in that view will be returned.
                The records will be sorted according to the order of the view.
            formula:
                The formula will be evaluated for each record.
                If the result is not ``0``, ``false``, ``""``, ``NaN``, ``[]``, or ``#Error!``,
                the record will be included in the response.

                If combined with view, only records in that view which satisfy the
                formula will be returned.

                For example, to only include records where ``COLUMN_A`` isn't empty,
                pass in: ``"NOT({COLUMN_A}='')"``

                For more information see `Airtable API Documentation`_

                .. code-block:: python
                    :caption: Usage - Text Column is not empty

                    airtable.get_all(formula="NOT({COLUMN_A}='')")

                .. code-block:: python
                    :caption: Usage - Text Column contains

                    airtable.get_all(formula="FIND('SomeSubText', {COLUMN_STR})=1")

            sort:
                Specifies how the records will be ordered.
                If you set the view parameter, the returned records
                in that view will be sorted by these fields.
                If sorting by multiple columns, column names can be passed as a list.
                Sorting Direction is ascending by default, but can be reversed
                by prefixing the column name with a minus sign ``-``.

                .. code-block:: python
                    :caption: Example usage

                    airtable.get_records(sort=['ColumnA', '-ColumnB'])

            sample_size:
                Number of rows to sample before determining columns

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

    def insert_record(self, row: dict[str, Any], typecast: bool = False) -> RecordDict:
        """
        Insert a single record into an Airtable.

        Args:
            row:
                Fields to insert.
                Must be dictionary with Column names as Key.
            typecast: Automatic data conversion from string values.

        Returns:
            Inserted row

        """

        resp = self.client.create(row, typecast=typecast)
        logger.info("Record inserted")
        return resp

    def insert_records(
        self, table: Table | list[dict[str, Any]], typecast: bool = False
    ) -> list[RecordDict]:
        """
        Insert multiple records into an Airtable.

        The columns in your Parsons table must exist in the Airtable.
        The method will attempt to map based on column name,
        so the order of the columns is irrelevant.

        Args:
            table: Insert a Parsons table or list
            typecast: Automatic data conversion from string values.

        Returns:
            Inserted rows

        """

        if isinstance(table, Table):
            table = table.to_dicts()

        resp = self.client.batch_create(table, typecast=typecast)
        logger.info(f"{len(table)} records inserted.")
        return resp

    def update_record(
        self, record_id: str, fields: dict[str, Any], typecast: bool = False, replace: bool = False
    ) -> RecordDict:
        """
        Updates a record by its record `id`.

        Only Fields passed are updated, the rest are left as-is.

        Args:
            record_id: The Airtable record `id`
            fields:
                Fields to insert.
                Must be dictionary with Column names as Key.
            typecast: Automatic data conversion from string values.
            replace:
                Only provided fields are updated.
                If `True`, record is replaced in its entirety by provided fields.
                If a field is not included its value will bet set to null.

        Returns:
            Updated row

        """

        resp = self.client.update(record_id, fields, typecast=typecast, replace=replace)
        logger.info(f"{record_id} updated")
        return resp

    def update_records(
        self, table: Table | list[dict[str, Any]], typecast: bool = False, replace: bool = False
    ) -> list[RecordDict]:
        """
        Update multiple records into an Airtable. The columns in your Parsons table must
        exist in the Airtable, and the record `id` column must be present. The method
        will attempt to map based on column name, so the order of the columns is irrelevant.

        Args:
            table:
                Insert a Parsons table or list.
                Record must contain the record `id` column
                and columns containing the fields to update
            typecast:
                Automatic data conversion from string values.
            replace:
                Only provided fields are updated.
                If `True`, record is replaced in its entirety by provided fields
                If a field is not included its value will be set to null.

        Returns:
            Updated records

        """

        # the update/upsert API call expects a dict/object shape of:
        # { id: str, fields: { column_name: value, ... } }
        # the map_update_fields helper will convert the flat table field
        # columns/keys into this nested structure
        table = list(map(map_update_fields, table))

        resp = self.client.batch_update(table, typecast=typecast, replace=replace)
        logger.info(f"{len(resp)} records updated.")
        return resp

    def upsert_records(
        self,
        table: Table | list[dict[str, Any]],
        key_fields: list[str] | None = None,
        typecast: bool = False,
        replace: bool = False,
    ) -> dict[str, list[str] | list[RecordDict]]:
        """
        Update and/or create records.

        You may either use `id` (if included) or a set of fields (`key_fields`) to look for matches.

        The columns in your Parsons table must exist in the Airtable.
        The method will attempt to map based on column name,
        so the order of the columns is irrelevant.

        Args:
            table:
                Records to upsert.
                Records must contain the record `id` column or
                the column(s) defined in `key_fields`.
            key_fields:
                Field names that Airtable should use to match
                records in the input with existing records.
            typecast:
                Automatic data conversion from string values.
            replace:
                Only provided fields are updated.
                If `True`, record is replaced in its entirety by provided fields.
                If a field is not included its value will bet set to null.

        Returns:
            - ``updated_records``, a list of each updated record `id`
            - ``created_records``, a list of each created records `id`
            - ``records``, a list of records

        """

        # the update/upsert API call expects a dict/object shape of:
        # { id: str, fields: { column_name: value, ... } }
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

    def delete_record(self, record_id: str) -> RecordDeletedDict:
        """
        Deletes a record by its record `id`.

        Args:
            record_id: The Airtable record `id`

        """

        resp = self.client.delete(record_id)
        logger.info(f"{record_id} updated")
        return resp

    def delete_records(
        self, table: Table | list[dict[str, Any]] | list[str]
    ) -> list[RecordDeletedDict]:
        """
        Delete multiple records from an Airtable.

        Args:
            table: A Parsons Table or list containing each record `id` to delete.

        """

        if isinstance(table, Table):
            table: list[dict[str, Any]] = table.to_dicts()

        # the API expects a list of ids which this method can accept directly;
        # otherwise if a table or list of dicts containing the `id` key/column
        # is provided then map the ids into the expected list of id strings.

        if any(isinstance(row, dict) for row in table):
            table: list[str] = [row["id"] for row in table]

        resp = self.client.batch_delete(table)
        logger.info(f"{len(table)} records deleted.")
        return resp


def map_update_fields(record: dict[str, Any]) -> dict[str, str | dict | None]:
    record_id: str | None = record.get("id")
    if "id" in record:
        del record["id"]
        return {"id": record_id, "fields": record}

    return {"fields": record}
