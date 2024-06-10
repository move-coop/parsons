from abc import ABC, abstractmethod
from typing import Optional
from parsons.etl.table import Table


class DatabaseConnector(ABC):
    """
    An abstract base class that provides a uniform interface for all Parsons database connectors.
    This class should be used in functions instead of the specific database connector classes
    when the functions don't rely on database-specific functionality.

    It ensures that any class that inherits from it implements the methods that are uniform
    operations when working with databases.

    Should you use `DatabaseConnector` instead of `Redshift`/`BigQuery`/etc?

    Overall this class is mostly useful for code in the Parsons library, not code using it.
    There could be some exceptions. In general though, if you are writing a script to do a task
    like moving data out of an API service and into a data warehouse, you probably do not need
    to use DatabaseConnector. You can probably just use the Parsons class that directly corresponds
    with the database that you use.

    Here are more examples of situations where you may or may not need to use DatabaseConnector:

        1. You do not use type annotations, or you don't know what "type annotations" are - No

            If you do not use type annotations for your code, then you do not need to think about
            `DatabaseConnector` when writing your code. This is the most common case. If none
            of the cases below apply to you, then you probably don't need it.

            In this simple example, we are not using type annotations in our code. We don't need
            to think about exactly what class is being passed in. Python will figure it out.

            ```python
            def my_database_function(db):
                    some_data = get_some_data()
                    db.copy("some_table", some_data)

            # These will all just work:
            my_database_function(Redshift())
            my_database_function(MySQL())
            my_database_functon(BigQuery())
            ```

        2. You only use one database in your work - No

            This is where most people will fall. Usually code is not intended to run on
            multiple databases without modification. For example, if you are working for
            an organization that uses Amazon Redshift as your data warehouse, you do not
            need to use `DatabaseConnector` to write ETL scripts to load data into your
            Redshift. It is rare that organizations switch databases. In the cases where
            that does occur, usually more work is required to migrate your environment and
            your vendor-specific SQL than would be saved by using `DatabaseConnector`.

        3. You are writing a sample script or a tutorial - Yes

            If you are using Parsons to write a sample script or tutorial, you should use
            `DatabaseConnector`! If you use `DatabaseConnector` type annotations and the
            `discover_database` function, then your sample code will run on any system.
            This makes it much easier for new programmers to get your code working on
            their system.

        4. Utility code inside Parsons or other libraries - Yes

            If you are writing a utility script inside Parsons or another library meant
            for broad distribution, you should probably use `DatabaseConnector` type
            annotations. This will ensure that your library code will be usable by the
            widest possible set of users, not just users on one specific database.

    Developer Notes:
        This class is an Abstract Base Class (ABC). It's designed to ensure that all classes
        inheriting from it implement certain methods, enforcing a consistent interface across
        database connectors.

        If you need to add a new method to the database connectors, there are three options:
        1. Add the method to this ABC and implement it for all databases.
        2. Add the method to this ABC and implement it for some databases while adding stubs for
           others.
        3. Implement the method on a specific database connector without touching the ABC.

        If you go the second route, you can add a stub method like this:

            .. code-block:: python

                def new_method(self, arg1, arg2):
                    raise NotImplementedError("Method not implemented for this database connector.")
            ```

        This communicates clearly to users that the method does not exist for certain connectors.

        If you go the third route, remember that you're responsible for making sure your new
        method matches the existing methods in other database connectors. For example, if you're
        adding a method that already exists in another connector, like Redshift, you need to ensure
        your new method behaves the same way and has the same parameters with the same types in the
        same order. See the note below for more detail.

    Note:
        The Python type system (as of 3.10.6) will not stop you from breaking the type contract
        of method signatures when implementing a subclass. It is up to the author of a database
        connector to ensure that it satisfies this interface. Be careful to, for example, not
        change the types of the parameters or leave out optional parameters that are specified
        in the interface.

        Any such inconsistencies can cause unexpected runtime errors that will not be caught by
        the type checker.

        It is safe to add additional features to subclasses, such as new methods or extra *optional*
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

    @abstractmethod
    def copy(self, tbl: Table, table_name: str, if_exists: str):
        """Copy a :ref:`parsons-table` to the database.

        `Args`:
            tbl (Table):
                Table containing the data to save.
            table_name (str):
                The destination table name (ex. ``my_schema.my_table``).
            if_exists (str):
                If the table already exists, either ``fail``, ``append``, ``drop``
                or ``truncate`` the table.
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
