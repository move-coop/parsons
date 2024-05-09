import logging

# import pkgutil

logger = logging.getLogger(__name__)


class RedshiftTableUtilities(object):
    def __init__(self):
        pass

    def table_exists(self, table_name: str, view: bool = True) -> bool:
        """
        Check if a table or view exists in the database.

        `Args:`
            table_name: str
                The table name and schema (e.g. ``myschema.mytable``).
            view: boolean
                Check to see if a view exists by the same name

        `Returns:`
            boolean
                ``True`` if the table exists and ``False`` if it does not.
        """
        with self.connection() as connection:
            return self.table_exists_with_connection(table_name, connection, view)

    def table_exists_with_connection(self, table_name, connection, view=True):
        table_name = table_name.lower().split(".")
        table_name = [x.strip() for x in table_name]

        # Check in pg tables for the table
        sql = """select count(*) from pg_tables where schemaname='{}' and
                 tablename='{}';""".format(
            table_name[0], table_name[1]
        )

        # TODO maybe convert these queries to use self.query_with_connection

        with self.cursor(connection) as cursor:

            cursor.execute(sql)
            result = cursor.fetchone()[0]

            # Check in the pg_views for the table
            if view:
                sql = """select count(*) from pg_views where schemaname='{}' and
                         viewname='{}';""".format(
                    table_name[0], table_name[1]
                )

            cursor.execute(sql)
            result += cursor.fetchone()[0]

        # If in either, return boolean
        if result >= 1:
            logger.debug(f"{table_name[0]}.{table_name[1]} exists.")
            return True
        else:
            logger.debug(f"{table_name[0]}.{table_name[1]} does NOT exist.")
            return False

    def get_row_count(self, table_name):
        """
        Return the row count of a table.

        **SQL Code**

        .. code-block:: sql

           SELECT COUNT(*) FROM myschema.mytable

        `Args:`
            table_name: str
                The schema and name (e.g. ``myschema.mytable``) of the table.
        `Returns:`
            int
        """

        count_query = self.query(f"select count(*) from {table_name}")
        return count_query[0]["count"]

    def rename_table(self, table_name, new_table_name):
        """
        Rename an existing table.

        .. note::
            You cannot move schemas when renaming a table. Instead, utilize
            the :meth:`table_duplicate()`. method.

        Args:
            table_name: str
                Name of existing schema and table (e.g. ``myschema.oldtable``)
            new_table_name: str
                New name for table with the schema omitted (e.g. ``newtable``).
        """

        sql = f"alter table {table_name} rename to {new_table_name}"
        self.query(sql)
        logger.info(f"{table_name} renamed to {new_table_name}")

    def move_table(self, source_table, new_table, drop_source_table=False):
        """
        Move an existing table in the database.It will inherit encoding, sortkey
        and distkey. **Once run, the source table rows will be empty.** This is
        more efficiant than running ``"create newtable as select * from oldtable"``.

        For more information see: `ALTER TABLE APPEND <https://docs.aws.amazon.com/redshift/latest/dg/r_ALTER_TABLE_APPEND.html>`_

        Args:
            source_table: str
                Name of existing schema and table (e.g. ``my_schema.old_table``)
            new_table: str
                New name of schema and table (e.g. ``my_schema.newtable``)
            drop_original: boolean
                Drop the source table.
        Returns:
                None
        """  # noqa: E501,E261

        # To Do: Add the grants
        # To Do: Argument for if the table exists?
        # To Do: Add the ignore extra kwarg.

        create_sql = f"create table {new_table} (like {source_table});"
        alter_sql = f"alter table {new_table} append from {source_table}"

        logger.info(f"Creating empty {new_table} from {source_table}.")
        self.query(create_sql)

        with self.connection() as conn:

            #  An ALTER TABLE statement can't be run within a block, meaning
            #  that it needs to be committed on running. To enable this,
            #  the connection must be set to autocommit.

            conn.set_session(autocommit=True)
            logger.info(f"Moving data from {source_table} to {new_table}.")
            self.query_with_connection(alter_sql, conn)

        if drop_source_table:
            self.query(f"drop table {source_table};")
            logger.info(f"{source_table} dropped.")

        logger.info(f"{source_table} data moved from {new_table}  .")

    def _create_table_precheck(self, connection, table_name, if_exists):
        """
        Helper to determine what to do when you need a table that may already exist.

        `Args:`
            connection: obj
                A connection object obtained from ``redshift.connection()``
            table_name: str
                The table to check
            if_exists: str
                If the table already exists, either ``fail``, ``append``, ``drop``,
                or ``truncate`` the table.
        `Returns:`
            bool
                True if the table needs to be created, False otherwise.
        """

        if if_exists not in ["fail", "truncate", "append", "drop"]:
            raise ValueError("Invalid value for `if_exists` argument")

        exists = self.table_exists_with_connection(table_name, connection)

        if exists and if_exists in ["fail", "truncate", "append"]:
            if if_exists == "fail":
                raise ValueError("Table already exists.")
            elif if_exists == "truncate":
                truncate_sql = f"truncate table {table_name}"
                self.query_with_connection(truncate_sql, connection, commit=False)

        else:
            if exists and if_exists == "drop":
                logger.debug(f"Table {table_name} exist, will drop...")
                drop_sql = f"drop table {table_name};\n"
                self.query_with_connection(drop_sql, connection, commit=False)

            return True

        return False

    def populate_table_from_query(
        self, query, destination_table, if_exists="fail", distkey=None, sortkey=None
    ):
        """
        Populate a Redshift table with the results of a SQL query, creating the table if it
        doesn't yet exist.

        `Args:`
            query: str
                The SQL query
            destination_table: str
                Name of destination schema and table (e.g. ``mys_chema.new_table``)
            if_exists: str
                If the table already exists, either ``fail``, ``append``, ``drop``,
                or ``truncate`` the table.
            distkey: str
                The column to use as the distkey for the table.
            sortkey: str
                The column to use as the sortkey for the table.
        """
        with self.connection() as conn:
            should_create = self._create_table_precheck(conn, destination_table, if_exists)

            if should_create:
                logger.info(f"Creating table {destination_table} from query...")
                sql = f"create table {destination_table}"
                if distkey:
                    sql += f" distkey({distkey})"
                if sortkey:
                    sql += f" sortkey({sortkey})"
                sql += f" as {query}"
            else:
                logger.info(f"Inserting data into {destination_table} from query...")
                sql = f"insert into {destination_table} ({query})"

            self.query_with_connection(sql, conn, commit=False)

        logger.info(f"{destination_table} created from query")

    def duplicate_table(
        self,
        source_table,
        destination_table,
        where_clause="",
        if_exists="fail",
        drop_source_table=False,
    ):
        """
        Create a copy of an existing table (or subset of rows) in a new
        table. It will inherit encoding, sortkey and distkey.

        `Args:`
            source_table: str
                Name of existing schema and table (e.g. ``myschema.oldtable``)
            destination_table: str
                Name of destination schema and table (e.g. ``myschema.newtable``)
            where_clause: str
                An optional where clause (e.g. ``where org = 1``).
            if_exists: str
                If the table already exists, either ``fail``, ``append``, ``drop``,
                or ``truncate`` the table.
            drop_source_table: boolean
                Drop the source table
        """

        with self.connection() as conn:
            should_create = self._create_table_precheck(conn, destination_table, if_exists)

            if should_create:
                logger.info(f"Creating {destination_table} from {source_table}...")
                create_sql = f"create table {destination_table} (like {source_table})"
                self.query_with_connection(create_sql, conn, commit=False)

            logger.info(f"Transferring data to {destination_table} from {source_table}")
            select_sql = f"select * from {source_table} {where_clause}"
            insert_sql = f"insert into {destination_table} ({select_sql})"
            self.query_with_connection(insert_sql, conn, commit=False)

            if drop_source_table:
                logger.info(f"Dropping table {source_table}...")
                drop_sql = f"drop table {source_table}"
                self.query_with_connection(drop_sql, conn, commit=False)

        logger.info(f"{destination_table} created from {source_table}.")

    def union_tables(self, new_table_name, tables, union_all=True, view=False):
        """
        Union a series of table into a new table.

        Args:
            new_table_name: str
                The new table and schema (e.g. ``myschema.newtable``)
            tables: list
                A list of tables to union
            union_all: boolean
                If ``False`` will deduplicate rows. If ``True`` will include
                duplicate rows.
            view: boolean
                Create a view rather than a static table
        Returns:
            None
        """

        union_type = " UNION ALL" if union_all else " UNION"
        table_type = "VIEW" if view else "TABLE"

        sql = f"CREATE {table_type} {new_table_name} AS"
        for index, t in enumerate(tables):
            if index != 0:
                sql += union_type
            sql += f" SELECT * FROM {t}"

        self.query(sql)

        logger.info(f"Created {new_table_name} from {', '.join(tables)}")

    def get_tables(self, schema=None, table_name=None):
        """
        List the tables in a schema including metadata.

        Args:
            schema: str
                Filter by a schema
            table_name: str
                Filter by a table name
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        logger.info("Retrieving tables info.")
        sql = "select * from pg_tables"
        if schema or table_name:
            sql += " where"
        if schema:
            sql += f" schemaname = '{schema}'"
        if table_name:
            if schema:
                sql += " and"
            sql += f" tablename = '{table_name}'"
        return self.query(sql)

    def get_table_stats(self, schema=None, table_name=None):
        """
        List the tables statistics includes row count and size.

        .. warning::
           This method is only accessible by Redshift *superusers*.

        `Args:`
            schema: str
                Filter by a schema
            table_name: str
                Filter by a table name
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        logger.info("Retrieving table statistics.")
        sql = "select * from svv_table_info"
        if schema or table_name:
            sql += " where"
        if schema:
            sql += f" schema = '{schema}'"
        if table_name:
            if schema:
                sql += " and "
            sql += f" \"table\" = '{table_name}'"
        return self.query(sql)

    def get_columns(self, schema, table_name):
        """
        Gets the column names (and some other column info) for a table.

        If you just need the column names, run ``get_columns_list()`` as it is faster.

        .. code-block:: python

            for col in rs.get_columns('some_schema', 'some_table'):
                print(col)

        `Args:`
            schema: str
                The schema name
            table_name: str
                The table name
        `Returns:`
            A dict mapping column name to a dict with extra info. The keys of the dict are ordered
            just like the columns in the table. The extra info is a dict with format

            .. code-block:: python

                {
                'data_type': str,
                'max_length': int or None,
                'max_precision': int or None,
                'max_scale': int or None,
                'is_nullable': bool
                }

        """

        query = f"""
            select ordinal_position,
                   column_name,
                   data_type,
                   character_maximum_length as max_length,
                   numeric_precision as max_precision,
                   numeric_scale as max_scale,
                   is_nullable
            from information_schema.columns
            where table_name = '{table_name}'
            and table_schema = '{schema}'
            order by ordinal_position
        """

        return {
            row["column_name"]: {
                "data_type": row["data_type"],
                "max_length": row["max_length"],
                "max_precision": row["max_precision"],
                "max_scale": row["max_scale"],
                "is_nullable": row["is_nullable"] == "YES",
            }
            for row in self.query(query)
        }

    def get_columns_list(self, schema, table_name):
        """
        Gets the just the column names for a table.

        `Args:`
            schema: str
                The schema name
            table_name: str
                The table name
        `Returns:`
            A list of column names.
        """
        schema = f'"{schema}"' if not (schema.startswith('"') and schema.endswith('"')) else schema

        table_name = (
            f'"{table_name}"'
            if not (table_name.startswith('"') and table_name.endswith('"'))
            else table_name
        )

        first_row = self.query(f"select * from {schema}.{table_name} limit 1")

        return first_row.columns

    def get_views(self, schema=None, view=None):
        """
        List views.

        Args:
            schema: str
                Filter by a schema
            view: str
                Filter by a table name
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        logger.info("Retrieving views info.")
        sql = """
              select table_schema as schema_name,
              table_name as view_name,
              view_definition
              from information_schema.views
              where table_schema not in ('information_schema', 'pg_catalog')
              """
        if schema:
            sql += f" and table_schema = '{schema}'"
        if view:
            sql += f" and table_name = '{view}'"
        return self.query(sql)

    def get_queries(self):
        """
        Return the Current queries running and queueing, along with resource consumption.

        .. warning::
            Must be a Redshift superuser to run this method.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        logger.info("Retrieving running and queued queries.")

        # Lifted from Redshift Utils https://github.com/awslabs/amazon-redshift-utils/blob/master/src/AdminScripts/running_queues.sql # noqa: E501
        sql = """
              select trim(u.usename) as user,
                s.pid,
                q.xid,
                q.query,
                q.service_class as service_class,
                q.slot_count as slot,
                date_trunc('second',
                q.wlm_start_time) as start,
                decode(trim(q.state),
                    'Running',
                    'Run',
                    'QueuedWaiting',
                    'Queue',
                    'Returning',
                    'Return',trim(q.state)) as state,
                q.queue_Time/1000000 as queue_sec,
                q.exec_time/1000000 as exec_sec,
                m.cpu_time/1000000 cpu_sec,
                m.blocks_read read_mb,
                decode(m.blocks_to_disk,-1,null,m.blocks_to_disk) spill_mb,
                m2.rows as return_rows,
                m3.rows as NL_rows,
                substring(replace(nvl(qrytext_cur.text,trim(translate(s.text,chr(10)||chr(13)||chr(9) ,''))),'\\n',' '),1,90) as sql, -- # noqa: E501
                trim(decode(event&1,1,'SK ','') || decode(event&2,2,'Del ','') || decode(event&4,4,'NL ','') ||  decode(event&8,8,'Dist ','') || decode(event&16,16,'Bcast ','') || decode(event&32,32,'Stats ','')) as Alert -- # noqa: E501
            from stv_wlm_query_state q
            left outer join stl_querytext s on (s.query=q.query and sequence = 0)
            left outer join stv_query_metrics m on ( q.query = m.query and m.segment=-1 and m.step=-1 )
            left outer join stv_query_metrics m2 on ( q.query = m2.query and m2.step_type = 38 )
            left outer join ( select query, sum(rows) as rows from stv_query_metrics m3 where step_type = 15 group by 1) as m3 on ( q.query = m3.query ) -- # noqa: E501
            left outer join pg_user u on ( s.userid = u.usesysid )
            LEFT OUTER JOIN (SELECT ut.xid,'CURSOR ' || TRIM( substring ( TEXT from strpos(upper(TEXT),'SELECT') )) as TEXT
            FROM stl_utilitytext ut
            WHERE sequence = 0
               AND upper(TEXT) like 'DECLARE%'
               GROUP BY text, ut.xid) qrytext_cur ON (q.xid = qrytext_cur.xid)
            left outer join ( select query,sum(decode(trim(split_part(event,':',1)),'Very selective query filter',1,'Scanned a large number of deleted rows',2,'Nested Loop Join in the query plan',4,'Distributed a large number of rows across the network',8,'Broadcasted a large number of rows across the network',16,'Missing query planner statistics',32,0)) as event from STL_ALERT_EVENT_LOG -- # noqa: E501
            where event_time >=  dateadd(hour, -8, current_Date) group by query  ) as alrt on alrt.query = q.query -- # noqa: E501
            """

        return self.query(sql)

    def get_max_value(self, table_name, value_column):
        """
        Return the max value from a table.

        `Args:`
            table_name: str
                Schema and table name
            value_column: str
                The column containing the values
        """

        return self.query(f"SELECT MAX({value_column}) value from {table_name}")[0]["value"]

    def get_object_type(self, object_name):
        """
        Get object type.

        One of `view`, `table`, `index`, `sequence`, or `TOAST table`.

        `Args:`
            object_name: str
                The schema.obj for which to get the object type.
        `Returns:`
            `str` of the object type.

        """
        sql_obj_type = f"""
            select n.nspname||'.'||c.relname as objname
            , case
                when relkind='v' then 'view'
                when relkind='r' then 'table'
                when relkind='i' then 'index'
                when relkind='s' then 'sequence'
                when relkind='t' then 'TOAST table'
                end as object_name
            from pg_catalog.pg_class as c
            inner join pg_catalog.pg_namespace as n
                on c.relnamespace = n.oid
            where objname='{object_name}'
        """
        tbl = self.query(sql_obj_type)

        if tbl.num_rows == 0:
            logger.info(f"{object_name} doesn't exist.")
            return None

        return tbl[0]["object_name"]

    def is_view(self, object_name):
        """
        Return true if the object is a view.

        `Args:`
            object_name: str
                The schema.obj to test if it's a view.
        `Returns:`
            `bool`

        """
        is_view = self.get_object_type(object_name) == "view"
        logger.info(f"{object_name} is {'' if is_view else 'not'} a view.")
        return is_view

    def is_table(self, object_name):
        """
        Return true if the object is a table.

        `Args:`
            object_name: str
                The schema.obj to test if it's a table.
        `Returns:`
            `bool`

        """
        is_table = self.get_object_type(object_name) == "table"
        logger.info(f"{object_name} is {'' if is_table else 'not'} a table.")
        return is_table

    def get_table_definition(self, table):
        """
        Get the table definition (i.e. the create statement).

        `Args:`
            table: str
                The schema.table for which to get the table definition.
        `Returns:`
            str
        """

        schema, table = self.split_full_table_name(table)

        if not self.is_table(f"{schema}.{table}"):
            return None

        results = self.get_table_definitions(schema, table)

        return results[0]["ddl"]

    def get_table_definitions(self, schema=None, table=None):
        """
        Get the table definition (i.e. the create statement) for multiple tables.

        This works similar to `get_table_def` except it runs a single query
        to get the ddl for multiple tables. It supports SQL wildcards for
        `schema` and `table`. Only returns the ddl for _tables_ that match
        `schema` and `table` if they exist.

        `Args:`
            schema: str
                The schema to filter by.
            table: str
                The table to filter by.
        `Returns:`
            `list` of dicts with matching tables.

        """

        conditions = []
        if schema:
            conditions.append(f"schemaname like '{schema}'")
        if table:
            conditions.append(f"tablename like '{table}'")

        conditions_str = " and ".join(conditions)
        where_clause = f"where {conditions_str}" if conditions_str else ""

        # ddl_query = pkgutil.get_data(
        #     __name__, "queries/v_generate_tbl_ddl.sql").decode()
        sql_get_ddl = f"""
            select *
            from admin.v_generate_tbl_ddl
            {where_clause}
        """
        ddl_table = self.query(sql_get_ddl)

        if ddl_table.num_rows == 0:
            logger.info(f"No tables matching {schema} and {table}.")
            return None

        def join_sql_parts(columns, rows):
            return [f"{columns[1]}.{columns[2]}", "\n".join([row[4] for row in rows])]

        # The query returns the sql over multiple rows
        # We need to join then into a single row
        ddl_table.reduce_rows(
            ["table_id", "schemaname", "tablename"],
            join_sql_parts,
            ["tablename", "ddl"],
            presorted=True,
        )

        return ddl_table.to_dicts()

    def get_view_definition(self, view):
        """
        Get the view definition (i.e. the create statement).

        `Args:`
            view: str
                The schema.view for which to get the view definition.
        `Returns:`
            str
        """

        schema, view = self.split_full_table_name(view)

        if not self.is_view(f"{schema}.{view}"):
            return None

        results = self.get_view_definitions(schema, view)

        return results[0]["ddl"]

    def get_view_definitions(self, schema=None, view=None):
        """
        Get the view definition (i.e. the create statement) for multiple views.

        This works similar to `get_view_def` except it runs a single query
        to get the ddl for multiple views. It supports SQL wildcards for
        `schema` and `view`. Only returns the ddl for _views_ that match
        `schema` and `view` if they exist.

        `Args:`
            schema: str
                The schema to filter by.
            view: str
                The view to filter by.
        `Returns:`
            `list` of dicts with matching views.

        """

        conditions = []
        if schema:
            conditions.append(f"schemaname like '{schema}'")
        if view:
            conditions.append(f"g.viewname like '{view}'")

        conditions_str = " and ".join(conditions)
        where_clause = f"where {conditions_str}" if conditions_str else ""

        # ddl_query = pkgutil.get_data(
        #     __name__, "queries/v_generate_view_ddl.sql").decode()
        sql_get_ddl = f"""
            select schemaname || '.' || viewname as viewname, ddl
            from admin.v_generate_view_ddl g
            {where_clause}
        """
        ddl_view = self.query(sql_get_ddl)

        if ddl_view.num_rows == 0:
            logger.info(f"No views matching {schema} and {view}.")
            return None

        return ddl_view.to_dicts()

    @staticmethod
    def split_full_table_name(full_table_name):
        """
        Split a full table name into its schema and table. If a schema isn't
        present, return `public` for the schema. Similarly, Redshift defaults
        to the `public` schema, when one isn't provided.

        Eg:
        ``(schema, table) = Redshift.split_full_table_name("some_schema.some_table")``

        `Args:`
            full_table_name: str
                The table name, as "schema.table"
        `Returns:`
            tuple
                A tuple containing (schema, table)
        """
        if "." not in full_table_name:
            return "public", full_table_name

        try:
            schema, table = full_table_name.split(".")
        except ValueError as e:
            if "too many values to unpack" in str(e):
                raise ValueError(f"Invalid Redshift table {full_table_name}")

        return schema, table

    @staticmethod
    def combine_schema_and_table_name(schema, table):
        """
        Creates a full table name by combining a schema and table.

        `Args:`
            schema: str
                The schema name
            table: str
                The table name
        `Returns:`
            str
                The combined full table name
        """
        return f"{schema}.{table}"
