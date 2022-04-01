Amazon Web Services
===================

******
Lambda
******

===
API
===

.. autofunction :: parsons.aws.distribute_task
.. autofunction :: parsons.aws.event_command

***
S3
***

========
Overview
========

The S3 class heavily reliant on the ``boto3`` python package. It includes a suite of common methods that are commonly
used with S3.

===
API
===

.. autoclass :: parsons.S3
   :inherited-members:
   :members:

********
Redshift
********

========
Overview
========

The Redshift class allows you to interact with an `Amazon Redshift <https://aws.amazon.com/redshift/>`_ relational database. The Redshift Connector utilizes the ``psycopg2`` python package to connect to the database.

.. note::
   S3 Credentials
      Redshift only allows data to be copied to the database via S3. As such, the the :meth:`copy` and :meth:`copy_s3()`
      methods require S3 credentials and write access on an S3 Bucket, which will be used for storing data en route to
      Redshift.
   Whitelisting
	Remember to ensure that the IP address from which you are connecting has been whitelisted.

==========
Quickstart
==========

**Query the Database**

.. code-block:: python

  from parsons import Redshift
  rs = Redshift()
  table = rs.query('select * from tmc_scratch.test_data')

**Copy a Parsons Table to the Database**

.. code-block:: python

  from parsons import Redshift
  rs = Redshift()
  table = rs.copy(tbl, 'tmc_scratch.test_table', if_exists='drop')

All of the standard copy options can be passed as kwargs. See the :meth:`copy` method for all
options.

========
Core API
========
Redshift core methods focus on input, output and querying of the database.

.. autoclass :: parsons.Redshift

.. autofunction:: parsons.Redshift.connection

.. autofunction:: parsons.Redshift.query

.. autofunction:: parsons.Redshift.query_with_connection

.. autofunction:: parsons.Redshift.copy

.. autofunction:: parsons.Redshift.copy_s3

.. autofunction:: parsons.Redshift.unload

.. autofunction:: parsons.Redshift.upsert

.. autofunction:: parsons.Redshift.generate_manifest

.. autofunction:: parsons.Redshift.alter_table_column_type

==================
Table and View API
==================
Table and view utilities are a series of helper methods, all built off of commonly
used SQL queries run against the Redshift database.

.. autoclass :: parsons.databases.redshift.redshift.RedshiftTableUtilities
   :inherited-members:

==========
Schema API
==========
Schema utilities are a series of helper methods, all built off of commonly
used SQL queries run against the Redshift database.

.. autoclass :: parsons.databases.redshift.redshift.RedshiftSchema
   :inherited-members:

