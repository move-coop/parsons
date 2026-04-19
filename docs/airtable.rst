########
Airtable
########

Overview
========

The :class:`~parsons.airtable.airtable.Airtable` class allows you to interact with an `Airtable <https://www.airtable.com/>`__ base. In order to use this class
you must generate an Airtable personal access token which can be found in your Airtable `settings <https://www.airtable.com/create/tokens>`__.

.. admonition:: Finding The Base Key

   The easiest place to find the ``base_key`` for the base that you wish to interact with is via the Airtable API documentation.
   * Go to the `Airtable API Documentation`_ and select the base.
   * The url of the resulting page will contain the ``base_key``.
   * Example: ``https://www.airtable.com/[BASE_KEY]/api/docs``

Quickstart
==========

To instantiate the :class:`~parsons.airtable.airtable.Airtable` class, you can either store your Airtable personal access token
``AIRTABLE_PERSONAL_ACCESS_TOKEN`` as an environmental variable or pass in your personal access token
as an argument. You also need to pass in the base key and table name.

.. code-block:: python
   :caption: Use personal access token via environmental variable and pass the base key and the table as arguments

   from parsons import Airtable
   at = Airtable(base_key, 'table01')

.. code-block:: python
   :caption: Pass personal access token, base key and table name as arguments

   from parsons import Airtable
   at = Airtable(base_key, 'table01', personal_access_token='MYFAKETOKEN')

You can then call various endpoints:

.. code-block:: python
   :caption: Get records from a base

   at.get_records(fields=['id', 'fn', 'ln'])

.. code-block:: python
   :caption: Get a single record from a base

   at.get_record(1233)

.. code-block:: python
   :caption: Insert records

   tbl.from_csv('my_new_records')
   at.insert_records(tbl)

API
====

.. autoclass:: parsons.airtable.airtable.Airtable
   :inherited-members:
   :members:

.. _Airtable API Documentation: https://airtable.com/developers/web/api/introduction
