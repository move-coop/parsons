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
    - Go to the `Airtable <https://airtable.com/api>`_ and select the base.
    - The url of the resulting page will contain the ``base_key``. 
    - E.g. ``https://airtable.com/[BASE_KEY]/api/docs#curl/introduction``

**************
Airtable Class
**************

.. autoclass :: parsons.Airtable
   :inherited-members:
