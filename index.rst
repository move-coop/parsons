.. Parsons documentation master file, created by
   sphinx-quickstart on Sat Sep  8 14:41:56 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

About
=====

Parsons, named after `Lucy Parsons <https://en.wikipedia.org/wiki/Lucy_Parsons>`_, is a Python package that contains a growing list of connectors and integrations to move data between various tools. Parsons is focused on integrations and connectors for tools utilized by the progressive community.

Parsons was built out of a belief that progressive organizations spend far too much time building the same integrations, over and over and over again, while they should be engaged in more important and impactful work. It
was built and is maintained by The Movement Cooperative.

The Movement Cooperative
========================
The Movement Cooperative is a member led organization focused on providing data, tools and strategic support for the progressive community. Our mission is to break down technological barriers for organizations that fight for social justice.

License and Usage
=================
Usage of Parsons is governed by the `TMC Parsons License <https://github.com/move-coop/parsons/blob/master/LICENSE.md>`_, which allows for unlimited non-commercial usage, provided that individuals and organizations adhere to our broad values statement.

Design Goals
============
The goal of Parsons is to make the movement of data between systems as easy and straightforward as possible. Simply put, we seek to reduce the lines of code that are written by the progressive community. Not only is this a waste of time, but we rarely have the capacity and resources to fully unittest our scripts.

.. image:: /_static/parsons_diagram.png

Parsons seeks to be flexible from a data ingestion and output perspective, while providing ETL tools that recognize that our data is **always** messy. Central to this concept is the :ref:`parsons-table` the table-like object that most methods return.

QuickStart
==========


.. code-block:: python

  # VAN - Download activist codes to a CSV

  from parsons import VAN
  van = VAN(db='MyVoters')
  ac = van.get_activist_codes()
  ac.to_csv('my_activist_codes.csv')

  # Redshift - Create a table from a CSV

  from parsons import Table
  tbl = Table.from_csv('my_table.csv')
  tbl.to_redshift('my_schema.my_table')

  # Redshift - Export from a query to CSV

  from parsons import Redshift
  sql = 'select * from my_schema.my_table'
  rs = Redshift()
  tbl = rs.query(sql)
  tbl.to_csv('my_table.csv')

  # Upload a file to S3

  from parsons import S3
  s3 = S3()
  s3.put_file('my_bucket','my_table.csv')

  # TargetSmart - Append data to a record

  from parsons import TargetSmart
  ts = TargetSmart(api_key='MY_KEY')
  record = ts.data_enhance(231231231, state='DC')

Sources
=======
* Documentation: `<https://move-coop.github.io/parsons/html/index.html>`_
* Source Code: `<https://github.com/move-coop/parsons>`_

Installation
============
You can install the most recent release by running: ``pip install parsons``

Logging
=======
Parsons uses the `native python logging system <https://docs.python.org/3/howto/logging.html>`_. By default, log output will go to the console and look like:

.. code-block:: none

    parsons.modulename LOGLEVEL the specific log message

In your scripts that use Parsons, if you want to override the default Parsons logging behavior, just grab the "parsons" logger and tweak it:

.. code-block:: python

   import logging
   parsons_logger = logging.getLogger('parsons')
   # parsons_logger.setLevel('DEBUG')
   # parsons_logger.addHandler(...)
   # parsons_logger.setFormatter(...)

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. toctree::
   :maxdepth: 1
   :caption: Integrations
   :name: integrations

   action_kit
   airtable
   civis
   copper
   crowdtangle
   databases
   facebook_ads
   google_sheets
   google_cloud
   hustle
   mobilize_america
   ngpvan
   p2a
   redshift
   s3
   salesforce
   sftp
   ts
   twilio
   turbovote

.. toctree::
   :maxdepth: 1
   :caption: Enhancements
   :name: enhancements

   google_civic
   census_geocoder

.. toctree::
   :maxdepth: 1
   :caption: Framework
   :name: framework

   table
   notifications
