Databases
=========

********
Overview
********

Parsons offers support for a variety of popular SQL database dialects. The functionality is focused on the ability to query and upload data to SQL databases. Each database class also includes the ability to infer datatypes and data schemas from a Parsons table and automatically create new tables.

Similar to other classes in Parsons, the query methods for databases all return :ref:`parsons-table`, which allow them to be easily converted to other data types.

There is also support for synchronization of tables between databases as part of the :doc:`dbsync` framework.

***************
Google BigQuery
***************

See :doc:`google` for documentation.


*****
MySQL
*****
.. _my-sql:

MySQL is the world's most popular open source database. The Parsons class leverages on the `MySQLdb1 <https://github.com/farcepest/MySQLdb1>`_ python package.

===========
Quick Start
===========

**Authentication**

.. code-block:: python

   from parsons import MySQL

   # Instantiate MySQL from environmental variables
   mysql = MySQL()

   # Instantiate MySQL from passed variables
   mysql = MySQL(username='me', password='secret', host='mydb.com', db='dev', port=3306)

**Quick Start**

.. code-block:: python

   # Query database
   tbl = mysql.query('select * from my_schema.secret_sauce')

   # Copy data to database
   tbl = Table.from_csv('my_file.csv') # Load from a CSV or other source.
   mysql.copy(tbl, 'my_schema.winning_formula')


.. autoclass:: parsons.databases.mysql.mysql.MySQL
   :inherited-members:
   :members:

.. _postgres:

********
Postgres
********

Postgres is popular open source SQL database dialect. The Parsons class leverages the `psycopg2 <https://www.psycopg.org/>`_ python package.

===========
Quick Start
===========

**Authentication**

.. code-block:: python

   from parsons import Postgres

   # Instantiate Postgres from environmental variables
   pg = Postgres()

   # Instantiate Postgres from passed variables
   pg = Postgres(username='me', password='secret', host='mydb.com', db='dev', port=3306)

   # Instantiate Postgres from a ~/.pgpass file
   pg = Postgres()

**Quick Start**

.. code-block:: python

   # Query database
   tbl = pg.query('select * from my_schema.secret_sauce')

   # Copy data to database
   tbl = Table.from_csv('my_file.csv') # Load from a CSV or other source.
   pg.copy(tbl, 'my_schema.winning_formula')

.. autoclass:: parsons.databases.postgres.postgres.Postgres
   :inherited-members:
   :members:

********
Redshift
********

See :ref:`Redshift <redshift>` for documentation.

.. _sqlite:

********
Sqlite
********

SQLite is a performant flat-file database that's often touted as the "zero-config" database. The Parsons class uses the python3 built-in sqlite3 connector.

===========
Quick Start
===========

**Authentication**

.. code-block:: python

   from parsons import Sqlite

   # Instantiate Sqlite from passed variables
   sqlite = Sqlite(db_path='local.db')

**Quick Start**

.. code-block:: python

   # Query database
   tbl = sqlite.query('select * from my_table')

   # Copy data to database
   tbl = Table.from_csv('my_file.csv') # Load from a CSV or other source.
   sqlite.copy(tbl, 'my_destination_table')

.. autoclass:: parsons.databases.sqlite.sqlite.Sqlite
   :inherited-members:
   :members:
   