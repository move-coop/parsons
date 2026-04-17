#######
Shopify
#######

Overview
========

`Shopify <https://www.shopify.com/>`__ is an e-commerce platform for online stores.
This Parsons integration with the `Shopify REST API <https://shopify.dev/api/admin/rest/reference>`__ supports fetching records of orders.

.. admonition:: Authentication

   Shopify supports different types of authentication methods for different types of apps, which are documented `here <https://shopify.dev/apps/auth>`__.

Quickstart
==========

To instantiate the :class:`~parsons.shopify.shopify.Shopify` class, you can either store your Shopify API subdomain, password, key, and version as environmental variables
(``SHOPIFY_SUBDOMAIN``, ``SHOPIFY_PASSWORD``, ``SHOPIFY_API_KEY``, and ``SHOPIFY_API_VERSION``, respectively)
or pass in your subdomain, password, key, and version as arguments.

.. code-block:: python
   :caption: Use API credentials via environmental variables

   from parsons import Shopify
   shopify = Shopify()

.. code-block:: python
   :caption: Pass API credentials as arguments

   from parsons import Shopify
   shopify = Shopify(subdomain='mysubdomain', password='1234', api_key='1234', api_version='2020-10')

You can then call various endpoints:

.. code-block:: python
   :caption: Fetch orders

   orders = shopify.get_orders()

API
====

.. autoclass:: parsons.shopify.Shopify
   :inherited-members:
   :members:
