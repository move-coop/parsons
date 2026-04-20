#########################
TargetSmart Developer API
#########################

`TargetSmart <https://targetsmart.com/>`__ provides access to voter and consumer data for the progressive community.

Overview
========

The :class:`~parsons.targetsmart.targetsmart_api.TargetSmartAPI` class provides methods to consume the data services provided by the
`TargetSmart Developer API <https://docs.targetsmart.com/developers/tsapis/v2/index.html>`__.
Parsons provides the following methods as convenient wrappers for interacting with the corresponding TargetSmart HTTP services:

* :meth:`~parsons.targetsmart.targetsmart_api.TargetSmartAPI.data_enhance`: Quickly retrieve voter and consumer data enrichment fields from TargetSmart’s platform database for a previously identified individual.
* :meth:`~parsons.targetsmart.targetsmart_api.TargetSmartAPI.radius_search`: Search for individuals within a user specified geographic area defined by a radius centered around a latitude/longitude point.
* :meth:`~parsons.targetsmart.targetsmart_api.TargetSmartAPI.phone`: Enrich a list of phone numbers with TargetSmart data
* :meth:`~parsons.targetsmart.targetsmart_api.TargetSmartAPI.district`: Retrieve political district data using one of several lookup options
* :meth:`~parsons.targetsmart.targetsmart_api.TargetSmartAPI.voter_registration_check`: Search TargetSmart’s service database of registered voters, to check if a voter is registered at a given address.
* :meth:`~parsons.targetsmart.targetsmart_api.TargetSmartAPI.smartmatch`: Match CSV file records to TargetSmart's service database of voting age individuals. Multiple matching strategies are applied to find accurate matches and return enriched data. Read more about `SmartMatch <https://docs.targetsmart.com/my_tsmart/smartmatch/overview.html>`_, TargetSmart's list matching solution.

Some TargetSmart API services have not yet been implemented in Parsons.
For more information, see the `API documentation <https://docs.targetsmart.com/developers/tsapis/v2/index.html>`__.

.. admonition:: Authentication

   Log in to `My TargetSmart <https://my.targetsmart.com/>`__ to access authentication credentials.
   You will need an API key to use the :class:`~parsons.targetsmart.targetsmart_api.TargetSmartAPI` class.

.. admonition:: Endpoint Access

   Access to endpoints is individually provisioned.
   If you encounter errors accessing an endpoint,
   please contact `TargetSmart Client Services <mailto:support@targetsmart.com>`__
   to verify that your API key has been provisioned access.

.. admonition:: Data Enrichment

   Most TargetSmart API services append a set of enrichment data fields as part of
   a matching or search request. The presence of these fields are provisioned by
   the TargetSmart Client Services team. Please contact `TargetSmart Client
   Services <mailto:support@targetsmart.com>`__ to learn more or request adjustments.

Quickstart
==========

To instantiate :class:`~parsons.targetsmart.targetsmart_api.TargetSmartAPI`, you can either store your API Key as the environmental variable
``TS_API_KEY``, or pass it in as an argument:

.. code-block:: python
   :caption: Store API key as an environmental variable

   from parsons import TargetSmartAPI
   ts_api = TargetSmartAPI()

.. code-block:: python
   :caption: Pass API key as an argument

   from parsons import TargetSmartAPI
   ts_api = TargetSmartAPI(api_key='my_api_key')

You can then call various methods that correspond to TargetSmart endpoints:

.. code-block:: python
   :caption: Search for a person record using an email address

   ts_api.data_enhance(search_id='test@email.com', search_id_type='email')

.. code-block:: python
   :caption: Search for district information using an address

   ts_api.district(search_type='address', address='123 test st, Durham NC 27708')

API
====

.. autoclass:: parsons.targetsmart.targetsmart_api.TargetSmartAPI
   :inherited-members:
   :members:
