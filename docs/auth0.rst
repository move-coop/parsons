#####
Auth0
#####

Overview
========

`Auth0 <https://auth0.com/>`_ is an authentication and authorization platform. This Parsons integration with the `Auth0 Management API <https://auth0.com/docs/api/management/v2>`_ supports fetching and deleting user records.

Quickstart
==========

To instantiate the :class:`~parsons.auth0.auth0.Auth0` class, you can either store your Auth0 API client ID, client secret, and domain as environment variables (``AUTH0_CLIENT_ID``, ``AUTH0_CLIENT_SECRET``, and ``AUTH0_DOMAIN``, respectively) or pass in your client ID, client secret, and domain as arguments:

.. code-block:: python
   :caption: Use API credentials via environmental variables

   from parsons import Auth0
   auth0 = Auth0()

.. code-block:: python
   :caption: Pass API credentials as arguments

   from parsons import Auth0
   auth0 = Shopify('auth0_client_id', 'auth0_client_secret', 'auth0_domain')

You can then call various endpoints:

.. code-block:: python
   :caption: Fetch user by email

   user = auth0.get_users_by_email('fakeemail@fakedomain.com')

API
====

.. autoclass:: parsons.auth0.auth0.Auth0
   :inherited-members:
   :members:
