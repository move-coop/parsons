Redash
======

********
Overview
********

The ``Redash`` class allows you to interact with a `Redash server <https://redash.io/>`_ to fetch fresh or cached
query results as a Parsons Table.

.. note::

  Authentication
    The `Redash API <https://redash.io/help/user-guide/integrations-and-api/api>`_ has two types of API keys:
    *User API keys* which are found on user profile pages, and *Query API keys* which are found on query pages. The
    ``Redash`` class supports fetching fresh queries with a User API Key, and cached queries with a Query API Key.

**********
Quickstart
**********

When instantiating the ``Redash`` class, you must provide the base URL for your Redash instance, either as the
environmental variable ``REDASH_BASE_URL`` or as a keyword argument.

For fresh queries, a User API Key is also required, and can be specified with either the environmental variable
``REDASH_USER_API_KEY`` or a keyword argument.

.. code-block:: python

   from parsons import Redash

   # Instantiate class with the base URL and User API key as keyword arguments
   redash = Redash(base_url='www.example.com', user_api_key='my_user_api_key')

   # Fetch fresh query results
   redash.load_to_table(query_id=1001, params={'datelimit': '2020-01-01'})

To fetch cached queries, you must provide a Query API Key, either as the environmental variable ``REDASH_QUERY_API_KEY``
or as a keyword argument. You do not need a User API Key to fetch a cached query.

Note that if you specify a Query API Key when loading a table, the method will fetch cached results even if you
provided a User API Key when instantiating the class.

.. code-block:: python

   # Pass a Query API Key to fetch cached results
   redash.load_to_table(query_api_key='my_query_api_key', query_id=1001)

***
API
***

.. autoclass:: parsons.redash.redash.Redash
   :inherited-members:
   :members:
   