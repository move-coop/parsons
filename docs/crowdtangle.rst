CrowdTangle
===========

********
Overview
********

`CrowdTangle <https://www.crowdtangle.com/>`_ is a Facebook-owned content monitoring and social monitoring platform.
This Parsons integration with the `CrowdTangle API <https://github.com/CrowdTangle/API/wiki>`_ supports getting posts
and leaderboard data.

.. note::

  Authentication
    An API Token is required to access the API. Assuming you have access to the CrowdTangle API, you can find the API
    Token in your dashboard under *Settings > API Access*. Contact your CrowdTangle representative for access.

.. note::

  Rate Limits
    The CrowdTangle API has strict rate limits that vary depending on the endpoint. In the ``CrowdTangle`` class, method
    docstrings indicate the rate limit for the relevant endpoint. For more information on rate limits and best practices
    for meeting them, check the `API documentation <https://help.crowdtangle.com/en/articles/1189612-crowdtangle-api>`_.

.. note::

  Performance
    CrowdTangle queries are expensive because they search and score billions of posts. Calls should be made from your
    server and stored in order to avoid making API calls every time someone hits your app server.

**********
Quickstart
**********

To instantiate the CrowdTangle class,either store your CrowdTangle API as the environmental variable
``CROWDTANGLE_API_KEY`` or pass it as a keyword argument:

.. code-block:: python

   from parsons import CrowdTangle

   # First approach: Use environmental variable for API Key
   ct = CrowdTangle()

   # Second approach: Pass API Key as argument
   ct = CrowdTangle(api_key='my_api_key')

   # Get posts matching the given parameters
   ct.get_posts(start_date='2020-06-01', min_interactions=50, search_term='test',
                types=['live_video', 'live_video_complete'])

***
API
***

.. autoclass:: parsons.crowdtangle.crowdtangle.CrowdTangle
   :inherited-members:
   :members:
   