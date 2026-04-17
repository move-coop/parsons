####
PDI
####

Overview
========

PDI is a political data provider that is primarily active in California. This class
allows you to interact with the `PDI API <https://api.bluevote.com/docs/index#>`__ .

This Parsons connector provides methods to fetch lists of acquisition types, flag IDs,
questions, universes, and flags given start and end dates.

.. admonition:: Authentication

   A user name, password, and API token are required to instantiate the :class:`~parsons.pdi.pdi.PDI` class.
   To obtain log in credentials, request a PDI API account from ``support@politicaldata.com``.
   The administrative process usually takes a couple of hours.

Quickstart
==========

To instantiate the :class:`~parsons.pdi.pdi.PDI` class, you can either store your PDI API username, password,
and API token as environmental variables (``PDI_USERNAME``, ``PDI_PASSWORD``, and
``PDI_API_TOKEN``, respectively) or pass them in as arguments.

.. code-block:: python
   :caption: Use API credentials via environmental variables

   from parsons import PDI
   pdi = PDI()

.. code-block:: python
   :caption: Pass API credentials as arguments

   from parsons import PDI
   pdi = PDI(username='my_username', password='my_password', api_token='my_token')

.. code-block:: python
   :caption: Get all contacts (flag IDs) available from PDI

   pdi.get_flag_ids()

.. code-block:: python
   :caption: Get all flags since the beginning of 2020

   pdi.get_flags(start_date='2020-01-01')

API
====

.. autoclass:: parsons.pdi.pdi.PDI
   :inherited-members:
   :members:
