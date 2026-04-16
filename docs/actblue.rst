#######
ActBlue
#######

Overview
========

The :class:`~actblue.ActBlue` class allows you to interact with the ActBlue CSV API. Users of this Parsons integration can generate CSVs and
manipulate entity CSV data within the Parsons table format.

.. admonition:: Authentication

   In order to use this class you must generate and use a Client UUID and Client Secret set of credentials. Instructions for
   generating the set of keys can be found within the `CSV API documentation <https://secure.actblue.com/docs/csv_api#authentication>`_.

Quickstart
==========

To instantiate the :class:`~actblue.ActBlue` class, you can either store your ``ACTBLUE_CLIENT_UUID`` and ``ACTBLUE_CLIENT_SECRET`` keys as environment
variables or pass them in as arguments:

.. code-block:: python

   from parsons import ActBlue

   # First approach: Use API key environment variables

   # In bash, set your environment variables like so:
   # export ACTBLUE_CLIENT_UUID='MY_UUID'
   # export ACTBLUE_CLIENT_SECRET='MY_SECRET'
   actblue = ActBlue()

   # Second approach: Pass API keys as arguments
   actblue = ActBlue(actblue_client_uuid='MY_UUID', actblue_client_secret='MY_SECRET')

You can then make a request to generate a CSV and save its data to a Parsons table using the main helper method, :meth:`~ActBlue.get_contributions`:

.. code-block:: python
   :caption: Create Parsons table with entity CSV data for the month of January 2020

   parsons_table = actblue.get_contributions(csv_type='paid_contributions', date_range_start='2020-01-01', date_range_end='2020-02-01')

API
====

.. autoclass:: parsons.actblue.actblue.ActBlue
   :inherited-members:
   :members:
