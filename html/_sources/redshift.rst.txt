Redshift
========

********
Overview
********

The Redshift class allows you to interact with an `Amazon Redshift <https://aws.amazon.com/redshift/>`_ relational batabase. The Redshift Connector utilizes the ``psycopg2`` python package to connect to the database.

.. note::
   S3 Credentials
      Redshift only allows data to be copied to the database via S3. As such, you need to include AWS
      S3 credentials in your copy methods or, better yet, store them as environmental variables.
      In addition, you'll need to provide the env var ``S3_TEMP_BUCKET``, which is the bucket name used
      for storing data en route to Redshift.
   Whitelisting
	Remember to ensure that the IP address from which you are connecting has been whitelisted.

**********
Quickstart
**********

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

**************
Redshift Class
**************

.. autoclass :: parsons.Redshift
   :inherited-members: