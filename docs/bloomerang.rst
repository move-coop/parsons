Bloomerang
==========

********
Overview
********

`Bloomerang <https://bloomerang.co/>`_ is a donor management platform for non-profits. This Parsons integration with
the private `Bloomerang REST API <https://bloomerang.co/features/integrations/api/rest-api>`_
supports fetching, creating, and updating records of constituents, donations, and interactions.

.. note::

  Authentication
    Authentication credentials can be created by Bloomerang database Administrator User.
    There are two authentication options for the private REST API, both of which are
    supported by Parsons:

    1. Use a private API Key (less secure)
    2. Use OAuth2 authentication, requiring a ``client_id`` and ``client_secret`` (more secure)

    See the `Bloomerang REST API documentation <https://bloomerang.co/features/integrations/api/rest-api>`_
    for more information on API authentication.

**********
Quickstart
**********

To instantiate the Bloomerang class, you can either store your Bloomerang private API key /
OAuth2 credentials as environmental variables (``BLOOMERANG_API_KEY`` for the private
key approach, ``BLOOMERANG_CLIENT_ID`` and ``BLOOMERANG_CLIENT_SECRET`` for the OAuth2
approach) or pass in your API Key / OAuth2 credentials as arguments:

.. code-block:: python

   from parsons import Bloomerang

   # First approach: Use environmental variables
   bloomerang = Bloomerang()

   # Second approach: Pass private API key as argument
   bloomerang = Bloomerang(api_key='my_key')

   # Third approach: Pass OAuth2 client_id and client_secret as arguments
   bloomerang = Bloomerang(client_id='my_client_id', client_secret='my_client_secret')

You can then call various endpoints:

.. code-block:: python

    # Create constituent
    bloomerang.create_constituent(email='john@email', first_name='John', last_name='Smith', city='Boston')

    # Get constituent
    constituent = bloomerang.get_constituent(user_id='123')

    # Update constituent
    bloomerang.update_constituent(user_id='123', city='New York')

    # Delete constituent
    bloomerang.delete_constituent(user_id='123')

***
API
***

.. autoclass:: parsons.bloomerang.bloomerang.Bloomerang
   :inherited-members:
   :members:
   