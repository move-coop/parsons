Scytl
=========

********
Overview
********

Scytl, or Clarity Elections, is a company that creates a tool for publishing election results in real-time. It's used in the U.S. by several states and over 800 counties, including Georgia, Colorado, Arkansas, and Dallas County. 

For each participating entity, they publish a site with results for every election night. Unfortunately, while that site contains downloadable data, that data is formatted in a complex way, making it difficult for developers to fetch election results. In general, their results either come zipped in either an unformatted text file or a complex XML document.

This connector provides methods to download the latest election results from their site and formats them into readable lists of dictionaries, which can easily be converted into a Parsons Table or Pandas dataframe.

**********
Quickstart
**********

To instantiate the Scytl class, ...

.. code-block:: python

   from parsons import Scytl

   scy = Scytl(state = 'GA', election_id = '114729')

   # Get all petitions
   scy.get_county_level_results()


**************
Scytl Class
**************

.. autoclass :: parsons.Scytl
    :inherited-members:
