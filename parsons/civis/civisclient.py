import civis
from parsons.etl.table import Table
from parsons.utilities import check_env


class CivisClient(object):
    """
    Instantiate the Civis class.

    `Args:`
        db: str or int
            The Civis Redshift database. Can be a database id or the name of the
            database.
        api_key: str
            The Civis api key.
        **kwargs: args
            Option settings for the client that are `described in the documentation <https://civis-python.readthedocs.io/en/stable/client.html#civis.APIClient>`_.
    `Returns:`
        Civis class
    """  # noqa: E501

    def __init__(self, db=None, api_key=None, **kwargs):

        self.db = check_env.check("CIVIS_DATABASE", db)
        self.api_key = check_env.check("CIVIS_API_KEY", api_key)
        self.client = civis.APIClient(api_key=api_key, **kwargs)
        """
        The Civis API client. Utilize this attribute to access to lower level and more
        advanced methods which might not be surfaced in Parsons. A list of the methods
        can be found by reading the Civis API client `documentation <https://civis-python.readthedocs.io/en/stable/client.html>`_.
        """  # noqa: E501

    def query(
        self, sql, preview_rows=10, polling_interval=None, hidden=True, wait=True
    ):
        """
        Execute a SQL statement as a Civis query.

        Run a query that may return no results or where only a small
        preview is required. To execute a query that returns a large number
        of rows, see :func:`~civis.io.read_civis_sql`.

        `Args`
            sql: str
                The SQL statement to execute.
            preview_rows: int, optional
                The maximum number of rows to return. No more than 100 rows can be
                returned at once.
            polling_interval: int or float, optional
                Number of seconds to wait between checks for query completion.
            hidden: bool, optional
                If ``True`` (the default), this job will not appear in the Civis UI.
            wait: boolean
                If ``True``, will wait for query to finish executing before exiting
                the method. If ``False``, returns the future object.
        `Returns`
            Parsons Table or ``civis.CivisFuture``
                See :ref:`parsons-table` for output options.
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
        **civisargs
    ):
        """
        Write the table to a Civis Redshift cluster. Additional key word
        arguments can passed to `civis.io.dataframe_to_civis()  <https://civis-python.readthedocs.io/en/v1.9.0/generated/civis.io.dataframe_to_civis.html#civis.io.dataframe_to_civis>`_ # noqa: E501

        `Args`
            table_obj: obj
                A Parsons Table object
            table: str
                The schema and table you want to upload to. E.g., 'scratch.table'. Schemas
                or tablenames with periods must be double quoted, e.g. 'scratch."my.table"'.
            api_key: str
                Your Civis API key. If not given, the CIVIS_API_KEY environment variable will be
                used.
            max_errors: int
                The maximum number of rows with errors to remove from the import before failing.
            existing_table_rows: str
                The behaviour if a table with the requested name already exists. One of
                `'fail'`, `'truncate'`, `'append'` or `'drop'`. Defaults to `'fail'`.
            diststyle: str
                The distribution style for the table. One of `'even'`, `'all'` or `'key'`.
            distkey: str
                The column to use as the distkey for the table.
            sortkey1: str
                The column to use as the sortkey for the table.
            sortkey2: str
                The second column in a compound sortkey for the table.
            wait: boolean
                Wait for write job to complete before exiting method. If ``False``, returns
                the future object.
        `Returns`
            ``None`` or ``civis.CivisFuture``
        """  # noqa: E501,E261

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
            **civisargs
        )

        if wait:
            return fut.result()

        return fut

    def update_sql_in_civis_script(self, civis_script_id, query):
        """
        This function updates the SQL within a SQL script
        `Args`
            id: int
                Civis SQL Script ID
            query: str
                The query to replace existing SQL with
        `Returns`
            None
        """

        self.client.scripts.patch_sql(civis_script_id, sql=query)
        return None

    def get_sql_from_civis_script(self, civis_script_id):
        """
        This function grabs the SQL from a Civis SQL Script.

        `Args`
            civis_script_id: int
                the Civis SQL Script ID

        `Returns`
            The SQL included in the Civis SQL Script.
        """

        sql_script = self.client.scripts.get_sql(civis_script_id)

        return sql_script["sql"]

    def get_sql_from_civis_project(self, civis_project_id):
        """
        This function allows you to grab all of the SQL from Civis SQL
        Scripts in a given Civis Project.

        `Args`
            civis_project_id: int
                the Civis Project ID

        `Returns`
            A Parsons Table with all of the relevant SQL.
        """

        sql_scripts = self.client.projects.get(civis_project_id)
        sql_dicts = [
            {
                "object_name": x["name"],
                "sql": self.client.scripts.get_sql(x["object_id"])["sql"],
            }
            for x in sql_scripts["all_objects"]
            if x["object_job_type"] == "Jobjob_types::SqlRunner"
        ]
        sql_table = Table(sql_dicts)

        return sql_table

    def trigger_existing_civis_sql_job(self, civis_script_id):
        """
        Runs an existing Civis SQL job.

        `Args:`
            civis_script_id: int

        `Returns:`
            object
                The Civis Run ID
        """
        id = int(civis_script_id)
        run = self.client.scripts.post_sql_runs(id)

        return run.id

    def trigger_existing_civis_container_job(self, civis_script_id):
        """
        Runs an existing Civis SQL job.

        `Args:`
            civis_script_id: int

        `Returns:`
            object
                The Civis Run ID
        """

        id = int(civis_script_id)
        run = self.client.scripts.post_containers_runs(id)

        return run.id

    def trigger_existing_civis_workflow(self, civis_wf_id):
        """
        Runs an existing Civis Workflow, waiting for it to complete before returning.
        `Args:`
            civis_wf_id: int
        `Returns:`
            object
                The Civis Workflow Execution ID
        """

        id = int(civis_wf_id)
        execute = self.client.workflows.post_executions(id)

        # Wait on the workflow to finish
        poller = self.client.workflows.get_executions
        poller_args = (id, execute.id)
        polling_interval = 10
        future = self.futures.CivisFuture(poller, poller_args, polling_interval)
        future.result()

        return execute.id
