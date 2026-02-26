US Census Geocoder
==================

********
Overview
********

The US Census Geocoder leverages the US Census Geocoding service for single record and batch geocoding. The
service enforces no limits and is free to US. More information can be found at the `US Census <https://geocoding.geo.census.gov/>`_
website. For multiple records, it is recommended that you use the :meth:`CensusGeocoder.geocode_address_batch` method.

***
API
***

.. autoclass:: parsons.geocode.census_geocoder.CensusGeocoder
   :inherited-members:
   :members:
   