Databases
=========

Parsons offers support for a variety of popular SQL database dialects. The functionality is focused on the ability to query and upload data to SQL databases. Each database class also includes the ability to infer datatypes and data schemas from a Parsons table and automatically create new tables.

***************
Google BigQuery
***************

See :doc:`google` for documentation.

*****
MySQL
*****

MySQL is the world's most popular open source database. The Parson's class leverages on the `mysql <https://github.com/farcepest/MySQLdb1>`_ python package.

===========
Quick Start
===========

.. code-block:: python

   from parsons import MySQL

   # Instantiate MySQL from environmental variables
   mysql = MySQL()

   # Instantiate MySQL from passed variables
   mysql = MySQL(username='me', password='secret', host='mydb.com', db='dev', port=3306)

   # Query database
   tbl = mysql.query('select * from my_schema.secret_sauce')

   # Copy data to database
   tbl = Table.from_csv('my_file.csv') # Load from a CSV or other source.
   mysql.copy(tbl, 'my_schema.winning_formula')


.. autoclass:: parsons.MySQL
   :inherited-members:

********
Postgres
********

.. autoclass:: parsons.Postgres
   :inherited-members:


********
Redshift
********

See :doc:`aws` section for documentation.

*************
Database Sync
*************

Sync tables between two databases with just a few lines of code. Currently supported
database types are:

* Google BigQuery
* MySQL
* Postgres
* Redshift

===========
Quick Start
===========

**Full Sync Of Tables**

Copy all data from a source table to a destination table.

.. code-block:: python

   # Create source and destination database objects
   source_rs = Redshift()
   destination_rs = Postgres()

   # Create db sync object and run sync.
   db_sync = DBSync(source_rs, destination_rs) # Create DBSync Object
   db_sync.table_sync_full('parsons.source_data', 'parsons.destination_data')

**Incremental Sync of Tables**

Copy just new data in the table. Utilize this method for tables with
distinct primary keys.

.. code-block:: python

   # Create source and destination database objects
   source_rs = Postgres()
   destination_rs = Postgres()

   # Create db sync object and run sync.
   db_sync = DBSync(source_pg, destination_pg) # Create DBSync Object
   db_sync.table_sync_incremental('parsons.source_data', 'parsons.destination_data', 'myid')

===
API
===

.. autoclass:: parsons.DBSync
   :inherited-members:
