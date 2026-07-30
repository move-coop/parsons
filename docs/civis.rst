#####
Civis
#####

Overview
========

The `Civis Platform <https://www.civisanalytics.com/platform/>`__ is a cloud-based data science platform.
This Parsons connector utilizes the `Civis API Python client <https://civis-python.readthedocs.io/en/stable/user_guide.html>`__
to interact with the Civis Platform. It supports executing Civis SQL queries and writing Parsons Tables to a Civis
Redshift cluster.

.. admonition:: Authentication

   The :class:`~parsons.civis.civisclient.CivisClient` class requires your Redshift database ID or name,
   and an API Key. To obtain an API Key, log in to Civis and follow the instructions for
   `Creating an API Key <https://support.civisanalytics.com/hc/en-us/articles/216341583-Generating-an-API-Key>`__.

Quickstart
==========

To instantiate the :class:`~parsons.civis.civisclient.CivisClient` class,
you can either store your database identifier and API Key as environmental variables
(``CIVIS_DATABASE`` and ``CIVIS_API_KEY``) or pass them as keyword arguments.

.. code-block:: python
   :caption: Authorize with environmental variables

   from parsons import CivisClient
   civis = CivisClient()

.. code-block:: python
   :caption: Pass API credentials as arguments

   from parsons import CivisClient
   civis = CivisClient(db='my_db_name', api_key='my_api_key')

.. code-block:: python
   :caption: Execute a Civis query

   civis.query(sql="SELECT * FROM my_table")

API
====

.. autoclass:: parsons.civis.civisclient.CivisClient
   :inherited-members:
   :members:
