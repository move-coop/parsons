Databases
=========

***************
Google BigQuery
***************

See :doc:`google_cloud` for documentation.

*****
MySQL
*****

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

See :doc:`redshift` section for documentation.

*************
Database Sync
*************

Sync tables between two databases with just a few lines of code. Currently supported
database types are:

* Postgres
* Redshift

========
Examples
========

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