#########
Databases
#########

Overview
========

Parsons offers support for a variety of popular SQL database dialects.
The functionality is focused on the ability to query and upload data to SQL databases.
Each database class also includes the ability to infer datatypes and
data schemas from a Parsons table and automatically create new tables.

Similar to other classes in Parsons, the query methods for databases all return :ref:`Table`,
which allow them to be easily converted to other data types.

There is also support for synchronization of tables between databases as part of the
:ref:`framework/dbsync:Database Sync` framework.

.. toctree::
   :name: databases

   bigquery
   mysql
   postgres
   redshift
   sqlite
   database_connector
