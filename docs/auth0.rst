Auth0
=========

********
Overview
********

`Auth0 <https://auth0.com/>`_ is an authentication and authorization platform. This Parsons integration with the `Auth0 Management API <https://auth0.com/docs/api/management/v2>`_ supports fetching and deleting user records.

**********
Quickstart
**********

To instantiate the Auth0 class, you can either store your Auth0 API client ID, client secret, and domain as environment variables (``AUTH0_CLIENT_ID``, ``AUTH0_CLIENT_SECRET``, and ``AUTH0_DOMAIN``, respectively) or pass in your client ID, client secret, and domain as arguments:

.. code-block:: python

   from parsons import Auth0

   # First approach: Use API credentials via environmental variables
   auth0 = Auth0()

   # Second approach: Pass API credentials as arguments
   auth0 = Shopify('auth0_client_id', 'auth0_client_secret', 'auth0_domain')

You can then call various endpoints:

.. code-block:: python

    # Fetch user by email
    user = auth0.get_users_by_email('fakeemail@fakedomain.com')

***
API
***

.. autoclass:: parsons.auth0.auth0.Auth0
   :inherited-members:
   :members:
   