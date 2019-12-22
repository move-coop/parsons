Databases
=========

***************
Google BigQuery
***************

See :doc:`google_cloud` for documentation.

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

Sync tables between two databases with just a few lines of code.

========
Examples
========

**Full Sync Of Tables**
Copy all data from a source table to a destination table. 

.. code-block:: python

   # Create source and destination database objects
   source_rs = Redshift()
   destination_rs = Redshift()

   # Create db sync object and run sync.
   db_sync = DBSync(source_rs, destination_rs) # Create DBSync Object
   db_sync.table_sync_full('parsons.source_data', 'parsons.destination_data')

===
API
===

.. autoclass:: parsons.DBSync
   :inherited-members: