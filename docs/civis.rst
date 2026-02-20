Civis
=====

********
Overview
********

The `Civis Platform <https://www.civisanalytics.com/civis-platform/>`_ is a cloud-based data science platform.
This Parsons connector utilizes the `Civis API Python client <https://civis-python.readthedocs.io/en/stable/user_guide.html>`_
to interact with the Civis Platform. It supports executing Civis SQL queries and writing Parsons Tables to a Civis
Redshift cluster.

.. note::

  Authentication
    The ``CivisClient`` class requires your Redshift database ID or name, and an API Key. To obtain an API Key, log in to
    Civis and follow the instructions for `Creating an API Key <https://civis.zendesk.com/hc/en-us/restricted?return_to=https%3A%2F%2Fcivis.zendesk.com%2Fhc%2Fen-us%2Farticles%2F216341583-Generating-an-API-Key>`_.

**********
Quickstart
**********

To instantiate the ``CivisClient`` class, you can either store your database identifier and API Key as
environmental variables (``CIVIS_DATABASE`` and ``CIVIS_API_KEY``) or pass them as keyword arguments.

.. code-block:: python

   from parsons import CivisClient

   # First approach: Authorize with environmental variables
   civis = CivisClient()

   # Second approach: Pass API credentials as arguments
   civis = CivisClient(db='my_db_name', api_key='my_api_key')

   # Execute a Civis query
   civis.query(sql="SELECT * FROM my_table")

***
API
***

.. autoclass:: parsons.civis.civisclient.CivisClient
   :inherited-members:
   :members:
   