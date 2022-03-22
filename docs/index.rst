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
Usage of Parsons is governed by a `modified Apache License with author attribution statement <https://github.com/move-coop/parsons/blob/master/LICENSE.md>`_.

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

Virtual Environments
====================

Normally, tools like `pip` install Python libraries directly to your system. Python scripts
or libraries look for their dependencies in your system. This can cause problems when you
have two scripts/libraries installed that require different versions of the same library.

To solve this problem, we recommend you use *virtual environments* to install Parsons.
Virtual environments allow you to keep different sets of installed libraries so that you can
use different versions of the same libraries for different purposes.

Windows
------------------------------

`Source <https://pypi.org/project/virtualenvwrapper-win/>`_

1. Install virtualenvwrappers from source::

      git clone git://github.com/davidmarble/virtualenvwrapper-win.git
      cd virtualenvwrapper-win
      python setup.py install

2. Find the ``Scripts\`` directory for your Python installation, such as ``C:\Users\<User>\AppData\Local\Programs\Python\Python37\Scripts\``.

3. Add the ``Scripts\`` directory to your Path.

4. To create a virtual environment for Parsons, execute: ``mkvirtualenv parsons``

5. To use this virtual environment, execute: ``workon parsons``


Linux / Mac OS
------------------------------

<Coming Soon>

Installation
============

There are two ways to install Parsons: Using pip and from source. Use pip if you just want to install Parsons and start using it. Install from source if you might want to patch Parsons to customize its behavior.

Installing Parsons (pip)
-----------------------------

1. Make sure you're in your parsons virtual environment: ``workon parsons``.

2. Execute: ``pip install parsons``

Installing Parsons from Source
----------------------------------


1. Make sure you're in your parsons virtual environment: ``workon parsons``.

2. Execute these commands::

      git clone https://github.com/move-coop/parsons.git
      pip install -r requirements.txt
      python setup.py install


3. To update your installation, pull the most recent branch from the Parsons GitHub repo (``git pull origin master``) and rerun ``python setup.py install``.

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

Minimizing Resource Utilization
===============================

A primary goal of Parsons is to make installing and using the library as easy as possible. Many
of the patterns and examples that we document are meant to show how easy it can be to use Parsons,
but sometimes these patterns trade accessibility for performance.

In environments where efficiency is important, we recommend users take the following steps to
minimize resource utilization:

  1. Don't import classes from the root Parsons package
  2. Install only the dependencies you need

*** Don't import from the root Parsons package ***

Throughout the Parsons documentation, users are encouraged to load Parsons classes like so:

```python
from parsons import Table
```

In order to support this pattern, Parsons imports all of its classes into the root `parsons`
package. Due to how Python loads modules and packages, importing even one Parsons class results
in ALL of them being loaded. In order to avoid the resource consumption associated with loading all
of Parsons, we have created a mechanism to skip loading of call of the Parsons classes.

If you set `PARSONS_SKIP_IMPORT_ALL` in your environment, Parsons will not import all of its classes
into the root `parsons` package. Setting this environment variable means you will **NOT** be able to
import using the `from parsons import X` pattern. Instead, you will need to import directly from the
package where a class is defined (e.g. `from parsons.etl import Table`).

If you use the `PARSONS_SKIP_IMPORT_ALL` and import directly from the appropriate sub-package,
you will only load the classes that you need and will not consume extra resources. Using this
method, you may see as much as an 8x decrease in memory usage for Parsons.

*** Install only the dependencies you need ***

Since Parsons needs to talk to so many different API's, it has a number of dependencies on other
Python libraries. It may be preferable to only install those external dependencies that you will
use.

For example, if you are running on Google Cloud, you might not need to use any of Parsons' AWS
connectors. If you don't use any of Parsons' AWS connectors, then you won't need to install the
Amazon Boto3 library that Parsons uses to access the Amazon APIs.

By default, installing Parsons will install all of its external dependencies. You can prevent
these dependencies from being installed with Parsons by passing the `--no-deps` flag to pip
when you install Parsons.

```
> pip install --no-deps parsons
```

Once you have Parsons installed without these external dependencies, you can then install
the libraries as you need them. You can use the requirements.txt as a reference to figure
out which version you need. At a minimum you will need to install the following libraries
for Parsons to work at all:

* petl

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. toctree::
   :maxdepth: 1
   :caption: Integrations
   :name: integrations

   actblue
   action_kit
   action_network
   airtable
   alchemer
   aws
   azure
   bill_com
   bloomerang
   bluelink
   box
   braintree
   civis
   controlshift
   copper
   crowdtangle
   databases
   facebook_ads
   freshdesk
   github
   google
   hustle
   mailchimp
   mobilize_america
   newmode
   ngpvan
   pdi
   p2a
   quickbase
   redash
   rockthevote
   salesforce
   sftp
   shopify
   sisense
   targetsmart
   turbovote
   twilio
   zoom

.. toctree::
   :maxdepth: 1
   :caption: Enhancements
   :name: enhancements

   census_geocoder

.. toctree::
   :maxdepth: 1
   :caption: Framework
   :name: framework

   dbsync
   table
   notifications
   utilities

.. toctree::
   :maxdepth: 1
   :caption: Contributor Documentation
   :name: contrib_docs

   contributing
   build_a_connector
   write_tests

.. toctree::
   :maxdepth: 1
   :caption: Use Cases and Sample Scripts
   :name: use_cases_and_sample_scripts

   use_cases/contribute_use_cases
   use_cases/civis_job_status_slack_alert
   use_cases/mysql_to_googlesheets

.. toctree::
   :maxdepth: 1
   :caption: Training Guides
   :name: training_guides

   training_guides/getting_set_up
