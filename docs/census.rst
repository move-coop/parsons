Census
=============

********
Overview
********

Connects to the `Census API <https://www.census.gov/data/developers/guidance/api-user-guide.html>`_.
It has been tested with the ACS and Economic Survey endpoints.

.. note::

  Authentication
    The API requires a key that you can get `here <https://www.census.gov/data/developers.html>`_ (click on the box that says "Request a KEY")

==========
Quickstart
==========

To instantiate the Census class, either store your ``CENSUS_API_KEY`` as an environment
variable or pass it as an argument:

.. code-block:: python

   from parsons import Census

   # First approach: Use API key environment variables

   # In Mac OS, for example, set your environment variables like so:
   # export CENSUS_API_KEY='MY_CENSUS_KEY'

   census = ActBlue()

   # Second approach: Pass API key as arguments
   actblue = ActBlue(api_key = 'MY_CENSUS_KEY')

**Example 1**

.. code-block:: python

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

This example pulls the population of the US in 2019 from the ACS 1-year estimates.

**Example 2**

.. code-block:: python

   year = '2017'
   dataset_acronym = '/ecnbasic'
   variables = 'NAICS2017_LABEL,NAICS2017,GEO_ID,FIRM,PAYANN'
   location = 'state:51'
   census = Census(api_key=acs_key)

   t = census.get_census(year, dataset_acronym, variables, location)
   print(t)

This example pulls data on payroll by industry in Virginia from the 2017 Economic Census.

***
API
***

.. autoclass:: parsons.census.census.Census
   :inherited-members:
   :members:
   