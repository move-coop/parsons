##################
US Census Geocoder
##################

.. admonition:: Required Extra

   To use the CensusGeocoder connector, you will need to install parsons with the geocode extra.
   To do this, you will need to install it with ``pip install parsons[geocode]`` or ``pip install parsons[all]``.

Overview
========

The US Census Geocoder leverages the US Census Geocoding service for single record and batch geocoding.
The service enforces no limits and is free to US. More information can
be found at the `US Census <https://geocoding.geo.census.gov/geocoder/>`__
website. For multiple records, it is recommended that you use the
:meth:`~parsons.geocode.census_geocoder.CensusGeocoder.geocode_address_batch` method.

API
====

.. autoclass:: parsons.geocode.census_geocoder.CensusGeocoder
   :inherited-members:
   :members:
