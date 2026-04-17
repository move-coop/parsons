######
Census
######

Overview
========

Connects to the `Census API <https://www.census.gov/data/developers/guidance/api-user-guide.html>`__.
It has been tested with the ACS and Economic Survey endpoints.

.. admonition:: Authentication

   The API requires a key that you can get `here <https://www.census.gov/data/developers.html>`__ (click on the box that says "Request a KEY")

Quickstart
==========

To instantiate the Census class, either store your ``CENSUS_API_KEY`` as an environment
variable or pass it as an argument:

.. code-block:: python
   :caption: Use API key environment variables

   from parsons import Census
   census = ActBlue()

.. code-block:: python
   :caption: Pass API key as arguments

   from parsons import Census
   actblue = ActBlue(api_key = 'MY_CENSUS_KEY')

.. code-block:: python
   :caption: Pull the population of the US in 2019 from the ACS 1-year estimates.

   from parsons import Census
   # year, dataset_acronym, variables and location tell the API what data we want
   # for example, 'B01001_001E' is population and 'us:1' is the entire U.S.
   year = '2019'
   dataset_acronym = '/acs/acs1'
   variables = 'NAME,B01001_001E'
   location = 'us:1'

   # here's our connector
   census = Census(api_key=acs_key)

   # now pull data into a Parsons table
   t = census.get_census(year, dataset_acronym, variables, location)
   print(t)

.. code-block:: python
   :caption: Pull data on payroll by industry in Virginia from the 2017 Economic Census

   year = '2017'
   dataset_acronym = '/ecnbasic'
   variables = 'NAICS2017_LABEL,NAICS2017,GEO_ID,FIRM,PAYANN'
   location = 'state:51'
   census = Census(api_key=acs_key)

   t = census.get_census(year, dataset_acronym, variables, location)
   print(t)

API
====

.. autoclass:: parsons.census.census.Census
   :inherited-members:
   :members:
