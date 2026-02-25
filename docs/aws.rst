Amazon Web Services
===================

Parsons provides utility functions and/or connectors for three different `AWS services <https://aws.amazon.com/>`_.

* :ref:`Lambda <aws_lambda>`: AWS's `serverless computing platform <https://aws.amazon.com/lambda/>`_
* :ref:`S3 <aws_s3>`: AWS's `object storage service <https://aws.amazon.com/s3/>`_
* :ref:`Redshift <redshift>`: AWS's `data warehousing service <https://aws.amazon.com/redshift/>`_, with two additional classes providing utility functions.

  * :ref:`redshift_table_and_view_api`: Methods for managing tables and views
  * :ref:`redshift_schema_api`: Methods for managing schema

See the documentation for each service for more details.

******
Lambda
******

.. _aws_lambda:

========
Overview
========

Parsons' ``distribute_task`` function allows you to distribute process rows of a table across multiple
`AWS Lambda <https://aws.amazon.com/lambda/>`_ invocations.

If you are running the processing of a table inside AWS Lambda, then you are limited by how many rows can be processed
within the Lambda's time limit (at time-of-writing, maximum 15min).

Based on experience and some napkin math, with the same data that would allow 1000 rows to be processed inside a single
AWS Lambda instance, this method allows 10 MILLION rows to be processed.

Rather than converting the table to SQS or other options, the fastest way is to upload the table to S3, and then invoke
multiple Lambda sub-invocations, each of which can be sent a byte-range of the data in the S3 CSV file for which to process.

Using this method requires some setup. You have three tasks:

#. Define the function to process rows, the first argument, must take your table's data (though only a subset of rows will be passed) (e.g. ``def task_for_distribution(table, **kwargs):``)
#. Where you would have run ``task_for_distribution(my_table, **kwargs)`` instead call ``distribute_task(my_table, task_for_distribution, func_kwargs=kwargs)`` (either setting env var S3_TEMP_BUCKET or passing a ``bucket=`` parameter)
#. Setup your Lambda handler to include :py:meth:`parsons.aws.event_command` (or run and deploy your lambda with `Zappa <https://github.com/Miserlou/Zappa>`_)

To test locally, include the argument ``storage="local"``, which will test the ``distribute_task`` function, but run the task sequentially and in local memory.

==========
QuickStart
==========

A minimalistic example Lambda handler might look something like this:

.. code-block:: python

   from parsons.aws import event_command, distribute_task

   def process_table(table, foo, bar=None):
       for row in table:
           do_sloooooow_thing(row, foo, bar)

   def handler(event, context):
       ## ADD THESE TWO LINES TO TOP OF HANDLER:
       if event_command(event, context):
           return
       table = FakeDatasource.load_to_table(username='123', password='abc')
       # table is so big that running
       #   process_table(table, foo=789, bar='baz') would timeout
       # so instead we:
       distribute_task(table, process_table,
                       bucket='my-temp-s3-bucket',
                       func_kwargs={'foo': 789, 'bar': 'baz'})

===
API
===

.. autofunction:: parsons.aws.lambda_distribute.distribute_task

.. autofunction:: parsons.aws.aws_async.event_command

***
S3
***

.. _aws_s3:

========
Overview
========

The ``S3`` class allows interaction with Amazon Web Service's `object storage service <https://aws.amazon.com/s3/>`_
to store and access data objects. It is a wrapper around the AWS SDK `boto3 <https://boto3.amazonaws.com/v1/documentation/api/latest/index.html>`_.
It provides methods to upload and download files from S3 as well as manipulate buckets.

.. note::

  Authentication
    Access to S3 is controlled through AWS Identity and Access Management (IAM) users in the `AWS Managerment Console <https://aws.amazon.com/console/>`_ .
    Users can be granted granular access to AWS resources, including S3. IAM users are provisioned keys, which are required to access the S3 class.

==========
QuickStart
==========

S3 credentials can be passed as environmental variables (``AWS_ACCESS_KEY_ID`` and ``AWS_SECRET_ACCESS_KEY``),
stored in an AWS CLI file ``~/.aws/credentials``, or passed as keyword arguments.

.. code-block:: python

   from parsons import S3

   # First approach: Pass API credentials via environmental variables or an AWS CLI file
   s3 = S3()

   # Second approach: Pass API credentials as arguments
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

.. autoclass:: parsons.aws.s3.S3
   :inherited-members:
   :members:

=====================
Temporary Credentials
=====================

The S3 API supports creating temporary credentials for one-off operations, such as pushing a file to a particular key in a particular bucket.
For example, the Mapbox API allows you to request temporary credentials that grant you access to a bucket where you can upload map data.
When S3 returns a set of temporary credentials it also returns a session token that needs to be included with the standard credentials for
them to be accepted. The ``S3`` class can be passed a session token as an environmental variable (``AWS_SESSION_TOKEN``) or as a keyword argument.

.. code-block:: python

   from parsons import S3

   # First approach: Pass session token via AWS_SESSION_TOKEN environmental variable
   s3 = S3()

   # Second approach: Pass session token as an argument
   creds = request_temporary_credentials()
   s3 = S3(aws_access_key_id=creds['id'], aws_secret_access_key=creds['key'],
           aws_session_token=creds['token'])

********
Redshift
********

.. _redshift:

========
Overview
========

The ``Redshift`` class allows you to interact with an `Amazon Redshift <https://aws.amazon.com/redshift/>`_ relational database.
The connector utilizes the `psycopg2 <https://pypi.org/project/psycopg2/>`_ Python package under the hood. The core methods
focus on input, output and querying of the database.

In addition to the core API integration provided by the ``Redshift`` class, Parsons also includes utility functions for
managing schemas and tables. See :ref:`redshift_table_and_view_api` and :ref:`redshift_schema_api` for more information.

.. note::

   S3 Credentials
      Redshift only allows data to be copied to the database via S3. As such, the the :meth:`copy` and :meth:`copy_s3`
      methods require S3 credentials and write access on an S3 Bucket, which will be used for storing data en route to
      Redshift. See the `API documentation <https://docs.aws.amazon.com/redshift/latest/dg/copy-parameters-authorization.html>`_
      for more information about AWS Redshift authorization.
   Whitelisting
      Remember to ensure that the IP address from which you are connecting has been whitelisted.

==========
Quickstart
==========

Redshift API credentials can either be passed as environmental variables (``REDSHIFT_USERNAME``, ``REDSHIFT_PASSWORD``,
``REDSHIFT_HOST``, ``REDSHIFT_DB``, and ``REDSHIFT_PORT``) or as keyword arguments. Methods that use COPY require an
`access key ID and a secret access key <https://docs.aws.amazon.com/redshift/latest/dg/copy-parameters-authorization.html>`_,
which can also be passed as environmental variables (``aws_access_key_id`` and ``aws_secret_access_key``)
or keyword arguments.

.. code-block:: python

  from parsons import Redshift

  # Pass credentials as environmental variables
  rs = Redshift()

  # Pass credentials as keyword arguments
  rs = Redshift(username='my_username', password='my_password', host='my_host',
                db='my_db', port='5439')

  # Query the Database
  table = rs.query('select * from tmc_scratch.test_data')

  # Copy a Parsons Table to the Database
  table = rs.copy(tbl, 'tmc_scratch.test_table', if_exists='drop')

All of the standard COPY options can be passed as kwargs. See the :meth:`copy` method for all
options.

========
Core API
========

.. autoclass:: parsons.databases.redshift.Redshift
   :inherited-members:
   :members:

.. _redshift_table_and_view_api:

==================
Table and View API
==================

Table and view utilities are a series of helper methods, all built off of commonly
used SQL queries run against the Redshift database.

.. autoclass:: parsons.databases.redshift.rs_table_utilities::RedshiftTableUtilities
   :inherited-members:
   :members:

.. _redshift_schema_api:

==========
Schema API
==========

Schema utilities are a series of helper methods, all built off of commonly
used SQL queries run against the Redshift database.

.. autoclass:: parsons.databases.redshift.rs_schema.RedshiftSchema
   :inherited-members:
   :members:
   