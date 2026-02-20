Scytl
=========

********
Overview
********

Scytl, or Clarity Elections, is a company that creates a tool for publishing election results in real-time. It's used in the U.S. by several states and over 800 counties, including Georgia, Colorado, Arkansas, and Dallas County, Texas.

For each participating election administrator, they publish a site with results that can be published on election night. Unfortunately, while that site contains downloadable data, that data is formatted in a complex way, making it difficult for developers to fetch election results. In general, their results either come zipped in either an unformatted text file or a complex XML document. Summary results come as a zipped CSV, but just contain top-line results. The JSON that powers the site results is even more complicated.

This connector provides methods to download the latest election results from their site and formats them into readable lists of dictionaries, which can easily be converted into a Parsons Table or Pandas dataframe.

Because this connector is can be useful for live reporting, it also contains a polling feature. As long as the class is instantiated, it will only fetch results that are new since the previous fetch of that method. To skip this feature, set force_update to true on any of the fetch methods.

.. note::

  Authentication
    All endpoints for Scytl are public, and do not need authentication.

**********
Quickstart
**********

To get started, initialize a Scytl class with the two-letter state code, the election id, and the county name (optional).

To get these details, go to the website for the given election, and look in the url. For example, if the url is "https://results.enr.clarityelections.com/TX/Dallas/114890/web.285569/", then the state is "TX", the county is "Dallas", and the election ID is "114890". If the url is "https://results.enr.clarityelections.com/GA/114729/web.285569/", the state is "GA" and the election ID is "114729".

.. code-block:: python

   from parsons import Scytl

   scy = Scytl(state = 'GA', election_id = '114729')

   # Get detailed results by geography
   scy.get_detailed_results()


***********
Scytl Class
***********

.. autoclass:: parsons.scytl.scytl.Scytl
   :inherited-members:
   :members:
   