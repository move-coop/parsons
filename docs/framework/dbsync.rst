#############
Database Sync
#############

The database sync framework allows tables between two databases with just a few lines of code.
Currently supported database types are:

* :ref:`google/bigquery:BigQuery`
* :ref:`databases/mysql:MySQL`
* :ref:`databases/postgres:Postgres`
* :ref:`aws/redshift:Redshift`

The :class:`DBSync` class is not a connector, but rather a class that joins in database classes and moves data seamlessly between them.

Quickstart
==========

Full Sync Of Tables
-------------------

.. code-block:: python
   :caption: Copy all data from a source table to a destination table

   # Create source and destination database objects
   source_rs = Redshift()
   destination_rs = Postgres()

   # Create db sync object and run sync.
   db_sync = DBSync(source_rs, destination_rs) # Create DBSync Object
   db_sync.table_sync_full('parsons.source_data', 'parsons.destination_data')

Incremental Sync of Tables
--------------------------

.. code-block:: python
   :caption: Copy just new data in the table. Utilize this method for tables with primary keys.

   # Create source and destination database objects
   source_rs = Postgres()
   destination_rs = Postgres()

   # Create db sync object and run sync.
   db_sync = DBSync(source_pg, destination_pg) # Create DBSync Object
   db_sync.table_sync_incremental('parsons.source_data', 'parsons.destination_data', 'myid')

API
====

.. autoclass:: parsons.databases.db_sync.DBSync
   :inherited-members:
   :members:
