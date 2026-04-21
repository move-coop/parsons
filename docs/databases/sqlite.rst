######
Sqlite
######

SQLite is a performant flat-file database that's often touted as the "zero-config" database.
The Parsons class uses the python3 built-in sqlite3 connector.

Quickstart
==========

.. code-block:: python
   :caption: Instantiate Sqlite from passed variables

   from parsons import Sqlite
   sqlite = Sqlite(db_path='local.db')

.. code-block:: python
   :caption: Query database

   tbl = sqlite.query('select * from my_table')

.. code-block:: python
   :caption: Copy data to database

   tbl = Table.from_csv('my_file.csv') # Load from a CSV or other source.
   sqlite.copy(tbl, 'my_destination_table')

API
====

.. autoclass:: parsons.databases.sqlite.sqlite.Sqlite
   :inherited-members:
   :members:
