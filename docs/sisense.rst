Sisense
=========

********
Overview
********

`Sisense for Cloud Data Teams <https://www.sisense.com/product/data-teams/>`_ is a business intelligence software
formerly known as `Periscope Data <https://www.sisense.com/blog/periscope-data-is-now-sisense-for-cloud-data-teams/>`_,
with functionality including dashboards, data warehousing, data mining, and predictive analytics.

This Parsons integration with the `Sisense REST API v1.0 <https://sisense.dev/reference/rest/v1.html>`_ supports
fetching, posting, and deleting shared dashboards.

.. note::

  Authentication
    Your site name and an authentication token are required to use the ``Sisense`` class. To obtain a token, log in to
    the Sisense Web Application and follow the instructions in the `Sisense REST API documentation <https://sisense.dev/guides/rest/using-rest-api.html#authentication>`_.
    Be sure to select version ``1.0`` of the API.

**********
Quickstart
**********

To instantiate the ``Sisense`` class, you can either store your Sisense credentials as environmental variables
(``SISENSE_SITE_NAME`` and ``SISENSE_API_KEY``) or pass them as keyword arguments:

.. code-block:: python

   from parsons import Sisense

   # First approach: Pass authentication credentials with environmental variables
   sisense = Sisense()

   # Second approach: Pass authentication credentials as arguments
   sisense = Sisense(site_name='my_site_name', api_key='my_api_key')

You can then call various endpoints:

.. code-block:: python

    # Get all the shares for a dashboard
    sisense.list_shared_dashboards(dashboard_id='1234')

    # Publish a dashboard
    sisense.publish_shared_dashboard(dashboard_id='1234')

    # Publish a chart
    sisense.publish_shared_dashboard(dashboard_id='1234', chart_id='567')

    # Delete a dashboard
    sisense.delete_shared_dashboard(dashboard_id='1234')

***
API
***

.. autoclass:: parsons.sisense.sisense.Sisense
   :inherited-members:
   :members:
   