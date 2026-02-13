Shopify
=========

********
Overview
********

`Shopify <https://www.shopify.com/>`_ is an e-commerce platform for online stores. This Parsons integration with the `Shopify REST API <https://shopify.dev/api/admin/rest/reference>`_ supports fetching records of orders.

.. note::

  Authentication
    Shopify supports different types of authentication methods for different types of apps, which are documented `here <https://shopify.dev/apps/auth>`_.

**********
Quickstart
**********

To instantiate the Shopify class, you can either store your Shopify API subdomain, password, key, and version as environmental variables (``SHOPIFY_SUBDOMAIN``, ``SHOPIFY_PASSWORD``, ``SHOPIFY_API_KEY``, and ``SHOPIFY_API_VERSION``, respectively) or pass in your subdomain, password, key, and version as arguments:

.. code-block:: python

   from parsons import Shopify

   # First approach: Use API credentials via environmental variables
   shopify = Shopify()

   # Second approach: Pass API credentials as arguments
   shopify = Shopify(subdomain='mysubdomain', password='1234', api_key='1234', api_version='2020-10')

You can then call various endpoints:

.. code-block:: python

    # Fetch orders
    orders = shopify.get_orders()

***
API
***

.. autoclass:: parsons.shopify.Shopify
   :inherited-members:
   :members:
   