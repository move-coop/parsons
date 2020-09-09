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

S3 is Amazon Web Service's object storage service that allows users to store and access data objects. The Parson's class is a high level wrapper of the AWS SDK `boto3 <https://boto3.amazonaws.com/v1/documentation/api/latest/index.html>`_. It allows users to upload and download files from S3 as well as manipulate buckets.

.. note::
  Authentication
    Access to S3 is controlled through AWS Identity and Access Management (IAM) users in the `AWS Managerment Console <https://aws.amazon.com/console/>`_ . Users can be granted granular access to AWS resources, including S3. IAM users are provisioned keys, which are required to access the S3 class. 

==========
QuickStart
==========

Instantiate class with credentials.

.. code-block:: python

   from parsons import S3

   # First approach: Use API credentials via environmental variables
   s3 = S3()

   # Second approach: Pass API credentials as arguments
   s3 = S3(aws_access_key_id='MY_KEY', aws_secret_access_key='MY_SECRET')

   # Third approach: Use credentials stored in AWS CLI file ~/.aws/credentials
   s3 = S3()

You can then call various endpoints:

.. code-block:: python
  
  from parsons import S3, Table

  s3 = S3(aws_access_key_id='MY_KEY', aws_secret_access_key='MY_SECRET')

  # Put an arbitrary file in an S3 bucket
  with open('winning_formula.csv') as w:
    s3.put_file('my_bucket', 'winning.csv, w)

  # Put a Parsons Table as a CSV using convenience method.
  tbl = Table.from_csv('winning_formula.csv')
  tbl.to_s3_csv('my_bucket', 'winning.csv')

  # Download a csv file and convert to a table
  f = s3.get_file('my_bucket', 'my_dir/my_file.csv')
  tbl = Table(f)

  # List buckets that you have access to
  s3.list_buckets()

  # List the keys in a bucket
  s3.list_keys('my_bucket')

===
API
===

.. autoclass :: parsons.S3
   :inherited-members:
   :members:

********
Redshift
********

.. _redshift:

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

