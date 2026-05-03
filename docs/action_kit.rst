#########
ActionKit
#########

Overview
========

`ActionKit <https://actionkit.com/>`__ is a platform for advocacy, fundraising, and
get-out-the-vote. This Parsons integration with the
`ActionKit REST API <https://roboticdogs.actionkit.com/docs/manual/api/rest/overview.html>`__
supports fetching, creating, and updating records of campaigns, events, mailers, orders, survey questions,
transactions, and users. Bulk upload of new users and user updates is also supported.

.. admonition:: Authentication

   ActionKit requires `HTTP Basic Auth <https://en.wikipedia.org/wiki/Basic_access_authentication>`__.
   Clients with an ActionKit account can obtain the domain, username, and password needed to access the ActionKit API.
   See the `ActionKit API Authentication Documentation`_ for more information on obtaining ActionKit API credentials.

Quickstart
==========

To instantiate the :class:`~parsons.action_kit.action_kit.ActionKit` class, you can either store your ActionKit API
domain, username, and password as environmental variables (``ACTION_KIT_DOMAIN``,
``ACTION_KIT_USERNAME``, and ``ACTION_KIT_PASSWORD``, respectively) or pass in your
domain, username, and password as arguments:

.. code-block:: python
   :caption: Use API credentials via environmental variables

   from parsons import ActionKit
   ak = ActionKit()

.. code-block:: python
   :caption: Pass API credentials as arguments

   from parsons import ActionKit
   ak = ActionKit(domain='myorg.actionkit.com', username='my_name', password='1234')

You can then call various endpoints:

.. code-block:: python
   :caption: Create a new user

   ak.create_user(email='john@email', first_name='John', last_name='Smith', city='Boston')

.. code-block:: python
   :caption: Fetch user fields

   user_fields = ak.get_user(user_id='123')

.. code-block:: python
   :caption: Update user fields

   ak.update_user(user_id='123', city='New York')

.. code-block:: python
   :caption: Delete user

   ak.delete_user(user_id='123')

API
====

.. autoclass:: parsons.action_kit.action_kit.ActionKit
   :inherited-members:
   :members:

.. autoclass:: parsons.action_kit.action_kit.BulkCSVUploadResult
   :members:

.. autoclass:: parsons.action_kit.action_kit.BulkTableUploadResults
   :members:

.. autoclass:: parsons.action_kit.action_kit.UploadErrorResult
   :members:

.. _ActionKit API Authentication Documentation: https://roboticdogs.actionkit.com/docs/manual/api/rest/overview.html#authentication
.. _ActionKit API Action processing Documentation: https://roboticdogs.actionkit.com/docs/manual/api/rest/actionprocessing.html
.. _ActionKit API Ordering Documentation: https://roboticdogs.actionkit.com/docs/manual/api/rest/overview.html#ordering
.. _ActionKit API Uploads Documentation: https://roboticdogs.actionkit.com/docs/manual/api/rest/uploads.html
.. _ActionKit API Autocreate_user_fields Documentation: https://roboticdogs.actionkit.com/docs/manual/api/rest/uploads.html#create-a-multipart-post-request
.. _ActionKit API Users Documentation: https://roboticdogs.actionkit.com/docs/manual/api/rest/users.html
.. _ActionKit API Mailer Documentation: https://roboticdogs.actionkit.com/docs/manual/api/rest/mailer.html
.. _ActionKit API Event Search Examples: https://roboticdogs.actionkit.com/docs/manual/api/rest/examples/eventsearch.html
.. _ActionKit Email Blackhole Documentation: https://docs.actionkit.com/docs/manual/guide/mailings_tools.html#blackhole
.. _Django Field Lookup Documentation: https://docs.djangoproject.com/en/3.1/topics/db/queries/#field-lookups
