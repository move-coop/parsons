:orphan:

TargetSmart Developer API
=========================

`TargetSmart <https://targetsmart.com/>`_ provides access to voter and consumer data for the progressive community.

Overview
--------

The ``TargetSmartAPI`` class provides methods to consume the data services provided by the `TargetSmart Developer API <https://docs.targetsmart.com/developers/tsapis/v2/index.html>`_. Parsons provides the following methods as convenient wrappers for interacting with the corresponding TargetSmart HTTP services:

* ``data_enhance``: Quickly retrieve voter and consumer data enrichment fields from TargetSmart’s platform database for a previously identified individual.
* ``radius_search``: Search for individuals within a user specified geographic area defined by a radius centered around a latitude/longitude point.
* ``phone``: Enrich a list of phone numbers with TargetSmart data
* ``district``: Retrieve political district data using one of several lookup options
* ``voter_registration_check``: Search TargetSmart’s service database of registered voters, to check if a voter is registered at a given address.
* ``smartmatch``: Match CSV file records to TargetSmart's service database of voting age individuals. Multiple matching strategies are applied to find accurate matches and return enriched data. Read more about `SmartMatch <https://docs.targetsmart.com/my_tsmart/smartmatch/overview.html>`_, TargetSmart's list matching solution.

Some TargetSmart API services have not yet been implemented in Parsons. For more information, see the `API documentation <https://docs.targetsmart.com/developers/tsapis/v2/index.html>`_.


Authentication
..............

Log in to `My TargetSmart <https://my.targetsmart.com/>`_ to access authentication credentials. You will need an API key to use the ``TargetSmartAPI`` class.

.. note::

  Endpoint Access
    Access to endpoints is individually provisioned.
    If you encounter errors accessing an endpoint, please contact `TargetSmart Client Services <mailto:support@targetsmart.com>`_ to verify that your API key has been provisioned access.


Data Enrichment
...............

Most TargetSmart API services append a set of enrichment data fields as part of
a matching or search request. The presence of these fields are provisioned by
the TargetSmart Client Services team. Please contact `TargetSmart Client
Services <mailto:support@targetsmart.com>`_ to learn more or request
adjustments.


Quickstart
==========

To instantiate ``TargetSmartAPI``, you can either store your API Key as the environmental variable
``TS_API_KEY``, or pass it in as an argument:

.. code-block:: python

   from parsons import TargetSmartAPI

   # First approach: Store API key as an environmental variable
   ts_api = TargetSmartAPI()

   # Second approach: Pass API key as an argument
   ts_api = TargetSmartAPI(api_key='my_api_key')

You can then call various methods that correspond to TargetSmart endpoints:

.. code-block:: python

   # Search for a person record using an email address
   ts_api.data_enhance(search_id='test@email.com', search_id_type='email')

   # Search for district information using an address
   ts_api.district(search_type='address', address='123 test st, Durham NC 27708')


API
===

.. autoclass:: parsons.targetsmart.targetsmart_api.TargetSmartAPI
   :inherited-members:
   :members:
   