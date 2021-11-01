Airtable
========

********
Overview
********

The Airtable class allows you to interact with an `Airtable <https://airtable.com/>`_. base. In order to use this class
you must generate an Airtable API Key which can be found in your Airtable `account settings <https://airtable.com/account>`_.

.. note:: 
   Finding The Base Key
   	The easiest place to find the ``base_key`` for the base that you wish to interact with is via the Airtable API documentation.
    * Go to the `Airtable API Base List <https://airtable.com/api>`_ and select the base.
    * The url of the resulting page will contain the ``base_key``.
    * Example: ``https://airtable.com/[BASE_KEY]/api/docs#curl/introduction``

**********
QuickStart
**********
To instantiate the Airtable class, you can either store your Airtable API
``AIRTABLE_API_KEY`` as an environmental variable or pass in your api key
as an argument. You also need to pass in the base key and table name.

.. code-block:: python

   from parsons import Airtable

   # First approach: Use API credentials via environmental variables and pass
   # the base key and the table as arguments.
   at = Airtable(base_key, 'table01')

   # Second approach: Pass API credentials, base key and table name as arguments.
   at = Airtable(base_key, 'table01', api_key='MYFAKEKEY')


You can then call various endpoints:

.. code-block:: python

    # Get records from a base
    at.get_records(fields=['id', 'fn', 'ln'])

    # Get a single record from a base
    at.get_record(1233)

    # Insert records
    tbl.from_csv('my_new_records')
    at.insert_records(tbl)


***
API
***

.. autoclass :: parsons.Airtable
   :inherited-members:
