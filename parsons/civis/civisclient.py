import civis

from parsons.etl.table import Table
from parsons.utilities import check_env


class CivisClient:
    """
    Instantiate the Civis class.

    Args:
        db (str | int, optional): The Civis Redshift database. Can be a database id or the name of the database.
            Defaults to None.
        api_key (str, optional): The Civis api key. Defaults to None.
        **kwargs: Args Option settings for the client that are `described in the documentation
            <https://civis-python.readthedocs.io/en/stable/client.html#civis.APIClient>`_.

    Returns:
        Civis class

    """

    def __init__(self, db=None, api_key=None, **kwargs):
        self.db = check_env.check("CIVIS_DATABASE", db)
        self.api_key = check_env.check("CIVIS_API_KEY", api_key)
        self.client = civis.APIClient(api_key=api_key, **kwargs)
        """
        The Civis API client. Utilize this attribute to access to lower level and more
        advanced methods which might not be surfaced in Parsons. A list of the methods
        can be found by reading the Civis API client `documentation <https://civis-python.readthedocs.io/en/stable/client.html>`_.
        """

    def query(
        self, sql, preview_rows=10, polling_interval=None, hidden=True, wait=True
    ) -> Table | civis.futures.CivisFuture:
        """
        Execute a SQL statement as a Civis query.

        Run a query that may return no results or where only a small preview is required. To execute a query that
        returns a large number of rows, see
        :func:`~civis.io.read_civis_sql`.

        Args:
            sql (str): The SQL statement to execute.
            preview_rows: Int, optional The maximum number of rows to return. No more than 100 rows can be returned
                at once. Defaults to 10.
            polling_interval (int | float, optional): Number of seconds to wait between checks for query completion.
                Defaults to None.
            hidden (bool, optional): If ``True`` (the default), this job will not appear in the Civis UI.
                Defaults to True.
            wait (bool, optional): If ``True``, will wait for query to finish executing before exiting the method.
                If ``False``, returns the future object. Defaults to True.

        Returns:
            Table or civis.futures.CivisFuture: See :ref:`parsons-table` for output options.

        """
        fut = civis.io.query_civis(
            sql,
            self.db,
            preview_rows=preview_rows,
            polling_interval=polling_interval,
            hidden=hidden,
        )

        if not wait:
            return fut

        result = fut.result()

        if result["result_rows"] is None:
            return None

        result["result_rows"].insert(0, result["result_columns"])

        return Table(result["result_rows"])

    def table_import(
        self,
        table_obj,
        table,
        max_errors=None,
        existing_table_rows="fail",
        diststyle=None,
        distkey=None,
        sortkey1=None,
        sortkey2=None,
        wait=True,
        **civisargs,
    ) -> civis.futures.CivisFuture | None:
        """
        Write the table to a Civis Redshift cluster.

        Additional key word arguments can passed to `civis.io.dataframe_to_civis()
        <https://civis-python.readthedocs.io/en/v1.9.0/generated/civis.io.dataframe_to_civis.html#civis.io.dataframe_to_civis>`_

        Args:
            **civisargs
            table_obj: Obj A Parsons Table object.
            table (str): The schema and table you want to upload to. E.g., 'scratch.table'.
                Schemas or tablenames with periods must be double quoted, e.g. 'scratch."my.table"'.
            api_key (str): Your Civis API key. If not given, the CIVIS_API_KEY environment variable will be used.
            max_errors (int, optional): The maximum number of rows with errors to remove from the import before
                failing. Defaults to None.
            existing_table_rows (str, optional): The behaviour if a table with the requested name already exists.
                One of
                `'fail'`, `'truncate'`, `'append'` or `'drop'`. Defaults to "fail".
            diststyle (str, optional): The distribution style for the table. One of `'even'`, `'all'` or
                `'key'`. Defaults to None.
            distkey (str, optional): The column to use as the distkey for the table. Defaults to None.
            sortkey1 (str, optional): The column to use as the sortkey for the table. Defaults to None.
            sortkey2 (str, optional): The second column in a compound sortkey for the table.
                Defaults to None.
            wait (bool, optional): Wait for write job to complete before exiting method. If ``False``, returns the
                future object. Defaults to True.

        Returns:
            ``None`` or ``civis.futures.CivisFuture``

        """
        fut = civis.io.dataframe_to_civis(
            table_obj.to_dataframe(),
            database=self.db,
            table=table,
            max_errors=max_errors,
            existing_table_rows=existing_table_rows,
            diststyle=diststyle,
            distkey=distkey,
            sortkey1=sortkey1,
            sortkey2=sortkey2,
            headers=True,
            **civisargs,
        )

        if wait:
            return fut.result()

        return fut
