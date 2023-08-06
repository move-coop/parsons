from abc import ABC, abstractmethod
from typing import Optional
from parsons.etl.table import Table


class DatabaseConnector(ABC):
    """
    An abstract base class that provides a uniform interface for all Parsons database connectors.
    This class should be used in functions instead of the specific database connector classes
    when the functions don't rely on database-specific functionality.

    It ensures that any class that inherits from it implements the `table_exists`, `copy`, and
    `query` methods, which are common operations when working with databases.

    Note:
        The Python type system (as of 3.10.6) will not stop you from breaking the type contract
        of method signatures when implementing a subclass. It is up to the author of a database
        connector to ensure that it satisfies this interface. Be careful to, for example, not
        change the types of the parameters or leave out optional parameters that are specified
        in the interface.

        Any such inconsistencies can cause unexpected runtime errors that will not be caught by
        the type checker.

        It is possible to safely add additional features, such as new methods or extra **optional**
        parameters to specified methods. In general adding new methods is safe, but adding optional
        parameters to methods specified in the interface should be considered bad practice, because
        it could result in unexpected behavior.

    Example usage:

    .. code-block:: python

        def my_function(db: DatabaseConnector, data: Table):
            # Your code here, using the db object

        # Pass an instance of a class that inherits from DatabaseConnector, e.g. Redshift
        my_function(some_db_instance, some_data)

    """

    @abstractmethod
    def table_exists(self, table_name: str) -> bool:
        """Check if a table or view exists in the database.

        `Args:`
            table_name: str
                The table name and schema (e.g. ``myschema.mytable``).

        `Returns:`
            boolean
                ``True`` if the table exists and ``False`` if it does not.
        """
        pass

    @abstractmethod  # TODO: does postgres/mysql have max errors too?
    def copy(self, tbl: Table, table_name: str, if_exists: str, max_errors: int = 0, **copy_kwargs):
        """Copy a :ref:`parsons-table` to the database.

        `Args`:
            tbl (Table):
                Table containing the data to save.
            table_name (str):
                The destination table name (ex. ``my_schema.my_table``).
            if_exists (str):
                If the table already exists, either ``fail``, ``append``, ``drop``
                or ``truncate`` the table.
            copy_kwargs (optional):
                Generic grab bag of additional parameters, often specific to an individual database.
        """
        pass

    @abstractmethod  # TODO: does postgres/mysql have this?
    def copy_s3(
        self,
        table_name,
        bucket,
        key,
        if_exists: str = "fail",
        max_errors: int = 0,
        data_type: str = "csv",
        csv_delimiter: str = ",",
        ignoreheader: int = 1,
        nullas: str = None,
        **copy_kwargs
    ):
        """Copy a :ref:`parsons-table` to the database.

        `Args`: TODO: update these
            tbl (Table):
                Table containing the data to save.
            table_name (str):
                The destination table name (ex. ``my_schema.my_table``).
            if_exists (str):
                If the table already exists, either ``fail``, ``append``, ``drop``
                or ``truncate`` the table.
            copy_kwargs (optional):
                Generic grab bag of additional parameters, often specific to an individual database.
        """
        pass

    @abstractmethod
    def query(self, sql: str, parameters: Optional[list] = None) -> Optional[Table]:
        """Execute a query against the database. Will return ``None`` if the query returns empty.

        To include python variables in your query, it is recommended to pass them as parameters,
        following the `psycopg style
          <http://initd.org/psycopg/docs/usage.html#passing-parameters-to-sql-queries>`.
        Using the ``parameters`` argument ensures that values are escaped properly, and avoids SQL
        injection attacks.

        **Parameter Examples**

        .. code-block:: python

            # Note that the name contains a quote, which could break your query if not escaped
            # properly.
            name = "Beatrice O'Brady"
            sql = "SELECT * FROM my_table WHERE name = %s"
            db.query(sql, parameters=[name])

        .. code-block:: python

            names = ["Allen Smith", "Beatrice O'Brady", "Cathy Thompson"]
            placeholders = ', '.join('%s' for item in names)
            sql = f"SELECT * FROM my_table WHERE name IN ({placeholders})"
            db.query(sql, parameters=names)

        `Args:`
            sql: str
                A valid SQL statement
            parameters: Optional[list]
                A list of python variables to be converted into SQL values in your query

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """
        pass
