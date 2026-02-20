PDI
===

********
Overview
********

PDI is a political data provider that is primarily active in California. This class
allows you to interact with the `PDI API <https://api.bluevote.com/docs/index#>`_ .

This Parsons connector provides methods to fetch lists of acquisition types, flag IDs,
questions, universes, and flags given start and end dates.

.. note::

  Authentication
    A user name, password, and API token are required to instantiate the ``PDI`` class.
    To obtain log in credentials, request a PDI API account from ``support@politicaldata.com``.
    The administrative process usually takes a couple of hours.

**********
Quickstart
**********

To instantiate the PDI class, you can either store your PDI API username, password,
and API token as environmental variables (``PDI_USERNAME``, ``PDI_PASSWORD``, and
``PDI_API_TOKEN``, respectively) or pass them in as arguments:

.. code-block:: python

   from parsons import PDI

   # First approach: Use API credentials via environmental variables
   pdi = PDI()

   # Second approach: Pass API credentials as arguments
   pdi = PDI(username='my_username', password='my_password', api_token='my_token')

   # Get all contacts (flag IDs) available from PDI
   pdi.get_flag_ids()

   # Get all flags since the beginning of 2020
   pdi.get_flags(start_date='2020-01-01')

*********
PDI Class
*********

.. autoclass:: parsons.pdi.pdi.PDI
   :inherited-members:
   :members:
   