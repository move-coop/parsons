class RedshiftSchema(object):
    def schema_exists(self, schema):
        sql = f"select * from pg_namespace where nspname = '{schema}'"
        res = self.query(sql)
        return res.num_rows > 0

    def create_schema_with_permissions(self, schema, group=None):
        """
        Creates a Redshift schema (if it doesn't already exist), and grants usage permissions to
        a Redshift group (if specified).

        `Args:`
            schema: str
                The schema name
            group: str
                The Redshift group name
            type: str
                The type of permissions to grant. Supports `select`, `all`, etc. (For
                full list, see the
                `Redshift GRANT docs <https://docs.aws.amazon.com/redshift/latest/dg/r_GRANT.html>`_)
        """  # noqa: E501,E261

        if not self.schema_exists(schema):
            self.query(f"create schema {schema}")
            self.query(f"grant usage on schema {schema} to group {group}")

    def grant_schema_permissions(self, schema, group, permissions_type="select"):
        """
        Grants a Redshift group permissions to all tables within an existing schema.

        `Args:`
            schema: str
                The schema name
            group: str
                The Redshift group name
            type: str
                The type of permissions to grant. Supports `select`, `all`, etc. (For
                full list, see the
                `Redshift GRANT docs <https://docs.aws.amazon.com/redshift/latest/dg/r_GRANT.html>`_)
        """  # noqa: E501,E261

        sql = f"""
            grant usage on schema {schema} to group {group};
            grant {permissions_type} on all tables in schema {schema} to group {group};
        """
        self.query(sql)
