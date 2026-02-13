ActionKit
=========

********
Overview
********

`ActionKit <https://actionkit.com/>`_ is a platform for advocacy, fundraising, and
get-out-the-vote. This Parsons integration with the
`ActionKit REST API <https://roboticdogs.actionkit.com/docs/manual/api/rest/overview.html>`_
supports fetching, creating, and updating records of campaigns, events, mailers, orders, survey questions, transactions, and users.
Bulk upload of new users and user updates is also supported.

.. note::

  Authentication
    ActionKit requires `HTTP Basic Auth <https://en.wikipedia.org/wiki/Basic_access_authentication>`_.
    Clients with an ActionKit account can obtain the domain, username, and password needed
    to access the ActionKit API. See the `ActionKit REST API Authentication <https://roboticdogs.actionkit.com/docs/manual/api/rest/overview.html#authentication>`_
    documentation for more information on obtaining ActionKit API credentials.

**********
Quickstart
**********

To instantiate the ActionKit class, you can either store your ActionKit API
domain, username, and password as environmental variables (``ACTION_KIT_DOMAIN``,
``ACTION_KIT_USERNAME``, and ``ACTION_KIT_PASSWORD``, respectively) or pass in your
domain, username, and password as arguments:

.. code-block:: python

   from parsons import ActionKit

   # First approach: Use API credentials via environmental variables
   ak = ActionKit()

   # Second approach: Pass API credentials as arguments
   ak = ActionKit(domain='myorg.actionkit.com', username='my_name', password='1234')

You can then call various endpoints:

.. code-block:: python

    # Create a new user
    ak.create_user(email='john@email', first_name='John', last_name='Smith', city='Boston')

    # Fetch user fields
    user_fields = ak.get_user(user_id='123')

    # Update user fields
    ak.update_user(user_id='123', city='New York')

    # Delete user
    ak.delete_user(user_id='123')

***
API
***

.. autoclass:: parsons.action_kit.action_kit.ActionKit
   :inherited-members:
   :members:
   