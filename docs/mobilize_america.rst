Mobilize America
================

********
Overview
********

`Mobilize America <https://www.mobilizeamerica.io/>`_ is an activist signup tool used by progressive organizations.
This class provides several methods for fetching organizations, people, and events from their
`API <https://github.com/mobilizeamerica/api#mobilizeamerica-api>`_, which is currently in alpha development.

.. note::

    Authentication
      Some methods in the ``MobilizeAmerica`` class require an API Key furnished by Mobilize America (private methods),
      while others do not (public methods). Each method in this class contains a note indicating whether it is public
      or private. For more information, see the `API documentation <https://github.com/mobilizeamerica/api#authentication>`_.

**********
Quickstart
**********

If you instantiate ``MobilizeAmerica`` without an API Key, you can only use public methods:

.. code-block:: python

   from parsons import MobilizeAmerica

   # Instantiate class without API key
   ma = MobilizeAmerica()

   # Use public method to get all organizations
   ma.get_organizations()


In order to use private methods, you must provide an API key either by setting the environmental
variable ``MOBILIZE_AMERICA_API_KEY`` or by passing an ``api_key`` argument as shown below:

.. code-block:: python

   # Instantiate class without API key as argument
   ma = MobilizeAmerica(api_key='my_api_key')

   # Use private method to get all people
   ma.get_people()

***
API
***

.. autoclass:: parsons.mobilize_america.ma.MobilizeAmerica
   :inherited-members:
   :members:
   