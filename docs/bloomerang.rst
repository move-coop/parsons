##########
Bloomerang
##########

Overview
========

`Bloomerang <https://bloomerang.com/>`__ is a donor management platform for non-profits.
This Parsons integration with the private `Bloomerang REST API Documentation`_
supports fetching, creating, and updating records of constituents, donations, and interactions.

.. admonition:: Authentication

   Authentication credentials can be created by Bloomerang database Administrator User.
   There are two authentication options for the private REST API, both of which are
   supported by Parsons:

   1. Use a private API Key (less secure)
   2. Use OAuth2 authentication, requiring a ``client_id`` and ``client_secret`` (more secure)

   See the `Bloomerang REST API Documentation`_ for more information on API authentication.

Quickstart
==========

To instantiate the :class:`~parsons.bloomerang.bloomerang.Bloomerang` class,
you can either store your Bloomerang private API key / OAuth2 credentialsas environmental variables
(``BLOOMERANG_API_KEY`` for the private key approach
or ``BLOOMERANG_CLIENT_ID`` and ``BLOOMERANG_CLIENT_SECRET`` for the OAuth2 approach)
or pass in your API Key / OAuth2 credentials as arguments:

.. code-block:: python
   :caption: Use environmental variables

   from parsons import Bloomerang
   bloomerang = Bloomerang()

.. code-block:: python
   :caption: Pass private API key as argument

   from parsons import Bloomerang
   bloomerang = Bloomerang(api_key='my_key')

.. code-block:: python
   :caption: Pass OAuth2 client_id and client_secret as arguments

   from parsons import Bloomerang
   bloomerang = Bloomerang(client_id='my_client_id', client_secret='my_client_secret')

You can then call various endpoints:

.. code-block:: python
   :caption: Create constituent

   bloomerang.create_constituent(email='john@email', first_name='John', last_name='Smith', city='Boston')

.. code-block:: python
   :caption: Get constituent

   constituent = bloomerang.get_constituent(user_id='123')

.. code-block:: python
   :caption: Update constituent

   bloomerang.update_constituent(user_id='123', city='New York')

.. code-block:: python
   :caption: Delete constituent

   bloomerang.delete_constituent(user_id='123')

API
====

.. autoclass:: parsons.bloomerang.bloomerang.Bloomerang
   :inherited-members:
   :members:

.. _Bloomerang REST API Documentation: https://bloomerang.com/api/rest-api/
.. _Bloomerang post_constituent Documentation: https://bloomerang.com/api/rest-api/#/Constituents/post_constituent
.. _Bloomerang put_constituent__id_ Documentation: https://bloomerang.com/api/rest-api/#/Constituents/put_constituent__id_
.. _Bloomerang post_transaction Documentation: https://bloomerang.com/api/rest-api/#/Constituents/post_transaction
.. _Bloomerang put_transaction__id_ Documentation: https://bloomerang.com/api/rest-api/#/Constituents/put_transaction__id_
.. _Bloomerang post_interaction Documentation: https://bloomerang.com/api/rest-api/#/Constituents/post_interaction
.. _Bloomerang put_interaction__id_ Documentation: https://bloomerang.com/api/rest-api/#/Constituents/put_interaction__id_
