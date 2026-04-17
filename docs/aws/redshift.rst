########
Redshift
########

Overview
========

The :class:`~parsons.databases.redshift.redshift.Redshift` class allows you to interact with an
`Amazon Redshift <https://aws.amazon.com/redshift/>`__ relational database.
The connector utilizes the `psycopg2 <https://pypi.org/project/psycopg2/>`__ Python package under the hood.
The core methods focus on input, output and querying of the database.

In addition to the core API integration provided by the :class:`~parsons.databases.redshift.redshift.Redshift` class,
Parsons also includes utility functions for managing schemas and tables.
See :ref:`aws/redshift:Table and View API` and :ref:`aws/redshift:Schema API` for more information.

.. admonition:: S3 Credentials

   Redshift only allows data to be copied to the database via S3. As such, the the :meth:`~parsons.databases.redshift.redshift.Redshift.copy`
   and :meth:`~parsons.databases.redshift.redshift.Redshift.copy_s3` methods require S3 credentials and write access on an S3 Bucket,
   which will be used for storing data en route to Redshift. For more information about AWS Redshift authorization,
   see the `API documentation <https://docs.aws.amazon.com/redshift/latest/dg/copy-parameters-authorization.html>`__.

.. admonition:: Whitelisting

   Remember to ensure that the IP address from which you are connecting has been whitelisted.

Quickstart
==========

Redshift API credentials can either be passed as environmental variables (``REDSHIFT_USERNAME``, ``REDSHIFT_PASSWORD``,
``REDSHIFT_HOST``, ``REDSHIFT_DB``, and ``REDSHIFT_PORT``) or as keyword arguments. Methods that use COPY require an
`access key ID and a secret access key <https://docs.aws.amazon.com/redshift/latest/dg/copy-parameters-authorization.html>`__,
which can also be passed as environmental variables (``aws_access_key_id`` and ``aws_secret_access_key``)
or keyword arguments.

.. code-block:: python
   :caption: Pass credentials as environmental variables

   from parsons import Redshift
   rs = Redshift()

.. code-block:: python
   :caption: Pass credentials as keyword arguments
   :emphasize-lines: 2-8

   from parsons import Redshift
   rs = Redshift(
      username='my_username',
      password='my_password',
      host='my_host',
      db='my_db',
      port='5439',
   )

.. code-block:: python
   :caption: Query the Database

   table = rs.query('select * from tmc_scratch.test_data')

.. code-block:: python
   :caption: Copy a Parsons Table to the Database

   table = rs.copy(tbl, 'tmc_scratch.test_table', if_exists='drop')

All of the standard COPY options can be passed as kwargs. See the :meth:`~parsons.databases.redshift.redshift.Redshift.copy` method for all
options.

Core API
--------

.. autoclass:: parsons.databases.redshift.redshift.Redshift
   :inherited-members:
   :members:

Table and View API
------------------

Table and view utilities are a series of helper methods, all built off of commonly
used SQL queries run against the Redshift database.

.. autoclass:: parsons.databases.redshift.rs_table_utilities.RedshiftTableUtilities
   :inherited-members:
   :members:

Schema API
----------

Schema utilities are a series of helper methods, all built off of commonly
used SQL queries run against the Redshift database.

.. autoclass:: parsons.databases.redshift.rs_schema.RedshiftSchema
   :inherited-members:
   :members:
