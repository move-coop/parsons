Quickbooks Time
===============

********
Overview
********

Quickbooks Time is a time tracking and scheduling tool that integrates with Quickbooks Online.
This integration allows you to pull time tracking data from Quickbooks Time into Parsons.

.. note::

  Authentication
    You need to generate a Quickbooks Time API token to use this integration. See the
    `Quickbooks Time API documentation <https://tsheetsteam.github.io/api_docs/#getting-started>`_

==========
Quickstart
==========

In order to instantiate the Quickbooks Time class, you need to pass in your Quickbooks Time API token
as an environment variable "QB_AUTH_TOKEN" or pass it in as a parameter called token="your_token".

**Example 1**

.. code-block:: python

  from parsons import QuickBooksTime

  # instantiate the quickbooks class
  qb = QuickBooksTime(token="your_token")

  #Timesheets Table
  timesheets_tbl = qb.get_timesheets(start_date="2024-01-01")

This example shows how to get timesheets for a given date range.

***
API
***

.. autoclass:: parsons.quickbooks.quickbookstime.QuickBooksTime
   :inherited-members:
   :members:
   